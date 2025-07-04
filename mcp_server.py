#!/usr/bin/env python3
"""
Standalone MCP server script for WisprMCP.
"""

import sys
import asyncio
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from wispr_mcp.mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())