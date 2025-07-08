"""
Document filtering tool for cAIdence.

This module provides functionality to filter clinical documents based on
various criteria such as document type, date range, and content.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from . import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class DocumentFilter(BaseTool):
    """Tool for filtering clinical documents based on criteria."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="document_filter",
            description="Filter clinical documents based on type, date, and other criteria",
            config=config
        )
    
    def initialize(self) -> bool:
        """Initialize document filter."""
        self._is_initialized = True
        logger.info("Document filter initialized")
        return True
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Filter documents based on specified criteria.
        
        Args:
            parameters: Dictionary containing:
                - documents: List of documents to filter
                - types: List of document types to include
                - date_range: Date range filter
                - keywords: Keywords that must be present
                - exclude_keywords: Keywords that must not be present
        
        Returns:
            ToolResult with filtered documents
        """
        try:
            documents = parameters.get("documents", [])
            doc_types = parameters.get("types", [])
            date_range = parameters.get("date_range")
            keywords = parameters.get("keywords", [])
            exclude_keywords = parameters.get("exclude_keywords", [])
            
            filtered_docs = []
            
            for doc in documents:
                if self._should_include_document(doc, doc_types, date_range, keywords, exclude_keywords):
                    filtered_docs.append(doc)
            
            return ToolResult(
                success=True,
                data={
                    "filtered_documents": filtered_docs,
                    "total_input": len(documents),
                    "total_output": len(filtered_docs),
                    "filter_ratio": len(filtered_docs) / len(documents) if documents else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Error in document filtering: {e}")
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    def _should_include_document(self, document: Dict[str, Any], 
                               doc_types: List[str], 
                               date_range: Dict[str, Any],
                               keywords: List[str],
                               exclude_keywords: List[str]) -> bool:
        """Check if a document should be included based on filters."""
        
        # Filter by document type
        if doc_types:
            doc_type = document.get("type", "").lower()
            if not any(dtype.lower() in doc_type for dtype in doc_types):
                return False
        
        # Filter by date range
        if date_range:
            doc_date = document.get("date")
            if doc_date and not self._is_in_date_range(doc_date, date_range):
                return False
        
        # Filter by required keywords
        content = document.get("content", "").lower()
        if keywords:
            if not any(keyword.lower() in content for keyword in keywords):
                return False
        
        # Filter by excluded keywords
        if exclude_keywords:
            if any(keyword.lower() in content for keyword in exclude_keywords):
                return False
        
        return True
    
    def _is_in_date_range(self, doc_date: str, date_range: Dict[str, Any]) -> bool:
        """Check if document date is within the specified range."""
        try:
            # Parse document date
            if isinstance(doc_date, str):
                doc_datetime = datetime.fromisoformat(doc_date.replace('Z', '+00:00'))
            else:
                doc_datetime = doc_date
            
            # Check against range
            start_date = date_range.get("start")
            end_date = date_range.get("end")
            
            if start_date and doc_datetime < start_date:
                return False
            
            if end_date and doc_datetime > end_date:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error parsing date {doc_date}: {e}")
            return True  # Include document if date parsing fails
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the parameter schema for document filter."""
        return {
            "type": "object",
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "type": {"type": "string"},
                            "date": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    },
                    "description": "List of documents to filter"
                },
                "types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Document types to include (e.g., 'surgical notes', 'discharge summary')"
                },
                "date_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string", "format": "date"},
                        "end": {"type": "string", "format": "date"}
                    },
                    "description": "Date range for filtering documents"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords that must be present in documents"
                },
                "exclude_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords that must not be present in documents"
                }
            }
        }
