# Contributing to cAIdence

Thank you for your interest in contributing to cAIdence! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:
- Be respectful and inclusive
- Focus on what is best for the community
- Show empathy towards other community members
- Handle disagreements constructively

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Run the setup script: `./scripts/setup.sh`
4. Create a new branch for your feature: `git checkout -b feature-name`

## Development Setup

### Prerequisites
- Python 3.8+
- Java 8+ (for cTAKES)
- Docker (optional but recommended)

### Local Development
```bash
# Clone the repository
git clone https://github.com/sonishsivarajkumar/cAIdence.git
cd cAIdence

# Run setup script
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate

# Start development server
python -m caidence.main
```

### Using Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Project Structure

```
caidence/
├── caidence/           # Main package
│   ├── agent/         # AI agent core
│   ├── tools/         # Tool implementations
│   ├── dashboard/     # Dashboard components
│   ├── connectors/    # Database connectors
│   └── security/      # Security modules
├── tests/             # Test suite
├── docs/              # Documentation
├── examples/          # Usage examples
└── scripts/           # Utility scripts
```

## Contributing Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use Black for code formatting: `black caidence/`
- Use flake8 for linting: `flake8 caidence/`
- Add type hints for function signatures
- Write docstrings for all public functions and classes

### Testing
- Write tests for all new functionality
- Ensure all tests pass before submitting: `pytest`
- Aim for at least 80% code coverage
- Include both unit tests and integration tests

### Documentation
- Update README.md for any new features
- Add docstrings to all public APIs
- Update type hints and schemas
- Include examples for new functionality

### Security Considerations
- Never commit PHI or sensitive data
- Follow HIPAA compliance guidelines
- Use local LLMs for PHI processing
- Implement proper access controls

## Submitting Changes

1. **Create an Issue**: For bugs or feature requests, create an issue first
2. **Create a Branch**: Create a feature branch from main
3. **Make Changes**: Implement your changes with tests
4. **Test**: Ensure all tests pass and code follows style guidelines
5. **Commit**: Make atomic commits with clear messages
6. **Pull Request**: Create a PR with a clear description

### Commit Message Format
```
type(scope): description

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(agent): add support for custom entity extraction

Add ability to specify custom entities for extraction in addition
to standard cTAKES entities.

Closes #123
```

### Pull Request Process
1. Update documentation for any new features
2. Add tests for bug fixes and new features
3. Ensure the PR description clearly describes the problem and solution
4. Link any relevant issues
5. Request review from maintainers

## Types of Contributions

### Bug Reports
When filing a bug report, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Relevant logs or error messages

### Feature Requests
For feature requests, please provide:
- Clear description of the feature
- Use case and rationale
- Proposed implementation approach
- Any relevant examples or mockups

### Code Contributions
We welcome contributions in these areas:
- New tool implementations
- Performance improvements
- Documentation improvements
- Test coverage improvements
- Bug fixes
- Security enhancements

### Clinical Domain Expertise
We especially value contributions from:
- Clinical informaticists
- Healthcare data scientists
- Medical professionals
- NLP researchers

## Tool Development

To contribute a new tool:

1. Inherit from `BaseTool` class
2. Implement required methods: `initialize()`, `execute()`, `get_schema()`
3. Add comprehensive tests
4. Document the tool's purpose and usage
5. Register the tool in the tool registry

Example:
```python
from caidence.tools import BaseTool, ToolResult

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Description of what the tool does"
        )
    
    def initialize(self) -> bool:
        # Setup code
        return True
    
    def execute(self, parameters: dict) -> ToolResult:
        # Implementation
        return ToolResult(success=True, data=result)
    
    def get_schema(self) -> dict:
        # Parameter schema
        return {...}
```

## Release Process

Releases follow semantic versioning (SemVer):
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes, backwards compatible

## Community

- **Discussions**: Use GitHub Discussions for questions and ideas
- **Issues**: Use GitHub Issues for bugs and feature requests
- **Email**: Contact maintainers for sensitive issues

## License

By contributing to cAIdence, you agree that your contributions will be licensed under the Apache License 2.0.

## Questions?

If you have questions about contributing, please:
1. Check the documentation
2. Search existing issues
3. Start a discussion on GitHub
4. Contact the maintainers

Thank you for contributing to cAIdence! 🏥
