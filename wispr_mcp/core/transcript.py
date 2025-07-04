"""
Transcript and conversation data models for WisprMCP.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class TranscriptEntry:
    """Represents a single transcript entry from the Wispr Flow database."""
    
    transcript_id: str
    asr_text: Optional[str] = None
    formatted_text: Optional[str] = None
    edited_text: Optional[str] = None
    timestamp: Optional[datetime] = None
    app: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[float] = None
    num_words: Optional[int] = None
    status: Optional[str] = None
    language: Optional[str] = None
    conversation_id: Optional[str] = None
    e2e_latency: Optional[float] = None
    confidence: Optional[float] = None
    is_archived: bool = False
    additional_context: Optional[Dict[str, Any]] = None
    
    @property
    def display_text(self) -> str:
        """Get the best available text for display."""
        if self.edited_text:
            return self.edited_text
        elif self.formatted_text:
            return self.formatted_text
        elif self.asr_text:
            return self.asr_text
        return ""
    
    @property
    def app_name(self) -> str:
        """Get human-readable app name."""
        if not self.app:
            return "Unknown"
        
        # Common app bundle ID mappings
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
        
        return app_mappings.get(self.app, self.app)
    
    @property
    def quality_score(self) -> Optional[float]:
        """Get a quality score for the transcript."""
        if self.confidence is not None:
            return self.confidence
        
        # Basic quality heuristics
        if self.status == "formatted" and self.num_words and self.num_words > 0:
            return 0.8
        elif self.status == "empty" or not self.display_text:
            return 0.1
        else:
            return 0.5
    
    @property
    def has_audio(self) -> bool:
        """Check if the entry has audio data."""
        return self.status not in ["no_audio", "empty"]
    
    @property
    def user_context(self) -> Dict[str, Any]:
        """Extract user context from additional context."""
        if not self.additional_context:
            return {}
        
        context = {}
        if isinstance(self.additional_context, str):
            try:
                data = json.loads(self.additional_context)
            except json.JSONDecodeError:
                return {}
        else:
            data = self.additional_context
        
        # Extract user information
        if "user" in data:
            context["user"] = data["user"]
        
        # Extract accessibility context
        if "axText" in data:
            context["accessibility_text"] = data["axText"]
        
        # Extract URL/app context
        if "activeUrl" in data:
            context["active_url"] = data["activeUrl"]
        
        return context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "transcript_id": self.transcript_id,
            "asr_text": self.asr_text,
            "formatted_text": self.formatted_text,
            "edited_text": self.edited_text,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "app": self.app,
            "app_name": self.app_name,
            "url": self.url,
            "duration": self.duration,
            "num_words": self.num_words,
            "status": self.status,
            "language": self.language,
            "conversation_id": self.conversation_id,
            "e2e_latency": self.e2e_latency,
            "confidence": self.confidence,
            "is_archived": self.is_archived,
            "display_text": self.display_text,
            "quality_score": self.quality_score,
            "has_audio": self.has_audio,
            "user_context": self.user_context,
        }


@dataclass
class Transcript:
    """Represents a collection of transcript entries."""
    
    entries: List[TranscriptEntry]
    total_duration: float = 0.0
    total_words: int = 0
    
    def __post_init__(self):
        """Calculate totals after initialization."""
        self.total_duration = sum(entry.duration or 0 for entry in self.entries)
        self.total_words = sum(entry.num_words or 0 for entry in self.entries)
    
    @property
    def app_breakdown(self) -> Dict[str, int]:
        """Get breakdown of entries by app."""
        breakdown = {}
        for entry in self.entries:
            app_name = entry.app_name
            breakdown[app_name] = breakdown.get(app_name, 0) + 1
        return breakdown
    
    @property
    def status_breakdown(self) -> Dict[str, int]:
        """Get breakdown of entries by status."""
        breakdown = {}
        for entry in self.entries:
            status = entry.status or "unknown"
            breakdown[status] = breakdown.get(status, 0) + 1
        return breakdown
    
    @property
    def conversations(self) -> Dict[str, List[TranscriptEntry]]:
        """Group entries by conversation ID."""
        conversations = {}
        for entry in self.entries:
            conv_id = entry.conversation_id or "no_conversation"
            if conv_id not in conversations:
                conversations[conv_id] = []
            conversations[conv_id].append(entry)
        return conversations
    
    def filter_by_app(self, app: str) -> "Transcript":
        """Filter entries by app."""
        filtered_entries = [
            entry for entry in self.entries 
            if entry.app == app or entry.app_name.lower() == app.lower()
        ]
        return Transcript(entries=filtered_entries)
    
    def filter_by_status(self, status: str) -> "Transcript":
        """Filter entries by status."""
        filtered_entries = [
            entry for entry in self.entries 
            if entry.status == status
        ]
        return Transcript(entries=filtered_entries)
    
    def filter_by_date_range(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> "Transcript":
        """Filter entries by date range."""
        filtered_entries = []
        for entry in self.entries:
            if not entry.timestamp:
                continue
            
            if start_date and entry.timestamp < start_date:
                continue
            if end_date and entry.timestamp > end_date:
                continue
            
            filtered_entries.append(entry)
        
        return Transcript(entries=filtered_entries)
    
    def search_text(self, query: str) -> "Transcript":
        """Search for text in transcript entries."""
        query_lower = query.lower()
        filtered_entries = [
            entry for entry in self.entries 
            if query_lower in entry.display_text.lower()
        ]
        return Transcript(entries=filtered_entries)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "total_duration": self.total_duration,
            "total_words": self.total_words,
            "app_breakdown": self.app_breakdown,
            "status_breakdown": self.status_breakdown,
            "conversation_count": len(self.conversations),
        }