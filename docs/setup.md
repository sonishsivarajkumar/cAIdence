# cAIdence Setup Guide

This guide will help you set up cAIdence for development or production use.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.8 or higher
- **Java**: Java 8 or higher (required for cTAKES)
- **Memory**: At least 8GB RAM (16GB recommended)
- **Storage**: At least 5GB free space

### Required Software
- Git
- Docker (optional but recommended)
- PostgreSQL (for database storage)

## Quick Start with Docker

The easiest way to get started is using Docker:

```bash
# Clone the repository
git clone https://github.com/sonishsivarajkumar/cAIdence.git
cd cAIdence

# Start all services
docker-compose up --build
```

This will start:
- cAIdence application on http://localhost:8501
- PostgreSQL database
- Ollama for local LLM support
- Redis for caching

## Manual Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sonishsivarajkumar/cAIdence.git
cd cAIdence
```

### 2. Run Setup Script

```bash
./scripts/setup.sh
```

This script will:
- Check system requirements
- Create a Python virtual environment
- Install Python dependencies
- Download and configure cTAKES
- Set up environment variables
- Create necessary directories

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 4. Start the Application

```bash
python -m caidence.main
```

The application will be available at http://localhost:8501

## Manual cTAKES Setup

If the automatic setup fails, you can manually install cTAKES:

### 1. Download cTAKES

```bash
# Download cTAKES 4.0.0
wget https://archive.apache.org/dist/ctakes/ctakes-4.0.0/apache-ctakes-4.0.0-bin.zip

# Extract
unzip apache-ctakes-4.0.0-bin.zip
mv apache-ctakes-4.0.0 ctakes
```

### 2. Configure Environment

Add to your `.env` file:
```bash
CTAKES_PATH=/path/to/cAIdence/ctakes
JAVA_HOME=/path/to/java
```

### 3. Test cTAKES Installation

```bash
cd ctakes
./bin/ctakes.sh --help
```

## Database Setup

### PostgreSQL Setup

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database**:
   ```bash
   sudo -u postgres createuser caidence
   sudo -u postgres createdb caidence
   sudo -u postgres psql -c "ALTER USER caidence PASSWORD 'caidence_password';"
   ```

3. **Initialize Schema**:
   ```bash
   psql -U caidence -d caidence -f docker/postgres/init.sql
   ```

### Alternative: SQLite (Development Only)

For development, you can use SQLite instead:

```bash
# Update .env file
echo "DATABASE_URL=sqlite:///./data/caidence.db" >> .env
```

## Local LLM Setup

### Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### Download a Model

```bash
# Download Llama 2 (7B model, ~4GB)
ollama pull llama2

# Or use a smaller model for testing
ollama pull orca-mini
```

### Configure cAIdence

Update your `.env` file:
```bash
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama2
```

## Configuration

### Environment Variables

Copy the example environment file and customize:

```bash
cp .env.example .env
```

Key variables:
- `CTAKES_PATH`: Path to cTAKES installation
- `DATABASE_URL`: Database connection string
- `OLLAMA_BASE_URL`: Ollama server URL
- `PHI_PROTECTION_ENABLED`: Enable PHI protection (default: true)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Application Configuration

Edit `config/config.yaml` to customize:

```yaml
# cTAKES settings
ctakes:
  java_heap_size: "4G"
  timeout: 300

# Security settings
security:
  phi_protection: true
  local_llm_only: true
  max_file_size: "100MB"

# Visualization settings
visualization:
  default_charts: ["bar", "pie"]
  max_entities: 50
```

## Verification

### Test the Installation

1. **Run the example**:
   ```bash
   python examples/basic_usage.py
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

3. **Check the web interface**:
   - Open http://localhost:8501
   - Try the chat interface
   - Upload a sample document

### Sample Query

Try this query in the chat interface:
```
Find all discharge summaries from the last month that mention diabetes but do not mention insulin.
```

## Troubleshooting

### Common Issues

1. **cTAKES not found**:
   - Check `CTAKES_PATH` in `.env`
   - Ensure Java is installed and in PATH
   - Verify cTAKES permissions

2. **Database connection failed**:
   - Check PostgreSQL is running
   - Verify connection string in `DATABASE_URL`
   - Check firewall settings

3. **Ollama not responding**:
   - Ensure Ollama service is running
   - Check `OLLAMA_BASE_URL` setting
   - Verify model is downloaded

4. **Memory issues**:
   - Increase Java heap size in config
   - Use smaller LLM models
   - Process documents in smaller batches

### Getting Help

- Check the [troubleshooting guide](troubleshooting.md)
- Search [GitHub issues](https://github.com/sonishsivarajkumar/cAIdence/issues)
- Start a [discussion](https://github.com/sonishsivarajkumar/cAIdence/discussions)

## Next Steps

1. **Upload Documents**: Add your clinical documents to start analysis
2. **Customize Tools**: Add custom entity extraction rules
3. **Create Dashboards**: Build custom visualizations
4. **Scale Up**: Configure for production deployment

## Security Considerations

- Never commit PHI or sensitive data to version control
- Use local LLMs only for PHI processing
- Enable audit logging for compliance
- Regular security updates and monitoring
- Follow your organization's HIPAA compliance guidelines

For production deployment, see the [deployment guide](deployment.md).
