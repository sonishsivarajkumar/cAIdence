"""
Enhanced Visualization Suite for cAIdence.

This module provides advanced visualization capabilities including charts, graphs,
timelines, and interactive dashboards for clinical data analysis.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class VisualizationConfig:
    """Configuration for visualizations."""
    theme: str = "plotly_white"
    color_scheme: List[str] = None
    width: int = 800
    height: int = 600
    interactive: bool = True
    
    def __post_init__(self):
        if self.color_scheme is None:
            self.color_scheme = px.colors.qualitative.Set3


class EnhancedVisualizer:
    """Enhanced visualization tools for clinical data."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """Initialize enhanced visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
    
    def create_entity_timeline(self, entities: List[Dict[str, Any]], 
                             patient_id: str = None) -> go.Figure:
        """Create an interactive timeline of clinical entities.
        
        Args:
            entities: List of entity dictionaries with timestamp info
            patient_id: Optional patient identifier for title
            
        Returns:
            Plotly figure with timeline visualization
        """
        if not entities:
            return self._create_empty_figure("No entities to display")
        
        # Convert entities to DataFrame
        df_data = []
        for entity in entities:
            df_data.append({
                'entity': entity.get('text', 'Unknown'),
                'type': entity.get('type', 'Unknown'),
                'date': entity.get('date', datetime.now()),
                'confidence': entity.get('confidence', 0.0),
                'negated': entity.get('negated', False),
                'source_doc': entity.get('source_document', 'Unknown')
            })
        
        df = pd.DataFrame(df_data)
        
        # Create timeline
        fig = px.timeline(
            df,
            x_start='date',
            x_end='date',
            y='type',
            color='type',
            hover_data=['entity', 'confidence', 'negated', 'source_doc'],
            title=f"Clinical Entity Timeline{' for ' + patient_id if patient_id else ''}",
            color_discrete_sequence=self.config.color_scheme
        )
        
        fig.update_layout(
            template=self.config.theme,
            width=self.config.width,
            height=self.config.height,
            xaxis_title="Date",
            yaxis_title="Entity Type"
        )
        
        return fig
    
    def create_entity_network(self, entities: List[Dict[str, Any]], 
                            relationships: List[Dict[str, Any]] = None) -> go.Figure:
        """Create a network graph of entity relationships.
        
        Args:
            entities: List of entity dictionaries
            relationships: Optional list of relationship dictionaries
            
        Returns:
            Plotly figure with network visualization
        """
        if not entities:
            return self._create_empty_figure("No entities to display")
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes (entities)
        for entity in entities:
            G.add_node(
                entity.get('text', 'Unknown'),
                type=entity.get('type', 'Unknown'),
                confidence=entity.get('confidence', 0.0)
            )
        
        # Add edges (relationships)
        if relationships:
            for rel in relationships:
                source = rel.get('source', '')
                target = rel.get('target', '')
                if source in G.nodes and target in G.nodes:
                    G.add_edge(source, target, relation=rel.get('type', 'related'))
        
        # Calculate layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Create edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_info.append(f"{edge[0]} - {edge[1]}")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node traces by type
        node_traces = []
        entity_types = list(set([data['type'] for node, data in G.nodes(data=True)]))
        
        for i, entity_type in enumerate(entity_types):
            nodes_of_type = [node for node, data in G.nodes(data=True) if data['type'] == entity_type]
            
            node_x = [pos[node][0] for node in nodes_of_type]
            node_y = [pos[node][1] for node in nodes_of_type]
            node_text = [f"{node}<br>Type: {G.nodes[node]['type']}<br>Confidence: {G.nodes[node]['confidence']:.2f}" 
                        for node in nodes_of_type]
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                hovertext=node_text,
                text=[node.split()[0] for node in nodes_of_type],  # Show first word as label
                textposition="middle center",
                marker=dict(
                    size=20,
                    color=self.config.color_scheme[i % len(self.config.color_scheme)],
                    line=dict(width=2, color='white')
                ),
                name=entity_type
            )
            node_traces.append(node_trace)
        
        # Create figure
        fig = go.Figure(data=[edge_trace] + node_traces)
        fig.update_layout(
            title="Clinical Entity Relationship Network",
            template=self.config.theme,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Hover over nodes for details",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            width=self.config.width,
            height=self.config.height
        )
        
        return fig
    
    def create_sentiment_analysis_chart(self, documents: List[Dict[str, Any]]) -> go.Figure:
        """Create sentiment analysis visualization.
        
        Args:
            documents: List of document dictionaries with sentiment scores
            
        Returns:
            Plotly figure with sentiment analysis
        """
        if not documents:
            return self._create_empty_figure("No documents to analyze")
        
        # Extract sentiment data
        sentiments = []
        dates = []
        doc_types = []
        
        for doc in documents:
            sentiment = doc.get('sentiment', {})
            sentiments.append(sentiment.get('compound', 0.0))
            dates.append(doc.get('date', datetime.now()))
            doc_types.append(doc.get('type', 'Unknown'))
        
        df = pd.DataFrame({
            'sentiment': sentiments,
            'date': dates,
            'doc_type': doc_types
        })
        
        # Create subplot with multiple charts
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Sentiment Over Time', 'Sentiment Distribution', 
                          'Sentiment by Document Type', 'Document Count by Type'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Sentiment over time
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['sentiment'],
                mode='lines+markers',
                name='Sentiment',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # 2. Sentiment distribution
        fig.add_trace(
            go.Histogram(
                x=df['sentiment'],
                nbinsx=20,
                name='Distribution',
                marker_color='lightblue'
            ),
            row=1, col=2
        )
        
        # 3. Box plot by document type
        for doc_type in df['doc_type'].unique():
            type_data = df[df['doc_type'] == doc_type]
            fig.add_trace(
                go.Box(
                    y=type_data['sentiment'],
                    name=doc_type,
                    boxpoints='all'
                ),
                row=2, col=1
            )
        
        # 4. Document count by type
        type_counts = df['doc_type'].value_counts()
        fig.add_trace(
            go.Bar(
                x=type_counts.index,
                y=type_counts.values,
                name='Count',
                marker_color='lightgreen'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Clinical Document Sentiment Analysis",
            template=self.config.theme,
            height=800,
            width=1200,
            showlegend=False
        )
        
        return fig
    
    def create_cohort_comparison(self, cohorts: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
        """Create cohort comparison visualization.
        
        Args:
            cohorts: Dictionary mapping cohort names to lists of patient data
            
        Returns:
            Plotly figure comparing cohorts
        """
        if not cohorts:
            return self._create_empty_figure("No cohorts to compare")
        
        # Calculate cohort statistics
        cohort_stats = {}
        for name, patients in cohorts.items():
            stats = {
                'count': len(patients),
                'avg_age': sum(p.get('age', 0) for p in patients) / len(patients) if patients else 0,
                'conditions': {},
                'medications': {}
            }
            
            # Count conditions and medications
            for patient in patients:
                for condition in patient.get('conditions', []):
                    stats['conditions'][condition] = stats['conditions'].get(condition, 0) + 1
                for medication in patient.get('medications', []):
                    stats['medications'][medication] = stats['medications'].get(medication, 0) + 1
            
            cohort_stats[name] = stats
        
        # Create comparison charts
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Cohort Sizes', 'Average Age', 'Top Conditions', 'Top Medications'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        cohort_names = list(cohort_stats.keys())
        
        # 1. Cohort sizes
        fig.add_trace(
            go.Bar(
                x=cohort_names,
                y=[stats['count'] for stats in cohort_stats.values()],
                name='Patient Count',
                marker_color='blue'
            ),
            row=1, col=1
        )
        
        # 2. Average ages
        fig.add_trace(
            go.Bar(
                x=cohort_names,
                y=[stats['avg_age'] for stats in cohort_stats.values()],
                name='Average Age',
                marker_color='green'
            ),
            row=1, col=2
        )
        
        # 3. Top conditions (showing most common across all cohorts)
        all_conditions = {}
        for stats in cohort_stats.values():
            for condition, count in stats['conditions'].items():
                all_conditions[condition] = all_conditions.get(condition, 0) + count
        
        top_conditions = sorted(all_conditions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for i, cohort_name in enumerate(cohort_names):
            condition_counts = [cohort_stats[cohort_name]['conditions'].get(cond[0], 0) 
                              for cond in top_conditions]
            fig.add_trace(
                go.Bar(
                    x=[cond[0] for cond in top_conditions],
                    y=condition_counts,
                    name=f'{cohort_name} Conditions',
                    marker_color=self.config.color_scheme[i % len(self.config.color_scheme)]
                ),
                row=2, col=1
            )
        
        # 4. Top medications
        all_medications = {}
        for stats in cohort_stats.values():
            for medication, count in stats['medications'].items():
                all_medications[medication] = all_medications.get(medication, 0) + count
        
        top_medications = sorted(all_medications.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for i, cohort_name in enumerate(cohort_names):
            med_counts = [cohort_stats[cohort_name]['medications'].get(med[0], 0) 
                         for med in top_medications]
            fig.add_trace(
                go.Bar(
                    x=[med[0] for med in top_medications],
                    y=med_counts,
                    name=f'{cohort_name} Medications',
                    marker_color=self.config.color_scheme[i % len(self.config.color_scheme)]
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Cohort Comparison Analysis",
            template=self.config.theme,
            height=800,
            width=1200,
            showlegend=True
        )
        
        return fig
    
    def create_temporal_heatmap(self, events: List[Dict[str, Any]], 
                              time_granularity: str = "month") -> go.Figure:
        """Create temporal heatmap of clinical events.
        
        Args:
            events: List of event dictionaries with dates and types
            time_granularity: Time granularity ('day', 'week', 'month', 'year')
            
        Returns:
            Plotly figure with temporal heatmap
        """
        if not events:
            return self._create_empty_figure("No events to display")
        
        # Convert to DataFrame
        df = pd.DataFrame(events)
        df['date'] = pd.to_datetime(df.get('date', datetime.now()))
        df['event_type'] = df.get('type', 'Unknown')
        
        # Create time groups based on granularity
        if time_granularity == "day":
            df['time_group'] = df['date'].dt.strftime('%Y-%m-%d')
        elif time_granularity == "week":
            df['time_group'] = df['date'].dt.strftime('%Y-W%U')
        elif time_granularity == "month":
            df['time_group'] = df['date'].dt.strftime('%Y-%m')
        else:  # year
            df['time_group'] = df['date'].dt.strftime('%Y')
        
        # Create pivot table for heatmap
        heatmap_data = df.groupby(['time_group', 'event_type']).size().unstack(fill_value=0)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Viridis',
            showscale=True,
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=f"Clinical Events Heatmap by {time_granularity.title()}",
            template=self.config.theme,
            xaxis_title="Event Type",
            yaxis_title=f"Time ({time_granularity.title()})",
            width=self.config.width,
            height=self.config.height
        )
        
        return fig
    
    def _create_empty_figure(self, message: str) -> go.Figure:
        """Create an empty figure with a message.
        
        Args:
            message: Message to display
            
        Returns:
            Empty Plotly figure
        """
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template=self.config.theme,
            width=self.config.width,
            height=self.config.height,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        return fig


def create_summary_dashboard(analysis_results: Dict[str, Any]) -> go.Figure:
    """Create a comprehensive summary dashboard.
    
    Args:
        analysis_results: Dictionary containing various analysis results
        
    Returns:
        Plotly figure with summary dashboard
    """
    visualizer = EnhancedVisualizer()
    
    # Extract key metrics
    total_documents = analysis_results.get('document_count', 0)
    total_entities = analysis_results.get('entity_count', 0)
    unique_patients = analysis_results.get('patient_count', 0)
    analysis_duration = analysis_results.get('duration_seconds', 0)
    
    # Create summary metrics
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=(
            'Document Summary', 'Entity Distribution', 'Processing Time',
            'Top Conditions', 'Sentiment Overview', 'Data Quality'
        ),
        specs=[[{"type": "indicator"}, {"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "gauge"}, {"type": "bar"}]]
    )
    
    # Key metrics indicators
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=total_documents,
            title={"text": "Documents Processed"},
            gauge={'axis': {'range': [0, total_documents * 1.2]}}
        ),
        row=1, col=1
    )
    
    # More dashboard components would be added here...
    
    fig.update_layout(
        title="cAIdence Analysis Dashboard",
        template="plotly_white",
        height=800,
        width=1400
    )
    
    return fig
