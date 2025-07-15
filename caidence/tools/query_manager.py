"""
Query History and Saved Searches for cAIdence.

This module manages user query history, saved searches, and query analytics
to improve user experience and provide insights into usage patterns.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import sqlite3
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class QueryRecord:
    """Represents a user query record."""
    id: str
    user_id: str
    query_text: str
    query_type: str  # 'search', 'analysis', 'export'
    timestamp: datetime
    execution_time_ms: int
    result_count: int
    success: bool
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = None
    results_summary: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.results_summary is None:
            self.results_summary = {}


@dataclass
class SavedSearch:
    """Represents a saved search configuration."""
    id: str
    user_id: str
    name: str
    description: str
    query_text: str
    parameters: Dict[str, Any]
    created_at: datetime
    last_modified: datetime
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    is_favorite: bool = False
    tags: List[str] = None
    shared: bool = False
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class QueryHistoryManager:
    """Manages query history and saved searches."""
    
    def __init__(self, db_path: str = "caidence_queries.db"):
        """Initialize query history manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    execution_time_ms INTEGER NOT NULL,
                    result_count INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    parameters TEXT,
                    results_summary TEXT
                )
            """)
            
            # Saved searches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    query_text TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_modified TEXT NOT NULL,
                    last_executed TEXT,
                    execution_count INTEGER DEFAULT 0,
                    is_favorite BOOLEAN DEFAULT FALSE,
                    tags TEXT,
                    shared BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Query analytics table for aggregated stats
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_analytics (
                    date TEXT PRIMARY KEY,
                    total_queries INTEGER DEFAULT 0,
                    successful_queries INTEGER DEFAULT 0,
                    failed_queries INTEGER DEFAULT 0,
                    avg_execution_time REAL DEFAULT 0.0,
                    unique_users INTEGER DEFAULT 0,
                    top_query_types TEXT,
                    updated_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def add_query_record(self, query_record: QueryRecord) -> None:
        """Add a query record to history.
        
        Args:
            query_record: Query record to add
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO query_history 
                    (id, user_id, query_text, query_type, timestamp, execution_time_ms,
                     result_count, success, error_message, parameters, results_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    query_record.id,
                    query_record.user_id,
                    query_record.query_text,
                    query_record.query_type,
                    query_record.timestamp.isoformat(),
                    query_record.execution_time_ms,
                    query_record.result_count,
                    query_record.success,
                    query_record.error_message,
                    json.dumps(query_record.parameters),
                    json.dumps(query_record.results_summary)
                ))
                conn.commit()
                
            # Update analytics
            self._update_daily_analytics(query_record)
            
        except Exception as e:
            logger.error(f"Error adding query record: {str(e)}")
    
    def get_query_history(self, user_id: str, limit: int = 50, 
                         days_back: int = 30) -> List[QueryRecord]:
        """Get query history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of records to return
            days_back: Number of days to look back
            
        Returns:
            List of query records
        """
        try:
            since_date = datetime.now() - timedelta(days=days_back)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM query_history 
                    WHERE user_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, since_date.isoformat(), limit))
                
                records = []
                for row in cursor.fetchall():
                    record = QueryRecord(
                        id=row[0],
                        user_id=row[1],
                        query_text=row[2],
                        query_type=row[3],
                        timestamp=datetime.fromisoformat(row[4]),
                        execution_time_ms=row[5],
                        result_count=row[6],
                        success=bool(row[7]),
                        error_message=row[8],
                        parameters=json.loads(row[9]) if row[9] else {},
                        results_summary=json.loads(row[10]) if row[10] else {}
                    )
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Error getting query history: {str(e)}")
            return []
    
    def save_search(self, saved_search: SavedSearch) -> bool:
        """Save a search configuration.
        
        Args:
            saved_search: Saved search to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO saved_searches
                    (id, user_id, name, description, query_text, parameters,
                     created_at, last_modified, last_executed, execution_count,
                     is_favorite, tags, shared)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    saved_search.id,
                    saved_search.user_id,
                    saved_search.name,
                    saved_search.description,
                    saved_search.query_text,
                    json.dumps(saved_search.parameters),
                    saved_search.created_at.isoformat(),
                    saved_search.last_modified.isoformat(),
                    saved_search.last_executed.isoformat() if saved_search.last_executed else None,
                    saved_search.execution_count,
                    saved_search.is_favorite,
                    json.dumps(saved_search.tags),
                    saved_search.shared
                ))
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving search: {str(e)}")
            return False
    
    def get_saved_searches(self, user_id: str, include_shared: bool = True) -> List[SavedSearch]:
        """Get saved searches for a user.
        
        Args:
            user_id: User identifier
            include_shared: Whether to include shared searches
            
        Returns:
            List of saved searches
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if include_shared:
                    cursor.execute("""
                        SELECT * FROM saved_searches 
                        WHERE user_id = ? OR shared = TRUE
                        ORDER BY is_favorite DESC, last_modified DESC
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT * FROM saved_searches 
                        WHERE user_id = ?
                        ORDER BY is_favorite DESC, last_modified DESC
                    """, (user_id,))
                
                searches = []
                for row in cursor.fetchall():
                    search = SavedSearch(
                        id=row[0],
                        user_id=row[1],
                        name=row[2],
                        description=row[3],
                        query_text=row[4],
                        parameters=json.loads(row[5]),
                        created_at=datetime.fromisoformat(row[6]),
                        last_modified=datetime.fromisoformat(row[7]),
                        last_executed=datetime.fromisoformat(row[8]) if row[8] else None,
                        execution_count=row[9],
                        is_favorite=bool(row[10]),
                        tags=json.loads(row[11]) if row[11] else [],
                        shared=bool(row[12])
                    )
                    searches.append(search)
                
                return searches
                
        except Exception as e:
            logger.error(f"Error getting saved searches: {str(e)}")
            return []
    
    def delete_saved_search(self, search_id: str, user_id: str) -> bool:
        """Delete a saved search.
        
        Args:
            search_id: Search identifier
            user_id: User identifier (for authorization)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM saved_searches 
                    WHERE id = ? AND user_id = ?
                """, (search_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting saved search: {str(e)}")
            return False
    
    def update_search_execution(self, search_id: str) -> None:
        """Update execution statistics for a saved search.
        
        Args:
            search_id: Search identifier
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE saved_searches 
                    SET last_executed = ?, execution_count = execution_count + 1
                    WHERE id = ?
                """, (datetime.now().isoformat(), search_id))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating search execution: {str(e)}")
    
    def get_query_suggestions(self, user_id: str, partial_query: str, 
                            limit: int = 5) -> List[str]:
        """Get query suggestions based on history.
        
        Args:
            user_id: User identifier
            partial_query: Partial query text
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested queries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT query_text, COUNT(*) as frequency
                    FROM query_history 
                    WHERE user_id = ? AND query_text LIKE ? AND success = TRUE
                    GROUP BY query_text
                    ORDER BY frequency DESC, timestamp DESC
                    LIMIT ?
                """, (user_id, f"%{partial_query}%", limit))
                
                suggestions = [row[0] for row in cursor.fetchall()]
                return suggestions
                
        except Exception as e:
            logger.error(f"Error getting query suggestions: {str(e)}")
            return []
    
    def get_analytics_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """Get analytics summary for the specified period.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Analytics summary dictionary
        """
        try:
            since_date = datetime.now() - timedelta(days=days_back)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total queries
                cursor.execute("""
                    SELECT COUNT(*), AVG(execution_time_ms), 
                           COUNT(DISTINCT user_id),
                           SUM(CASE WHEN success THEN 1 ELSE 0 END)
                    FROM query_history 
                    WHERE timestamp >= ?
                """, (since_date.isoformat(),))
                
                row = cursor.fetchone()
                total_queries = row[0] or 0
                avg_execution_time = row[1] or 0.0
                unique_users = row[2] or 0
                successful_queries = row[3] or 0
                
                # Top query types
                cursor.execute("""
                    SELECT query_type, COUNT(*) as count
                    FROM query_history 
                    WHERE timestamp >= ?
                    GROUP BY query_type
                    ORDER BY count DESC
                    LIMIT 10
                """, (since_date.isoformat(),))
                
                top_query_types = [{"type": row[0], "count": row[1]} 
                                 for row in cursor.fetchall()]
                
                # Daily trend
                cursor.execute("""
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM query_history 
                    WHERE timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """, (since_date.isoformat(),))
                
                daily_trend = [{"date": row[0], "count": row[1]} 
                             for row in cursor.fetchall()]
                
                return {
                    "total_queries": total_queries,
                    "successful_queries": successful_queries,
                    "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
                    "avg_execution_time_ms": avg_execution_time,
                    "unique_users": unique_users,
                    "top_query_types": top_query_types,
                    "daily_trend": daily_trend,
                    "period_days": days_back
                }
                
        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return {}
    
    def _update_daily_analytics(self, query_record: QueryRecord) -> None:
        """Update daily analytics with new query record.
        
        Args:
            query_record: Query record to add to analytics
        """
        try:
            date_str = query_record.timestamp.date().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if record exists for today
                cursor.execute("""
                    SELECT total_queries, successful_queries, avg_execution_time
                    FROM query_analytics WHERE date = ?
                """, (date_str,))
                
                row = cursor.fetchone()
                
                if row:
                    # Update existing record
                    total_queries = row[0] + 1
                    successful_queries = row[1] + (1 if query_record.success else 0)
                    # Calculate new average execution time
                    old_avg = row[2]
                    new_avg = ((old_avg * (total_queries - 1)) + query_record.execution_time_ms) / total_queries
                    
                    cursor.execute("""
                        UPDATE query_analytics 
                        SET total_queries = ?, successful_queries = ?, 
                            failed_queries = ?, avg_execution_time = ?, updated_at = ?
                        WHERE date = ?
                    """, (
                        total_queries, successful_queries,
                        total_queries - successful_queries, new_avg,
                        datetime.now().isoformat(), date_str
                    ))
                else:
                    # Create new record
                    cursor.execute("""
                        INSERT INTO query_analytics 
                        (date, total_queries, successful_queries, failed_queries,
                         avg_execution_time, unique_users, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date_str, 1, 1 if query_record.success else 0,
                        0 if query_record.success else 1,
                        query_record.execution_time_ms, 1,
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating daily analytics: {str(e)}")
    
    def export_history(self, user_id: str, format: str = "json") -> str:
        """Export user's query history.
        
        Args:
            user_id: User identifier
            format: Export format ('json', 'csv')
            
        Returns:
            Exported data as string
        """
        try:
            history = self.get_query_history(user_id, limit=1000, days_back=365)
            
            if format == "json":
                return json.dumps([asdict(record) for record in history], 
                                default=str, indent=2)
            elif format == "csv":
                # Simple CSV format
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Header
                writer.writerow(['timestamp', 'query_text', 'query_type', 
                               'execution_time_ms', 'result_count', 'success'])
                
                # Data
                for record in history:
                    writer.writerow([
                        record.timestamp.isoformat(),
                        record.query_text,
                        record.query_type,
                        record.execution_time_ms,
                        record.result_count,
                        record.success
                    ])
                
                return output.getvalue()
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting history: {str(e)}")
            return ""


def generate_query_id(user_id: str, query_text: str, timestamp: datetime) -> str:
    """Generate a unique query ID.
    
    Args:
        user_id: User identifier
        query_text: Query text
        timestamp: Query timestamp
        
    Returns:
        Unique query identifier
    """
    content = f"{user_id}:{query_text}:{timestamp.isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


def generate_search_id(user_id: str, name: str) -> str:
    """Generate a unique saved search ID.
    
    Args:
        user_id: User identifier
        name: Search name
        
    Returns:
        Unique search identifier
    """
    content = f"{user_id}:{name}:{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:16]
