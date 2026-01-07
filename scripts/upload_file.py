#!/usr/bin/env python3
"""
File Upload Helper Script

Uploads a file to the PKC system via n8n webhook.
"""

import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
N8N_URL = os.getenv("N8N_WEBHOOK_URL", "http://192.168.9.98:30109/webhook")
UPLOAD_WEBHOOK = os.getenv("N8N_FILE_UPLOAD_WEBHOOK", "upload-file")


def upload_file(file_path: Path, metadata: dict = None):
    """
    Upload a file to PKC via n8n webhook.
    
    Args:
        file_path: Path to file to upload
        metadata: Optional metadata dictionary
        
    Returns:
        True if successful, False otherwise
    """
    if not file_path.exists():
        print(f"✗ File not found: {file_path}")
        return False
    
    print(f"Uploading: {file_path.name}")
    
    # Prepare webhook URL
    webhook_url = f"{N8N_URL}/{UPLOAD_WEBHOOK}"
    
    # Prepare files
    files = {
        'file': (file_path.name, open(file_path, 'rb'))
    }
    
    # Prepare form data
    data = metadata or {}
    data['filename'] = file_path.name
    
    try:
        response = requests.post(
            webhook_url,
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✓ Successfully uploaded {file_path.name}")
            print(f"  Response: {response.text}")
            return True
        else:
            print(f"✗ Upload failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Could not connect to n8n webhook at {webhook_url}")
        print("  Make sure n8n is running and the webhook is configured")
        return False
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return False
    finally:
        files['file'][1].close()


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python upload_file.py <file_path> [metadata_key=value ...]")
        print()
        print("Example:")
        print("  python upload_file.py document.pdf title='My Document' source=manual")
        return 1
    
    file_path = Path(sys.argv[1])
    
    # Parse metadata from command line
    metadata = {}
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            metadata[key] = value
    
    success = upload_file(file_path, metadata)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
