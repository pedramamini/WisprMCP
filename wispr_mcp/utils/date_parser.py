"""
Date parsing utilities for WisprMCP.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union


class DateParser:
    """Parse various date formats including relative dates."""
    
    @staticmethod
    def parse_relative_date(date_string: str) -> Optional[datetime]:
        """
        Parse relative date strings like '1h', '2d', '3w', etc.
        
        Args:
            date_string: String like '1h', '2d', '3w', '1m' (month), '1y'
            
        Returns:
            datetime object representing the parsed date or None if invalid
        """
        if not date_string:
            return None
            
        # Clean the string
        date_string = date_string.strip().lower()
        
        # Pattern for relative dates
        pattern = r'^(\d+)\s*(h|hour|hours|d|day|days|w|week|weeks|m|month|months|y|year|years)$'
        match = re.match(pattern, date_string)
        
        if not match:
            return None
            
        amount = int(match.group(1))
        unit = match.group(2)
        
        now = datetime.now()
        
        if unit in ['h', 'hour', 'hours']:
            return now - timedelta(hours=amount)
        elif unit in ['d', 'day', 'days']:
            return now - timedelta(days=amount)
        elif unit in ['w', 'week', 'weeks']:
            return now - timedelta(weeks=amount)
        elif unit in ['m', 'month', 'months']:
            return now - timedelta(days=amount * 30)  # Approximate
        elif unit in ['y', 'year', 'years']:
            return now - timedelta(days=amount * 365)  # Approximate
        
        return None
    
    @staticmethod
    def parse_absolute_date(date_string: str) -> Optional[datetime]:
        """
        Parse absolute date strings in various formats.
        
        Args:
            date_string: Date string in various formats
            
        Returns:
            datetime object or None if invalid
        """
        if not date_string:
            return None
            
        # List of common date formats to try
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%m/%d/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
                
        return None
    
    @staticmethod
    def parse_date(date_string: str) -> Optional[datetime]:
        """
        Parse date string, trying both relative and absolute formats.
        
        Args:
            date_string: Date string to parse
            
        Returns:
            datetime object or None if invalid
        """
        # Try relative date first
        relative_date = DateParser.parse_relative_date(date_string)
        if relative_date:
            return relative_date
            
        # Try absolute date
        return DateParser.parse_absolute_date(date_string)
    
    @staticmethod
    def parse_date_range(start_date: str, end_date: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Parse a date range.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            Tuple of (start_datetime, end_datetime)
        """
        start_dt = DateParser.parse_date(start_date) if start_date else None
        end_dt = DateParser.parse_date(end_date) if end_date else None
        
        return start_dt, end_dt
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in seconds to human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def format_timestamp(timestamp: Union[str, datetime]) -> str:
        """
        Format timestamp for display.
        
        Args:
            timestamp: Timestamp string or datetime object
            
        Returns:
            Formatted timestamp string
        """
        if isinstance(timestamp, str):
            dt = DateParser.parse_date(timestamp)
            if not dt:
                return timestamp
        else:
            dt = timestamp
            
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            return dt.strftime("%H:%M")
        elif diff.days == 1:
            return f"Yesterday {dt.strftime('%H:%M')}"
        elif diff.days < 7:
            return dt.strftime("%a %H:%M")
        else:
            return dt.strftime("%m/%d %H:%M")