"""
Interactive dashboard for cAIdence.

This module provides the main dashboard interface for displaying
clinical analysis results in an interactive format.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class Dashboard:
    """Main dashboard class for displaying clinical analysis results."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the dashboard.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.results = []
        self._setup_dashboard()
    
    def _setup_dashboard(self):
        """Set up the dashboard components."""
        logger.info("Setting up dashboard...")
    
    def add_result(self, result: Dict[str, Any]):
        """
        Add an analysis result to the dashboard.
        
        Args:
            result: Analysis result dictionary
        """
        self.results.append(result)
        logger.info(f"Added result to dashboard: {result.get('query', 'Unknown query')}")
    
    def clear_results(self):
        """Clear all results from the dashboard."""
        self.results = []
        logger.info("Cleared dashboard results")
    
    def render_summary(self) -> Dict[str, Any]:
        """
        Render a summary of all results.
        
        Returns:
            Dictionary containing summary statistics
        """
        if not self.results:
            return {
                "total_queries": 0,
                "total_documents": 0,
                "total_entities": 0,
                "avg_execution_time": 0
            }
        
        total_queries = len(self.results)
        total_documents = sum(r.get("documents_processed", 0) for r in self.results)
        total_entities = sum(len(r.get("entities_found", [])) for r in self.results)
        avg_execution_time = sum(r.get("execution_time", 0) for r in self.results) / total_queries
        
        return {
            "total_queries": total_queries,
            "total_documents": total_documents,
            "total_entities": total_entities,
            "avg_execution_time": avg_execution_time
        }
    
    def render_results_table(self) -> List[Dict[str, Any]]:
        """
        Render results in table format.
        
        Returns:
            List of results formatted for table display
        """
        table_data = []
        
        for i, result in enumerate(self.results):
            table_data.append({
                "id": i + 1,
                "query": result.get("query", ""),
                "documents": result.get("documents_processed", 0),
                "entities": len(result.get("entities_found", [])),
                "execution_time": f"{result.get('execution_time', 0):.2f}s",
                "confidence": f"{result.get('confidence', 0):.2f}"
            })
        
        return table_data
    
    def render_visualizations(self) -> List[Dict[str, Any]]:
        """
        Render all visualizations from results.
        
        Returns:
            List of visualization dictionaries
        """
        visualizations = []
        
        for result in self.results:
            result_viz = result.get("visualizations", [])
            for viz in result_viz:
                viz["query"] = result.get("query", "")
                visualizations.append(viz)
        
        return visualizations
    
    def get_entity_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all entities across results.
        
        Returns:
            Dictionary with entity statistics
        """
        all_entities = []
        for result in self.results:
            all_entities.extend(result.get("entities_found", []))
        
        if not all_entities:
            return {"total": 0, "by_type": {}, "most_common": []}
        
        # Count by type
        by_type = {}
        entity_texts = {}
        
        for entity in all_entities:
            entity_type = entity.get("type", "Unknown")
            entity_text = entity.get("entity", entity.get("text", "Unknown"))
            
            by_type[entity_type] = by_type.get(entity_type, 0) + 1
            entity_texts[entity_text] = entity_texts.get(entity_text, 0) + 1
        
        # Get most common entities
        most_common = sorted(entity_texts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total": len(all_entities),
            "by_type": by_type,
            "most_common": most_common
        }
    
    def export_results(self, format_type: str = "json") -> Any:
        """
        Export results in specified format.
        
        Args:
            format_type: Export format (json, csv, excel)
            
        Returns:
            Exported data in requested format
        """
        if format_type == "json":
            return self.results
        elif format_type == "csv":
            return self._export_csv()
        elif format_type == "excel":
            return self._export_excel()
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_csv(self) -> str:
        """Export results as CSV string."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Query", "Documents", "Entities", "Execution Time", "Confidence"])
        
        # Write data
        for result in self.results:
            writer.writerow([
                result.get("query", ""),
                result.get("documents_processed", 0),
                len(result.get("entities_found", [])),
                result.get("execution_time", 0),
                result.get("confidence", 0)
            ])
        
        return output.getvalue()
    
    def _export_excel(self) -> bytes:
        """Export results as Excel file."""
        try:
            import pandas as pd
            import io
            
            # Create DataFrame
            data = []
            for result in self.results:
                data.append({
                    "Query": result.get("query", ""),
                    "Documents": result.get("documents_processed", 0),
                    "Entities": len(result.get("entities_found", [])),
                    "Execution Time": result.get("execution_time", 0),
                    "Confidence": result.get("confidence", 0)
                })
            
            df = pd.DataFrame(data)
            
            # Export to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Results', index=False)
            
            return output.getvalue()
            
        except ImportError:
            logger.error("pandas and openpyxl required for Excel export")
            raise ValueError("Excel export requires pandas and openpyxl")
