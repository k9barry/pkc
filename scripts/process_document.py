#!/usr/bin/env python3
"""
Document Processing Module

Handles document processing including text extraction, chunking, 
embedding generation, and storage in Qdrant.
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Document parsers
import PyPDF2
from docx import Document
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://192.168.9.98:30333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.9.98:30068")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "pkc_documents")
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


class DocumentProcessor:
    """Document processor for PKC."""
    
    def __init__(self):
        """Initialize the document processor."""
        self.qdrant = QdrantClient(url=QDRANT_URL)
        self.ollama_url = OLLAMA_URL
        self.collection = COLLECTION_NAME
        self.embedding_model = EMBEDDING_MODEL
    
    def extract_text(self, file_path: Path) -> Optional[str]:
        """
        Extract text from a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text or None if extraction failed
        """
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.txt' or suffix == '.md':
                return file_path.read_text(encoding='utf-8')
            
            elif suffix == '.pdf':
                text = []
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text.append(page.extract_text())
                return '\n'.join(text)
            
            elif suffix in ['.docx', '.doc']:
                doc = Document(file_path)
                return '\n'.join([para.text for para in doc.paragraphs])
            
            elif suffix == '.html':
                html = file_path.read_text(encoding='utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text()
            
            else:
                print(f"Unsupported file type: {suffix}")
                return None
                
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return None
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > CHUNK_SIZE // 2:
                    end = start + break_point + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - CHUNK_OVERLAP
        
        return [c for c in chunks if c]
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using Ollama.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if generation failed
        """
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                print(f"Embedding generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def compute_hash(self, text: str) -> str:
        """
        Compute hash of text for deduplication.
        
        Args:
            text: Text to hash
            
        Returns:
            Hash string
        """
        return hashlib.sha256(text.encode()).hexdigest()
    
    def store_chunks(
        self, 
        chunks: List[str], 
        metadata: Dict,
        file_path: Path
    ) -> int:
        """
        Store document chunks in Qdrant.
        
        Args:
            chunks: List of text chunks
            metadata: Document metadata
            file_path: Original file path
            
        Returns:
            Number of chunks stored
        """
        points = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self.generate_embedding(chunk)
            if not embedding:
                print(f"Skipping chunk {i+1} due to embedding failure")
                continue
            
            # Create point
            point_id = self.compute_hash(f"{file_path}_{i}")
            point_metadata = {
                "text": chunk,
                "source": str(file_path),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
            
            points.append(PointStruct(
                id=point_id,
                vector=embedding,
                payload=point_metadata
            ))
        
        # Store in Qdrant
        try:
            self.qdrant.upsert(
                collection_name=self.collection,
                points=points
            )
            return len(points)
        except Exception as e:
            print(f"Error storing chunks in Qdrant: {e}")
            return 0
    
    def process_file(
        self, 
        file_path: Path,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Process a document file end-to-end.
        
        Args:
            file_path: Path to the document file
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Processing: {file_path.name}")
        
        # Extract text
        text = self.extract_text(file_path)
        if not text:
            print(f"✗ Failed to extract text from {file_path.name}")
            return False
        
        print(f"  - Extracted {len(text)} characters")
        
        # Chunk text
        chunks = self.chunk_text(text)
        print(f"  - Created {len(chunks)} chunks")
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "filename": file_path.name,
            "file_type": file_path.suffix,
            "file_size": file_path.stat().st_size
        })
        
        # Store chunks
        stored = self.store_chunks(chunks, metadata, file_path)
        
        if stored > 0:
            print(f"  - Stored {stored} chunks in Qdrant")
            print(f"✓ Successfully processed {file_path.name}")
            return True
        else:
            print(f"✗ Failed to store chunks from {file_path.name}")
            return False


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python process_document.py <file_path> [metadata_key=value ...]")
        return 1
    
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print(f"✗ File not found: {file_path}")
        return 1
    
    # Parse metadata from command line
    metadata = {}
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            metadata[key] = value
    
    # Process file
    processor = DocumentProcessor()
    success = processor.process_file(file_path, metadata)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
