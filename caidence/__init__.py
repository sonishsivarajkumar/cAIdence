"""
cAIdence: Democratizing Clinical NLP through Agentic AI

An open-source, agentic AI layer over Apache cTAKES that allows clinical 
researchers, hospital administrators, data analysts, and students to unlock 
insights from clinical text using natural language.
"""

__version__ = "0.1.0"
__author__ = "Sonish Sivarajkumar"
__email__ = "sonish@example.com"
__license__ = "Apache 2.0"

from .agent import CaidenceAgent
from .tools import ToolRegistry
from .dashboard import Dashboard

__all__ = ["CaidenceAgent", "ToolRegistry", "Dashboard"]
