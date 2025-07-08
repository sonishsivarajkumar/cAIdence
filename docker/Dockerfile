FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    wget \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and install cTAKES
ENV CTAKES_VERSION=4.0.0
ENV CTAKES_HOME=/opt/ctakes
RUN mkdir -p $CTAKES_HOME && \
    wget -O /tmp/ctakes.zip "https://archive.apache.org/dist/ctakes/ctakes-$CTAKES_VERSION/apache-ctakes-$CTAKES_VERSION-bin.zip" && \
    unzip /tmp/ctakes.zip -d /tmp && \
    mv /tmp/apache-ctakes-$CTAKES_VERSION/* $CTAKES_HOME/ && \
    rm -rf /tmp/ctakes.zip /tmp/apache-ctakes-$CTAKES_VERSION

# Copy application code
COPY . .

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV CTAKES_PATH=/opt/ctakes
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "caidence/main.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
