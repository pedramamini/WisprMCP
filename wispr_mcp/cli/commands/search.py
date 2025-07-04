"""
Search command for WisprMCP CLI.
"""

import argparse
import json
from typing import List

from ...core.parser import WisprParser
from ...core.transcript import TranscriptEntry
from ...utils.date_parser import DateParser
from ..formatters.colors import Colors
from ..formatters.table import format_transcript_table


class SearchCommand:
    """Search transcript entries."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.parser = WisprParser(args.db_path)
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """Add arguments for the search command."""
        parser.add_argument(
            "query",
            help="Text to search for"
        )
        parser.add_argument(
            "--limit", "-l",
            type=int,
            default=50,
            help="Maximum number of results (default: 50)"
        )
        parser.add_argument(
            "--since",
            help="Search entries since this date/time (e.g. '3d', '1w', '2024-01-01')"
        )
        parser.add_argument(
            "--until",
            help="Search entries until this date/time"
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
            "--case-sensitive",
            action="store_true",
            help="Case-sensitive search"
        )
        parser.add_argument(
            "--highlight",
            action="store_true",
            help="Highlight search terms in results"
        )
        parser.add_argument(
            "--context", "-c",
            type=int,
            default=0,
            help="Show N characters of context around matches"
        )
    
    def run(self) -> int:
        """Execute the search command."""
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
        
        # Perform search
        transcript = self.parser.search_text(
            self.args.query,
            limit=self.args.limit,
            start_date=start_date,
            end_date=end_date,
            app=app_filter,
            status=self.args.status,
            conversation_id=self.args.conversation,
            include_archived=self.args.include_archived
        )
        
        if not transcript.entries:
            print(Colors.muted(f"No results found for '{self.args.query}'."))
            return 0
        
        # Format output
        if self.args.format == "json":
            data = transcript.to_dict()
            print(json.dumps(data, indent=2, default=str))
        
        elif self.args.format == "text":
            for entry in transcript.entries:
                self._print_search_result(entry)
        
        else:  # table format
            data = [entry.to_dict() for entry in transcript.entries]
            
            # If highlighting, modify display text
            if self.args.highlight:
                for item in data:
                    item["display_text"] = self._highlight_matches(item["display_text"], self.args.query)
            
            table = format_transcript_table(data)
            print(table)
            
            # Summary
            print(f"\n{Colors.success('Found:')} {len(transcript.entries)} matches for '{Colors.highlight(self.args.query)}'")
            print(f"{Colors.muted('Total:')} {Colors.duration(transcript.total_duration)}, "
                  f"{Colors.word_count(transcript.total_words)} words")
        
        return 0
    
    def _print_search_result(self, entry: TranscriptEntry) -> None:
        """Print search result in text format."""
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
        
        # Text content with context
        text = entry.display_text
        if text:
            if self.args.context > 0:
                # Show context around matches
                matches = self._find_matches(text, self.args.query)
                if matches:
                    for match_start, match_end in matches:
                        context_start = max(0, match_start - self.args.context)
                        context_end = min(len(text), match_end + self.args.context)
                        
                        context = text[context_start:context_end]
                        if self.args.highlight:
                            context = self._highlight_matches(context, self.args.query)
                        
                        if context_start > 0:
                            context = "..." + context
                        if context_end < len(text):
                            context = context + "..."
                        
                        print(f"  {context}")
                else:
                    print(f"  {text}")
            else:
                # Show full text
                if self.args.highlight:
                    text = self._highlight_matches(text, self.args.query)
                print(f"  {text}")
        else:
            print(Colors.muted("  (no text)"))
        
        print()  # Blank line
    
    def _find_matches(self, text: str, query: str) -> List[tuple]:
        """Find all matches of query in text."""
        matches = []
        search_text = text if self.args.case_sensitive else text.lower()
        search_query = query if self.args.case_sensitive else query.lower()
        
        start = 0
        while True:
            pos = search_text.find(search_query, start)
            if pos == -1:
                break
            matches.append((pos, pos + len(query)))
            start = pos + 1
        
        return matches
    
    def _highlight_matches(self, text: str, query: str) -> str:
        """Highlight matches in text."""
        if not self.args.highlight:
            return text
        
        # Simple highlighting (replace all occurrences)
        search_query = query if self.args.case_sensitive else query
        
        if self.args.case_sensitive:
            highlighted = text.replace(search_query, Colors.highlight(search_query))
        else:
            # Case-insensitive highlighting is more complex
            # For now, just do simple replacement
            import re
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            highlighted = pattern.sub(lambda m: Colors.highlight(m.group(0)), text)
        
        return highlighted