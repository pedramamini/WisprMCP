"""
ANSI color formatting for CLI output.
"""

import os
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    
    # Color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Semantic colors
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = BLUE
    DEBUG = BRIGHT_BLACK
    HIGHLIGHT = BRIGHT_CYAN
    MUTED = BRIGHT_BLACK
    
    @classmethod
    def should_colorize(cls) -> bool:
        """Check if output should be colorized."""
        # Check if NO_COLOR environment variable is set
        if os.environ.get("NO_COLOR"):
            return False
        
        # Check if FORCE_COLOR is set
        if os.environ.get("FORCE_COLOR"):
            return True
        
        # Check if we're in a TTY
        return hasattr(os.sys.stdout, 'isatty') and os.sys.stdout.isatty()
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text if colorization is enabled."""
        if cls.should_colorize():
            return f"{color}{text}{cls.RESET}"
        return text
    
    @classmethod
    def success(cls, text: str) -> str:
        """Format text as success."""
        return cls.colorize(text, cls.SUCCESS)
    
    @classmethod
    def error(cls, text: str) -> str:
        """Format text as error."""
        return cls.colorize(text, cls.ERROR)
    
    @classmethod
    def warning(cls, text: str) -> str:
        """Format text as warning."""
        return cls.colorize(text, cls.WARNING)
    
    @classmethod
    def info(cls, text: str) -> str:
        """Format text as info."""
        return cls.colorize(text, cls.INFO)
    
    @classmethod
    def debug(cls, text: str) -> str:
        """Format text as debug."""
        return cls.colorize(text, cls.DEBUG)
    
    @classmethod
    def highlight(cls, text: str) -> str:
        """Format text as highlight."""
        return cls.colorize(text, cls.HIGHLIGHT)
    
    @classmethod
    def muted(cls, text: str) -> str:
        """Format text as muted."""
        return cls.colorize(text, cls.MUTED)
    
    @classmethod
    def bold(cls, text: str) -> str:
        """Format text as bold."""
        return cls.colorize(text, cls.BOLD)
    
    @classmethod
    def dim(cls, text: str) -> str:
        """Format text as dim."""
        return cls.colorize(text, cls.DIM)
    
    @classmethod
    def app_name(cls, app_name: str) -> str:
        """Format app name."""
        # Different colors for different apps
        app_colors = {
            "Slack": cls.BRIGHT_MAGENTA,
            "Obsidian": cls.BRIGHT_BLUE,
            "VS Code": cls.BRIGHT_CYAN,
            "Chrome": cls.BRIGHT_YELLOW,
            "Messages": cls.BRIGHT_GREEN,
            "ChatGPT": cls.BRIGHT_RED,
            "Safari": cls.BLUE,
            "Mail": cls.CYAN,
            "Notes": cls.YELLOW,
            "Wispr Flow": cls.MAGENTA,
        }
        
        color = app_colors.get(app_name, cls.WHITE)
        return cls.colorize(app_name, color)
    
    @classmethod
    def status(cls, status: str) -> str:
        """Format status."""
        status_colors = {
            "formatted": cls.SUCCESS,
            "empty": cls.MUTED,
            "no_audio": cls.WARNING,
            "dismissed": cls.ERROR,
            "extension_other": cls.INFO,
            "extension_paste": cls.INFO,
        }
        
        color = status_colors.get(status, cls.WHITE)
        return cls.colorize(status, color)
    
    @classmethod
    def quality_score(cls, score: float) -> str:
        """Format quality score with color."""
        if score >= 0.8:
            color = cls.SUCCESS
        elif score >= 0.6:
            color = cls.WARNING
        else:
            color = cls.ERROR
        
        return cls.colorize(f"{score:.1f}", color)
    
    @classmethod
    def duration(cls, duration) -> str:
        """Format duration with color."""
        if duration is None:
            duration = 0.0
        
        duration = float(duration)
        
        if duration >= 60:
            color = cls.BRIGHT_YELLOW
        elif duration >= 10:
            color = cls.YELLOW
        else:
            color = cls.MUTED
        
        # Format duration
        if duration >= 60:
            minutes = duration / 60
            formatted = f"{minutes:.1f}m"
        else:
            formatted = f"{duration:.1f}s"
        
        return cls.colorize(formatted, color)
    
    @classmethod
    def word_count(cls, count) -> str:
        """Format word count with color."""
        if count is None:
            count = 0
        
        count = int(count)
        
        if count >= 100:
            color = cls.BRIGHT_GREEN
        elif count >= 20:
            color = cls.GREEN
        else:
            color = cls.MUTED
        
        return cls.colorize(str(count), color)
    
    @classmethod
    def timestamp(cls, timestamp: str) -> str:
        """Format timestamp."""
        return cls.colorize(timestamp, cls.MUTED)