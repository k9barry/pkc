# Detailed Setup Guide

This guide provides step-by-step instructions for setting up the Personal Knowledge Cloud system.

## Prerequisites Verification

### 1. Verify TrueNAS Services

Before starting, ensure all services are running on your TrueNAS Scale server (192.168.9.98):

```bash
# Test OpenWebUI
curl http://192.168.9.98:31028

# Test Ollama
curl http://192.168.9.98:30068/api/tags

# Test Qdrant
curl http://192.168.9.98:30333/collections

# Test n8n
curl http://192.168.9.98:30109
```

All services should respond without connection errors.

## Step 1: Initial Setup

### Clone the Repository

```bash
git clone https://github.com/k9barry/pkc.git
cd pkc
```

### Install Python Dependencies

#### Option 1: Standard Installation (Most Systems)

```bash
# Recommended: Use a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: TrueNAS or Systems Without python3-venv Package

If you encounter an error like "ensurepip is not available" on TrueNAS or similar systems where package management is restricted:

```bash
# Create virtual environment without pip
python3 -m venv --without-pip venv
source venv/bin/activate

# Manually install pip using get-pip.py (official PyPA bootstrap script)
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
rm get-pip.py

# Install dependencies
pip install -r requirements.txt
```

**Note for TrueNAS users**: Since TrueNAS restricts package management tools like `apt`, the `--without-pip` method allows you to create a virtual environment and then manually bootstrap pip without requiring system package installation.

**Security note**: The `get-pip.py` script is downloaded from the official Python Packaging Authority (PyPA) over HTTPS. If you want additional security, you can verify the script before running it by comparing checksums available at https://pip.pypa.io/en/stable/installation/

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file with your settings. Key configurations:

```env
PKC_SERVER_IP=192.168.9.98
WATCH_FOLDER_PATH=/path/to/your/watch/folder
WATCH_FOLDER_ARCHIVE_PATH=/path/to/archive
```

## Step 2: Qdrant Setup

### Initialize Qdrant Collection

```bash
python scripts/setup_qdrant.py
```

This will:
1. Connect to Qdrant
2. Create the `pkc_documents` collection
3. Configure vector dimensions based on your embedding model

### Verify Collection

```bash
curl http://192.168.9.98:30333/collections/pkc_documents
```

## Step 3: Ollama Model Setup

### Pull Required Models

```bash
# Pull embedding model
curl http://192.168.9.98:30068/api/pull -d '{"name": "nomic-embed-text"}'

# Pull LLM model (optional, for testing)
curl http://192.168.9.98:30068/api/pull -d '{"name": "llama2"}'
```

### Verify Models

```bash
curl http://192.168.9.98:30068/api/tags
```

## Step 4: Gmail API Setup

### Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Personal Knowledge Cloud"
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Configure consent screen if prompted:
   - User Type: External
   - App name: Personal Knowledge Cloud
   - User support email: Your email
   - Developer contact: Your email
4. Application type: Desktop app
5. Name: PKC Desktop Client
6. Click "Create"
7. Download the JSON file
8. Save as `config/gmail_credentials.json`

### Authenticate Gmail

```bash
python scripts/gmail_auth.py
```

This will:
1. Open a browser for authentication
2. Request permission to read Gmail
3. Save credentials for future use

## Step 5: Watch Folder Setup

### Create Watch and Archive Folders

```bash
# Create folders (adjust paths as needed)
mkdir -p /mnt/user/pkc/watch
mkdir -p /mnt/user/pkc/archive

# Set permissions
chmod 755 /mnt/user/pkc/watch
chmod 755 /mnt/user/pkc/archive
```

### Update Environment

Edit `.env`:

```env
WATCH_FOLDER_PATH=/mnt/user/pkc/watch
WATCH_FOLDER_ARCHIVE_PATH=/mnt/user/pkc/archive
WATCH_FOLDER_ARCHIVE=true
```

## Step 6: n8n Workflow Import

### Access n8n

Open your browser and navigate to:
```
http://192.168.9.98:30109
```

### Import Workflows

1. Click on "Workflows" in the sidebar
2. Click "Import from File"
3. Import each workflow file:
   - `n8n-workflows/file-upload-workflow.json`
   - `n8n-workflows/watch-folder-workflow.json`
   - `n8n-workflows/gmail-integration-workflow.json`

### Configure Workflows

For each workflow:

#### File Upload Workflow
1. Open the workflow
2. Update "Process Document" node:
   - Set correct path to `process_document.py` script
3. Save and activate

#### Watch Folder Workflow
1. Open the workflow
2. Set schedule (default: every 5 minutes)
3. Update "Find New Files" node with correct watch folder path
4. Update "Process File" node with correct script path
5. Save and activate

#### Gmail Integration Workflow
1. Open the workflow
2. Configure Gmail OAuth2 credentials:
   - Click on "Get Emails" node
   - Add new credential
   - Use the credentials from Google Cloud Console
3. Update schedule (default: every 15 minutes)
4. Update script paths in processing nodes
5. Save and activate

## Step 7: Test the System

### Test Service Health

```bash
python scripts/check_services.py
```

All services should show as operational.

### Test File Upload

```bash
# Create a test file
echo "This is a test document for PKC." > test.txt

# Upload via script
python scripts/upload_file.py test.txt title="Test Document"
```

### Test Watch Folder

```bash
# Copy a file to watch folder
cp test.txt /mnt/user/pkc/watch/

# Wait for the next scheduled run (5 minutes by default)
# Or trigger manually in n8n
```

### Test Document Processing

```bash
# Process a document directly
python scripts/process_document.py test.txt source=test
```

### Verify in Qdrant

```bash
# Check collection stats
curl http://192.168.9.98:30333/collections/pkc_documents

# Search for test content
curl -X POST http://192.168.9.98:30333/collections/pkc_documents/points/search \
  -H 'Content-Type: application/json' \
  -d '{
    "vector": [0.1, 0.2, ...],  # Use actual embedding
    "limit": 5
  }'
```

## Step 8: OpenWebUI Configuration

### Access OpenWebUI

Open your browser and navigate to:
```
http://192.168.9.98:31028
```

### Configure RAG (Retrieval Augmented Generation)

1. Go to Settings
2. Navigate to "Document Collections"
3. Configure Qdrant connection:
   - URL: `http://192.168.9.98:30333`
   - Collection: `pkc_documents`
4. Configure Ollama:
   - URL: `http://192.168.9.98:30068`
   - Model: `llama2`
   - Embedding Model: `nomic-embed-text`
5. Save settings

### Test Queries

1. Start a new chat
2. Enable RAG/Document search
3. Ask questions about your documents:
   - "What documents do I have about [topic]?"
   - "Summarize the document about [subject]"
   - "Find information about [query]"

## Troubleshooting

### Services Not Accessible

If any service is not accessible:

1. Check TrueNAS container status
2. Verify network connectivity
3. Check firewall rules
4. Review container logs in TrueNAS

### Qdrant Connection Issues

```bash
# Check Qdrant health
curl http://192.168.9.98:30333/healthz

# Check collection exists
curl http://192.168.9.98:30333/collections
```

### Ollama Model Issues

```bash
# List available models
curl http://192.168.9.98:30068/api/tags

# Test embedding generation
curl http://192.168.9.98:30068/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "test"
}'
```

### Gmail Authentication Issues

If authentication fails:

1. Verify OAuth2 credentials are correct
2. Check that Gmail API is enabled
3. Ensure you're using the correct Google account
4. Try re-running `python scripts/gmail_auth.py`
5. Delete `config/gmail_token.pickle` and re-authenticate

### Watch Folder Not Processing

1. Verify folder permissions
2. Check n8n workflow is activated
3. Review n8n execution logs
4. Verify supported file types in `.env`

### Document Processing Failures

Check logs for specific errors:

```bash
# Test document processing manually
python scripts/process_document.py /path/to/file.pdf
```

Common issues:
- Unsupported file format
- File too large
- Ollama model not available
- Qdrant connection failed

## Next Steps

1. **Customize workflows**: Adjust schedules and processing logic in n8n
2. **Add more models**: Pull additional Ollama models for different use cases
3. **Optimize embeddings**: Experiment with different embedding models
4. **Configure Gmail filters**: Set up labels and filters in Gmail for better organization
5. **Monitor performance**: Track Qdrant collection size and query performance
6. **Backup data**: Set up regular backups of Qdrant data

## Support

For additional help:
- Check the main README.md
- Review TROUBLESHOOTING.md
- Review n8n execution logs
- Check service logs in TrueNAS
