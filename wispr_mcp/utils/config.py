"""
Configuration management for WisprMCP.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Configuration manager for WisprMCP."""
    
    def __init__(self):
        self.config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables and .env file."""
        # Load from environment variables first
        self.config_data.update(dict(os.environ))
        
        # Try to load from .env file
        env_file_paths = [
            Path(".env"),
            Path.home() / ".wispr_mcp" / ".env",
            Path.home() / ".config" / "wispr_mcp" / ".env"
        ]
        
        for env_file in env_file_paths:
            if env_file.exists():
                self._load_env_file(env_file)
                break
    
    def _load_env_file(self, env_file: Path) -> None:
        """Load environment variables from a .env file."""
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Only set if not already in config (env vars take precedence)
                        if key.strip() not in self.config_data:
                            self.config_data[key.strip()] = value.strip().strip('"\'')
        except Exception as e:
            print(f"Warning: Could not load .env file {env_file}: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value."""
        return self.config_data.get(key, default)
    
    @property
    def wispr_database_path(self) -> Path:
        """Get the path to the Wispr Flow database."""
        db_path = self.get('WISPR_DATABASE_PATH')
        if db_path:
            return Path(db_path)
        
        # Default path on macOS
        default_path = Path.home() / "Library" / "Application Support" / "Wispr Flow" / "flow.sqlite"
        return default_path
    
    @property
    def wispr_backup_dir(self) -> Path:
        """Get the path to the Wispr Flow backup directory."""
        backup_dir = self.get('WISPR_BACKUP_DIR')
        if backup_dir:
            return Path(backup_dir)
        
        # Default backup directory
        return self.wispr_database_path.parent / "backups"


# Global config instance
config = Config()