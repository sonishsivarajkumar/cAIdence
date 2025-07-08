# Getting Started with cAIdence

Welcome to cAIdence! This guide will help you get up and running quickly, whether you're a healthcare professional, researcher, developer, or student interested in clinical NLP.

## 🎯 What You'll Learn

By the end of this guide, you'll be able to:
- Set up cAIdence on your local machine
- Process your first clinical document
- Create a natural language query
- Understand the results and visualizations
- Extend the system with custom tools

## 🏥 Who Is This For?

### Healthcare Professionals
- **Clinical Researchers**: Analyze clinical notes for research studies
- **Hospital Administrators**: Extract insights from patient records
- **Quality Improvement Teams**: Identify patterns in clinical documentation
- **Medical Students**: Learn clinical NLP and informatics

### Technical Users
- **Data Scientists**: Build clinical analytics workflows
- **Software Developers**: Extend and customize the platform
- **IT Administrators**: Deploy and maintain the system
- **Healthcare Informaticists**: Integrate with existing systems

## 🚀 Quick Start (5 Minutes)

### Option 1: Docker (Recommended)

The fastest way to get started is with Docker:

```bash
# 1. Clone the repository
git clone https://github.com/sonishsivarajkumar/cAIdence.git
cd cAIdence

# 2. Start the services
docker-compose up -d

# 3. Open your browser
open http://localhost:8501
```

That's it! cAIdence is now running with:
- Web interface at http://localhost:8501
- PostgreSQL database
- Local LLM (Ollama)
- Redis cache

### Option 2: Local Installation

For development or custom deployments:

```bash
# 1. Clone and setup
git clone https://github.com/sonishsivarajkumar/cAIdence.git
cd cAIdence
./scripts/setup.sh

# 2. Activate environment
source venv/bin/activate

# 3. Run the application
python -m caidence.main
```

## 📝 Your First Analysis

Let's walk through analyzing a clinical document step by step.

### Step 1: Access the Interface

1. Open http://localhost:8501 in your browser
2. You'll see the cAIdence welcome screen
3. Navigate to the "Chat Interface" tab

### Step 2: Upload a Document (Optional)

If you have clinical documents, upload them via the "Data Analysis" tab:

1. Click "Data Analysis" in the sidebar
2. Use the file uploader to add documents
3. Supported formats: .txt, .pdf, .docx

### Step 3: Ask Your First Question

In the chat interface, try these example queries:

#### Example 1: Basic Entity Search
```
Find all mentions of diabetes in the uploaded documents.
```

#### Example 2: Complex Query with Negation
```
Find surgical notes that mention arterial graft but do not mention infection or complications.
```

#### Example 3: Temporal Analysis
```
Show me all discharge summaries from the last month that mention medication changes.
```

### Step 4: Understand the Results

cAIdence will:

1. **Parse your query** and show its understanding
2. **Create an execution plan** with step-by-step actions
3. **Execute the analysis** using appropriate tools
4. **Present results** with:
   - Summary statistics
   - Extracted entities
   - Interactive visualizations
   - Detailed findings

### Step 5: Explore Visualizations

Click on the "Dashboard" tab to see:
- Entity frequency charts
- Document timelines
- Co-occurrence networks
- Statistical summaries

## 🔧 Configuration

### Basic Configuration

Edit `config/config.yaml` to customize:

```yaml
# Application settings
app:
  name: "My Clinical NLP"
  debug: false

# cTAKES configuration
ctakes:
  java_heap_size: "4G"
  timeout: 300

# Security settings
security:
  phi_protection: true
  local_llm_only: true
```

### Environment Variables

Create a `.env` file for sensitive settings:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/caidence

# Security
SECRET_KEY=your-secret-key-here
PHI_PROTECTION_ENABLED=true

# LLM
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama2
```

## 📊 Understanding Results

### Entity Extraction Results

When cAIdence processes clinical text, it identifies:

- **Medical Concepts**: Diseases, symptoms, procedures
- **Medications**: Drug names, dosages, frequencies
- **Anatomy**: Body parts, organ systems
- **Temporal Information**: Dates, time periods
- **Negations**: What is explicitly NOT present

### Confidence Scores

Each extracted entity includes:
- **Confidence**: How certain the system is (0.0-1.0)
- **Context**: Surrounding text for verification
- **Source**: Which tool or model made the extraction

### Visualization Types

cAIdence creates several types of visualizations:

1. **Bar Charts**: Entity frequency distributions
2. **Pie Charts**: Category breakdowns
3. **Timelines**: Temporal patterns in documents
4. **Heatmaps**: Co-occurrence matrices
5. **Network Graphs**: Entity relationships (coming soon)

## 🛠️ Common Use Cases

### Clinical Research

**Use Case**: Identify patients for clinical trial enrollment

```
Find all patients with Type 2 diabetes who are not on insulin therapy and have HbA1c > 7.0
```

**Result**: List of matching patients with supporting documentation

### Quality Improvement

**Use Case**: Analyze medication adherence documentation

```
Find discharge summaries where medication adherence is discussed but compliance issues are mentioned
```

**Result**: Patterns of adherence problems and interventions

### Administrative Analysis

**Use Case**: Track surgical complications

```
Find all surgical notes from the last quarter that mention post-operative complications
```

**Result**: Complication rates and types by procedure

### Educational Analysis

**Use Case**: Study clinical documentation patterns

```
Compare the language used in cardiology notes versus endocrinology notes
```

**Result**: Vocabulary differences and specialization patterns

## 🔍 Advanced Features

### Custom Entity Recognition

Add your own medical concepts:

```python
# In your custom tool
custom_entities = [
    "custom_medication_name",
    "specific_procedure_type",
    "organization_specific_term"
]
```

### Query Templates

Save frequently used queries:

```yaml
# config/query_templates.yaml
templates:
  medication_review: "Find all notes mentioning medication changes in the last {days} days"
  adverse_events: "Find mentions of {drug_name} with adverse reactions or side effects"
```

### Batch Processing

Process multiple documents:

```python
from caidence import CaidenceAgent

agent = CaidenceAgent()
results = agent.batch_analyze(documents, query)
```

## 🚨 Troubleshooting

### Common Issues

#### cTAKES Not Found
```bash
# Check cTAKES installation
ls $CTAKES_PATH
java -version

# Reinstall if needed
./scripts/setup.sh
```

#### Database Connection Failed
```bash
# Check PostgreSQL status
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Out of Memory
```bash
# Increase Java heap size
export JAVA_OPTS="-Xmx8g"

# Or edit config/config.yaml
ctakes:
  java_heap_size: "8G"
```

#### Slow Performance
```bash
# Check resource usage
docker stats

# Enable caching
redis-cli ping

# Optimize queries
# Use more specific search terms
```

### Getting Help

1. **Documentation**: Check [docs/](../docs/) folder
2. **Issues**: [GitHub Issues](https://github.com/sonishsivarajkumar/cAIdence/issues)
3. **Discussions**: [GitHub Discussions](https://github.com/sonishsivarajkumar/cAIdence/discussions)
4. **Community**: Join our Slack/Discord (coming soon)

## 📚 Next Steps

### For Healthcare Professionals
1. **Try with your data**: Upload sample clinical documents
2. **Explore queries**: Test different question types
3. **Share feedback**: Help improve the interface
4. **Join research**: Participate in validation studies

### For Developers
1. **Read the code**: Explore the [architecture](architecture.md)
2. **Write tests**: Add test cases for your use cases
3. **Create tools**: Build custom analysis tools
4. **Contribute**: Submit pull requests

### For Researchers
1. **Validate results**: Compare with gold standard datasets
2. **Publish findings**: Share your research using cAIdence
3. **Collaborate**: Connect with other researchers
4. **Extend capabilities**: Add domain-specific features

## 🎓 Learning Resources

### Clinical NLP Fundamentals
- [Introduction to Clinical NLP](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6568084/)
- [Apache cTAKES Documentation](https://ctakes.apache.org/)
- [UMLS Knowledge Sources](https://www.nlm.nih.gov/research/umls/)

### Healthcare Informatics
- [HIMSS Healthcare Informatics](https://www.himss.org/)
- [AMIA Academic Informatics](https://www.amia.org/)
- [HL7 FHIR Specification](https://www.hl7.org/fhir/)

### Python & AI Development
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Documentation](https://plotly.com/python/)

## 🤝 Community

### Ways to Contribute
- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new capabilities
- **Documentation**: Improve guides and examples
- **Code**: Submit bug fixes and enhancements
- **Testing**: Help validate new features
- **Research**: Collaborate on clinical NLP studies

### Code of Conduct
We follow the [Contributor Covenant](https://www.contributor-covenant.org/):
- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment
- Follow professional standards

---

**Ready to start analyzing clinical text?** 

Jump in with: `docker-compose up` and visit http://localhost:8501

**Questions?** Open an issue or start a discussion on GitHub!

**Want to contribute?** See our [Contributing Guide](../CONTRIBUTING.md)!
