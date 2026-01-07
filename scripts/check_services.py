#!/usr/bin/env python3
"""
Service Health Check Script

Checks the health and availability of all PKC services.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from typing import Dict, Tuple

# Load environment variables
load_dotenv()

# Service configuration
SERVICES = {
    "OpenWebUI": {
        "url": f"http://{os.getenv('PKC_SERVER_IP', '192.168.9.98')}:{os.getenv('OPENWEBUI_PORT', '31028')}",
        "endpoint": "/"
    },
    "Ollama": {
        "url": f"http://{os.getenv('PKC_SERVER_IP', '192.168.9.98')}:{os.getenv('OLLAMA_PORT', '30068')}",
        "endpoint": "/api/tags"
    },
    "Qdrant": {
        "url": f"http://{os.getenv('PKC_SERVER_IP', '192.168.9.98')}:{os.getenv('QDRANT_PORT', '30333')}",
        "endpoint": "/collections"
    },
    "n8n": {
        "url": f"http://{os.getenv('PKC_SERVER_IP', '192.168.9.98')}:{os.getenv('N8N_PORT', '30109')}",
        "endpoint": "/"
    }
}


def check_service(name: str, config: Dict[str, str]) -> Tuple[bool, str]:
    """
    Check if a service is accessible.
    
    Args:
        name: Service name
        config: Service configuration with URL and endpoint
        
    Returns:
        Tuple of (success, message)
    """
    try:
        url = f"{config['url']}{config['endpoint']}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return True, f"✓ {name} is accessible at {config['url']}"
        else:
            return False, f"✗ {name} returned status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"✗ {name} is not accessible at {config['url']} (Connection refused)"
    except requests.exceptions.Timeout:
        return False, f"✗ {name} timed out at {config['url']}"
    except Exception as e:
        return False, f"✗ {name} error: {str(e)}"


def main():
    """Main function to check all services."""
    print("=" * 60)
    print("Personal Knowledge Cloud - Service Health Check")
    print("=" * 60)
    print()
    
    results = []
    
    for name, config in SERVICES.items():
        success, message = check_service(name, config)
        results.append(success)
        print(message)
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✓ All services are operational")
        return 0
    else:
        failed_count = sum(1 for r in results if not r)
        print(f"✗ {failed_count} service(s) failed health check")
        return 1


if __name__ == "__main__":
    sys.exit(main())
