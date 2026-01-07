# Personal Knowledge Cloud (PKC) v2

A comprehensive Personal Knowledge Cloud system that integrates OpenWebUI, Ollama, Qdrant, and n8n to create an intelligent document management and retrieval system with email integration and automated file processing.

## Architecture Overview

This PKC implementation leverages four key services running on TrueNAS Scale v25.04:

- **OpenWebUI** (port 31028): User interface for interacting with AI models
- **Ollama** (port 30068): Local LLM inference engine
- **Qdrant** (port 30333): Vector database for semantic search
- **n8n** (port 30109): Workflow automation platform

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Personal Knowledge Cloud                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  OpenWebUI   │◄────►│    Ollama    │                   │
│  │  (UI Layer)  │      │ (LLM Engine) │                   │
│  └──────┬───────┘      └──────┬───────┘                   │
│         │                     │                            │
│         │                     │                            │
│         ▼                     ▼                            │
│  ┌──────────────────────────────────┐                     │
│  │           Qdrant                 │                     │
│  │      (Vector Database)           │                     │
│  └──────────────────────────────────┘                     │
│         ▲                                                  │
│         │                                                  │
│         │                                                  │
│  ┌──────┴───────────────────────────┐                     │
│  │            n8n                    │                     │
│  │    (Workflow Automation)          │                     │
│  └───────────────────────────────────┘                     │
│         ▲                                                  │
│         │                                                  │
│  ┌──────┴───────────────────────────┐                     │
│  │   File Upload | Watch Folder     │                     │
│  │         Gmail Integration         │                     │
│  └───────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. File Upload & Processing
- Manual file upload through web interface
- Automatic text extraction and chunking
- Vector embedding generation using Ollama
- Storage in Qdrant for semantic search

### 2. Watch Folder Monitoring
- Monitors designated folder for new files
- Automatic processing of supported file types (PDF, TXT, MD, DOCX)
- Periodic scanning with configurable intervals
- Error handling and logging

### 3. Gmail Integration
- OAuth2 authentication with Gmail API
- Automated email fetching based on filters
- Email content extraction and processing
- Attachment handling
- Deduplication and tracking

### 4. Semantic Search & Retrieval
- Vector-based semantic search using Qdrant
- Context-aware document retrieval
- Integration with OpenWebUI for natural language queries

## Prerequisites

- TrueNAS Scale v25.04 with Docker containers
- Services running:
  - OpenWebUI (192.168.9.98:31028)
  - Ollama (192.168.9.98:30068)
  - Qdrant (192.168.9.98:30333)
  - n8n (192.168.9.98:30109)
- Python 3.9+ (for utility scripts)
- Node.js 18+ (for n8n workflows)
- Gmail API credentials (for email integration)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/k9barry/pkc.git
cd pkc
```

### 2. Configure Environment

Copy the example environment file and configure with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Server Configuration
PKC_SERVER_IP=192.168.9.98

# Service Ports
OPENWEBUI_PORT=31028
OLLAMA_PORT=30068
QDRANT_PORT=30333
N8N_PORT=30109

# Watch Folder Configuration
WATCH_FOLDER_PATH=/path/to/watch/folder
WATCH_FOLDER_INTERVAL=60

# Gmail Configuration
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token

# Qdrant Configuration
QDRANT_COLLECTION_NAME=pkc_documents
QDRANT_VECTOR_SIZE=4096

# Ollama Configuration
OLLAMA_MODEL=llama2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (if using custom scripts)
npm install
```

### 4. Import n8n Workflows

1. Access n8n at `http://192.168.9.98:30109`
2. Import workflow files from `n8n-workflows/` directory:
   - `file-upload-workflow.json`
   - `watch-folder-workflow.json`
   - `gmail-integration-workflow.json`

### 5. Configure Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials and update `.env` file
6. Run the authentication helper:

```bash
python scripts/gmail_auth.py
```

## Usage

### Starting the System

All services should already be running on TrueNAS Scale. Verify they're accessible:

```bash
# Check service status
python scripts/check_services.py
```

### File Upload

#### Via n8n Webhook
```bash
curl -X POST http://192.168.9.98:30109/webhook/upload-file \
  -F "file=@document.pdf" \
  -F "metadata={\"title\":\"My Document\",\"source\":\"manual_upload\"}"
```

#### Via Python Script
```bash
python scripts/upload_file.py /path/to/document.pdf
```

### Watch Folder

1. Place files in the configured watch folder
2. The n8n workflow automatically detects and processes new files
3. Monitor processing status in n8n execution logs

### Gmail Integration

The Gmail workflow runs on a schedule (configurable in n8n):

1. Connects to Gmail using OAuth2
2. Fetches unread emails matching criteria
3. Extracts content and attachments
4. Processes and stores in Qdrant
5. Marks emails as processed

### Querying Your Knowledge Base

Use OpenWebUI at `http://192.168.9.98:31028`:

1. Ask natural language questions
2. The system retrieves relevant context from Qdrant
3. Ollama generates responses based on your documents

## Project Structure

```
pkc/
├── README.md                          # This file
├── .env.example                       # Environment configuration template
├── requirements.txt                   # Python dependencies
├── package.json                       # Node.js dependencies (optional)
├── n8n-workflows/                     # n8n workflow definitions
│   ├── file-upload-workflow.json
│   ├── watch-folder-workflow.json
│   └── gmail-integration-workflow.json
├── scripts/                           # Utility scripts
│   ├── check_services.py             # Service health check
│   ├── gmail_auth.py                 # Gmail OAuth setup
│   ├── upload_file.py                # File upload helper
│   ├── process_document.py           # Document processing logic
│   └── setup_qdrant.py               # Qdrant collection setup
├── config/                            # Configuration files
│   ├── qdrant_config.yaml
│   └── ollama_models.txt
└── docs/                              # Additional documentation
    ├── SETUP.md                       # Detailed setup guide
    ├── API.md                         # API documentation
    └── TROUBLESHOOTING.md            # Common issues and solutions
```

## Configuration

### Qdrant Collection

Initialize the Qdrant collection:

```bash
python scripts/setup_qdrant.py
```

This creates a collection with proper vector dimensions for the selected embedding model.

### Ollama Models

Ensure required models are available:

```bash
# List available models
curl http://192.168.9.98:30068/api/tags

# Pull embedding model if needed
curl http://192.168.9.98:30068/api/pull -d '{"name": "nomic-embed-text"}'
```

## Best Practices

### Security
- Store credentials in `.env` file (never commit to git)
- Use OAuth2 for Gmail (avoid app passwords)
- Implement rate limiting on webhook endpoints
- Regularly rotate API keys and tokens

### Performance
- Batch process documents when possible
- Use appropriate chunk sizes (recommended: 512-1024 tokens)
- Monitor Qdrant collection size and optimize as needed
- Configure appropriate n8n execution timeouts

### Data Management
- Implement deduplication logic for emails and files
- Regular backup of Qdrant data
- Archive processed files in watch folder
- Maintain metadata for source tracking

### Monitoring
- Set up n8n error notifications
- Monitor disk space for watch folder
- Track Qdrant collection metrics
- Log all processing activities

## Troubleshooting

### Services Not Accessible
```bash
# Check if services are running
curl http://192.168.9.98:31028  # OpenWebUI
curl http://192.168.9.98:30068  # Ollama
curl http://192.168.9.98:30333  # Qdrant
curl http://192.168.9.98:30109  # n8n
```

### Gmail Authentication Issues
- Verify OAuth2 credentials are correct
- Check token expiration
- Ensure Gmail API is enabled in Google Cloud Console
- Run `python scripts/gmail_auth.py` to re-authenticate

### File Processing Failures
- Check file format is supported
- Verify file size limits
- Review n8n execution logs
- Check Ollama model availability

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check documentation in `docs/` folder

## Acknowledgments

Built with:
- [OpenWebUI](https://github.com/open-webui/open-webui)
- [Ollama](https://ollama.ai/)
- [Qdrant](https://qdrant.tech/)
- [n8n](https://n8n.io/)
