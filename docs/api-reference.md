# API Reference

This document provides comprehensive API documentation for cAIdence's programmatic interfaces.

## 🌐 REST API

### Base URL
```
http://localhost:8501/api/v1
```

### Authentication

All API requests require authentication:

```bash
# Bearer token authentication
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     https://api.caidence.org/v1/analyze
```

### Rate Limiting

API requests are rate limited:
- **Free tier**: 100 requests/hour
- **Professional**: 1,000 requests/hour
- **Enterprise**: Unlimited

## 📝 Analysis Endpoints

### POST /analyze
Process a clinical text analysis query.

**Request Body:**
```json
{
  "query": "Find all surgical notes mentioning arterial graft",
  "documents": ["doc_id_1", "doc_id_2"],
  "options": {
    "include_negated": false,
    "confidence_threshold": 0.8,
    "max_results": 100
  }
}
```

**Response:**
```json
{
  "id": "analysis_12345",
  "status": "completed",
  "query": "Find all surgical notes mentioning arterial graft",
  "results": {
    "documents_processed": 42,
    "entities_found": [
      {
        "text": "arterial graft",
        "type": "PROCEDURE",
        "count": 15,
        "documents": ["doc_1", "doc_5", "doc_12"],
        "confidence": 0.95
      }
    ],
    "summary": "Found 15 mentions of arterial graft in 8 documents",
    "execution_time": 2.4,
    "confidence": 0.92
  },
  "visualizations": [
    {
      "type": "bar_chart",
      "title": "Entity Frequency",
      "data": {...}
    }
  ]
}
```

**Error Response:**
```json
{
  "error": {
    "code": "INVALID_QUERY",
    "message": "Query contains invalid syntax",
    "details": "Unsupported operator 'XOR' at position 45"
  }
}
```

### GET /analyze/{analysis_id}
Retrieve analysis results by ID.

**Response:**
```json
{
  "id": "analysis_12345",
  "status": "completed",
  "created_at": "2025-07-08T10:30:00Z",
  "completed_at": "2025-07-08T10:30:02Z",
  "results": {...}
}
```

### GET /analyze
List all analysis results with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)
- `status`: Filter by status (pending, completed, failed)
- `created_after`: ISO 8601 timestamp

**Response:**
```json
{
  "analyses": [
    {
      "id": "analysis_12345",
      "query": "Find diabetes mentions",
      "status": "completed",
      "created_at": "2025-07-08T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "pages": 8
  }
}
```

## 📄 Document Endpoints

### POST /documents
Upload a clinical document.

**Request (multipart/form-data):**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@clinical_note.txt" \
  -F "metadata={\"type\":\"surgical_note\",\"date\":\"2025-07-08\"}" \
  http://localhost:8501/api/v1/documents
```

**Response:**
```json
{
  "id": "doc_12345",
  "filename": "clinical_note.txt",
  "size": 1024,
  "type": "surgical_note",
  "status": "uploaded",
  "uploaded_at": "2025-07-08T10:30:00Z"
}
```

### GET /documents
List documents with filtering.

**Query Parameters:**
- `type`: Document type filter
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)
- `search`: Text search in content
- `page`, `limit`: Pagination

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_12345",
      "title": "Surgical Note - Cardiac Bypass",
      "type": "surgical_note",
      "date": "2025-07-08",
      "size": 1024,
      "uploaded_at": "2025-07-08T10:30:00Z"
    }
  ],
  "pagination": {...}
}
```

### GET /documents/{document_id}
Retrieve document details and content.

**Response:**
```json
{
  "id": "doc_12345",
  "title": "Surgical Note - Cardiac Bypass",
  "type": "surgical_note",
  "content": "Patient underwent successful...",
  "metadata": {
    "patient_id": "encrypted_id",
    "physician": "Dr. Smith",
    "department": "Cardiology"
  },
  "entities": [
    {
      "text": "arterial graft",
      "type": "PROCEDURE",
      "begin": 45,
      "end": 58
    }
  ]
}
```

### DELETE /documents/{document_id}
Delete a document.

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

## 🔧 Tools Endpoints

### GET /tools
List available analysis tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "ctakes_processor",
      "description": "Apache cTAKES clinical entity extraction",
      "version": "4.0.0",
      "capabilities": ["entity_extraction", "umls_mapping"],
      "status": "available"
    },
    {
      "name": "negation_detector",
      "description": "Clinical negation detection",
      "version": "1.0.0",
      "capabilities": ["negation_detection"],
      "status": "available"
    }
  ]
}
```

### GET /tools/{tool_name}
Get detailed tool information and schema.

**Response:**
```json
{
  "name": "ctakes_processor",
  "description": "Apache cTAKES clinical entity extraction",
  "version": "4.0.0",
  "schema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Clinical text to process"
      },
      "output_format": {
        "type": "string",
        "enum": ["json", "xml"],
        "default": "json"
      }
    },
    "required": ["text"]
  },
  "examples": [
    {
      "text": "Patient has diabetes mellitus",
      "output_format": "json"
    }
  ]
}
```

### POST /tools/{tool_name}/execute
Execute a specific tool.

**Request:**
```json
{
  "parameters": {
    "text": "Patient underwent arterial bypass surgery without complications",
    "output_format": "json"
  }
}
```

**Response:**
```json
{
  "tool": "ctakes_processor",
  "execution_id": "exec_12345",
  "status": "completed",
  "results": {
    "entities": [
      {
        "text": "arterial bypass surgery",
        "type": "PROCEDURE",
        "begin": 17,
        "end": 40,
        "cui": "C0741847"
      }
    ],
    "execution_time": 0.8
  }
}
```

## 📊 Dashboard Endpoints

### GET /dashboard/summary
Get dashboard summary statistics.

**Response:**
```json
{
  "total_documents": 1234,
  "total_analyses": 567,
  "total_entities": 45678,
  "recent_activity": [
    {
      "type": "analysis_completed",
      "query": "Find diabetes mentions",
      "timestamp": "2025-07-08T10:30:00Z"
    }
  ]
}
```

### GET /dashboard/visualizations
Get available visualizations.

**Query Parameters:**
- `analysis_id`: Specific analysis ID
- `type`: Visualization type (bar, pie, timeline)

**Response:**
```json
{
  "visualizations": [
    {
      "id": "viz_12345",
      "type": "bar_chart",
      "title": "Entity Frequency",
      "data": {
        "labels": ["diabetes", "hypertension", "medication"],
        "values": [45, 32, 28]
      },
      "config": {
        "x_axis": "Entity",
        "y_axis": "Frequency"
      }
    }
  ]
}
```

## 🐍 Python SDK

### Installation
```bash
pip install caidence-sdk
```

### Basic Usage
```python
from caidence import CaidenceClient

# Initialize client
client = CaidenceClient(
    base_url="http://localhost:8501/api/v1",
    api_token="your_api_token"
)

# Analyze text
result = client.analyze(
    query="Find all mentions of diabetes",
    documents=["doc_1", "doc_2"]
)

print(f"Found {len(result.entities)} entities")
for entity in result.entities:
    print(f"- {entity.text} ({entity.type})")
```

### Advanced Usage
```python
# Upload document
document = client.upload_document(
    file_path="clinical_note.txt",
    metadata={"type": "discharge_summary", "date": "2025-07-08"}
)

# Custom tool execution
result = client.execute_tool(
    tool_name="ctakes_processor",
    parameters={"text": "Patient has diabetes", "output_format": "json"}
)

# Batch processing
documents = client.list_documents(type="surgical_note")
results = client.batch_analyze(
    queries=["Find complications", "Find medications"],
    documents=[doc.id for doc in documents]
)
```

### Error Handling
```python
from caidence.exceptions import CaidenceError, AuthenticationError, ValidationError

try:
    result = client.analyze("Invalid query syntax +++")
except ValidationError as e:
    print(f"Query validation failed: {e.message}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except CaidenceError as e:
    print(f"General error: {e.message}")
```

## 📱 JavaScript SDK

### Installation
```bash
npm install @caidence/sdk
```

### Basic Usage
```javascript
import { CaidenceClient } from '@caidence/sdk';

const client = new CaidenceClient({
  baseUrl: 'http://localhost:8501/api/v1',
  apiToken: 'your_api_token'
});

// Analyze query
const result = await client.analyze({
  query: 'Find all mentions of diabetes',
  documents: ['doc_1', 'doc_2']
});

console.log(`Found ${result.entities.length} entities`);
```

### React Integration
```jsx
import React, { useState, useEffect } from 'react';
import { useCaidence } from '@caidence/react';

function AnalysisComponent() {
  const { analyze, loading, error } = useCaidence();
  const [results, setResults] = useState(null);

  const handleAnalysis = async () => {
    const result = await analyze({
      query: 'Find diabetes mentions'
    });
    setResults(result);
  };

  return (
    <div>
      <button onClick={handleAnalysis} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
      {error && <div className="error">{error.message}</div>}
      {results && (
        <div>
          <h3>Results</h3>
          <p>Found {results.entities.length} entities</p>
        </div>
      )}
    </div>
  );
}
```

## 🔗 Webhooks

### Configuration
```json
{
  "webhook_url": "https://your-app.com/webhook",
  "events": ["analysis_completed", "document_uploaded"],
  "secret": "webhook_secret_key"
}
```

### Event Types

#### analysis_completed
```json
{
  "event": "analysis_completed",
  "timestamp": "2025-07-08T10:30:00Z",
  "data": {
    "analysis_id": "analysis_12345",
    "query": "Find diabetes mentions",
    "status": "completed",
    "results_summary": {
      "entities_found": 15,
      "documents_processed": 5
    }
  }
}
```

#### document_uploaded
```json
{
  "event": "document_uploaded",
  "timestamp": "2025-07-08T10:30:00Z",
  "data": {
    "document_id": "doc_12345",
    "filename": "clinical_note.txt",
    "type": "surgical_note",
    "size": 1024
  }
}
```

### Webhook Verification
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """Verify webhook signature."""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

## 📚 SDK Examples

### Batch Document Processing
```python
import asyncio
from caidence import CaidenceClient

async def process_documents_batch():
    client = CaidenceClient(api_token="your_token")
    
    # Upload multiple documents
    documents = []
    for file_path in ["note1.txt", "note2.txt", "note3.txt"]:
        doc = await client.upload_document(file_path)
        documents.append(doc.id)
    
    # Analyze all documents
    result = await client.analyze(
        query="Find all medication mentions",
        documents=documents
    )
    
    return result

# Run batch processing
result = asyncio.run(process_documents_batch())
```

### Custom Tool Integration
```python
from caidence.tools import BaseTool, ToolResult

class CustomMedicationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="medication_extractor",
            description="Custom medication extraction tool"
        )
    
    def execute(self, parameters):
        text = parameters["text"]
        medications = self.extract_medications(text)
        
        return ToolResult(
            success=True,
            data={"medications": medications}
        )

# Register custom tool
client.register_tool(CustomMedicationTool())
```

### Real-time Analysis
```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8501/ws');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  
  if (update.type === 'analysis_progress') {
    console.log(`Progress: ${update.progress}%`);
  } else if (update.type === 'analysis_complete') {
    console.log('Analysis completed:', update.results);
  }
};

// Start analysis with real-time updates
client.analyze({
  query: 'Find diabetes mentions',
  real_time: true
});
```

## 🚨 Error Codes

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Rate Limited
- `500`: Internal Server Error

### Application Error Codes
- `INVALID_QUERY`: Query syntax error
- `TOOL_NOT_FOUND`: Requested tool not available
- `DOCUMENT_NOT_FOUND`: Document ID not found
- `PROCESSING_FAILED`: Analysis processing failed
- `QUOTA_EXCEEDED`: API quota exceeded
- `PHI_DETECTED`: PHI detected in insecure context

---

For more examples and detailed documentation, visit our [API documentation website](https://docs.caidence.org) or explore the [SDK repositories](https://github.com/sonishsivarajkumar/cAIdence-sdks).
