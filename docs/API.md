# API Documentation

This document describes the APIs and endpoints available in the Personal Knowledge Cloud system.

## n8n Webhooks

### File Upload Webhook

Upload files directly to PKC for processing.

**Endpoint**: `POST http://192.168.9.98:30109/webhook/upload-file`

**Request**:
- Content-Type: `multipart/form-data`
- Body:
  - `file`: File to upload (binary)
  - `title`: Optional title for the document
  - `source`: Optional source identifier
  - Additional metadata fields as needed

**Example**:
```bash
curl -X POST http://192.168.9.98:30109/webhook/upload-file \
  -F "file=@document.pdf" \
  -F "title=My Document" \
  -F "source=manual_upload"
```

**Response**:
```json
{
  "success": true,
  "message": "File uploaded and processed successfully",
  "filename": "document.pdf",
  "timestamp": "2024-01-07T12:00:00.000Z"
}
```

## Ollama API

### Generate Embeddings

Generate vector embeddings for text.

**Endpoint**: `POST http://192.168.9.98:30068/api/embeddings`

**Request**:
```json
{
  "model": "nomic-embed-text",
  "prompt": "Text to embed"
}
```

**Response**:
```json
{
  "embedding": [0.123, -0.456, ...]
}
```

### List Models

Get list of available models.

**Endpoint**: `GET http://192.168.9.98:30068/api/tags`

**Response**:
```json
{
  "models": [
    {
      "name": "llama2",
      "modified_at": "2024-01-01T00:00:00.000Z",
      "size": 3825819519
    }
  ]
}
```

### Pull Model

Download a new model.

**Endpoint**: `POST http://192.168.9.98:30068/api/pull`

**Request**:
```json
{
  "name": "nomic-embed-text"
}
```

**Response**: Streaming JSON with progress updates

## Qdrant API

### Get Collection Info

Retrieve information about a collection.

**Endpoint**: `GET http://192.168.9.98:30333/collections/{collection_name}`

**Example**:
```bash
curl http://192.168.9.98:30333/collections/pkc_documents
```

**Response**:
```json
{
  "result": {
    "status": "green",
    "optimizer_status": "ok",
    "vectors_count": 1250,
    "points_count": 1250,
    "config": {
      "params": {
        "vectors": {
          "size": 768,
          "distance": "Cosine"
        }
      }
    }
  }
}
```

### Search Vectors

Search for similar documents.

**Endpoint**: `POST http://192.168.9.98:30333/collections/{collection_name}/points/search`

**Request**:
```json
{
  "vector": [0.123, -0.456, ...],
  "limit": 10,
  "with_payload": true,
  "with_vector": false,
  "score_threshold": 0.7
}
```

**Response**:
```json
{
  "result": [
    {
      "id": "abc123...",
      "version": 0,
      "score": 0.95,
      "payload": {
        "text": "Document content...",
        "source": "gmail",
        "filename": "email_123.txt",
        "timestamp": "2024-01-07T12:00:00.000Z"
      }
    }
  ]
}
```

### Upsert Points

Add or update documents in the collection.

**Endpoint**: `PUT http://192.168.9.98:30333/collections/{collection_name}/points`

**Request**:
```json
{
  "points": [
    {
      "id": "unique-id-123",
      "vector": [0.123, -0.456, ...],
      "payload": {
        "text": "Document content",
        "source": "manual",
        "metadata": {}
      }
    }
  ]
}
```

**Response**:
```json
{
  "result": {
    "operation_id": 0,
    "status": "completed"
  }
}
```

### Delete Points

Remove documents from the collection.

**Endpoint**: `POST http://192.168.9.98:30333/collections/{collection_name}/points/delete`

**Request**:
```json
{
  "points": ["id1", "id2", "id3"]
}
```

### Filter Search

Search with filters on metadata.

**Endpoint**: `POST http://192.168.9.98:30333/collections/{collection_name}/points/search`

**Request**:
```json
{
  "vector": [0.123, -0.456, ...],
  "limit": 10,
  "filter": {
    "must": [
      {
        "key": "source",
        "match": {
          "value": "gmail"
        }
      }
    ]
  }
}
```

## Python Scripts API

### process_document.py

Process a document file and store in Qdrant.

**Usage**:
```bash
python scripts/process_document.py <file_path> [metadata_key=value ...]
```

**Example**:
```bash
python scripts/process_document.py document.pdf source=manual title="My Doc"
```

**Returns**: Exit code 0 on success, 1 on failure

### upload_file.py

Upload a file via n8n webhook.

**Usage**:
```bash
python scripts/upload_file.py <file_path> [metadata_key=value ...]
```

**Example**:
```bash
python scripts/upload_file.py document.pdf title="My Document"
```

**Returns**: Exit code 0 on success, 1 on failure

### setup_qdrant.py

Initialize Qdrant collection.

**Usage**:
```bash
python scripts/setup_qdrant.py
```

**Interactive**: Will prompt before recreating existing collections

### gmail_auth.py

Set up Gmail OAuth2 authentication.

**Usage**:
```bash
python scripts/gmail_auth.py
```

**Interactive**: Opens browser for authentication

### check_services.py

Check health of all PKC services.

**Usage**:
```bash
python scripts/check_services.py
```

**Returns**: Exit code 0 if all services are healthy, 1 otherwise

## Python Module API

### DocumentProcessor Class

Process documents programmatically.

```python
from scripts.process_document import DocumentProcessor

# Initialize processor
processor = DocumentProcessor()

# Process a file
success = processor.process_file(
    Path('/path/to/document.pdf'),
    metadata={'source': 'api', 'title': 'My Document'}
)

# Extract text only
text = processor.extract_text(Path('/path/to/document.pdf'))

# Generate embedding
embedding = processor.generate_embedding("Some text to embed")

# Chunk text
chunks = processor.chunk_text(long_text)
```

### Methods

#### `extract_text(file_path: Path) -> Optional[str]`

Extract text from a document file.

**Supported formats**: .txt, .md, .pdf, .docx, .doc, .html

#### `chunk_text(text: str) -> List[str]`

Split text into overlapping chunks.

**Parameters**:
- `text`: Text to chunk
- Uses `CHUNK_SIZE` and `CHUNK_OVERLAP` from environment

#### `generate_embedding(text: str) -> Optional[List[float]]`

Generate vector embedding using Ollama.

**Parameters**:
- `text`: Text to embed

**Returns**: Vector embedding or None on failure

#### `process_file(file_path: Path, metadata: Optional[Dict] = None) -> bool`

Process a document end-to-end.

**Steps**:
1. Extract text
2. Chunk text
3. Generate embeddings
4. Store in Qdrant

**Returns**: True on success, False on failure

## OpenWebUI API

OpenWebUI provides its own API for chat and document management.

### Chat Completion

**Endpoint**: `POST http://192.168.9.98:31028/api/chat`

**Note**: Requires authentication. Refer to OpenWebUI documentation for details.

## Rate Limits and Considerations

### Ollama
- Local inference, no rate limits
- Processing time depends on model size and hardware
- Concurrent requests limited by available resources

### Qdrant
- No hard rate limits on local installation
- Performance depends on collection size and hardware
- Recommend batching upsert operations

### Gmail API
- 250 quota units per user per second
- 25,000 quota units per user per day
- Batch operations recommended for large volumes

### n8n
- Execution timeout: Configurable (default 2 minutes)
- Concurrent executions: Depends on server resources
- Webhook timeout: 120 seconds default

## Best Practices

### Document Processing
- Process files in batches when possible
- Monitor Qdrant collection size
- Use appropriate chunk sizes for your content
- Include meaningful metadata for better filtering

### Search Queries
- Use score thresholds to filter low-quality matches
- Combine vector search with metadata filters
- Cache frequently used embeddings
- Optimize limit parameter based on use case

### Error Handling
- Implement retry logic for network operations
- Log all processing errors
- Monitor n8n execution logs
- Set up alerts for repeated failures

### Security
- Keep OAuth2 credentials secure
- Use environment variables for configuration
- Implement access controls on webhooks
- Regularly rotate API keys and tokens

## Examples

### Complete Document Upload Flow

```python
import requests
from pathlib import Path

# 1. Upload file
file_path = Path('document.pdf')
webhook_url = 'http://192.168.9.98:30109/webhook/upload-file'

with open(file_path, 'rb') as f:
    response = requests.post(
        webhook_url,
        files={'file': (file_path.name, f)},
        data={'title': 'My Document', 'source': 'api'}
    )

print(response.json())

# 2. Wait for processing (handled by n8n)

# 3. Search for the document
from scripts.process_document import DocumentProcessor

processor = DocumentProcessor()
query_embedding = processor.generate_embedding("search query")

search_response = requests.post(
    'http://192.168.9.98:30333/collections/pkc_documents/points/search',
    json={
        'vector': query_embedding,
        'limit': 5,
        'with_payload': True
    }
)

results = search_response.json()
for result in results['result']:
    print(f"Score: {result['score']}")
    print(f"Text: {result['payload']['text'][:100]}...")
```

### Batch Processing

```python
from pathlib import Path
from scripts.process_document import DocumentProcessor

processor = DocumentProcessor()
folder = Path('/path/to/documents')

for file_path in folder.glob('*.pdf'):
    try:
        processor.process_file(
            file_path,
            metadata={'source': 'batch', 'batch_id': 'batch_001'}
        )
        print(f"Processed: {file_path.name}")
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
```

## Changelog

### Version 1.0.0
- Initial API release
- File upload webhook
- Document processing
- Qdrant integration
- Gmail integration
- OpenWebUI support
