# Changelog

All notable changes to the cAIdence project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.2.0
- Enhanced cTAKES configuration options
- FHIR resource support
- Advanced visualization suite
- Query history and saved searches
- Basic user authentication

## [0.1.0] - 2025-07-08

### Added
- Initial release of cAIdence platform
- Core agentic AI system with query understanding and execution planning
- Apache cTAKES integration for clinical entity extraction
- Document filtering and search capabilities
- Clinical text negation detection
- Intelligent summarization of analysis results
- Interactive data visualization with Plotly
- Streamlit-based web interface with conversational chat
- PostgreSQL database integration with clinical data schema
- Docker containerization with multi-service setup
- Local LLM support via Ollama integration
- Security-first design with PHI protection
- Comprehensive tool registry and extensible architecture
- Apache 2.0 open source licensing
- Complete project documentation and setup guides
- Automated setup scripts for easy installation
- Test suite with pytest framework
- Contributing guidelines and code of conduct

### Core Features
- **Conversational Interface**: Natural language queries for clinical text analysis
- **Dynamic Plan Generation**: AI creates transparent, step-by-step execution plans
- **Extensible Toolkit**: Built around cTAKES with expandable tool system
- **Interactive Dashboards**: Business-ready visualizations and data export
- **Security & Privacy First**: On-premise deployment with local LLM processing
- **Open Source**: Apache 2.0 licensed for free use and modification

### Technical Implementation
- Python 3.8+ with modern packaging (pyproject.toml)
- LangChain for AI agent orchestration
- Streamlit for web interface
- Plotly for interactive visualizations
- PostgreSQL for data persistence
- Docker Compose for development and deployment
- Comprehensive error handling and logging
- Type hints and documentation throughout codebase

### Documentation
- README with quick start guide
- Detailed setup documentation
- Architecture overview and diagrams
- Contributing guidelines
- Project roadmap
- Code examples and usage patterns
- Docker deployment instructions
- Security and compliance considerations

### Infrastructure
- Docker multi-service setup (app, database, LLM, cache)
- PostgreSQL with clinical data schema
- Redis for caching and session management
- Ollama for local LLM hosting
- Health checks and monitoring
- Volume management for persistent data
- Network isolation for security

---

## Version Numbering

cAIdence follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
  - **MAJOR**: Breaking changes that require user action
  - **MINOR**: New features that are backwards compatible
  - **PATCH**: Bug fixes and small improvements

### Pre-release Versions
- **Alpha** (0.x.y): Early development, expect breaking changes
- **Beta** (x.y.z-beta): Feature complete, testing phase
- **Release Candidate** (x.y.z-rc): Final testing before stable release

### Long-Term Support (LTS)
Starting with v1.0.0, LTS versions will be released annually with 2 years of support.

---

## Release Process

### Development Workflow
1. **Feature Development**: Create feature branch from `main`
2. **Testing**: Ensure all tests pass and coverage >80%
3. **Documentation**: Update relevant documentation
4. **Code Review**: Submit pull request for review
5. **Integration**: Merge to `main` after approval

### Release Preparation
1. **Version Bump**: Update version in `pyproject.toml` and `__init__.py`
2. **Changelog**: Update this file with all changes
3. **Documentation**: Review and update all documentation
4. **Testing**: Run full test suite including integration tests
5. **Tagging**: Create git tag with version number

### Release Distribution
1. **GitHub Release**: Create release with changelog and assets
2. **Docker Images**: Build and push to container registry
3. **PyPI Package**: Publish to Python Package Index
4. **Documentation**: Deploy updated docs to website
5. **Announcements**: Notify community via discussions and social media

---

## Support Policy

### Current Support Status
- **v0.1.x**: Active development and bug fixes
- **Future LTS**: Will be announced with v1.0.0

### Security Updates
- **Critical vulnerabilities**: Patched within 48 hours
- **High severity**: Patched within 1 week
- **Medium/Low severity**: Included in next regular release

### Bug Fix Policy
- **Blocking bugs**: Hotfix release within 48 hours
- **High priority**: Fixed in next patch release
- **Normal priority**: Fixed in next minor release
- **Low priority**: Fixed when resources allow

---

## Migration Guides

### Upgrading from Development Versions
Since this is the initial release, no migration is needed. Future releases will include migration guides for breaking changes.

### Database Migrations
Database schema changes will be handled automatically with migration scripts starting in v0.2.0.

---

## Contributors

Special thanks to all contributors who made this release possible:

- **Sonish Sivarajkumar** - Project Lead and Core Developer

We welcome new contributors! See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get involved.

---

**Note**: This changelog is automatically updated with each release. For the most current information, see the [project roadmap](ROADMAP.md) and [GitHub releases](https://github.com/sonishsivarajkumar/cAIdence/releases).
