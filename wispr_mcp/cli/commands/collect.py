"""
Collect command for WisprMCP CLI - extract YOUR spoken words by day.
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

from ...core.parser import WisprParser
from ...utils.date_parser import DateParser
from ..formatters.colors import Colors


class CollectCommand:
    """Collect YOUR spoken words and save by day to text files."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.parser = WisprParser(args.db_path)
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """Add arguments for the collect command."""
        parser.add_argument(
            "output_dir",
            help="Directory to save daily files with YOUR spoken words"
        )
        parser.add_argument(
            "--since",
            default="7d",
            help="Collect YOUR spoken words since this date/time (default: 7d)"
        )
        parser.add_argument(
            "--until",
            help="Collect words until this date/time"
        )
        parser.add_argument(
            "--app",
            help="Filter by specific app"
        )
        parser.add_argument(
            "--min-words",
            type=int,
            default=1,
            help="Minimum words per entry to include (default: 1)"
        )
        parser.add_argument(
            "--exclude-short",
            action="store_true",
            help="Exclude entries with less than 5 words"
        )
        parser.add_argument(
            "--exclude-apps",
            nargs="+",
            help="Apps to exclude (e.g. 'Wispr Flow' 'ChatGPT')"
        )
        parser.add_argument(
            "--format",
            choices=["words", "sentences", "entries", "raw"],
            default="raw",
            help="Output format (default: raw - just YOUR words, no headers)"
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing files"
        )
    
    def run(self) -> int:
        """Execute the collect command."""
        # Parse dates
        start_date = DateParser.parse_date(self.args.since)
        if not start_date:
            print(Colors.error(f"Invalid date format: {self.args.since}"))
            return 1
        
        end_date = None
        if self.args.until:
            end_date = DateParser.parse_date(self.args.until)
            if not end_date:
                print(Colors.error(f"Invalid date format: {self.args.until}"))
                return 1
        
        # Create output directory
        output_dir = Path(self.args.output_dir)
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                print(Colors.success(f"Created directory: {output_dir}"))
            except Exception as e:
                print(Colors.error(f"Failed to create directory {output_dir}: {e}"))
                return 1
        
        # Handle app filter
        app_filter = None
        if self.args.app:
            app_filter = self._resolve_app_filter(self.args.app)
        
        # Get entries
        print(Colors.info("Collecting transcript entries..."))
        entries = self.parser.get_entries(
            start_date=start_date,
            end_date=end_date,
            app=app_filter,
            include_archived=False
        )
        
        if not entries:
            print(Colors.muted("No entries found for the specified criteria."))
            return 0
        
        # Filter entries
        filtered_entries = self._filter_entries(entries)
        
        print(Colors.info(f"Found {len(filtered_entries)} entries after filtering"))
        
        # Group by date
        daily_data = self._group_by_date(filtered_entries)
        
        # Generate files
        files_created = 0
        files_skipped = 0
        
        for date_str, day_entries in daily_data.items():
            file_path = output_dir / f"{date_str}.txt"
            
            # Check if file exists and overwrite setting
            if file_path.exists() and not self.args.overwrite:
                print(Colors.warning(f"Skipping {file_path} (already exists, use --overwrite to replace)"))
                files_skipped += 1
                continue
            
            # Generate content
            content = self._generate_file_content(date_str, day_entries)
            
            # Write file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                word_count = self._count_words(content)
                print(Colors.success(f"Created {file_path} ({len(day_entries)} entries, {word_count} words)"))
                files_created += 1
                
            except Exception as e:
                print(Colors.error(f"Failed to write {file_path}: {e}"))
                return 1
        
        # Summary
        total_words = sum(entry.num_words or 0 for day_entries in daily_data.values() for entry in day_entries)
        total_duration = sum(entry.duration or 0 for day_entries in daily_data.values() for entry in day_entries)
        
        print()
        print(Colors.bold("Collection Summary:"))
        print(f"  Files created: {Colors.success(str(files_created))}")
        if files_skipped > 0:
            print(f"  Files skipped: {Colors.warning(str(files_skipped))}")
        print(f"  Date range: {Colors.muted(start_date.strftime('%Y-%m-%d'))} to {Colors.muted((end_date or datetime.now()).strftime('%Y-%m-%d'))}")
        print(f"  Total words: {Colors.word_count(total_words)}")
        print(f"  Total duration: {Colors.duration(total_duration)}")
        print(f"  Output directory: {Colors.muted(str(output_dir))}")
        
        return 0
    
    def _resolve_app_filter(self, app: str) -> str:
        """Resolve app name to bundle ID if needed."""
        if "." in app:
            return app
        
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
        
        return name_to_bundle.get(app.lower(), app)
    
    def _filter_entries(self, entries):
        """Filter entries based on criteria."""
        filtered = []
        
        for entry in entries:
            # Skip if no text
            if not entry.display_text or not entry.display_text.strip():
                continue
            
            # Check minimum words
            if entry.num_words and entry.num_words < self.args.min_words:
                continue
            
            # Exclude short entries if requested
            if self.args.exclude_short and entry.num_words and entry.num_words < 5:
                continue
            
            # Exclude apps if specified
            if self.args.exclude_apps:
                app_name = entry.app_name.lower()
                if any(excluded.lower() in app_name for excluded in self.args.exclude_apps):
                    continue
            
            # Skip if status indicates no real speech
            if entry.status in ["empty", "no_audio", "dismissed"]:
                continue
            
            filtered.append(entry)
        
        return filtered
    
    def _group_by_date(self, entries) -> Dict[str, List]:
        """Group entries by date (YYYY-MM-DD)."""
        daily_data = defaultdict(list)
        
        for entry in entries:
            if entry.timestamp:
                # Convert to local date
                date_str = entry.timestamp.strftime("%Y-%m-%d")
                daily_data[date_str].append(entry)
        
        # Sort by date
        return dict(sorted(daily_data.items()))
    
    def _generate_file_content(self, date_str: str, entries) -> str:
        """Generate content for a daily file."""
        lines = []
        
        # For raw format, just output words with no headers or metadata
        if self.args.format == "raw":
            all_words = []
            for entry in entries:
                text = entry.display_text.strip()
                if text:
                    # Clean word extraction - remove punctuation, normalize spacing
                    words = text.replace(".", " ").replace(",", " ").replace("!", " ").replace("?", " ")
                    words = words.replace("(", " ").replace(")", " ").replace(";", " ").replace(":", " ")
                    words = " ".join(words.split())  # Normalize whitespace
                    if words:
                        all_words.append(words)
            return "\n".join(all_words)
        
        # For other formats, include headers
        lines.append(f"# Words spoken on {date_str}")
        lines.append(f"# Total entries: {len(entries)}")
        
        total_words = sum(entry.num_words or 0 for entry in entries)
        total_duration = sum(entry.duration or 0 for entry in entries)
        
        lines.append(f"# Total words: {total_words}")
        lines.append(f"# Total duration: {total_duration:.1f}s")
        lines.append("")
        
        # App breakdown
        app_counts = defaultdict(int)
        for entry in entries:
            app_counts[entry.app_name] += 1
        
        lines.append("# App breakdown:")
        for app, count in sorted(app_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"# {app}: {count} entries")
        lines.append("")
        
        # Content based on format
        if self.args.format == "words":
            # Extract just words (similar to GranolaMCP)
            all_words = []
            for entry in entries:
                text = entry.display_text.strip()
                if text:
                    # Simple word extraction
                    words = text.replace(".", " ").replace(",", " ").replace("!", " ").replace("?", " ")
                    words = " ".join(words.split())  # Normalize whitespace
                    all_words.append(words)
            
            lines.append("\n".join(all_words))
        
        elif self.args.format == "sentences":
            # Keep sentences intact
            for entry in sorted(entries, key=lambda x: x.timestamp or datetime.min):
                text = entry.display_text.strip()
                if text:
                    lines.append(text)
        
        elif self.args.format == "entries":
            # Include metadata for each entry
            for entry in sorted(entries, key=lambda x: x.timestamp or datetime.min):
                time_str = entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else "unknown"
                lines.append(f"[{time_str}] [{entry.app_name}] {entry.display_text}")
        
        return "\n".join(lines)
    
    def _count_words(self, content: str) -> int:
        """Count words in content."""
        if self.args.format == "raw":
            # For raw format, count all words directly
            return len(content.split()) if content.strip() else 0
        else:
            # Skip header lines (those starting with #)
            text_lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
            text = ' '.join(text_lines)
            return len(text.split()) if text.strip() else 0