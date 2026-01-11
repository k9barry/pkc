#!/bin/bash

# Personal Knowledge Cloud - Quickstart Script
# This script helps you get started with PKC quickly

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# Main script
print_header "Personal Knowledge Cloud - Quickstart"

# Check prerequisites
print_info "Checking prerequisites..."

ALL_DEPS_OK=true

if ! check_command python3; then
    ALL_DEPS_OK=false
    print_error "Please install Python 3.9 or higher"
fi

if ! check_command pip3; then
    ALL_DEPS_OK=false
    print_error "Please install pip3"
fi

if ! check_command curl; then
    ALL_DEPS_OK=false
    print_error "Please install curl"
fi

if [ "$ALL_DEPS_OK" = false ]; then
    print_error "Missing required dependencies. Please install them and try again."
    exit 1
fi

print_success "All prerequisites met!"

# Check if .env exists
print_header "Environment Configuration"

if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_success "Created .env file"
    print_warning "Please edit .env with your configuration before continuing"
    print_info "Run: nano .env (or your preferred editor)"
    
    read -p "Press Enter to continue after editing .env..."
else
    print_success ".env file already exists"
fi

# Check if virtual environment exists
print_header "Python Environment Setup"

if [ ! -d venv ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate || {
    print_error "Failed to activate virtual environment"
    exit 1
}
print_success "Virtual environment activated"

# Install dependencies
print_info "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_success "Dependencies installed"

# Check services
print_header "Service Health Check"

print_info "Checking if PKC services are accessible..."
if python scripts/check_services.py; then
    print_success "All services are operational!"
else
    print_error "Some services are not accessible"
    print_warning "Please ensure all services are running in TrueNAS Scale"
    print_info "Check the docs/TROUBLESHOOTING.md for help"
    
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Setup Qdrant
print_header "Qdrant Setup"

print_info "Checking Qdrant collection..."
read -p "Do you want to initialize Qdrant collection? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    python scripts/setup_qdrant.py
    print_success "Qdrant setup complete"
else
    print_info "Skipping Qdrant setup"
fi

# Gmail setup
print_header "Gmail Integration Setup"

if [ ! -f config/gmail_credentials.json ]; then
    print_warning "Gmail credentials not found"
    print_info "To enable Gmail integration:"
    print_info "1. Go to https://console.cloud.google.com/"
    print_info "2. Create OAuth2 credentials"
    print_info "3. Download and save as config/gmail_credentials.json"
    print_info "4. Run: python scripts/gmail_auth.py"
    
    read -p "Do you have gmail_credentials.json ready? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Continue with Gmail authentication? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python scripts/gmail_auth.py
        fi
    fi
else
    print_success "Gmail credentials found"
    
    if [ ! -f config/gmail_token.pickle ]; then
        print_info "Setting up Gmail authentication..."
        python scripts/gmail_auth.py
    else
        print_success "Gmail authentication already configured"
    fi
fi

# Create watch folders
print_header "Watch Folder Setup"

# Source .env to get folder paths
set -a
source .env
set +a

if [ ! -z "$WATCH_FOLDER_PATH" ]; then
    if [ ! -d "$WATCH_FOLDER_PATH" ]; then
        print_info "Creating watch folder: $WATCH_FOLDER_PATH"
        read -p "Create folder? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            mkdir -p "$WATCH_FOLDER_PATH"
            print_success "Watch folder created"
        fi
    else
        print_success "Watch folder exists"
    fi
fi

if [ ! -z "$WATCH_FOLDER_ARCHIVE_PATH" ]; then
    if [ ! -d "$WATCH_FOLDER_ARCHIVE_PATH" ]; then
        print_info "Creating archive folder: $WATCH_FOLDER_ARCHIVE_PATH"
        read -p "Create folder? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            mkdir -p "$WATCH_FOLDER_ARCHIVE_PATH"
            print_success "Archive folder created"
        fi
    else
        print_success "Archive folder exists"
    fi
fi

# Test document processing
print_header "Test Document Processing"

read -p "Do you want to test document processing with a sample file? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    print_info "Creating test document..."
    echo "This is a test document for Personal Knowledge Cloud." > /tmp/pkc_test.txt
    echo "It contains sample text to verify the system is working correctly." >> /tmp/pkc_test.txt
    echo "Document processing includes text extraction, chunking, and embedding generation." >> /tmp/pkc_test.txt
    
    print_info "Processing test document..."
    if python scripts/process_document.py /tmp/pkc_test.txt source=quickstart title="Test Document"; then
        print_success "Test document processed successfully!"
        print_info "You can now query this document in OpenWebUI"
    else
        print_error "Test document processing failed"
        print_info "Check the error messages above"
    fi
    
    rm -f /tmp/pkc_test.txt
fi

# Summary
print_header "Setup Complete!"

print_success "PKC is ready to use!"
echo ""
print_info "Next steps:"
echo "  1. Import n8n workflows from n8n-workflows/ directory"
echo "  2. Configure workflows in n8n web interface: http://192.168.9.98:30109"
echo "  3. Access OpenWebUI: http://192.168.9.98:31028"
echo "  4. Test file upload: python scripts/upload_file.py <file>"
echo "  5. Test watch folder: copy files to $WATCH_FOLDER_PATH"
echo ""
print_info "Documentation:"
echo "  - Setup guide: docs/SETUP.md"
echo "  - API docs: docs/API.md"
echo "  - Troubleshooting: docs/TROUBLESHOOTING.md"
echo ""
print_info "Service URLs:"
echo "  - OpenWebUI: http://192.168.9.98:31028"
echo "  - Ollama: http://192.168.9.98:30068"
echo "  - Qdrant: http://192.168.9.98:30333"
echo "  - n8n: http://192.168.9.98:30109"
echo ""

print_success "Happy knowledge cloud building! 🚀"
