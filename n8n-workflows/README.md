# n8n Workflows for Personal Knowledge Cloud

This directory contains n8n workflow definitions for the PKC system.

## Workflows

1. **file-upload-workflow.json** - Handles file uploads via webhook
2. **watch-folder-workflow.json** - Monitors folder for new files
3. **gmail-integration-workflow.json** - Fetches and processes emails from Gmail

## Installation

### 1. Import Workflows

1. Access n8n at `http://192.168.9.98:30109`
2. Click "Workflows" → "Import from File"
3. Import each JSON file from this directory

### 2. Configure Environment Variables

The workflows use environment variables that must be set in n8n:

#### Required Environment Variables

Add these to your n8n environment (in TrueNAS app configuration or docker-compose):

```bash
# Path to PKC installation
PKC_HOME=/absolute/path/to/pkc

# Watch folder configuration
WATCH_FOLDER_PATH=/path/to/watch/folder
WATCH_FOLDER_ARCHIVE_PATH=/path/to/archive/folder
WATCH_FOLDER_ARCHIVE=true

# Supported file types
SUPPORTED_FILE_TYPES=.pdf,.txt,.md,.docx,.doc,.html

# Qdrant configuration
QDRANT_URL=http://192.168.9.98:30333
QDRANT_COLLECTION_NAME=pkc_documents

# Gmail configuration
GMAIL_QUERY=is:unread label:pkc
```

#### Setting Environment Variables in TrueNAS

1. Go to Apps → n8n → Edit
2. Navigate to Environment Variables section
3. Add each variable with its value
4. Save and restart the app

### 3. Update Script Paths

All workflows now use `{{ $env.PKC_HOME }}` to reference script paths.

**Important**: Ensure `PKC_HOME` environment variable is set correctly in your n8n installation.

### 4. Configure Gmail Credentials

For the Gmail workflow:

1. Open the workflow in n8n
2. Click on "Get Emails" node
3. Add Gmail OAuth2 credentials:
   - Use credentials from Google Cloud Console
   - Follow instructions in `docs/SETUP.md`

### 5. Activate Workflows

After configuration:

1. Test each workflow manually
2. Check execution logs for errors
3. Activate workflows (toggle switch in n8n)

## Workflow Details

### File Upload Workflow

- **Trigger**: Webhook at `/webhook/upload-file`
- **Function**: Processes uploaded files
- **Steps**:
  1. Receive file via webhook
  2. Extract file information
  3. Process document (extract text, chunk, embed)
  4. Verify storage in Qdrant
  5. Return success/error response

### Watch Folder Workflow

- **Trigger**: Schedule (every 5 minutes by default)
- **Function**: Monitors folder for new files
- **Steps**:
  1. Scan watch folder for new files
  2. Filter by supported file types
  3. Process each file sequentially
  4. Archive processed files
  5. Update timestamp marker

**Configuration**:
- Edit schedule in "Schedule Trigger" node
- Adjust interval as needed (e.g., `*/10 * * * *` for 10 minutes)

### Gmail Integration Workflow

- **Trigger**: Schedule (every 15 minutes by default)
- **Function**: Fetches and processes emails
- **Steps**:
  1. Fetch emails matching query
  2. Parse email content
  3. Create temporary files for email content
  4. Process email text
  5. Check for attachments
  6. Process attachments
  7. Mark emails as processed
  8. Clean up temporary files

**Configuration**:
- Edit Gmail query in environment variables
- Adjust schedule as needed
- Configure Gmail OAuth2 credentials

## Troubleshooting

### Workflows Not Triggering

- Verify workflows are activated (green toggle)
- Check schedule trigger configuration
- Review execution logs in n8n

### Script Execution Errors

- Ensure `PKC_HOME` environment variable is set correctly
- Verify Python scripts are executable: `chmod +x scripts/*.py`
- Check that Python virtual environment is accessible
- Review error messages in execution logs

### Path Issues

- All paths should be absolute
- Use `{{ $env.PKC_HOME }}` for PKC installation path
- Use `{{ $env.WATCH_FOLDER_PATH }}` for watch folder

### Permission Issues

- Ensure n8n container can access PKC scripts
- Mount PKC directory in n8n container if needed
- Check file permissions on scripts and folders

## Customization

### Modifying Processing Logic

Edit the "Process Document" nodes to:
- Add custom metadata
- Change processing parameters
- Add additional validation

### Changing Schedules

Edit schedule expressions in trigger nodes:
- `*/5 * * * *` - Every 5 minutes
- `*/15 * * * *` - Every 15 minutes
- `0 * * * *` - Every hour
- `0 0 * * *` - Daily at midnight

### Adding Error Notifications

Add nodes to send notifications on errors:
- Email notification
- Slack message
- Discord webhook
- Custom webhook

## Support

For issues:
- Check execution logs in n8n
- Review `docs/TROUBLESHOOTING.md`
- Verify environment variables are set
- Test scripts manually outside n8n

## Notes

- Workflows use environment variables for portability
- All file paths should be absolute
- Ensure sufficient execution timeout for large files
- Monitor disk space for temporary files
- Regular cleanup of archived files recommended
