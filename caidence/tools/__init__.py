"""
Tool registry and management for cAIdence.

This module provides a registry for all available tools and implements
the base tool interface that all tools must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    """Base class for all cAIdence tools."""
    
    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.config = config or {}
        self._is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the tool. Returns True if successful."""
        pass
    
    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the parameter schema for this tool."""
        pass
    
    def is_available(self) -> bool:
        """Check if the tool is available and properly initialized."""
        return self._is_initialized


class ToolRegistry:
    """Registry for managing all available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._initialize_default_tools()
    
    def register_tool(self, tool: BaseTool) -> bool:
        """
        Register a tool in the registry.
        
        Args:
            tool: Tool instance to register
            
        Returns:
            True if registration successful
        """
        try:
            if tool.initialize():
                self._tools[tool.name] = tool
                logger.info(f"Registered tool: {tool.name}")
                return True
            else:
                logger.error(f"Failed to initialize tool: {tool.name}")
                return False
        except Exception as e:
            logger.error(f"Error registering tool {tool.name}: {e}")
            return False
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def execute_tool(self, name: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool by name.
        
        Args:
            name: Tool name
            parameters: Tool parameters
            
        Returns:
            ToolResult with execution results
        """
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                error_message=f"Tool '{name}' not found"
            )
        
        if not tool.is_available():
            return ToolResult(
                success=False,
                data=None,
                error_message=f"Tool '{name}' is not available"
            )
        
        try:
            return tool.execute(parameters)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    def _initialize_default_tools(self):
        """Initialize default tools."""
        from .ctakes import CTAKESProcessor
        from .document_filter import DocumentFilter
        from .negation_detector import NegationDetector
        from .summarizer import Summarizer
        from .visualizer import Visualizer
        
        # Register default tools
        default_tools = [
            CTAKESProcessor(),
            DocumentFilter(),
            NegationDetector(),
            Summarizer(),
            Visualizer()
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
