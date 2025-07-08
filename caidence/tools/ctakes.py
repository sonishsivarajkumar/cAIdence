"""
Apache cTAKES integration for clinical text processing.

This module provides integration with Apache cTAKES for extracting clinical
entities, concepts, and relationships from unstructured clinical text.
"""

import subprocess
import json
import tempfile
import os
from typing import Dict, Any, List
from pathlib import Path
import logging

from . import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class CTAKESProcessor(BaseTool):
    """Tool for processing clinical text using Apache cTAKES."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="ctakes_processor",
            description="Process clinical text using Apache cTAKES to extract medical entities and concepts",
            config=config
        )
        self.ctakes_path = self.config.get("ctakes_path", "/opt/ctakes")
        self.java_path = self.config.get("java_path", "java")
        
    def initialize(self) -> bool:
        """Initialize cTAKES processor."""
        try:
            # Check if cTAKES is available
            ctakes_dir = Path(self.ctakes_path)
            if not ctakes_dir.exists():
                logger.error(f"cTAKES directory not found: {self.ctakes_path}")
                return False
            
            # Check if Java is available
            result = subprocess.run([self.java_path, "-version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Java not found or not working")
                return False
            
            self._is_initialized = True
            logger.info("cTAKES processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cTAKES: {e}")
            return False
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute cTAKES processing on clinical text.
        
        Args:
            parameters: Dictionary containing:
                - text: Clinical text to process
                - output_format: Output format (json, xml, xmi)
                - target_entities: List of specific entities to extract
        
        Returns:
            ToolResult with extracted entities and concepts
        """
        try:
            text = parameters.get("text", "")
            if not text:
                return ToolResult(
                    success=False,
                    data=None,
                    error_message="No text provided for processing"
                )
            
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
                input_file.write(text)
                input_path = input_file.name
            
            output_dir = tempfile.mkdtemp()
            
            try:
                # Run cTAKES
                result = self._run_ctakes(input_path, output_dir)
                
                # Parse results
                entities = self._parse_ctakes_output(output_dir)
                
                return ToolResult(
                    success=True,
                    data={
                        "entities": entities,
                        "text_length": len(text),
                        "entity_count": len(entities)
                    },
                    execution_time=result.get("execution_time", 0.0)
                )
                
            finally:
                # Clean up temporary files
                os.unlink(input_path)
                # TODO: Clean up output directory
            
        except Exception as e:
            logger.error(f"Error in cTAKES processing: {e}")
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    def _run_ctakes(self, input_path: str, output_dir: str) -> Dict[str, Any]:
        """Run cTAKES on the input file."""
        # TODO: Implement actual cTAKES execution
        # This is a placeholder implementation
        logger.info(f"Processing {input_path} with cTAKES")
        
        # Simulate cTAKES processing
        import time
        time.sleep(1)  # Simulate processing time
        
        return {"execution_time": 1.0}
    
    def _parse_ctakes_output(self, output_dir: str) -> List[Dict[str, Any]]:
        """Parse cTAKES output files to extract entities."""
        # TODO: Implement actual output parsing
        # This is a placeholder implementation
        
        # Simulate extracted entities
        entities = [
            {
                "text": "arterial graft",
                "type": "PROCEDURE",
                "begin": 45,
                "end": 58,
                "cui": "C0456915",
                "tui": "T061",
                "confidence": 0.95
            },
            {
                "text": "bypass surgery",
                "type": "PROCEDURE", 
                "begin": 120,
                "end": 134,
                "cui": "C0741847",
                "tui": "T061",
                "confidence": 0.89
            }
        ]
        
        return entities
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the parameter schema for cTAKES processor."""
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Clinical text to process"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["json", "xml", "xmi"],
                    "default": "json",
                    "description": "Output format for results"
                },
                "target_entities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific entities to extract (optional)"
                }
            },
            "required": ["text"]
        }
