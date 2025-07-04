"""
Entry point for running wispr_mcp as a module.
"""

import sys
from .cli.main import main

if __name__ == "__main__":
    sys.exit(main())