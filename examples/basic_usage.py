"""
Basic usage example for cAIdence.

This example demonstrates how to use the cAIdence agent to analyze clinical text.
"""

from caidence.agent import CaidenceAgent
from caidence.dashboard import Dashboard
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run a basic example of cAIdence usage."""
    print("🏥 cAIdence Basic Usage Example")
    print("=" * 50)
    
    # Initialize the agent
    print("Initializing cAIdence agent...")
    agent = CaidenceAgent()
    
    # Example clinical query
    query = "Find all surgical notes from the last year that mention 'arterial graft' but do not mention 'infection'."
    
    print(f"\n📝 Query: {query}")
    
    # Analyze the query
    print("\n🤖 Agent is analyzing your request...")
    result = agent.analyze(query)
    
    # Display results
    print(f"\n📊 Analysis Results:")
    print(f"- Documents processed: {result.documents_processed}")
    print(f"- Entities found: {len(result.entities_found)}")
    print(f"- Execution time: {result.execution_time:.2f} seconds")
    print(f"- Confidence: {result.confidence:.2f}")
    
    print(f"\n📋 Summary:")
    print(result.summary)
    
    if result.entities_found:
        print(f"\n🔍 Entities Found:")
        for entity in result.entities_found[:5]:  # Show first 5
            print(f"- {entity.get('entity', 'Unknown')}: {entity.get('count', 0)} occurrences")
    
    # Initialize dashboard
    print(f"\n📈 Setting up dashboard...")
    dashboard = Dashboard()
    dashboard.add_result({
        "query": result.query,
        "documents_processed": result.documents_processed,
        "entities_found": result.entities_found,
        "execution_time": result.execution_time,
        "confidence": result.confidence,
        "visualizations": result.visualizations
    })
    
    # Display dashboard summary
    summary = dashboard.render_summary()
    print(f"\n📊 Dashboard Summary:")
    print(f"- Total queries: {summary['total_queries']}")
    print(f"- Total documents: {summary['total_documents']}")
    print(f"- Total entities: {summary['total_entities']}")
    print(f"- Avg execution time: {summary['avg_execution_time']:.2f}s")
    
    print(f"\n✅ Example completed successfully!")
    print(f"\nTo run the full application: python -m caidence.main")


if __name__ == "__main__":
    main()
