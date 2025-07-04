"""
Apps command for WisprMCP CLI.
"""

import argparse
import json
from typing import List, Dict, Any

from ...core.parser import WisprParser
from ..formatters.colors import Colors
from ..formatters.table import format_app_stats_table


class AppsCommand:
    """Show app usage statistics."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.parser = WisprParser(args.db_path)
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """Add arguments for the apps command."""
        parser.add_argument(
            "--format",
            choices=["table", "json", "text"],
            default="table",
            help="Output format (default: table)"
        )
        parser.add_argument(
            "--limit", "-l",
            type=int,
            default=20,
            help="Maximum number of apps to show (default: 20)"
        )
        parser.add_argument(
            "--sort",
            choices=["entries", "words", "duration", "latency", "last_used"],
            default="entries",
            help="Sort by field (default: entries)"
        )
        parser.add_argument(
            "--min-entries",
            type=int,
            default=1,
            help="Minimum number of entries to include app (default: 1)"
        )
    
    def run(self) -> int:
        """Execute the apps command."""
        # Get app statistics
        apps = self.parser.get_apps()
        
        if not apps:
            print(Colors.muted("No app usage data found."))
            return 0
        
        # Filter by minimum entries
        apps = [app for app in apps if app["total_entries"] >= self.args.min_entries]
        
        # Sort apps
        sort_key_map = {
            "entries": "total_entries",
            "words": "total_words",
            "duration": "total_duration",
            "latency": "avg_latency",
            "last_used": "last_used"
        }
        
        sort_key = sort_key_map.get(self.args.sort, "total_entries")
        apps.sort(key=lambda x: x[sort_key] or 0, reverse=True)
        
        # Limit results
        if self.args.limit:
            apps = apps[:self.args.limit]
        
        # Format output
        if self.args.format == "json":
            print(json.dumps(apps, indent=2, default=str))
        
        elif self.args.format == "text":
            self._print_apps_text(apps)
        
        else:  # table format
            table = format_app_stats_table(apps)
            print(table)
            
            # Summary
            total_entries = sum(app["total_entries"] for app in apps)
            total_words = sum(app["total_words"] for app in apps)
            total_duration = sum(app["total_duration"] for app in apps)
            
            print(f"\n{Colors.muted('Summary:')} {len(apps)} apps, "
                  f"{total_entries} entries, "
                  f"{Colors.duration(total_duration)}, "
                  f"{Colors.word_count(total_words)} words")
        
        return 0
    
    def _print_apps_text(self, apps: List[Dict[str, Any]]) -> None:
        """Print apps in text format."""
        print(Colors.bold("App Usage Statistics"))
        print()
        
        for i, app in enumerate(apps, 1):
            # App header
            print(f"{Colors.bold(f'{i}.')} {Colors.app_name(app['app_name'])}")
            
            # Bundle ID if different from name
            if app["app_id"] != app["app_name"]:
                print(f"    {Colors.muted('Bundle ID:')} {app['app_id']}")
            
            # Statistics
            stats = []
            stats.append(f"{app['total_entries']} entries")
            
            if app["total_words"] > 0:
                stats.append(f"{Colors.word_count(app['total_words'])} words")
            
            if app["total_duration"] > 0:
                stats.append(f"{Colors.duration(app['total_duration'])}")
            
            if app["avg_latency"] > 0:
                stats.append(f"{app['avg_latency']:.2f}s avg latency")
            
            if app["last_used"]:
                try:
                    from datetime import datetime
                    last_used = datetime.fromisoformat(app["last_used"].replace("Z", "+00:00"))
                    stats.append(f"last used {Colors.timestamp(last_used.strftime('%Y-%m-%d %H:%M'))}")
                except:
                    stats.append(f"last used {app['last_used']}")
            
            print(f"    {' | '.join(stats)}")
            print()
        
        # Total summary
        if apps:
            total_entries = sum(app["total_entries"] for app in apps)
            total_words = sum(app["total_words"] for app in apps)
            total_duration = sum(app["total_duration"] for app in apps)
            
            print(Colors.bold("Total Summary:"))
            print(f"  Apps: {len(apps)}")
            print(f"  Entries: {total_entries}")
            print(f"  Words: {Colors.word_count(total_words)}")
            print(f"  Duration: {Colors.duration(total_duration)}")
            
            if total_entries > 0:
                avg_words_per_entry = total_words / total_entries
                avg_duration_per_entry = total_duration / total_entries
                print(f"  Average per entry: {Colors.word_count(int(avg_words_per_entry))} words, "
                      f"{Colors.duration(avg_duration_per_entry)}")
            
            # Top apps summary
            print()
            print(Colors.bold("Top 3 Apps:"))
            for i, app in enumerate(apps[:3], 1):
                percentage = (app["total_entries"] / total_entries) * 100
                print(f"  {i}. {Colors.app_name(app['app_name'])} - "
                      f"{app['total_entries']} entries ({percentage:.1f}%)")