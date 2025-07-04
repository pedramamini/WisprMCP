"""
List command for WisprMCP CLI.
"""

import argparse
from typing import List, Dict, Any

from ...core.parser import WisprParser
from ...utils.date_parser import DateParser
from ..formatters.colors import Colors
from ..formatters.table import format_transcript_table


class ListCommand:
    """List transcript entries."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.parser = WisprParser(args.db_path)
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """Add arguments for the list command."""
        parser.add_argument(
            "--limit", "-l",
            type=int,
            default=20,
            help="Maximum number of entries to show (default: 20)"
        )
        parser.add_argument(
            "--offset",
            type=int,
            default=0,
            help="Number of entries to skip (default: 0)"
        )
        parser.add_argument(
            "--since",
            default="2d",
            help="Show entries since this date/time (default: 2d)"
        )
        parser.add_argument(
            "--until",
            help="Show entries until this date/time"
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
            "--format",
            choices=["table", "json", "text"],
            default="table",
            help="Output format (default: table)"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Show full text content"
        )
    
    def run(self) -> int:
        """Execute the list command."""
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
        
        # Handle app filter (support both bundle ID and name)
        app_filter = None
        if self.args.app:
            # Check if it's a bundle ID or name
            if "." in self.args.app:
                app_filter = self.args.app
            else:
                # Convert name to bundle ID
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
        
        # Get entries
        entries = self.parser.get_entries(
            limit=self.args.limit,
            offset=self.args.offset,
            start_date=start_date,
            end_date=end_date,
            app=app_filter,
            status=self.args.status,
            conversation_id=self.args.conversation,
            include_archived=self.args.include_archived
        )
        
        if not entries:
            print(Colors.muted("No entries found."))
            return 0
        
        # Format output
        if self.args.format == "json":
            import json
            data = [entry.to_dict() for entry in entries]
            print(json.dumps(data, indent=2, default=str))
        
        elif self.args.format == "text":
            for entry in entries:
                self._print_entry_text(entry)
        
        else:  # table format
            data = [entry.to_dict() for entry in entries]
            table = format_transcript_table(data)
            print(table)
            
            # Summary
            total_duration = sum(entry.duration or 0 for entry in entries)
            total_words = sum(entry.num_words or 0 for entry in entries)
            
            print(f"\n{Colors.muted('Total:')} {len(entries)} entries, "
                  f"{Colors.duration(total_duration)}, "
                  f"{Colors.word_count(total_words)} words")
        
        return 0
    
    def _print_entry_text(self, entry) -> None:
        """Print entry in text format."""
        # Header
        header_parts = []
        if entry.timestamp:
            header_parts.append(Colors.timestamp(entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
        header_parts.append(Colors.app_name(entry.app_name))
        if entry.status:
            header_parts.append(Colors.status(entry.status))
        if entry.duration:
            header_parts.append(Colors.duration(entry.duration))
        if entry.num_words:
            header_parts.append(Colors.word_count(f"{entry.num_words} words"))
        
        print(Colors.bold(f"[{entry.transcript_id[:8]}]") + " " + " | ".join(header_parts))
        
        # Text content
        text = entry.display_text
        if text:
            if not self.args.verbose and len(text) > 200:
                text = text[:197] + "..."
            print(f"  {text}")
        else:
            print(Colors.muted("  (no text)"))
        
        print()  # Blank line