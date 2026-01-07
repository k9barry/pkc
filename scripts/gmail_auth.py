#!/usr/bin/env python3
"""
Gmail OAuth2 Authentication Setup Script

Helps set up OAuth2 authentication for Gmail API access.
"""

import os
import sys
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Token storage path
TOKEN_PATH = Path(__file__).parent.parent / 'config' / 'gmail_token.pickle'
CREDENTIALS_PATH = Path(__file__).parent.parent / 'config' / 'gmail_credentials.json'


def get_credentials():
    """
    Get valid Gmail API credentials.
    
    Returns:
        Valid credentials object or None
    """
    creds = None
    
    # Load existing token if available
    if TOKEN_PATH.exists():
        print("Loading existing credentials...")
        try:
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(f"Warning: Could not load existing token: {e}")
    
    # If credentials are invalid or don't exist, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            try:
                creds.refresh(Request())
                print("✓ Credentials refreshed")
            except Exception as e:
                print(f"✗ Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            if not CREDENTIALS_PATH.exists():
                print()
                print("=" * 60)
                print("Gmail Credentials Not Found")
                print("=" * 60)
                print()
                print("To set up Gmail authentication:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Gmail API")
                print("4. Create OAuth 2.0 credentials (Desktop app)")
                print("5. Download credentials JSON")
                print(f"6. Save as: {CREDENTIALS_PATH}")
                print()
                return None
            
            print("Starting OAuth2 flow...")
            print("A browser window will open for authentication.")
            print()
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_PATH), SCOPES)
                creds = flow.run_local_server(port=0)
                print("✓ Authentication successful")
            except Exception as e:
                print(f"✗ Authentication failed: {e}")
                return None
        
        # Save credentials for future use
        try:
            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
            print(f"✓ Credentials saved to {TOKEN_PATH}")
        except Exception as e:
            print(f"Warning: Could not save credentials: {e}")
    
    return creds


def test_connection(creds):
    """
    Test Gmail API connection.
    
    Args:
        creds: Valid credentials object
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print()
        print("Testing Gmail API connection...")
        service = build('gmail', 'v1', credentials=creds)
        
        # Get user profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"✓ Connected to Gmail account: {profile.get('emailAddress')}")
        print(f"  - Total messages: {profile.get('messagesTotal', 0)}")
        print(f"  - Total threads: {profile.get('threadsTotal', 0)}")
        
        return True
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Personal Knowledge Cloud - Gmail Authentication Setup")
    print("=" * 60)
    print()
    
    # Get credentials
    creds = get_credentials()
    
    if not creds:
        print()
        print("✗ Authentication setup failed")
        return 1
    
    # Test connection
    if not test_connection(creds):
        return 1
    
    print()
    print("=" * 60)
    print("✓ Gmail authentication setup completed successfully")
    print()
    print("You can now use the Gmail integration workflows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
