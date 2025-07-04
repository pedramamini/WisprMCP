"""
Conversation data model for WisprMCP.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .transcript import TranscriptEntry


@dataclass
class Conversation:
    """Represents a conversation consisting of multiple transcript entries."""
    
    conversation_id: str
    entries: List[TranscriptEntry]
    app: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Calculate conversation metadata after initialization."""
        if not self.entries:
            return
        
        # Sort entries by timestamp
        self.entries.sort(key=lambda x: x.timestamp or datetime.min)
        
        # Set start and end times
        timestamps = [entry.timestamp for entry in self.entries if entry.timestamp]
        if timestamps:
            self.start_time = min(timestamps)
            self.end_time = max(timestamps)
        
        # Set app if not provided (use most common app)
        if not self.app:
            app_counts = {}
            for entry in self.entries:
                if entry.app:
                    app_counts[entry.app] = app_counts.get(entry.app, 0) + 1
            if app_counts:
                self.app = max(app_counts, key=app_counts.get)
    
    @property
    def duration(self) -> float:
        """Get total duration of the conversation."""
        return sum(entry.duration or 0 for entry in self.entries)
    
    @property
    def total_words(self) -> int:
        """Get total word count for the conversation."""
        return sum(entry.num_words or 0 for entry in self.entries)
    
    @property
    def app_name(self) -> str:
        """Get human-readable app name."""
        if not self.app:
            return "Unknown"
        
        # Use the same mapping as TranscriptEntry
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
    def full_text(self) -> str:
        """Get the full conversation text."""
        texts = []
        for entry in self.entries:
            text = entry.display_text
            if text:
                texts.append(text)
        return " ".join(texts)
    
    @property
    def summary(self) -> str:
        """Get a summary of the conversation."""
        if not self.entries:
            return "Empty conversation"
        
        # Use first 100 characters of full text
        full_text = self.full_text
        if len(full_text) <= 100:
            return full_text
        
        # Try to break at word boundary
        summary = full_text[:100]
        last_space = summary.rfind(' ')
        if last_space > 50:  # Only break at space if it's not too early
            summary = summary[:last_space]
        
        return summary + "..."
    
    @property
    def quality_score(self) -> float:
        """Get average quality score for the conversation."""
        scores = [entry.quality_score for entry in self.entries if entry.quality_score is not None]
        return sum(scores) / len(scores) if scores else 0.0
    
    @property
    def has_audio(self) -> bool:
        """Check if any entry in the conversation has audio."""
        return any(entry.has_audio for entry in self.entries)
    
    @property
    def entry_count(self) -> int:
        """Get number of entries in the conversation."""
        return len(self.entries)
    
    def get_entries_in_range(self, start_time: Optional[datetime], end_time: Optional[datetime]) -> List[TranscriptEntry]:
        """Get entries within a time range."""
        filtered_entries = []
        for entry in self.entries:
            if not entry.timestamp:
                continue
            
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
            
            filtered_entries.append(entry)
        
        return filtered_entries
    
    def search_text(self, query: str) -> List[TranscriptEntry]:
        """Search for text within the conversation."""
        query_lower = query.lower()
        matching_entries = []
        
        for entry in self.entries:
            if query_lower in entry.display_text.lower():
                matching_entries.append(entry)
        
        return matching_entries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "conversation_id": self.conversation_id,
            "app": self.app,
            "app_name": self.app_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "total_words": self.total_words,
            "entry_count": self.entry_count,
            "summary": self.summary,
            "quality_score": self.quality_score,
            "has_audio": self.has_audio,
            "full_text": self.full_text,
            "entries": [entry.to_dict() for entry in self.entries],
        }
    
    def to_markdown(self) -> str:
        """Convert conversation to markdown format."""
        lines = []
        
        # Header
        lines.append(f"# Conversation: {self.conversation_id}")
        lines.append(f"**App:** {self.app_name}")
        if self.start_time:
            lines.append(f"**Start:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.end_time:
            lines.append(f"**End:** {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Duration:** {self.duration:.1f}s")
        lines.append(f"**Total Words:** {self.total_words}")
        lines.append(f"**Entries:** {self.entry_count}")
        lines.append("")
        
        # Entries
        lines.append("## Transcript")
        for i, entry in enumerate(self.entries, 1):
            lines.append(f"### Entry {i}")
            if entry.timestamp:
                lines.append(f"**Time:** {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            if entry.duration:
                lines.append(f"**Duration:** {entry.duration:.1f}s")
            if entry.num_words:
                lines.append(f"**Words:** {entry.num_words}")
            lines.append(f"**Status:** {entry.status}")
            lines.append("")
            lines.append(entry.display_text)
            lines.append("")
        
        return "\n".join(lines)