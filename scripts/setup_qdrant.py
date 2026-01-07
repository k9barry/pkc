#!/usr/bin/env python3
"""
Qdrant Collection Setup Script

Initializes the Qdrant collection for storing document embeddings.
"""

import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Load environment variables
load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://192.168.9.98:30333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "pkc_documents")
VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE", "768"))
DISTANCE_METRIC = os.getenv("QDRANT_DISTANCE_METRIC", "Cosine")

# Map distance metric string to Qdrant Distance enum
DISTANCE_MAP = {
    "Cosine": Distance.COSINE,
    "Euclidean": Distance.EUCLID,
    "Dot": Distance.DOT
}


def setup_collection():
    """
    Create or recreate the Qdrant collection.
    """
    print("=" * 60)
    print("Personal Knowledge Cloud - Qdrant Setup")
    print("=" * 60)
    print()
    
    # Connect to Qdrant
    print(f"Connecting to Qdrant at {QDRANT_URL}...")
    try:
        client = QdrantClient(url=QDRANT_URL)
    except Exception as e:
        print(f"✗ Failed to connect to Qdrant: {e}")
        return 1
    
    print("✓ Connected to Qdrant")
    print()
    
    # Check if collection exists
    try:
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if COLLECTION_NAME in collection_names:
            print(f"Collection '{COLLECTION_NAME}' already exists.")
            response = input("Do you want to recreate it? (y/N): ")
            
            if response.lower() == 'y':
                print(f"Deleting collection '{COLLECTION_NAME}'...")
                client.delete_collection(collection_name=COLLECTION_NAME)
                print("✓ Collection deleted")
            else:
                print("Keeping existing collection")
                return 0
    except Exception as e:
        print(f"Warning: Could not check existing collections: {e}")
    
    # Create collection
    print()
    print(f"Creating collection '{COLLECTION_NAME}'...")
    print(f"  - Vector size: {VECTOR_SIZE}")
    print(f"  - Distance metric: {DISTANCE_METRIC}")
    
    try:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=DISTANCE_MAP.get(DISTANCE_METRIC, Distance.COSINE)
            )
        )
        print("✓ Collection created successfully")
    except Exception as e:
        print(f"✗ Failed to create collection: {e}")
        return 1
    
    # Verify collection
    try:
        info = client.get_collection(collection_name=COLLECTION_NAME)
        print()
        print("Collection info:")
        print(f"  - Name: {info.config.params}")
        print(f"  - Vectors count: {info.vectors_count}")
        print(f"  - Points count: {info.points_count}")
    except Exception as e:
        print(f"Warning: Could not retrieve collection info: {e}")
    
    print()
    print("=" * 60)
    print("✓ Qdrant setup completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(setup_collection())
