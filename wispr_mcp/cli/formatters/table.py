"""
ASCII table formatting for CLI output.
"""

from typing import List, Dict, Any, Optional
from .colors import Colors


class TableFormatter:
    """Simple ASCII table formatter."""
    
    def __init__(self, headers: List[str], max_width: Optional[int] = None):
        """
        Initialize table formatter.
        
        Args:
            headers: Column headers
            max_width: Maximum table width (auto-detects terminal width if None)
        """
        self.headers = headers
        self.max_width = max_width or self._get_terminal_width()
        self.rows: List[List[str]] = []
    
    def _get_terminal_width(self) -> int:
        """Get terminal width dynamically, with fallback."""
        try:
            import shutil
            width = shutil.get_terminal_size().columns
            # Use most of the width but leave some margin
            return max(80, width - 4)
        except:
            return 120
    
    def add_row(self, row: List[str]) -> None:
        """Add a row to the table."""
        self.rows.append([str(cell) for cell in row])
    
    def _calculate_column_widths(self) -> List[int]:
        """Calculate optimal column widths."""
        if not self.rows:
            return [len(header) for header in self.headers]
        
        # Calculate content width for each column
        widths = []
        for col_idx in range(len(self.headers)):
            # Start with header width
            max_width = len(self.headers[col_idx])
            
            # Check all rows for this column
            for row in self.rows:
                if col_idx < len(row):
                    # Remove ANSI codes for width calculation
                    clean_cell = self._strip_ansi(row[col_idx])
                    max_width = max(max_width, len(clean_cell))
            
            widths.append(max_width)
        
        # Adjust widths to fit within max_width
        total_width = sum(widths) + len(widths) * 3 + 1  # 3 chars per column (| + space + space)
        
        if total_width > self.max_width:
            # Give priority to the last column (usually text content)
            available_width = self.max_width - len(widths) * 3 - 1
            
            if len(widths) > 1:
                # Cap non-text columns at reasonable sizes
                for i in range(len(widths) - 1):
                    if i == 0:  # Time column
                        widths[i] = min(widths[i], 12)
                    elif i == 1:  # App column
                        widths[i] = min(widths[i], 15)
                    else:  # Other columns
                        widths[i] = min(widths[i], 10)
                
                # Give remaining space to text column
                used_width = sum(widths[:-1])
                text_width = available_width - used_width
                widths[-1] = max(40, text_width)
                
                # Final check - if still too wide, scale down
                if sum(widths) > available_width:
                    scale_factor = available_width / sum(widths)
                    widths = [max(6, int(w * scale_factor)) for w in widths]
            else:
                widths = [available_width]
        
        return widths
    
    def _strip_ansi(self, text: str) -> str:
        """Strip ANSI escape sequences from text."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _truncate_cell(self, cell: str, width: int) -> str:
        """Truncate cell content to fit width."""
        clean_cell = self._strip_ansi(cell)
        if len(clean_cell) <= width:
            return cell
        
        # If cell has ANSI codes, we need to preserve them
        if len(cell) != len(clean_cell):
            # For now, just truncate the whole thing
            return cell[:width - 3] + "..."
        
        return clean_cell[:width - 3] + "..."
    
    def format(self) -> str:
        """Format the table as a string."""
        if not self.rows:
            return ""
        
        widths = self._calculate_column_widths()
        
        lines = []
        
        # Header separator
        separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
        lines.append(separator)
        
        # Header row
        header_cells = []
        for i, header in enumerate(self.headers):
            if i < len(widths):
                width = widths[i]
                cell = Colors.bold(header.ljust(width))
                header_cells.append(f" {cell} ")
        
        lines.append("|" + "|".join(header_cells) + "|")
        lines.append(separator)
        
        # Data rows
        for row in self.rows:
            row_cells = []
            for i, cell in enumerate(row):
                if i < len(widths):
                    width = widths[i]
                    truncated = self._truncate_cell(cell, width)
                    # Pad to width (accounting for ANSI codes)
                    clean_len = len(self._strip_ansi(truncated))
                    padding = width - clean_len
                    padded = truncated + " " * padding
                    row_cells.append(f" {padded} ")
            
            lines.append("|" + "|".join(row_cells) + "|")
        
        # Bottom separator
        lines.append(separator)
        
        return "\n".join(lines)
    
    def print(self) -> None:
        """Print the table."""
        print(self.format())


def format_transcript_table(entries: List[Dict[str, Any]], max_width: Optional[int] = None) -> str:
    """Format transcript entries as a table."""
    if not entries:
        return Colors.muted("No entries found.")
    
    headers = ["Time", "App", "Status", "Words", "Duration", "Text"]
    table = TableFormatter(headers, max_width)
    
    for entry in entries:
        # Format timestamp
        timestamp = entry.get("timestamp", "")
        if timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%m/%d %H:%M")
            except:
                time_str = timestamp[:10]
        else:
            time_str = ""
        
        # Format other fields
        app_name = entry.get("app_name", "Unknown")
        status = entry.get("status", "")
        words = entry.get("num_words", 0)
        duration = entry.get("duration", 0.0)
        text = entry.get("display_text", "")
        
        # Let the table formatter handle truncation dynamically
        # Don't pre-truncate here - let the table use full terminal width
        
        row = [
            Colors.timestamp(time_str),
            Colors.app_name(app_name),
            Colors.status(status),
            Colors.word_count(words),
            Colors.duration(duration),
            text
        ]
        
        table.add_row(row)
    
    return table.format()


def format_conversation_table(conversations: List[Dict[str, Any]], max_width: Optional[int] = None) -> str:
    """Format conversations as a table."""
    if not conversations:
        return Colors.muted("No conversations found.")
    
    headers = ["Time", "App", "Entries", "Words", "Duration", "Summary"]
    table = TableFormatter(headers, max_width)
    
    for conv in conversations:
        # Format start time
        start_time = conv.get("start_time", "")
        if start_time:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                time_str = dt.strftime("%m/%d %H:%M")
            except:
                time_str = start_time[:10]
        else:
            time_str = ""
        
        # Format other fields
        app_name = conv.get("app_name", "Unknown")
        entry_count = conv.get("entry_count", 0)
        total_words = conv.get("total_words", 0)
        duration = conv.get("duration", 0.0)
        summary = conv.get("summary", "")
        
        # Let the table formatter handle truncation dynamically
        
        row = [
            Colors.timestamp(time_str),
            Colors.app_name(app_name),
            str(entry_count),
            Colors.word_count(total_words),
            Colors.duration(duration),
            summary
        ]
        
        table.add_row(row)
    
    return table.format()


def format_app_stats_table(apps: List[Dict[str, Any]], max_width: Optional[int] = None) -> str:
    """Format app statistics as a table."""
    if not apps:
        return Colors.muted("No app statistics found.")
    
    headers = ["App", "Entries", "Words", "Duration", "Avg Latency", "Last Used"]
    table = TableFormatter(headers, max_width)
    
    for app in apps:
        # Format fields
        app_name = app.get("app_name", "Unknown")
        total_entries = app.get("total_entries", 0)
        total_words = app.get("total_words", 0)
        total_duration = app.get("total_duration", 0.0)
        avg_latency = app.get("avg_latency", 0.0)
        last_used = app.get("last_used", "")
        
        # Format last used
        if last_used:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_used.replace("Z", "+00:00"))
                last_used_str = dt.strftime("%m/%d")
            except:
                last_used_str = last_used[:10]
        else:
            last_used_str = ""
        
        row = [
            Colors.app_name(app_name),
            str(total_entries),
            Colors.word_count(total_words),
            Colors.duration(total_duration),
            f"{avg_latency:.2f}s" if avg_latency > 0 else "",
            Colors.timestamp(last_used_str)
        ]
        
        table.add_row(row)
    
    return table.format()