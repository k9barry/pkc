# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-01-07

### Security
- Updated `aiohttp` from 3.9.1 to 3.13.3
  - Fixed zip bomb vulnerability (CVE)
  - Fixed Denial of Service vulnerability in POST request parsing
  - Fixed directory traversal vulnerability
- Updated `langchain-community` from 0.0.10 to 0.3.27
  - Fixed XML External Entity (XXE) attack vulnerability
  - Fixed SSRF vulnerability in RequestsToolkit component
  - Fixed pickle deserialization of untrusted data vulnerability
- Updated `qdrant-client` from 1.7.0 to 1.9.0
  - Fixed input validation failure vulnerability

## [1.0.0] - 2024-01-07

### Added
- Initial release of Personal Knowledge Cloud (PKC) v2
- Integration with TrueNAS Scale v25.04
- OpenWebUI integration for user interface
- Ollama integration for local LLM inference and embeddings
- Qdrant vector database integration for semantic search
- n8n workflow automation platform integration

#### File Processing
- Document text extraction for PDF, DOCX, DOC, TXT, MD, HTML formats
- Intelligent text chunking with configurable size and overlap
- Vector embedding generation using Ollama models
- Automatic storage in Qdrant vector database
- Support for custom metadata tagging

#### Watch Folder
- Automatic monitoring of designated folder for new files
- Configurable scanning intervals
- Archive functionality for processed files
- Support for multiple file types
- Error handling and logging

#### Gmail Integration
- OAuth2 authentication with Gmail API
- Automated email fetching based on filters
- Email content extraction and processing
- Attachment handling and processing
- Deduplication tracking
- Configurable fetch intervals

#### n8n Workflows
- File upload workflow with webhook endpoint
- Watch folder workflow with scheduled triggers
- Gmail integration workflow with email processing
- Modular and extensible workflow design

#### Python Scripts
- `check_services.py` - Service health monitoring
- `setup_qdrant.py` - Qdrant collection initialization
- `gmail_auth.py` - Gmail OAuth2 authentication setup
- `process_document.py` - Document processing engine
- `upload_file.py` - File upload helper

#### Configuration
- Environment-based configuration (.env)
- Qdrant configuration templates
- Ollama model recommendations
- Docker Compose reference configuration

#### Documentation
- Comprehensive README with architecture overview
- Detailed setup guide (SETUP.md)
- API documentation (API.md)
- Troubleshooting guide (TROUBLESHOOTING.md)
- Contributing guidelines (CONTRIBUTING.md)

#### Developer Tools
- Quickstart script for easy setup
- Virtual environment support
- Requirements file for Python dependencies
- Git ignore rules
- MIT License

### Technical Details
- Python 3.9+ support
- Async processing capabilities
- Modular architecture
- RESTful API integration
- Vector similarity search
- Semantic document retrieval

### Infrastructure
- TrueNAS Scale v25.04 compatibility
- Docker container support
- Network-based service communication
- Persistent storage configuration

## [Unreleased]

### Planned Features
- Additional file format support (CSV, XLSX, PPTX)
- Advanced search filters and faceted search
- Multi-language support
- Web UI for file upload and search
- Real-time document preview
- Batch processing optimization
- Cloud storage integration (Dropbox, OneDrive)
- Additional email provider support (Outlook, ProtonMail)
- Metrics and monitoring dashboard
- Unit and integration tests
- CI/CD pipeline
- Docker Hub images
- Kubernetes deployment manifests

### Known Issues
- None reported yet

## Links

- [Repository](https://github.com/k9barry/pkc)
- [Issues](https://github.com/k9barry/pkc/issues)
- [Pull Requests](https://github.com/k9barry/pkc/pulls)

## Version History

- **1.0.0** (2024-01-07) - Initial release with core functionality
