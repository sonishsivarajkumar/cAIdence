#!/bin/bash

# cAIdence Setup Script
# This script sets up the development environment for cAIdence

set -e

echo "🏥 Setting up cAIdence Development Environment"

# Check if Python 3.8+ is installed
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Java is required for cTAKES but not found"
    echo "Please install Java 8+ and try again"
    exit 1
fi

java_version=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
echo "✅ Java found: $java_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/documents
mkdir -p data/models
mkdir -p logs
mkdir -p config

# Download cTAKES if not present
CTAKES_DIR="./ctakes"
if [ ! -d "$CTAKES_DIR" ]; then
    echo "⬇️  Downloading Apache cTAKES..."
    CTAKES_VERSION="4.0.0"
    CTAKES_URL="https://archive.apache.org/dist/ctakes/ctakes-${CTAKES_VERSION}/apache-ctakes-${CTAKES_VERSION}-bin.zip"
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    
    # Download cTAKES
    curl -L "$CTAKES_URL" -o "$TEMP_DIR/ctakes.zip"
    
    # Extract cTAKES
    unzip "$TEMP_DIR/ctakes.zip" -d "$TEMP_DIR"
    mv "$TEMP_DIR/apache-ctakes-${CTAKES_VERSION}" "$CTAKES_DIR"
    
    # Clean up
    rm -rf "$TEMP_DIR"
    
    echo "✅ cTAKES installed successfully"
else
    echo "✅ cTAKES already installed"
fi

# Set up environment variables
echo "⚙️  Setting up environment variables..."
cat > .env << EOF
# cAIdence Configuration
CTAKES_PATH=$(pwd)/ctakes
JAVA_HOME=${JAVA_HOME:-$(which java | xargs dirname | xargs dirname)}
PYTHONPATH=$(pwd)

# Database Configuration
DATABASE_URL=postgresql://caidence:caidence_password@localhost:5432/caidence

# Security
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
PHI_PROTECTION_ENABLED=true

# Local LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama2

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/caidence.log
EOF

# Create sample configuration
echo "📝 Creating sample configuration..."
cat > config/config.yaml << EOF
# cAIdence Configuration File

# Application Settings
app:
  name: "cAIdence"
  version: "0.1.0"
  debug: false

# cTAKES Configuration
ctakes:
  path: "${CTAKES_DIR}"
  java_heap_size: "4G"
  timeout: 300

# Security Settings
security:
  phi_protection: true
  local_llm_only: true
  max_file_size: "100MB"
  allowed_file_types: [".txt", ".pdf", ".docx"]

# Database Settings
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "caidence"
  user: "caidence"
  password: "caidence_password"

# Visualization Settings
visualization:
  default_charts: ["bar", "pie"]
  max_entities: 50
  color_scheme: "clinical"
EOF

# Set up git hooks (if in git repo)
if [ -d ".git" ]; then
    echo "🔧 Setting up git hooks..."
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run basic linting before commit
python -m black --check caidence/
python -m flake8 caidence/
EOF
    chmod +x .git/hooks/pre-commit
fi

echo ""
echo "🎉 cAIdence setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the application: python -m caidence.main"
echo "3. Or use Docker: docker-compose up"
echo ""
echo "📖 For more information, see the documentation in docs/"
