# Troubleshooting Guide

Common issues and solutions for the Personal Knowledge Cloud system.

## Service Connection Issues

### Cannot Connect to Services

**Symptoms**: Scripts fail with connection errors

**Diagnosis**:
```bash
python scripts/check_services.py
```

**Solutions**:

1. **Verify services are running in TrueNAS**:
   - Log into TrueNAS web interface
   - Navigate to Apps
   - Check that all PKC containers are running
   - Restart any stopped containers

2. **Check network connectivity**:
   ```bash
   ping 192.168.9.98
   ```

3. **Verify ports are accessible**:
   ```bash
   telnet 192.168.9.98 31028  # OpenWebUI
   telnet 192.168.9.98 30068  # Ollama
   telnet 192.168.9.98 30333  # Qdrant
   telnet 192.168.9.98 30109  # n8n
   ```

4. **Check firewall rules**:
   - Ensure TrueNAS firewall allows connections on required ports
   - Check your local firewall settings

### Intermittent Connection Failures

**Cause**: Network timeouts or service overload

**Solutions**:
- Increase timeout values in scripts
- Reduce concurrent processing load
- Check TrueNAS system resources (CPU, memory, disk)

## Qdrant Issues

### Collection Not Found

**Error**: `Collection 'pkc_documents' not found`

**Solution**:
```bash
python scripts/setup_qdrant.py
```

### Wrong Vector Dimensions

**Error**: `Vector dimension mismatch`

**Cause**: Embedding model output doesn't match collection configuration

**Solution**:
1. Check embedding model dimensions:
   ```bash
   curl http://192.168.9.98:30068/api/show -d '{"name": "nomic-embed-text"}'
   ```

2. Update `.env`:
   ```env
   QDRANT_VECTOR_SIZE=768  # Must match model output
   ```

3. Recreate collection:
   ```bash
   python scripts/setup_qdrant.py
   ```

### Qdrant Out of Memory

**Symptoms**: Qdrant becomes unresponsive, high memory usage

**Solutions**:
1. Enable on-disk storage in `config/qdrant_config.yaml`
2. Increase memory allocation in TrueNAS
3. Reduce collection size:
   ```bash
   # Delete old documents
   curl -X POST http://192.168.9.98:30333/collections/pkc_documents/points/delete \
     -H 'Content-Type: application/json' \
     -d '{"filter": {"must": [{"key": "timestamp", "range": {"lt": "2024-01-01"}}]}}'
   ```

## Ollama Issues

### Model Not Found

**Error**: `Model 'nomic-embed-text' not found`

**Solution**:
```bash
# Pull the model
curl http://192.168.9.98:30068/api/pull -d '{"name": "nomic-embed-text"}'

# Wait for download to complete
# Verify
curl http://192.168.9.98:30068/api/tags
```

### Embedding Generation Timeout

**Symptoms**: Document processing hangs or times out

**Solutions**:
1. Check Ollama service status
2. Verify model is fully loaded:
   ```bash
   curl http://192.168.9.98:30068/api/embeddings -d '{
     "model": "nomic-embed-text",
     "prompt": "test"
   }'
   ```
3. Increase timeout in `process_document.py`
4. Use a lighter embedding model (e.g., all-minilm)

### Ollama Out of Resources

**Symptoms**: Slow generation, timeouts, errors

**Solutions**:
1. Check TrueNAS resource allocation
2. Unload unused models
3. Use smaller models
4. Increase Ollama container resources in TrueNAS

## Gmail Integration Issues

### Authentication Failed

**Error**: `Authentication failed` or `Invalid credentials`

**Solutions**:
1. Delete existing token:
   ```bash
   rm config/gmail_token.pickle
   ```

2. Re-authenticate:
   ```bash
   python scripts/gmail_auth.py
   ```

3. Verify OAuth2 credentials:
   - Check `config/gmail_credentials.json` exists
   - Verify client ID and secret are correct
   - Ensure Gmail API is enabled in Google Cloud Console

### No Emails Found

**Symptoms**: Gmail workflow finds no emails to process

**Solutions**:
1. Check Gmail query in `.env`:
   ```env
   GMAIL_QUERY=is:unread label:pkc
   ```

2. Verify the label exists in Gmail

3. Test query manually in Gmail search

4. Check OAuth2 permissions include Gmail read access

### Token Expired

**Error**: `Token has been expired or revoked`

**Solution**:
```bash
python scripts/gmail_auth.py
```

This will refresh the token.

### Rate Limit Exceeded

**Error**: `Rate limit exceeded`

**Solutions**:
1. Increase fetch interval in n8n workflow (default: 15 minutes)
2. Reduce `GMAIL_MAX_RESULTS` in `.env`
3. Implement exponential backoff in workflow

## Document Processing Issues

### Unsupported File Type

**Error**: `Unsupported file type: .xyz`

**Solution**:
1. Check supported types in `.env`:
   ```env
   SUPPORTED_FILE_TYPES=.pdf,.txt,.md,.docx,.doc,.html,.csv
   ```

2. Convert file to supported format

3. Add support for new format in `process_document.py`

### Text Extraction Failed

**Error**: `Failed to extract text from file`

**Causes and Solutions**:

1. **PDF is scanned/image-based**:
   - Use OCR tool first (e.g., tesseract)
   - Or skip and log error

2. **File is corrupted**:
   - Try opening in original application
   - Re-download or re-create file

3. **Missing dependencies**:
   ```bash
   pip install PyPDF2 python-docx beautifulsoup4
   ```

### Embedding Generation Failed

**Symptoms**: Processing completes but no vectors stored

**Diagnosis**:
```bash
# Test embedding generation
python -c "
from scripts.process_document import DocumentProcessor
p = DocumentProcessor()
emb = p.generate_embedding('test')
print('Success!' if emb else 'Failed!')
"
```

**Solutions**:
1. Verify Ollama is running
2. Check model is available
3. Test Ollama directly:
   ```bash
   curl http://192.168.9.98:30068/api/embeddings -d '{
     "model": "nomic-embed-text",
     "prompt": "test"
   }'
   ```

## n8n Workflow Issues

### Workflow Not Triggering

**Symptoms**: Watch folder or Gmail workflow doesn't run

**Solutions**:
1. Verify workflow is activated in n8n
2. Check schedule trigger configuration
3. Review n8n execution logs
4. Manually trigger workflow to test

### Execution Timeout

**Error**: `Workflow execution timed out`

**Solutions**:
1. Increase timeout in n8n settings
2. Process fewer items per execution
3. Optimize processing scripts
4. Split into multiple smaller workflows

### Script Path Errors

**Error**: `Command not found` or `No such file or directory`

**Solution**:
Update script paths in n8n nodes to absolute paths:
```
/absolute/path/to/pkc/scripts/process_document.py
```

### Webhook Not Responding

**Symptoms**: File upload webhook returns errors or timeouts

**Solutions**:
1. Verify workflow is activated
2. Check webhook URL is correct
3. Test webhook in n8n test mode
4. Review n8n execution logs for errors

## Watch Folder Issues

### Files Not Being Processed

**Symptoms**: Files in watch folder are ignored

**Diagnosis**:
1. Check n8n workflow is activated
2. Review n8n execution logs
3. Verify folder path in `.env`

**Solutions**:
1. Check folder permissions:
   ```bash
   ls -la /path/to/watch/folder
   chmod 755 /path/to/watch/folder
   ```

2. Verify file types are supported

3. Check for errors in n8n logs

4. Manually trigger workflow to test

### Files Not Archived

**Symptoms**: Processed files remain in watch folder

**Solutions**:
1. Check archive setting in `.env`:
   ```env
   WATCH_FOLDER_ARCHIVE=true
   ```

2. Verify archive folder exists and is writable:
   ```bash
   mkdir -p /path/to/archive
   chmod 755 /path/to/archive
   ```

3. Check n8n workflow archive node configuration

## OpenWebUI Issues

### Cannot Access OpenWebUI

**Solution**:
```bash
curl http://192.168.9.98:31028
```

If this fails, check TrueNAS container status.

### RAG Not Working

**Symptoms**: OpenWebUI doesn't retrieve documents

**Solutions**:
1. Verify Qdrant configuration in OpenWebUI settings
2. Check documents are in Qdrant:
   ```bash
   curl http://192.168.9.98:30333/collections/pkc_documents
   ```
3. Verify embedding model matches in both Qdrant and OpenWebUI
4. Test search directly in Qdrant

### Queries Return No Results

**Symptoms**: Search returns empty results

**Solutions**:
1. Check collection has documents:
   ```bash
   curl http://192.168.9.98:30333/collections/pkc_documents
   ```

2. Verify vector dimensions match

3. Lower score threshold in searches

4. Test with known content

## Performance Issues

### Slow Document Processing

**Solutions**:
1. Use lighter embedding model
2. Reduce chunk size
3. Increase TrueNAS container resources
4. Process files in smaller batches

### High Memory Usage

**Solutions**:
1. Enable Qdrant on-disk storage
2. Increase container memory allocation
3. Use smaller Ollama models
4. Reduce concurrent processing

### Disk Space Issues

**Solutions**:
1. Archive or delete old processed files
2. Clean up Qdrant collection
3. Remove unused Ollama models
4. Increase storage allocation in TrueNAS

## Debugging Tips

### Enable Verbose Logging

Update `.env`:
```env
LOG_LEVEL=DEBUG
```

### Check Logs

**n8n**:
- View execution logs in n8n web interface
- Check detailed error messages

**Python Scripts**:
```bash
python scripts/process_document.py test.pdf 2>&1 | tee debug.log
```

**Ollama**:
Check TrueNAS container logs for Ollama service

**Qdrant**:
```bash
curl http://192.168.9.98:30333/telemetry
```

### Test Individual Components

Test each service independently:

```bash
# Test Qdrant
python scripts/setup_qdrant.py

# Test Ollama
curl http://192.168.9.98:30068/api/tags

# Test document processing
python scripts/process_document.py test.txt

# Test services
python scripts/check_services.py
```

## Getting Help

If you're still experiencing issues:

1. Check n8n execution logs for detailed errors
2. Review TrueNAS container logs
3. Test each component individually
4. Check GitHub issues for similar problems
5. Create a new issue with:
   - Error messages
   - Steps to reproduce
   - Environment details
   - Service status output

## Common Error Messages Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Service not running | Start service in TrueNAS |
| `Timeout` | Service overloaded or slow | Increase timeout, check resources |
| `Collection not found` | Qdrant not initialized | Run `setup_qdrant.py` |
| `Model not found` | Ollama model missing | Pull model with Ollama API |
| `Invalid credentials` | OAuth2 issue | Re-run `gmail_auth.py` |
| `Vector dimension mismatch` | Config mismatch | Update `.env` and recreate collection |
| `Command not found` | Wrong script path | Use absolute paths in n8n |
| `Permission denied` | File/folder permissions | Check and fix with `chmod` |
| `Unsupported file type` | File type not supported | Convert file or add support |
| `Rate limit exceeded` | Too many API calls | Reduce frequency or batch size |
