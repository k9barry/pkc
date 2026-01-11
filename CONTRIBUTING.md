# Contributing to Personal Knowledge Cloud

Thank you for your interest in contributing to PKC! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow best practices

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- Access to TrueNAS Scale server with PKC services
- Basic understanding of Docker, n8n, and vector databases

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pkc.git
   cd pkc
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy environment template:
   ```bash
   cp .env.example .env
   ```
6. Configure your `.env` file with test settings

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-parser` - New features
- `fix/email-authentication` - Bug fixes
- `docs/improve-setup-guide` - Documentation
- `refactor/optimize-chunking` - Code refactoring

### Commit Messages

Follow conventional commit format:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(parser): add CSV file support

Add CSV parsing capability to document processor.
Supports both comma and tab-delimited files.

Closes #123
```

```
fix(gmail): handle OAuth token expiration

Automatically refresh expired tokens instead of failing.
```

### Code Style

#### Python

Follow PEP 8 guidelines:

- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter)
- Use type hints where appropriate
- Write docstrings for functions and classes

Example:
```python
def process_file(
    file_path: Path,
    metadata: Optional[Dict[str, str]] = None
) -> bool:
    """
    Process a document file and store in Qdrant.
    
    Args:
        file_path: Path to the document file
        metadata: Optional metadata dictionary
        
    Returns:
        True if successful, False otherwise
    """
    # Implementation
```

#### n8n Workflows

- Use clear node names
- Add comments/notes for complex logic
- Group related nodes
- Use consistent error handling
- Test workflows before committing

### Testing

Before submitting:

1. Test your changes locally
2. Run existing scripts to ensure no breakage:
   ```bash
   python scripts/check_services.py
   python scripts/setup_qdrant.py
   ```
3. Test with sample files
4. Verify n8n workflows work as expected

### Documentation

Update documentation when:
- Adding new features
- Changing configuration options
- Updating dependencies
- Fixing significant bugs

Files to update:
- `README.md` - Overview and features
- `docs/SETUP.md` - Setup instructions
- `docs/API.md` - API changes
- `docs/TROUBLESHOOTING.md` - New issues and solutions

## Pull Request Process

1. **Create a Pull Request**:
   - Clear title describing the change
   - Detailed description of what and why
   - Link to related issues
   - Screenshots for UI changes (if applicable)

2. **PR Description Template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring
   
   ## Changes Made
   - Detailed list of changes
   
   ## Testing
   - How was this tested?
   - What test cases were covered?
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] Changes tested locally
   - [ ] No breaking changes (or documented)
   ```

3. **Review Process**:
   - Maintainers will review your PR
   - Address feedback and comments
   - Update PR as needed
   - Once approved, PR will be merged

## Areas for Contribution

### High Priority

- **Additional file format support**: Add parsers for more document types
- **Error handling**: Improve error handling and recovery
- **Performance optimization**: Speed up embedding generation and storage
- **Testing**: Add unit tests and integration tests
- **Monitoring**: Add health checks and metrics

### Documentation

- **Tutorials**: Step-by-step guides for common tasks
- **Examples**: More code examples and use cases
- **Video guides**: Setup and usage videos
- **Translations**: Documentation in other languages

### Features

- **Advanced search**: Implement filters and faceted search
- **UI improvements**: Better OpenWebUI integration
- **Batch processing**: Optimize bulk document processing
- **Scheduling**: More flexible scheduling options
- **Notifications**: Email/webhook notifications for events

### Integration

- **Cloud storage**: Add Dropbox, OneDrive, etc. support
- **Other email providers**: Outlook, ProtonMail support
- **Messaging platforms**: Slack, Discord integration
- **Note-taking apps**: Notion, Obsidian integration

## Development Tips

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Test individual components:
```bash
# Test document processing
python scripts/process_document.py test_file.pdf

# Test embedding generation
python -c "
from scripts.process_document import DocumentProcessor
p = DocumentProcessor()
emb = p.generate_embedding('test text')
print(f'Embedding size: {len(emb) if emb else 0}')
"
```

### Working with n8n

- Use n8n test mode to debug workflows
- Check execution logs for errors
- Test with small datasets first
- Use function nodes for debugging

### Common Issues

**Import errors**: Ensure virtual environment is activated
**Connection errors**: Verify services are running
**Path issues**: Use absolute paths in n8n workflows

## Questions and Support

- Open an issue for bugs or feature requests
- Use discussions for questions
- Check existing issues before creating new ones
- Provide as much detail as possible

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to PKC!
