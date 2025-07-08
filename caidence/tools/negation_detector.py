"""
Negation detection tool for clinical text analysis.

This module provides functionality to detect negated medical concepts
in clinical text, which is crucial for accurate clinical NLP.
"""

from typing import Dict, Any, List, Tuple
import re
import logging

from . import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class NegationDetector(BaseTool):
    """Tool for detecting negated medical concepts in clinical text."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="negation_detector",
            description="Detect negated medical concepts in clinical text",
            config=config
        )
        
        # Common negation patterns in clinical text
        self.negation_patterns = [
            r'\b(no|not|never|without|absent|negative|denies?|ruled?\s+out)\b',
            r'\b(free\s+of|clear\s+of|unremarkable\s+for)\b',
            r'\b(shows?\s+no|reveals?\s+no|demonstrates?\s+no)\b',
            r'\b(fails?\s+to\s+show|fails?\s+to\s+reveal)\b'
        ]
        
        # Scope of negation (words after negation that are affected)
        self.negation_scope = 6  # words
    
    def initialize(self) -> bool:
        """Initialize negation detector."""
        self._is_initialized = True
        logger.info("Negation detector initialized")
        return True
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Detect negated concepts in clinical text.
        
        Args:
            parameters: Dictionary containing:
                - text: Clinical text to analyze
                - entities: List of entities to check for negation
                - negated_terms: Specific terms to look for negation
        
        Returns:
            ToolResult with negation analysis results
        """
        try:
            text = parameters.get("text", "")
            entities = parameters.get("entities", [])
            negated_terms = parameters.get("negated_terms", [])
            
            if not text:
                return ToolResult(
                    success=False,
                    data=None,
                    error_message="No text provided for negation analysis"
                )
            
            # Find negation markers in text
            negation_markers = self._find_negation_markers(text)
            
            # Check entities for negation
            negated_entities = []
            for entity in entities:
                if self._is_entity_negated(entity, text, negation_markers):
                    negated_entities.append(entity)
            
            # Check specific terms for negation
            negated_term_results = {}
            for term in negated_terms:
                negated_term_results[term] = self._is_term_negated(term, text, negation_markers)
            
            return ToolResult(
                success=True,
                data={
                    "negation_markers": negation_markers,
                    "negated_entities": negated_entities,
                    "negated_terms": negated_term_results,
                    "total_negations_found": len(negation_markers)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in negation detection: {e}")
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    def _find_negation_markers(self, text: str) -> List[Dict[str, Any]]:
        """Find all negation markers in the text."""
        markers = []
        text_lower = text.lower()
        
        for pattern in self.negation_patterns:
            for match in re.finditer(pattern, text_lower):
                markers.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "pattern": pattern
                })
        
        # Sort markers by position
        markers.sort(key=lambda x: x["start"])
        return markers
    
    def _is_entity_negated(self, entity: Dict[str, Any], text: str, markers: List[Dict[str, Any]]) -> bool:
        """Check if an entity is negated."""
        entity_start = entity.get("begin", entity.get("start", 0))
        entity_end = entity.get("end", entity_start + len(entity.get("text", "")))
        
        # Check if entity falls within scope of any negation marker
        for marker in markers:
            if self._is_in_negation_scope(entity_start, entity_end, marker, text):
                return True
        
        return False
    
    def _is_term_negated(self, term: str, text: str, markers: List[Dict[str, Any]]) -> bool:
        """Check if a specific term is negated in the text."""
        text_lower = text.lower()
        term_lower = term.lower()
        
        # Find all occurrences of the term
        term_positions = []
        start = 0
        while True:
            pos = text_lower.find(term_lower, start)
            if pos == -1:
                break
            term_positions.append((pos, pos + len(term)))
            start = pos + 1
        
        # Check if any occurrence is negated
        for term_start, term_end in term_positions:
            for marker in markers:
                if self._is_in_negation_scope(term_start, term_end, marker, text):
                    return True
        
        return False
    
    def _is_in_negation_scope(self, entity_start: int, entity_end: int, 
                             marker: Dict[str, Any], text: str) -> bool:
        """Check if entity falls within the scope of a negation marker."""
        marker_end = marker["end"]
        
        # Calculate scope end (number of words after negation)
        words_after_marker = text[marker_end:].split()[:self.negation_scope]
        if not words_after_marker:
            return False
        
        scope_text = " ".join(words_after_marker)
        scope_end = marker_end + len(scope_text)
        
        # Check if entity is within scope
        return marker_end <= entity_start <= scope_end
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the parameter schema for negation detector."""
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Clinical text to analyze for negation"
                },
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "begin": {"type": "integer"},
                            "end": {"type": "integer"}
                        }
                    },
                    "description": "List of entities to check for negation"
                },
                "negated_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific terms to check for negation"
                }
            },
            "required": ["text"]
        }
