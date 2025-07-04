"""
Export command for WisprMCP CLI.
"""

import argparse
import json
from typing import List, Dict, Any

from ...core.parser import WisprParser
from ...utils.date_parser import DateParser
from ..formatters.colors import Colors


class ExportCommand:
    """Export transcript data."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.parser = WisprParser(args.db_path)
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """Add arguments for the export command."""
        parser.add_argument(
            "--format",
            choices=["json", "csv", "markdown", "text"],
            default="json",
            help="Export format (default: json)"
        )
        parser.add_argument(
            "--output", "-o",
            help="Output file path (default: stdout)"
        )
        parser.add_argument(
            "--limit", "-l",
            type=int,
            help="Maximum number of entries to export"
        )
        parser.add_argument(
            "--since",
            help="Export entries since this date/time (e.g. '3d', '1w', '2024-01-01')"
        )
        parser.add_argument(
            "--until",
            help="Export entries until this date/time"
        )
        parser.add_argument(
            "--app",
            help="Filter by app (bundle ID or name)"
        )
        parser.add_argument(
            "--status",
            help="Filter by status (e.g. 'formatted', 'empty')"
        )
        parser.add_argument(
            "--conversation",
            help="Filter by conversation ID"
        )
        parser.add_argument(
            "--include-archived",
            action="store_true",
            help="Include archived entries"
        )
        parser.add_argument(
            "--include-context",
            action="store_true",
            help="Include additional context in export"
        )
        parser.add_argument(
            "--group-by-conversation",
            action="store_true",
            help="Group entries by conversation"
        )
    
    def run(self) -> int:
        """Execute the export command."""
        # Parse date filters
        start_date = None
        end_date = None
        
        if self.args.since:
            start_date = DateParser.parse_date(self.args.since)
            if not start_date:
                print(Colors.error(f"Invalid date format: {self.args.since}"))
                return 1
        
        if self.args.until:
            end_date = DateParser.parse_date(self.args.until)
            if not end_date:
                print(Colors.error(f"Invalid date format: {self.args.until}"))
                return 1
        
        # Handle app filter
        app_filter = None
        if self.args.app:
            if "." in self.args.app:
                app_filter = self.args.app
            else:
                name_to_bundle = {
                    "slack": "com.tinyspeck.slackmacgap",
                    "obsidian": "md.obsidian",
                    "messages": "com.apple.MobileSMS",
                    "vscode": "com.microsoft.VSCode",
                    "vs code": "com.microsoft.VSCode",
                    "chrome": "com.google.Chrome",
                    "wispr": "com.electron.wispr-flow",
                    "wispr flow": "com.electron.wispr-flow",
                    "chatgpt": "com.openai.chat",
                    "safari": "com.apple.Safari",
                    "mail": "com.apple.mail",
                    "notes": "com.apple.Notes",
                }
                app_filter = name_to_bundle.get(self.args.app.lower(), self.args.app)
        
        # Get data
        if self.args.group_by_conversation:
            conversations = self.parser.get_conversations(
                limit=self.args.limit,
                start_date=start_date,
                end_date=end_date,
                app=app_filter,
                status=self.args.status,
                conversation_id=self.args.conversation,
                include_archived=self.args.include_archived
            )
            data = [conv.to_dict() for conv in conversations]
        else:
            entries = self.parser.get_entries(
                limit=self.args.limit,
                start_date=start_date,
                end_date=end_date,
                app=app_filter,
                status=self.args.status,
                conversation_id=self.args.conversation,
                include_archived=self.args.include_archived
            )
            data = [entry.to_dict() for entry in entries]
        
        if not data:
            print(Colors.muted("No data to export."))
            return 0
        
        # Generate export content
        content = self._generate_export_content(data)
        
        # Output
        if self.args.output:
            try:
                with open(self.args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(Colors.success(f"Exported {len(data)} items to {self.args.output}"))
            except Exception as e:
                print(Colors.error(f"Failed to write to {self.args.output}: {e}"))
                return 1
        else:
            print(content)
        
        return 0
    
    def _generate_export_content(self, data: List[Dict[str, Any]]) -> str:
        """Generate export content based on format."""
        if self.args.format == "json":
            return self._export_json(data)
        elif self.args.format == "csv":
            return self._export_csv(data)
        elif self.args.format == "markdown":
            return self._export_markdown(data)
        elif self.args.format == "text":
            return self._export_text(data)
        else:
            raise ValueError(f"Unsupported format: {self.args.format}")
    
    def _export_json(self, data: List[Dict[str, Any]]) -> str:
        """Export as JSON."""
        export_data = {
            "format": "wispr_mcp_export",
            "version": "1.0",
            "exported_at": DateParser.format_timestamp(DateParser.parse_date("now") or ""),
            "count": len(data),
            "grouped_by_conversation": self.args.group_by_conversation,
            "include_context": self.args.include_context,
            "data": data
        }
        
        # Remove context if not requested
        if not self.args.include_context:
            for item in export_data["data"]:
                item.pop("additional_context", None)
                item.pop("user_context", None)
        
        return json.dumps(export_data, indent=2, default=str)
    
    def _export_csv(self, data: List[Dict[str, Any]]) -> str:
        """Export as CSV."""
        import csv
        import io
        
        if not data:
            return ""
        
        output = io.StringIO()
        
        if self.args.group_by_conversation:
            # CSV for conversations
            fieldnames = [
                "conversation_id", "app_name", "start_time", "end_time",
                "duration", "total_words", "entry_count", "summary"
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for conv in data:
                row = {
                    "conversation_id": conv.get("conversation_id", ""),
                    "app_name": conv.get("app_name", ""),
                    "start_time": conv.get("start_time", ""),
                    "end_time": conv.get("end_time", ""),
                    "duration": conv.get("duration", 0),
                    "total_words": conv.get("total_words", 0),
                    "entry_count": conv.get("entry_count", 0),
                    "summary": conv.get("summary", ""),
                }
                writer.writerow(row)
        else:
            # CSV for entries
            fieldnames = [
                "transcript_id", "timestamp", "app_name", "status", "duration",
                "num_words", "language", "conversation_id", "display_text"
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in data:
                row = {
                    "transcript_id": entry.get("transcript_id", ""),
                    "timestamp": entry.get("timestamp", ""),
                    "app_name": entry.get("app_name", ""),
                    "status": entry.get("status", ""),
                    "duration": entry.get("duration", 0),
                    "num_words": entry.get("num_words", 0),
                    "language": entry.get("language", ""),
                    "conversation_id": entry.get("conversation_id", ""),
                    "display_text": entry.get("display_text", ""),
                }
                writer.writerow(row)
        
        return output.getvalue()
    
    def _export_markdown(self, data: List[Dict[str, Any]]) -> str:
        """Export as Markdown."""
        lines = []
        
        # Header
        lines.append("# Wispr Flow Export")
        lines.append("")
        lines.append(f"**Exported:** {DateParser.format_timestamp(DateParser.parse_date('now') or '')}")
        lines.append(f"**Count:** {len(data)}")
        lines.append("")
        
        if self.args.group_by_conversation:
            # Conversations
            for conv in data:
                lines.append(f"## Conversation: {conv.get('conversation_id', 'Unknown')}")
                lines.append("")
                lines.append(f"**App:** {conv.get('app_name', 'Unknown')}")
                lines.append(f"**Start:** {conv.get('start_time', 'Unknown')}")
                lines.append(f"**End:** {conv.get('end_time', 'Unknown')}")
                lines.append(f"**Duration:** {conv.get('duration', 0):.1f}s")
                lines.append(f"**Words:** {conv.get('total_words', 0)}")
                lines.append(f"**Entries:** {conv.get('entry_count', 0)}")
                lines.append("")
                lines.append("### Summary")
                lines.append(conv.get('summary', ''))
                lines.append("")
                
                # Entries
                entries = conv.get('entries', [])
                if entries:
                    lines.append("### Entries")
                    for i, entry in enumerate(entries, 1):
                        lines.append(f"#### Entry {i}")
                        lines.append(f"**Time:** {entry.get('timestamp', 'Unknown')}")
                        lines.append(f"**Duration:** {entry.get('duration', 0):.1f}s")
                        lines.append(f"**Words:** {entry.get('num_words', 0)}")
                        lines.append("")
                        lines.append(entry.get('display_text', ''))
                        lines.append("")
        else:
            # Individual entries
            for entry in data:
                lines.append(f"## Entry: {entry.get('transcript_id', 'Unknown')}")
                lines.append("")
                lines.append(f"**Time:** {entry.get('timestamp', 'Unknown')}")
                lines.append(f"**App:** {entry.get('app_name', 'Unknown')}")
                lines.append(f"**Status:** {entry.get('status', 'Unknown')}")
                lines.append(f"**Duration:** {entry.get('duration', 0):.1f}s")
                lines.append(f"**Words:** {entry.get('num_words', 0)}")
                lines.append("")
                lines.append(entry.get('display_text', ''))
                lines.append("")
        
        return "\n".join(lines)
    
    def _export_text(self, data: List[Dict[str, Any]]) -> str:
        """Export as plain text."""
        lines = []
        
        # Header
        lines.append("WISPR FLOW EXPORT")
        lines.append("=" * 50)
        lines.append(f"Exported: {DateParser.format_timestamp(DateParser.parse_date('now') or '')}")
        lines.append(f"Count: {len(data)}")
        lines.append("")
        
        if self.args.group_by_conversation:
            # Conversations
            for conv in data:
                lines.append(f"CONVERSATION: {conv.get('conversation_id', 'Unknown')}")
                lines.append("-" * 50)
                lines.append(f"App: {conv.get('app_name', 'Unknown')}")
                lines.append(f"Start: {conv.get('start_time', 'Unknown')}")
                lines.append(f"End: {conv.get('end_time', 'Unknown')}")
                lines.append(f"Duration: {conv.get('duration', 0):.1f}s")
                lines.append(f"Words: {conv.get('total_words', 0)}")
                lines.append(f"Entries: {conv.get('entry_count', 0)}")
                lines.append("")
                lines.append("SUMMARY:")
                lines.append(conv.get('summary', ''))
                lines.append("")
                
                # Entries
                entries = conv.get('entries', [])
                if entries:
                    lines.append("ENTRIES:")
                    for i, entry in enumerate(entries, 1):
                        lines.append(f"  [{i}] {entry.get('timestamp', 'Unknown')} - {entry.get('duration', 0):.1f}s")
                        lines.append(f"      {entry.get('display_text', '')}")
                        lines.append("")
        else:
            # Individual entries
            for entry in data:
                lines.append(f"ENTRY: {entry.get('transcript_id', 'Unknown')}")
                lines.append("-" * 50)
                lines.append(f"Time: {entry.get('timestamp', 'Unknown')}")
                lines.append(f"App: {entry.get('app_name', 'Unknown')}")
                lines.append(f"Status: {entry.get('status', 'Unknown')}")
                lines.append(f"Duration: {entry.get('duration', 0):.1f}s")
                lines.append(f"Words: {entry.get('num_words', 0)}")
                lines.append("")
                lines.append(entry.get('display_text', ''))
                lines.append("")
        
        return "\n".join(lines)