# Claude Development Guide for WisprMCP

This document provides guidance for Claude Code when working with the WisprMCP project.

## Project Overview

WisprMCP is a Python library that provides access to Wispr Flow's SQLite database. It includes:

1. **Core Library** (`wispr_mcp/core/`): Database access and data models
2. **CLI Tools** (`wispr_mcp/cli/`): Command-line interface with 6 commands
3. **MCP Server** (`wispr_mcp/mcp/`): JSON-RPC 2.0 server for AI integration
4. **Utilities** (`wispr_mcp/utils/`): Configuration and date parsing

## Development Practices

### Code Style
- Follow PEP 8 style guidelines
- Use type hints where possible
- Keep functions focused and well-documented
- Zero external dependencies policy

### Testing
- Run tests with: `pytest`
- Test coverage with: `pytest --cov=wispr_mcp`
- Test specific files: `pytest tests/test_parser.py`

### Formatting
- Format code with: `black wispr_mcp/`
- Check style with: `flake8 wispr_mcp/`
- Type checking with: `mypy wispr_mcp/`

## Common Commands

### Installation
```bash
pip install -e .                    # Install in development mode
pip install -e ".[dev]"             # Install with dev dependencies
```

### CLI Testing
```bash
wispr list                          # List recent transcripts
wispr search "test"                 # Search functionality
wispr stats                         # Database statistics
wispr --help                        # Show help
```

### MCP Server Testing
```bash
python wispr_mcp/mcp/server.py --debug    # Run MCP server in debug mode
```

## Architecture Notes

### Database Access
- Uses SQLite3 from Python standard library
- Read-only access to Wispr Flow database
- Context manager pattern for connection handling
- Graceful error handling for missing/corrupted data

### Data Models
- `TranscriptEntry`: Individual transcript with metadata
- `Conversation`: Grouped transcript entries
- `Transcript`: Collection of entries with statistics

### CLI Design
- Argparse-based command structure
- Colored output with ANSI escape codes
- Multiple output formats (table, JSON, text, markdown)
- Consistent error handling and user feedback

### MCP Integration
- JSON-RPC 2.0 compliant server
- 10 comprehensive tools for AI integration
- Async/await pattern for server handling
- Proper error responses and tool schemas

## File Structure

```
wispr_mcp/
├── __init__.py                 # Package exports
├── __main__.py                 # Module execution entry
├── core/
│   ├── parser.py              # Main database access
│   ├── transcript.py          # Transcript data models
│   └── conversation.py        # Conversation data models
├── utils/
│   ├── config.py              # Configuration management
│   └── date_parser.py         # Date parsing utilities
├── cli/
│   ├── main.py                # CLI entry point
│   ├── commands/              # Individual commands
│   └── formatters/            # Output formatting
└── mcp/
    ├── server.py              # MCP JSON-RPC server
    └── tools.py               # MCP tool implementations
```

## Database Schema Reference

The Wispr Flow database contains:

- **History table**: Main transcript entries
- **Dictionary table**: Custom vocabulary
- **RemoteNotifications**: Push notifications (usually empty)
- **Notes**: User notes (usually empty)

Key fields in History table:
- `transcriptEntityId`: Unique identifier
- `asrText`, `formattedText`, `editedText`: Text versions
- `timestamp`: Creation time
- `app`: Application bundle ID
- `conversationId`: Conversation grouping
- `duration`, `numWords`: Metrics
- `additionalContext`: JSON context data

## Common Issues and Solutions

### Database Not Found
- Check Wispr Flow installation
- Verify database path in config
- Ensure proper permissions

### Permission Errors
- Make sure Wispr Flow isn't exclusively locking database
- Check file permissions
- Try running with appropriate user permissions

### CLI Output Issues
- Use `--no-color` flag for terminals without color support
- Set `NO_COLOR` environment variable to disable colors
- Use `FORCE_COLOR` to force color output

### MCP Server Issues
- Run with `--debug` flag for detailed error messages
- Check Claude Desktop configuration
- Verify JSON-RPC message format

## When Making Changes

1. **Core Library Changes**: Update data models and parser logic carefully
2. **CLI Changes**: Maintain consistent command patterns and help text
3. **MCP Changes**: Ensure tool schemas match implementation
4. **Documentation**: Update README.md for user-facing changes

## Key Design Principles

1. **Zero Dependencies**: Use only Python standard library
2. **Read-Only Access**: Never modify the Wispr Flow database
3. **Graceful Degradation**: Handle missing/malformed data gracefully
4. **Multiple Interfaces**: Support library, CLI, and MCP equally well
5. **Privacy First**: All processing happens locally, no network requests

## Development Workflow

1. Make changes to code
2. Run tests: `pytest`
3. Format code: `black wispr_mcp/`
4. Check style: `flake8 wispr_mcp/`
5. Test CLI: `wispr --help`
6. Test MCP: Run server and verify tools
7. Update documentation if needed
8. Commit changes

## Performance Considerations

- Use LIMIT in database queries for large datasets
- Implement lazy loading where possible
- Cache configuration but not data (always read live)
- Use context managers for database connections
- Optimize CLI output for terminal display