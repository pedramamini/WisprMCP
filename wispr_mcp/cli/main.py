"""
Main CLI entry point for WisprMCP.
"""

import argparse
import sys
from typing import Optional

from .commands.list import ListCommand
from .commands.show import ShowCommand
from .commands.search import SearchCommand
from .commands.stats import StatsCommand
from .commands.export import ExportCommand
from .commands.apps import AppsCommand
from .commands.collect import CollectCommand
from .formatters.colors import Colors


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="wispr",
        description="WisprMCP - Access and analyze your Wispr Flow transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wispr list                          # List recent transcripts (last 2 days)
  wispr list --app Slack              # List Slack transcripts
  wispr list --since 3d               # List transcripts from last 3 days
  wispr show abc123                   # Show specific transcript
  wispr search "hello world"          # Search for text
  wispr stats                         # Show database statistics
  wispr export --format json > data.json  # Export to JSON
  wispr apps                          # Show app usage statistics
  wispr collect ./my-words            # Collect YOUR spoken words by day (last 7 days)
  wispr collect ./words --since 1m    # Collect YOUR words from last month

Date formats:
  Relative: 1h, 2d, 3w, 1m, 6m, 1y
  Absolute: 2024-01-01, 2024-01-01 10:30, 01/01/2024
        """
    )
    
    # Global options
    parser.add_argument(
        "--db-path",
        help="Path to Wispr Flow database (default: auto-detect)"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List transcript entries")
    ListCommand.add_arguments(list_parser)
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show specific transcript")
    ShowCommand.add_arguments(show_parser)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search transcripts")
    SearchCommand.add_arguments(search_parser)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    StatsCommand.add_arguments(stats_parser)
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export data")
    ExportCommand.add_arguments(export_parser)
    
    # Apps command
    apps_parser = subparsers.add_parser("apps", help="Show app usage statistics")
    AppsCommand.add_arguments(apps_parser)
    
    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect YOUR spoken words by day")
    CollectCommand.add_arguments(collect_parser)
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle no-color flag
    if args.no_color:
        import os
        os.environ["NO_COLOR"] = "1"
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0
    
    # Get command class
    commands = {
        "list": ListCommand,
        "show": ShowCommand,
        "search": SearchCommand,
        "stats": StatsCommand,
        "export": ExportCommand,
        "apps": AppsCommand,
        "collect": CollectCommand,
    }
    
    command_class = commands.get(args.command)
    if not command_class:
        print(Colors.error(f"Unknown command: {args.command}"))
        return 1
    
    # Execute command
    try:
        command = command_class(args)
        return command.run()
    except FileNotFoundError as e:
        print(Colors.error(f"Database not found: {e}"))
        print(Colors.info("Make sure Wispr Flow is installed and has been run at least once."))
        return 1
    except KeyboardInterrupt:
        print(Colors.muted("\nCancelled by user"))
        return 130
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(Colors.error(f"Error: {e}"))
        return 1


if __name__ == "__main__":
    sys.exit(main())