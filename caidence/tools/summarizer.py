"""
Text summarization tool for clinical analysis results.

This module provides functionality to generate human-readable summaries
of clinical text analysis results.
"""

from typing import Dict, Any, List
import logging

from . import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class Summarizer(BaseTool):
    """Tool for generating summaries of clinical analysis results."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="summarizer",
            description="Generate human-readable summaries of clinical analysis results",
            config=config
        )
    
    def initialize(self) -> bool:
        """Initialize summarizer."""
        self._is_initialized = True
        logger.info("Summarizer initialized")
        return True
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Generate a summary of analysis results.
        
        Args:
            parameters: Dictionary containing:
                - entities: List of extracted entities
                - documents: List of processed documents
                - query: Original user query
                - format: Summary format (clinical_report, executive, technical)
        
        Returns:
            ToolResult with generated summary
        """
        try:
            entities = parameters.get("entities", [])
            documents = parameters.get("documents", [])
            query = parameters.get("query", "")
            format_type = parameters.get("format", "clinical_report")
            
            if format_type == "clinical_report":
                summary = self._generate_clinical_report(entities, documents, query)
            elif format_type == "executive":
                summary = self._generate_executive_summary(entities, documents, query)
            elif format_type == "technical":
                summary = self._generate_technical_summary(entities, documents, query)
            else:
                summary = self._generate_basic_summary(entities, documents, query)
            
            return ToolResult(
                success=True,
                data={
                    "summary": summary,
                    "format": format_type,
                    "entity_count": len(entities),
                    "document_count": len(documents)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    def _generate_clinical_report(self, entities: List[Dict[str, Any]], 
                                documents: List[Dict[str, Any]], 
                                query: str) -> str:
        """Generate a clinical report style summary."""
        
        # Count entities by type
        entity_counts = {}
        for entity in entities:
            entity_type = entity.get("type", "Unknown")
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        # Generate summary
        summary_parts = []
        
        # Header
        summary_parts.append("## Clinical Text Analysis Report")
        summary_parts.append(f"**Query**: {query}")
        summary_parts.append(f"**Documents Analyzed**: {len(documents)}")
        summary_parts.append(f"**Total Entities Found**: {len(entities)}")
        summary_parts.append("")
        
        # Entity breakdown
        summary_parts.append("### Entity Analysis")
        if entity_counts:
            for entity_type, count in sorted(entity_counts.items()):
                summary_parts.append(f"- **{entity_type}**: {count} occurrences")
        else:
            summary_parts.append("No entities found matching the criteria.")
        summary_parts.append("")
        
        # Key findings
        summary_parts.append("### Key Findings")
        if entities:
            # Group similar entities
            unique_entities = {}
            for entity in entities:
                text = entity.get("text", "").lower()
                if text not in unique_entities:
                    unique_entities[text] = []
                unique_entities[text].append(entity)
            
            for entity_text, entity_list in list(unique_entities.items())[:5]:  # Top 5
                count = len(entity_list)
                entity_type = entity_list[0].get("type", "Unknown")
                summary_parts.append(f"- '{entity_text.title()}' ({entity_type}): Found {count} time(s)")
        else:
            summary_parts.append("No significant findings based on the query criteria.")
        
        return "\n".join(summary_parts)
    
    def _generate_executive_summary(self, entities: List[Dict[str, Any]], 
                                  documents: List[Dict[str, Any]], 
                                  query: str) -> str:
        """Generate an executive summary."""
        
        summary_parts = []
        
        summary_parts.append("## Executive Summary")
        summary_parts.append("")
        
        if entities:
            summary_parts.append(f"Analysis of {len(documents)} clinical documents revealed "
                               f"{len(entities)} relevant medical entities matching your criteria.")
            
            # Top entity types
            entity_types = {}
            for entity in entities:
                entity_type = entity.get("type", "Unknown")
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            if entity_types:
                top_type = max(entity_types.items(), key=lambda x: x[1])
                summary_parts.append(f"The most frequently mentioned entity type was "
                                   f"{top_type[0]} with {top_type[1]} occurrences.")
        else:
            summary_parts.append(f"Analysis of {len(documents)} clinical documents found "
                               "no entities matching the specified criteria.")
        
        summary_parts.append("")
        summary_parts.append("This analysis provides insights into the prevalence and "
                           "context of specific medical concepts within your document collection.")
        
        return "\n".join(summary_parts)
    
    def _generate_technical_summary(self, entities: List[Dict[str, Any]], 
                                  documents: List[Dict[str, Any]], 
                                  query: str) -> str:
        """Generate a technical summary."""
        
        summary_parts = []
        
        summary_parts.append("## Technical Analysis Summary")
        summary_parts.append("")
        summary_parts.append("### Processing Statistics")
        summary_parts.append(f"- Input Documents: {len(documents)}")
        summary_parts.append(f"- Entities Extracted: {len(entities)}")
        
        if entities:
            # Calculate confidence statistics
            confidences = [e.get("confidence", 0) for e in entities if "confidence" in e]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                summary_parts.append(f"- Average Confidence: {avg_confidence:.3f}")
            
            # Entity type distribution
            entity_types = {}
            for entity in entities:
                entity_type = entity.get("type", "Unknown")
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            summary_parts.append("")
            summary_parts.append("### Entity Type Distribution")
            for entity_type, count in sorted(entity_types.items()):
                percentage = (count / len(entities)) * 100
                summary_parts.append(f"- {entity_type}: {count} ({percentage:.1f}%)")
        
        return "\n".join(summary_parts)
    
    def _generate_basic_summary(self, entities: List[Dict[str, Any]], 
                              documents: List[Dict[str, Any]], 
                              query: str) -> str:
        """Generate a basic summary."""
        
        if entities:
            return (f"Found {len(entities)} entities in {len(documents)} documents "
                   f"matching your query: '{query}'")
        else:
            return (f"No entities found in {len(documents)} documents "
                   f"matching your query: '{query}'")
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the parameter schema for summarizer."""
        return {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "type": {"type": "string"},
                            "confidence": {"type": "number"}
                        }
                    },
                    "description": "List of extracted entities"
                },
                "documents": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of processed documents"
                },
                "query": {
                    "type": "string",
                    "description": "Original user query"
                },
                "format": {
                    "type": "string",
                    "enum": ["clinical_report", "executive", "technical", "basic"],
                    "default": "clinical_report",
                    "description": "Summary format type"
                }
            }
        }
