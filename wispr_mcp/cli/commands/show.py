"""
Show command for WisprMCP CLI.
"""

import argparse
import json
from typing import Optional

from ...core.parser import WisprParser
from ...core.transcript import TranscriptEntry
from ..formatters.colors import Colors


class ShowCommand:
    """Show specific transcript entry."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.parser = WisprParser(args.db_path)
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """Add arguments for the show command."""
        parser.add_argument(
            "transcript_id",
            help="Transcript ID to show (full ID or first 8 characters)"
        )
        parser.add_argument(
            "--format",
            choices=["text", "json"],
            default="text",
            help="Output format (default: text)"
        )
        parser.add_argument(
            "--show-context",
            action="store_true",
            help="Show additional context information"
        )
        parser.add_argument(
            "--show-all-versions",
            action="store_true",
            help="Show ASR, formatted, and edited versions"
        )
    
    def run(self) -> int:
        """Execute the show command."""
        # Get the entry
        entry = self._find_entry(self.args.transcript_id)
        
        if not entry:
            print(Colors.error(f"Transcript not found: {self.args.transcript_id}"))
            return 1
        
        # Format output
        if self.args.format == "json":
            data = entry.to_dict()
            if self.args.show_context:
                data["additional_context"] = entry.additional_context
            print(json.dumps(data, indent=2, default=str))
        else:
            self._print_entry_text(entry)
        
        return 0
    
    def _find_entry(self, transcript_id: str) -> Optional[TranscriptEntry]:
        """Find entry by full ID or partial ID."""
        # First try exact match
        entry = self.parser.get_entry_by_id(transcript_id)
        if entry:
            return entry
        
        # If not found and it's a partial ID, search for matches
        if len(transcript_id) < 36:  # UUID length
            # Get recent entries and search
            entries = self.parser.get_entries(limit=1000)
            
            matches = []
            for entry in entries:
                if entry.transcript_id.startswith(transcript_id):
                    matches.append(entry)
            
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(Colors.warning(f"Multiple matches found for '{transcript_id}':"))
                for match in matches[:10]:  # Show first 10
                    print(f"  {match.transcript_id[:16]}... - {match.app_name} - {match.display_text[:50]}...")
                return None
        
        return None
    
    def _print_entry_text(self, entry: TranscriptEntry) -> None:
        """Print entry in detailed text format."""
        # Header
        print(Colors.bold(f"Transcript: {entry.transcript_id}"))
        print()
        
        # Metadata
        metadata = []
        if entry.timestamp:
            metadata.append(("Time", Colors.timestamp(entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"))))
        
        metadata.append(("App", Colors.app_name(entry.app_name)))
        
        if entry.status:
            metadata.append(("Status", Colors.status(entry.status)))
        
        if entry.duration is not None:
            metadata.append(("Duration", Colors.duration(entry.duration)))
        
        if entry.num_words is not None:
            metadata.append(("Words", Colors.word_count(str(entry.num_words))))
        
        if entry.language:
            metadata.append(("Language", entry.language))
        
        if entry.conversation_id:
            metadata.append(("Conversation", entry.conversation_id[:16] + "..."))
        
        if entry.e2e_latency is not None:
            metadata.append(("Latency", f"{entry.e2e_latency:.2f}s"))
        
        if entry.quality_score is not None:
            metadata.append(("Quality", Colors.quality_score(entry.quality_score)))
        
        if entry.url:
            metadata.append(("URL", entry.url))
        
        # Print metadata
        for key, value in metadata:
            print(f"{Colors.muted(key + ':'):15} {value}")
        
        print()
        
        # Text content
        if self.args.show_all_versions:
            # Show all text versions
            if entry.asr_text:
                print(Colors.bold("ASR Text:"))
                print(entry.asr_text)
                print()
            
            if entry.formatted_text:
                print(Colors.bold("Formatted Text:"))
                print(entry.formatted_text)
                print()
            
            if entry.edited_text:
                print(Colors.bold("Edited Text:"))
                print(entry.edited_text)
                print()
        else:
            # Show best available text
            print(Colors.bold("Text:"))
            text = entry.display_text
            if text:
                print(text)
            else:
                print(Colors.muted("(no text available)"))
            print()
        
        # Additional context
        if self.args.show_context and entry.additional_context:
            print(Colors.bold("Additional Context:"))
            if isinstance(entry.additional_context, dict):
                for key, value in entry.additional_context.items():
                    if isinstance(value, (dict, list)):
                        print(f"{Colors.muted(key + ':'):15} {json.dumps(value, indent=2)}")
                    else:
                        print(f"{Colors.muted(key + ':'):15} {value}")
            else:
                print(json.dumps(entry.additional_context, indent=2))
            print()
        
        # User context summary
        user_context = entry.user_context
        if user_context:
            print(Colors.bold("Context Summary:"))
            for key, value in user_context.items():
                if isinstance(value, (dict, list)):
                    print(f"{Colors.muted(key + ':'):15} {json.dumps(value)}")
                else:
                    print(f"{Colors.muted(key + ':'):15} {value}")
            print()