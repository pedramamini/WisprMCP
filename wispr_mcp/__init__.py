"""
WisprMCP - A Python library for accessing Wispr Flow's SQLite database.

This package provides programmatic access to Wispr Flow's local SQLite database,
enabling users to query transcripts, search conversations, and analyze communication data.
"""

from .core.parser import WisprParser
from .core.transcript import Transcript, TranscriptEntry
from .core.conversation import Conversation

__version__ = "0.1.0"
__author__ = "Pedram"

__all__ = [
    "WisprParser",
    "Transcript", 
    "TranscriptEntry",
    "Conversation",
]