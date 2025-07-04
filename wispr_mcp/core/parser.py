"""
Database parser for WisprMCP - handles SQLite database access.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from contextlib import contextmanager

from ..utils.config import config
from .transcript import TranscriptEntry, Transcript
from .conversation import Conversation


class WisprParser:
    """Parser for Wispr Flow SQLite database."""
    
    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """
        Initialize the parser.
        
        Args:
            db_path: Path to the SQLite database. If None, uses config default.
        """
        self.db_path = Path(db_path) if db_path else config.wispr_database_path
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def _row_to_transcript_entry(self, row: sqlite3.Row) -> TranscriptEntry:
        """Convert a database row to a TranscriptEntry object."""
        # Parse timestamp
        timestamp = None
        if row["timestamp"]:
            try:
                # Handle format like "2025-06-20 04:34:15.319 +00:00"
                timestamp_str = row["timestamp"]
                if " +00:00" in timestamp_str:
                    timestamp_str = timestamp_str.replace(" +00:00", "+00:00")
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                try:
                    # Try without timezone
                    timestamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        # Try with microseconds
                        timestamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        pass
        
        # Parse additional context
        additional_context = None
        if row["additionalContext"]:
            try:
                additional_context = json.loads(row["additionalContext"])
            except json.JSONDecodeError:
                pass
        
        return TranscriptEntry(
            transcript_id=row["transcriptEntityId"],
            asr_text=row["asrText"],
            formatted_text=row["formattedText"],
            edited_text=row["editedText"],
            timestamp=timestamp,
            app=row["app"],
            url=row["url"],
            duration=row["duration"],
            num_words=row["numWords"],
            status=row["status"],
            language=row["language"],
            conversation_id=row["conversationId"],
            e2e_latency=row["e2eLatency"],
            confidence=row["averageLogProb"],
            is_archived=bool(row["isArchived"]) if row["isArchived"] is not None else False,
            additional_context=additional_context,
        )
    
    def get_entries(self, 
                   limit: Optional[int] = None,
                   offset: Optional[int] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   app: Optional[str] = None,
                   status: Optional[str] = None,
                   conversation_id: Optional[str] = None,
                   include_archived: bool = False) -> List[TranscriptEntry]:
        """
        Get transcript entries from the database.
        
        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            start_date: Start date filter
            end_date: End date filter
            app: App filter
            status: Status filter
            conversation_id: Conversation ID filter
            include_archived: Whether to include archived entries
            
        Returns:
            List of TranscriptEntry objects
        """
        query = """
        SELECT 
            transcriptEntityId, asrText, formattedText, editedText, 
            timestamp, app, url, duration, numWords, status, language,
            conversationId, e2eLatency, averageLogProb, isArchived, 
            additionalContext
        FROM History
        WHERE 1=1
        """
        params = []
        
        if not include_archived:
            query += " AND (isArchived = 0 OR isArchived IS NULL)"
        
        if start_date:
            query += " AND timestamp >= ? AND timestamp IS NOT NULL"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ? AND timestamp IS NOT NULL"
            params.append(end_date.isoformat())
        
        if app:
            query += " AND app = ?"
            params.append(app)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if conversation_id:
            query += " AND conversationId = ?"
            params.append(conversation_id)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        if offset:
            query += " OFFSET ?"
            params.append(offset)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_transcript_entry(row) for row in cursor.fetchall()]
    
    def get_entry_by_id(self, transcript_id: str) -> Optional[TranscriptEntry]:
        """Get a specific transcript entry by ID."""
        query = """
        SELECT 
            transcriptEntityId, asrText, formattedText, editedText, 
            timestamp, app, url, duration, numWords, status, language,
            conversationId, e2eLatency, averageLogProb, isArchived, 
            additionalContext
        FROM History
        WHERE transcriptEntityId = ?
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (transcript_id,))
            row = cursor.fetchone()
            return self._row_to_transcript_entry(row) if row else None
    
    def get_transcript(self, **kwargs) -> Transcript:
        """Get a Transcript object containing filtered entries."""
        entries = self.get_entries(**kwargs)
        return Transcript(entries=entries)
    
    def search_text(self, query: str, **kwargs) -> Transcript:
        """Search for text in transcript entries."""
        # Get base entries
        entries = self.get_entries(**kwargs)
        
        # Filter by text search
        query_lower = query.lower()
        filtered_entries = [
            entry for entry in entries 
            if (entry.asr_text and query_lower in entry.asr_text.lower()) or
               (entry.formatted_text and query_lower in entry.formatted_text.lower()) or
               (entry.edited_text and query_lower in entry.edited_text.lower())
        ]
        
        return Transcript(entries=filtered_entries)
    
    def get_conversations(self, **kwargs) -> List[Conversation]:
        """Get conversations (grouped transcript entries)."""
        entries = self.get_entries(**kwargs)
        
        # Group by conversation ID
        conversations_dict = {}
        for entry in entries:
            conv_id = entry.conversation_id or f"single_{entry.transcript_id}"
            if conv_id not in conversations_dict:
                conversations_dict[conv_id] = []
            conversations_dict[conv_id].append(entry)
        
        # Create Conversation objects
        conversations = []
        for conv_id, conv_entries in conversations_dict.items():
            conversation = Conversation(
                conversation_id=conv_id,
                entries=conv_entries
            )
            conversations.append(conversation)
        
        # Sort by start time
        conversations.sort(key=lambda c: c.start_time or datetime.min, reverse=True)
        
        return conversations
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a specific conversation by ID."""
        entries = self.get_entries(conversation_id=conversation_id)
        if not entries:
            return None
        
        return Conversation(conversation_id=conversation_id, entries=entries)
    
    def get_apps(self) -> List[Dict[str, Any]]:
        """Get list of apps with usage statistics."""
        query = """
        SELECT 
            app,
            COUNT(*) as total_entries,
            SUM(duration) as total_duration,
            SUM(numWords) as total_words,
            AVG(e2eLatency) as avg_latency,
            MAX(timestamp) as last_used
        FROM History
        WHERE app IS NOT NULL AND app != ''
        GROUP BY app
        ORDER BY total_entries DESC
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query)
            apps = []
            for row in cursor.fetchall():
                # Get human-readable app name
                app_mappings = {
                    "com.tinyspeck.slackmacgap": "Slack",
                    "md.obsidian": "Obsidian",
                    "com.apple.MobileSMS": "Messages",
                    "com.microsoft.VSCode": "VS Code",
                    "com.google.Chrome": "Chrome",
                    "com.electron.wispr-flow": "Wispr Flow",
                    "com.openai.chat": "ChatGPT",
                    "com.apple.Safari": "Safari",
                    "com.apple.mail": "Mail",
                    "com.apple.Notes": "Notes",
                    "com.apple.TextEdit": "TextEdit",
                }
                
                app_name = app_mappings.get(row["app"], row["app"])
                
                apps.append({
                    "app_id": row["app"],
                    "app_name": app_name,
                    "total_entries": row["total_entries"],
                    "total_duration": row["total_duration"] or 0,
                    "total_words": row["total_words"] or 0,
                    "avg_latency": row["avg_latency"] or 0,
                    "last_used": row["last_used"],
                })
            
            return apps
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            # Basic counts
            cursor = conn.execute("SELECT COUNT(*) FROM History")
            total_entries = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM History WHERE isArchived = 0")
            active_entries = cursor.fetchone()[0]
            
            # Duration and word stats
            cursor = conn.execute("""
                SELECT 
                    SUM(duration) as total_duration,
                    SUM(numWords) as total_words,
                    AVG(duration) as avg_duration,
                    AVG(numWords) as avg_words
                FROM History
                WHERE duration IS NOT NULL AND numWords IS NOT NULL
            """)
            stats_row = cursor.fetchone()
            
            # Status breakdown
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM History
                GROUP BY status
                ORDER BY count DESC
            """)
            status_breakdown = {row["status"] or "unknown": row["count"] for row in cursor.fetchall()}
            
            # Date range
            cursor = conn.execute("""
                SELECT MIN(timestamp) as first_entry, MAX(timestamp) as last_entry
                FROM History
                WHERE timestamp IS NOT NULL
            """)
            date_row = cursor.fetchone()
            
            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "archived_entries": total_entries - active_entries,
                "total_duration": stats_row["total_duration"] or 0,
                "total_words": stats_row["total_words"] or 0,
                "avg_duration": stats_row["avg_duration"] or 0,
                "avg_words": stats_row["avg_words"] or 0,
                "status_breakdown": status_breakdown,
                "first_entry": date_row["first_entry"],
                "last_entry": date_row["last_entry"],
                "database_path": str(self.db_path),
            }
    
    def get_dictionary_entries(self) -> List[Dict[str, Any]]:
        """Get custom dictionary entries."""
        query = """
        SELECT 
            phrase, replacement, frequencyUsed, frequencySeen,
            lastUsed, lastSeen, manualEntry, source,
            createdAt, modifiedAt
        FROM Dictionary
        WHERE isDeleted = 0 OR isDeleted IS NULL
        ORDER BY frequencyUsed DESC, lastUsed DESC
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]