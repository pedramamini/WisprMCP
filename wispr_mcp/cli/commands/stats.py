"""
Stats command for WisprMCP CLI.
"""

import argparse
import json
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from rich.panel import Panel
from datetime import datetime, timedelta
from collections import defaultdict

from ...core.parser import WisprParser
from ...utils.date_parser import DateParser
from ..formatters.colors import Colors

# Try to import Rich for beautiful dashboard
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    from rich.align import Align
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class StatsCommand:
    """Show database statistics."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.parser = WisprParser(args.db_path)
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """Add arguments for the stats command."""
        parser.add_argument(
            "--format",
            choices=["dashboard", "text", "json"],
            default="dashboard",
            help="Output format (default: dashboard if Rich available, else text)"
        )
        parser.add_argument(
            "--since",
            help="Show stats since this date/time (e.g. '3d', '1w', '2024-01-01')"
        )
        parser.add_argument(
            "--until",
            help="Show stats until this date/time"
        )
        parser.add_argument(
            "--app",
            help="Filter by app (bundle ID or name)"
        )
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Show verbose text statistics (appended to dashboard)"
        )
    
    def run(self) -> int:
        """Execute the stats command."""
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
        app_filter = self._resolve_app_filter(self.args.app)
        
        # Get statistics
        if start_date or end_date or app_filter:
            stats = self._get_filtered_stats(start_date, end_date, app_filter)
        else:
            stats = self.parser.get_statistics()
        
        # Get additional data for dashboard
        entries = self.parser.get_entries(
            start_date=start_date,
            end_date=end_date,
            app=app_filter,
            include_archived=True
        )
        
        # Format output
        if self.args.format == "json":
            print(json.dumps(stats, indent=2, default=str))
        elif self.args.format == "text":
            self._print_stats_text(stats)
        else:
            # Dashboard format
            if RICH_AVAILABLE and self.args.format == "dashboard":
                self._show_dashboard(stats, entries)
                if self.args.verbose:
                    print("\n" + "="*50 + " VERBOSE DETAILS " + "="*50)
                    self._print_stats_text(stats)
            else:
                self._print_stats_text(stats)
        
        return 0
    
    def _resolve_app_filter(self, app: str) -> str:
        """Resolve app name to bundle ID if needed."""
        if not app:
            return None
        
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
    
    def _show_dashboard(self, stats: Dict[str, Any], entries: list) -> None:
        """Show beautiful Rich dashboard."""
        # Create console with max width of 120
        dashboard_console = Console(width=min(120, console.size.width))
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )
        
        layout["left"].split_column(
            Layout(name="overview", size=10),
            Layout(name="quality", size=10)
        )
        
        layout["right"].split_column(
            Layout(name="trends", size=14),
            Layout(name="apps", size=6)
        )
        
        # Header
        title = Text("🎤 Wispr Flow Statistics Dashboard", style="bold blue")
        if stats.get("filtered"):
            title.append(" (Filtered)", style="yellow")
        layout["header"].update(Panel(Align.center(title), style="blue"))
        
        # Overview panel
        layout["overview"].update(self._create_overview_panel(stats, entries))
        
        # Apps panel
        layout["apps"].update(self._create_apps_panel(entries))
        
        # Trends panel
        layout["trends"].update(self._create_trends_panel(entries))
        
        # Quality panel
        layout["quality"].update(self._create_quality_panel(entries, stats))
        
        # Footer
        footer_text = f"Database: {stats.get('database_path', 'Unknown')}"
        layout["footer"].update(Panel(Align.center(footer_text), style="dim"))
        
        # Render
        dashboard_console.print(layout)
    
    def _create_overview_panel(self, stats: Dict[str, Any], entries: list) -> "Panel":
        """Create overview statistics panel."""
        table = Table.grid(padding=1)
        table.add_column(style="bold cyan", no_wrap=True)
        table.add_column(style="bold white")
        
        table.add_row("📊 Total Entries:", f"{stats['total_entries']:,}")
        table.add_row("✅ Active:", f"{stats['active_entries']:,}")
        table.add_row("📁 Archived:", f"{stats['archived_entries']:,}")
        table.add_row("")
        table.add_row("⏱️  Total Duration:", f"{stats['total_duration']/60:.1f} minutes")
        table.add_row("💬 Total Words:", f"{stats['total_words']:,}")
        table.add_row("📈 Avg Duration:", f"{stats['avg_duration']:.1f}s")
        table.add_row("📝 Avg Words:", f"{stats['avg_words']:.0f}")
        
        # Calculate peak WPM for overview - use the same logic as trends
        peak_wpm = self._get_peak_wpm_from_trends(entries)
        if peak_wpm > 0:
            table.add_row("🚀 Peak WPM:", f"{peak_wpm:.0f}")
        
        return Panel(table, title="[bold green]Overview[/bold green]", border_style="green")
    
    def _calculate_peak_wpm(self, entries: list) -> float:
        """Calculate peak words per minute from all entries."""
        if not entries:
            return 0
        
        # Group by day and calculate daily WPM
        daily_words = defaultdict(int)
        daily_duration = defaultdict(float)
        
        for entry in entries:
            if entry.timestamp:
                day = entry.timestamp.date()
                daily_words[day] += entry.num_words or 0
                daily_duration[day] += entry.duration or 0
        
        # Calculate WPM for each day
        peak_wpm = 0
        for day in daily_words:
            if daily_duration[day] > 0 and daily_words[day] > 0:
                wpm = (daily_words[day] / daily_duration[day]) * 60
                peak_wpm = max(peak_wpm, wpm)
        
        return peak_wpm
    
    def _get_peak_wpm_from_trends(self, entries: list) -> float:
        """Get peak WPM using the same logic as trends panel."""
        if not entries:
            return 0
        
        # Group by day (same as trends)
        daily_words = defaultdict(int)
        daily_duration = defaultdict(float)
        
        for entry in entries:
            if entry.timestamp:
                day = entry.timestamp.date()
                daily_words[day] += entry.num_words or 0
                daily_duration[day] += entry.duration or 0
        
        # Calculate WPM for each day and find peak
        wpm_values = []
        for day in daily_words:
            if daily_duration[day] > 0 and daily_words[day] > 0:
                wpm = (daily_words[day] / daily_duration[day]) * 60  # Convert to per minute
                wpm_values.append(wpm)
        
        return max(wpm_values) if wpm_values else 0
    
    def _create_apps_panel(self, entries: list) -> Panel:
        """Create apps usage panel with progress bars."""
        if not entries:
            return Panel("No data", title="Apps", border_style="red")
        
        # Count entries by app
        app_counts = defaultdict(int)
        for entry in entries:
            app_counts[entry.app_name] += 1
        
        # Create table with progress bars
        table = Table.grid(padding=(0, 1))
        table.add_column(style="cyan", no_wrap=True, width=12)
        table.add_column(width=20)
        table.add_column(style="bold", justify="right", width=6)
        
        total_entries = len(entries)
        sorted_apps = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        
        for app, count in sorted_apps:
            percentage = (count / total_entries) * 100
            bar_length = int((count / sorted_apps[0][1]) * 15)
            bar = "█" * bar_length + "░" * (15 - bar_length)
            
            table.add_row(
                app[:11],
                f"[blue]{bar}[/blue]",
                f"{count}"
            )
        
        return Panel(table, title="[bold magenta]Top Apps[/bold magenta]", border_style="magenta")
    
    def _create_trends_panel(self, entries: list) -> Panel:
        """Create daily trends panel with sparklines."""
        if not entries:
            return Panel("No data", title="Trends", border_style="red")
        
        # Group by day
        daily_counts = defaultdict(int)
        daily_words = defaultdict(int)
        daily_duration = defaultdict(float)
        
        for entry in entries:
            if entry.timestamp:
                day = entry.timestamp.date()
                daily_counts[day] += 1
                daily_words[day] += entry.num_words or 0
                daily_duration[day] += entry.duration or 0
        
        if not daily_counts:
            return Panel("No dated entries", title="Trends", border_style="yellow")
        
        # Get last 30 days for wider graphs
        today = datetime.now().date()
        days = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
        
        counts = [daily_counts.get(day, 0) for day in days]
        words = [daily_words.get(day, 0) for day in days]
        durations = [daily_duration.get(day, 0) for day in days]
        
        # Calculate words per minute for each day
        wpm_values = []
        for i in range(len(days)):
            if durations[i] > 0 and words[i] > 0:
                wpm = (words[i] / durations[i]) * 60  # Convert to per minute
                wpm_values.append(wpm)
            else:
                wpm_values.append(0)
        
        # Create sparklines
        def make_sparkline(values):
            if not values or max(values) == 0:
                return "▁" * len(values)
            
            max_val = max(values)
            sparks = "▁▂▃▄▅▆▇█"
            return "".join(sparks[min(int(v / max_val * 7), 7)] for v in values)
        
        entries_spark = make_sparkline(counts)
        words_spark = make_sparkline(words)
        wpm_spark = make_sparkline(wpm_values)
        
        table = Table.grid(padding=1)
        table.add_column(style="yellow", no_wrap=True)
        table.add_column()
        
        # Calculate current values for display
        recent_entries = sum(counts[-7:])  # Last 7 days
        recent_words = sum(words[-7:])  # Last 7 days
        recent_wpm = sum([wpm for wpm in wpm_values[-7:] if wpm > 0]) / max(1, len([w for w in wpm_values[-7:] if w > 0])) if wpm_values else 0
        
        table.add_row("📈 Entries (30d):", f"[green]{entries_spark}[/green] {recent_entries}/week")
        table.add_row("💭 Words (30d):", f"[blue]{words_spark}[/blue] {recent_words}/week")
        table.add_row("⚡ WPM (30d):", f"[cyan]{wpm_spark}[/cyan] {recent_wpm:.0f} avg")
        table.add_row("")
        table.add_row("📅 Most Active:", max(daily_counts, key=daily_counts.get).strftime("%m/%d") if daily_counts else "N/A")
        table.add_row("🔥 Peak Entries:", str(max(daily_counts.values())) if daily_counts else "0")
        table.add_row("💪 Peak Words:", str(max(daily_words.values())) if daily_words else "0")
        
        # Add WPM stats
        if wpm_values and any(wpm > 0 for wpm in wpm_values):
            valid_wpm = [wpm for wpm in wpm_values if wpm > 0]
            avg_wpm = sum(valid_wpm) / len(valid_wpm)
            peak_wpm = max(wpm_values)
            table.add_row("⚡ Avg WPM:", f"{avg_wpm:.0f}")
            table.add_row("🚀 Peak WPM:", f"{peak_wpm:.0f}")
        
        return Panel(table, title="[bold yellow]Trends[/bold yellow]", border_style="yellow")
    
    def _create_quality_panel(self, entries: list, stats: Dict[str, Any]) -> Panel:
        """Create quality metrics panel."""
        if not entries:
            return Panel("No data", title="Quality", border_style="red")
        
        # Calculate quality metrics
        status_breakdown = stats.get("status_breakdown", {})
        formatted_count = status_breakdown.get("formatted", 0)
        total = stats.get("total_entries", 1)
        
        success_rate = (formatted_count / total) * 100 if total > 0 else 0
        
        # Average quality score
        quality_scores = [e.quality_score for e in entries if e.quality_score is not None]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Latency stats
        latencies = [e.e2e_latency for e in entries if e.e2e_latency is not None and e.e2e_latency > 0]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        table = Table.grid(padding=1)
        table.add_column(style="bold red", no_wrap=True)
        table.add_column()
        
        # Success rate with color
        if success_rate >= 80:
            rate_color = "green"
        elif success_rate >= 60:
            rate_color = "yellow"
        else:
            rate_color = "red"
        
        table.add_row("✅ Success Rate:", f"[{rate_color}]{success_rate:.1f}%[/{rate_color}]")
        table.add_row("⭐ Avg Quality:", f"{avg_quality:.2f}")
        table.add_row("⚡ Avg Latency:", f"{abs(avg_latency):.0f}ms" if avg_latency != 0 else "N/A")
        table.add_row("")
        
        # Status breakdown
        for status, count in sorted(status_breakdown.items(), key=lambda x: x[1], reverse=True)[:4]:
            percentage = (count / total) * 100
            table.add_row(f"{status}:", f"{count} ({percentage:.1f}%)")
        
        return Panel(table, title="[bold red]Quality[/bold red]", border_style="red")
    
    def _get_filtered_stats(self, start_date, end_date, app_filter) -> Dict[str, Any]:
        """Get statistics for filtered data."""
        # Get entries based on filters
        entries = self.parser.get_entries(
            start_date=start_date,
            end_date=end_date,
            app=app_filter,
            include_archived=True
        )
        
        # Calculate statistics
        total_entries = len(entries)
        active_entries = len([e for e in entries if not e.is_archived])
        archived_entries = total_entries - active_entries
        
        total_duration = sum(e.duration or 0 for e in entries)
        total_words = sum(e.num_words or 0 for e in entries)
        
        valid_entries = [e for e in entries if e.duration is not None and e.num_words is not None]
        avg_duration = sum(e.duration for e in valid_entries) / len(valid_entries) if valid_entries else 0
        avg_words = sum(e.num_words for e in valid_entries) / len(valid_entries) if valid_entries else 0
        
        # Status breakdown
        status_breakdown = {}
        for entry in entries:
            status = entry.status or "unknown"
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        # App breakdown
        app_breakdown = {}
        for entry in entries:
            app_name = entry.app_name
            app_breakdown[app_name] = app_breakdown.get(app_name, 0) + 1
        
        # Date range
        timestamps = [e.timestamp for e in entries if e.timestamp]
        first_entry = min(timestamps).isoformat() if timestamps else None
        last_entry = max(timestamps).isoformat() if timestamps else None
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "archived_entries": archived_entries,
            "total_duration": total_duration,
            "total_words": total_words,
            "avg_duration": avg_duration,
            "avg_words": avg_words,
            "status_breakdown": status_breakdown,
            "app_breakdown": app_breakdown,
            "first_entry": first_entry,
            "last_entry": last_entry,
            "filtered": True,
            "database_path": str(self.parser.db_path),
        }
    
    def _print_stats_text(self, stats: Dict[str, Any]) -> None:
        """Print statistics in text format."""
        # Header
        if stats.get("filtered"):
            print(Colors.bold("Filtered Statistics"))
        else:
            print(Colors.bold("Database Statistics"))
        print()
        
        # Basic counts
        print(Colors.info("Entry Counts:"))
        print(f"  Total entries:    {Colors.highlight(str(stats['total_entries']))}")
        print(f"  Active entries:   {Colors.success(str(stats['active_entries']))}")
        print(f"  Archived entries: {Colors.muted(str(stats['archived_entries']))}")
        print()
        
        # Duration and words
        print(Colors.info("Content Statistics:"))
        print(f"  Total duration:   {Colors.duration(stats['total_duration'])}")
        print(f"  Total words:      {Colors.word_count(stats['total_words'])}")
        print(f"  Average duration: {Colors.duration(stats['avg_duration'])}")
        print(f"  Average words:    {Colors.word_count(int(stats['avg_words']))}")
        print()
        
        # Date range
        if stats.get("first_entry") and stats.get("last_entry"):
            print(Colors.info("Date Range:"))
            try:
                from datetime import datetime
                first = datetime.fromisoformat(stats["first_entry"].replace("Z", "+00:00"))
                last = datetime.fromisoformat(stats["last_entry"].replace("Z", "+00:00"))
                print(f"  First entry: {Colors.timestamp(first.strftime('%Y-%m-%d %H:%M:%S'))}")
                print(f"  Last entry:  {Colors.timestamp(last.strftime('%Y-%m-%d %H:%M:%S'))}")
                
                # Calculate time span
                time_span = last - first
                if time_span.days > 0:
                    print(f"  Time span:   {Colors.muted(f'{time_span.days} days')}")
                print()
            except:
                print(f"  First entry: {stats['first_entry']}")
                print(f"  Last entry:  {stats['last_entry']}")
                print()
        
        # Status breakdown
        if stats.get("status_breakdown"):
            print(Colors.info("Status Breakdown:"))
            status_items = sorted(stats["status_breakdown"].items(), key=lambda x: x[1], reverse=True)
            for status, count in status_items:
                percentage = (count / stats["total_entries"]) * 100
                print(f"  {Colors.status(status):15} {count:6} ({percentage:5.1f}%)")
            print()
        
        # App breakdown (if verbose or filtered)
        if self.args.verbose or stats.get("filtered"):
            app_breakdown = stats.get("app_breakdown", {})
            if app_breakdown:
                print(Colors.info("App Breakdown:"))
                app_items = sorted(app_breakdown.items(), key=lambda x: x[1], reverse=True)
                for app, count in app_items[:10]:  # Show top 10
                    percentage = (count / stats["total_entries"]) * 100
                    print(f"  {Colors.app_name(app):15} {count:6} ({percentage:5.1f}%)")
                
                if len(app_items) > 10:
                    print(f"  {Colors.muted('... and')} {len(app_items) - 10} {Colors.muted('more')}")
                print()
        
        # Database info
        print(Colors.info("Database:"))
        print(f"  Path: {Colors.muted(stats['database_path'])}")
        
        # Quality metrics (if available)
        if self.args.verbose:
            print()
            print(Colors.info("Quality Metrics:"))
            
            # Get some quality statistics
            entries = self.parser.get_entries(limit=1000)
            if entries:
                quality_scores = [e.quality_score for e in entries if e.quality_score is not None]
                if quality_scores:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    print(f"  Average quality: {Colors.quality_score(avg_quality)}")
                
                # Latency stats
                latencies = [e.e2e_latency for e in entries if e.e2e_latency is not None]
                if latencies:
                    avg_latency = sum(latencies) / len(latencies)
                    print(f"  Average latency: {avg_latency:.2f}s")
                
                # Audio availability
                has_audio = len([e for e in entries if e.has_audio])
                print(f"  Entries with audio: {has_audio}/{len(entries)} ({(has_audio/len(entries)*100):.1f}%)")