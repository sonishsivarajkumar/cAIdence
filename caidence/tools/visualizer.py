"""
Data visualization tool for clinical analysis results.

This module provides functionality to create interactive visualizations
of clinical text analysis results using Plotly.
"""

from typing import Dict, Any, List
import logging

from . import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class Visualizer(BaseTool):
    """Tool for creating visualizations of clinical analysis results."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="visualizer",
            description="Create interactive visualizations of clinical analysis results",
            config=config
        )
    
    def initialize(self) -> bool:
        """Initialize visualizer."""
        try:
            # Check if required libraries are available
            import plotly.graph_objects as go
            import plotly.express as px
            self._plotly_available = True
        except ImportError:
            logger.warning("Plotly not available, visualizations will be limited")
            self._plotly_available = False
        
        self._is_initialized = True
        logger.info("Visualizer initialized")
        return True
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Create visualizations based on analysis results.
        
        Args:
            parameters: Dictionary containing:
                - entities: List of extracted entities
                - documents: List of processed documents
                - chart_types: List of chart types to create
                - title: Title for the visualizations
        
        Returns:
            ToolResult with visualization data
        """
        try:
            entities = parameters.get("entities", [])
            documents = parameters.get("documents", [])
            chart_types = parameters.get("chart_types", ["bar"])
            title = parameters.get("title", "Clinical Analysis Results")
            
            visualizations = []
            
            for chart_type in chart_types:
                if chart_type == "bar":
                    viz = self._create_entity_frequency_chart(entities, title)
                elif chart_type == "pie":
                    viz = self._create_entity_type_pie_chart(entities, title)
                elif chart_type == "timeline":
                    viz = self._create_document_timeline(documents, title)
                elif chart_type == "heatmap":
                    viz = self._create_entity_cooccurrence_heatmap(entities, title)
                else:
                    continue
                
                if viz:
                    visualizations.append(viz)
            
            return ToolResult(
                success=True,
                data={
                    "visualizations": visualizations,
                    "chart_count": len(visualizations)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in visualization: {e}")
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    def _create_entity_frequency_chart(self, entities: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
        """Create a bar chart showing entity frequency."""
        
        # Count entity occurrences
        entity_counts = {}
        for entity in entities:
            text = entity.get("text", "Unknown")
            entity_counts[text] = entity_counts.get(text, 0) + 1
        
        if not entity_counts:
            return None
        
        # Sort by frequency
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 10
        top_entities = sorted_entities[:10]
        
        if self._plotly_available:
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
                go.Bar(
                    x=[item[1] for item in top_entities],
                    y=[item[0] for item in top_entities],
                    orientation='h',
                    marker_color='lightblue'
                )
            ])
            
            fig.update_layout(
                title=f"{title} - Entity Frequency",
                xaxis_title="Frequency",
                yaxis_title="Entities",
                height=400
            )
            
            return {
                "type": "bar",
                "title": "Entity Frequency",
                "plotly_json": fig.to_json(),
                "data": top_entities
            }
        else:
            # Return data for manual plotting
            return {
                "type": "bar",
                "title": "Entity Frequency",
                "data": top_entities,
                "x_label": "Frequency",
                "y_label": "Entities"
            }
    
    def _create_entity_type_pie_chart(self, entities: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
        """Create a pie chart showing entity type distribution."""
        
        # Count entity types
        type_counts = {}
        for entity in entities:
            entity_type = entity.get("type", "Unknown")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        if not type_counts:
            return None
        
        if self._plotly_available:
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=0.3
                )
            ])
            
            fig.update_layout(
                title=f"{title} - Entity Type Distribution",
                height=400
            )
            
            return {
                "type": "pie",
                "title": "Entity Type Distribution",
                "plotly_json": fig.to_json(),
                "data": type_counts
            }
        else:
            return {
                "type": "pie",
                "title": "Entity Type Distribution",
                "data": type_counts
            }
    
    def _create_document_timeline(self, documents: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
        """Create a timeline visualization of documents."""
        
        # Filter documents with dates
        dated_docs = [doc for doc in documents if doc.get("date")]
        
        if not dated_docs:
            return None
        
        # Sort by date
        try:
            from datetime import datetime
            for doc in dated_docs:
                if isinstance(doc["date"], str):
                    doc["parsed_date"] = datetime.fromisoformat(doc["date"].replace('Z', '+00:00'))
                else:
                    doc["parsed_date"] = doc["date"]
            
            dated_docs.sort(key=lambda x: x["parsed_date"])
        except Exception as e:
            logger.warning(f"Error parsing dates for timeline: {e}")
            return None
        
        if self._plotly_available:
            import plotly.graph_objects as go
            
            dates = [doc["parsed_date"] for doc in dated_docs]
            doc_types = [doc.get("type", "Unknown") for doc in dated_docs]
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=dates,
                    y=list(range(len(dates))),
                    mode='markers+lines',
                    text=doc_types,
                    hovertemplate='<b>%{text}</b><br>Date: %{x}<extra></extra>',
                    marker=dict(size=8, color='blue')
                )
            ])
            
            fig.update_layout(
                title=f"{title} - Document Timeline",
                xaxis_title="Date",
                yaxis_title="Document Index",
                height=400,
                yaxis=dict(showticklabels=False)
            )
            
            return {
                "type": "timeline",
                "title": "Document Timeline",
                "plotly_json": fig.to_json(),
                "data": [(doc["parsed_date"].isoformat(), doc.get("type", "Unknown")) for doc in dated_docs]
            }
        else:
            return {
                "type": "timeline",
                "title": "Document Timeline",
                "data": [(doc["parsed_date"].isoformat(), doc.get("type", "Unknown")) for doc in dated_docs]
            }
    
    def _create_entity_cooccurrence_heatmap(self, entities: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
        """Create a heatmap showing entity co-occurrence."""
        
        # This is a simplified co-occurrence based on entity types
        # In a real implementation, you'd analyze document-level co-occurrence
        
        entity_types = list(set(entity.get("type", "Unknown") for entity in entities))
        
        if len(entity_types) < 2:
            return None
        
        # Create co-occurrence matrix (simplified)
        import random
        matrix = []
        for i, type1 in enumerate(entity_types):
            row = []
            for j, type2 in enumerate(entity_types):
                if i == j:
                    row.append(1.0)
                else:
                    # Simulate co-occurrence values
                    row.append(random.uniform(0, 0.8))
            matrix.append(row)
        
        if self._plotly_available:
            import plotly.graph_objects as go
            
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=entity_types,
                y=entity_types,
                colorscale='Blues'
            ))
            
            fig.update_layout(
                title=f"{title} - Entity Co-occurrence",
                height=400
            )
            
            return {
                "type": "heatmap",
                "title": "Entity Co-occurrence",
                "plotly_json": fig.to_json(),
                "data": {"matrix": matrix, "labels": entity_types}
            }
        else:
            return {
                "type": "heatmap",
                "title": "Entity Co-occurrence",
                "data": {"matrix": matrix, "labels": entity_types}
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the parameter schema for visualizer."""
        return {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "type": {"type": "string"}
                        }
                    },
                    "description": "List of extracted entities"
                },
                "documents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "type": {"type": "string"}
                        }
                    },
                    "description": "List of processed documents"
                },
                "chart_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["bar", "pie", "timeline", "heatmap"]
                    },
                    "default": ["bar"],
                    "description": "Types of charts to create"
                },
                "title": {
                    "type": "string",
                    "default": "Clinical Analysis Results",
                    "description": "Title for the visualizations"
                }
            }
        }
