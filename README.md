# WisprMCP

**A Python library for accessing Wispr Flow's SQLite database with CLI and MCP server support.**

WisprMCP provides programmatic access to your Wispr Flow local database, enabling you to query transcripts, search conversations, analyze usage patterns, and integrate with AI workflows through the Model Context Protocol (MCP).

## Recent Updates

- **2025-07-04**: Added collect command for word extraction by day (similar to GranolaMCP)
- **2025-07-04**: Added sane defaults - `wispr list` now defaults to last 2 days
- **2025-07-04**: Fixed timestamp parsing for proper date filtering and time display
- **2025-07-04**: Initial release with full database access, CLI tools, and MCP server
- Zero external dependencies - built entirely with Python standard library
- Comprehensive search and filtering capabilities
- Rich CLI with colored output and multiple formats
- JSON-RPC 2.0 compliant MCP server for AI integration

## Complete Feature Overview

### 📚 **Library Access**
- Direct SQLite database access to Wispr Flow transcripts
- Rich data models for transcripts, conversations, and metadata
- Comprehensive search and filtering capabilities
- Zero external dependencies - pure Python standard library

### 🖥️ **Command Line Interface (7 Commands)**

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `list` | List recent transcripts | Defaults to 2 days, rich table output, filtering |
| `show` | Show specific transcript | Full details, context, all text versions |
| `search` | Search transcript text | Highlighting, context, date filtering |
| `stats` | Database statistics | Overall stats, app breakdown, quality metrics |
| `apps` | App usage analysis | Usage by app, sorting, filtering |
| `export` | Export data | JSON/CSV/Markdown, conversation grouping |
| `collect` | **Extract YOUR words** | **Daily files (YYYY-MM-DD.txt) for analysis** |

**Output Features:**
- Rich colored output with semantic highlighting
- Multiple formats: table, JSON, text, markdown
- Advanced filtering: date, app, status, conversation, word count
- Sane defaults: `wispr list` shows last 2 days automatically

### 🗣️ **Word Collection (Like GranolaMCP)**
- **Extract YOUR spoken words** into daily text files
- **4 output formats**: `raw` (pure text), `words`, `sentences`, `entries`
- **Smart filtering**: Exclude apps, minimum word counts, date ranges
- **Ready for analysis**: Word clouds, linguistic analysis, voice training
- **Example**: `wispr collect ./my-words` → creates `2025-07-04.txt` with YOUR words

### 🤖 **MCP Server Integration (10 Tools)**

| Tool | Purpose |
|------|---------|
| `get_recent_transcripts` | Get most recent entries |
| `list_transcripts` | List with date/app filters |
| `search_transcripts` | Search for specific text |
| `get_transcript` | Get specific transcript by ID |
| `get_conversations` | Get grouped conversations |
| `get_conversation` | Get specific conversation |
| `get_app_statistics` | App usage statistics |
| `get_database_statistics` | Overall database stats |
| `export_transcripts` | Export data in various formats |
| `get_dictionary_entries` | Custom dictionary entries |

**MCP Features:**
- JSON-RPC 2.0 STDIO compliant for Claude Desktop
- Real-time database access for AI workflows
- Conversation grouping and analysis
- Usage statistics and patterns

## Installation

### Quick Install

```bash
# Clone and install
git clone https://github.com/pedram/WisprMCP.git
cd WisprMCP
pip install -e .

# Verify installation
wispr --help
```

### Development Install

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black wispr_mcp/
```

## Configuration

WisprMCP automatically detects your Wispr Flow database. You can also configure custom paths:

### Environment Variables

```bash
# Custom database path
export WISPR_DATABASE_PATH="/path/to/custom/flow.sqlite"

# Custom backup directory
export WISPR_BACKUP_DIR="/path/to/backups"
```

### Configuration File

Create `~/.wispr_mcp/.env`:

```bash
WISPR_DATABASE_PATH=/custom/path/flow.sqlite
WISPR_BACKUP_DIR=/custom/backups
```

## CLI Usage

### List Recent Transcripts

```bash
# List recent transcripts (defaults to last 2 days)
wispr list

# List from specific app
wispr list --app Slack

# List from last 3 days
wispr list --since 3d

# List with custom limit
wispr list --limit 50

# JSON output
wispr list --format json
```

### Search Transcripts

```bash
# Search for text
wispr search "hello world"

# Search in specific app
wispr search "meeting" --app Slack

# Search with date range
wispr search "project" --since 1w --until 2d

# Highlight matches
wispr search "important" --highlight

# Show context around matches
wispr search "error" --context 50
```

### Show Specific Transcript

```bash
# Show by full ID
wispr show abc123-def456-789...

# Show by partial ID (first 8 characters)
wispr show abc123de

# Show with additional context
wispr show abc123de --show-context

# Show all text versions (ASR, formatted, edited)
wispr show abc123de --show-all-versions
```

### Database Statistics

```bash
# Overall statistics
wispr stats

# Detailed statistics
wispr stats --detailed

# Statistics for specific period
wispr stats --since 1m

# Statistics for specific app
wispr stats --app Obsidian
```

### App Usage Analysis

```bash
# Top apps by usage
wispr apps

# Sort by different metrics
wispr apps --sort words
wispr apps --sort duration
wispr apps --sort last_used

# Filter by minimum entries
wispr apps --min-entries 10
```

### Export Data

```bash
# Export to JSON
wispr export --format json > transcripts.json

# Export to CSV
wispr export --format csv > transcripts.csv

# Export to Markdown
wispr export --format markdown > transcripts.md

# Export with filters
wispr export --since 1w --app Slack --format json

# Group by conversations
wispr export --group-by-conversation --format json
```

### Collect YOUR Spoken Words by Day

Extract YOUR spoken words into daily text files (YYYY-MM-DD.txt) for word cloud generation, linguistic analysis, or voice training data.

```bash
# Collect YOUR raw spoken words only (default: 7 days, no headers/metadata)
wispr collect ./my-words

# Collect YOUR words from last month
wispr collect ./words --since 1m

# Raw format: YOUR words with punctuation cleaned (default)
wispr collect ./clean --format raw --since 2w

# Sentence format: YOUR words as complete sentences (with headers)
wispr collect ./sentences --format sentences --since 2w

# Entries format: YOUR words with metadata (timestamps, apps)
wispr collect ./detailed --format entries --since 3d

# Exclude certain apps from YOUR word collection
wispr collect ./clean --exclude-apps "Wispr Flow" "ChatGPT"

# Only include longer spoken entries
wispr collect ./quality --exclude-short --min-words 10

# Example output files:
# ./my-words/2025-07-04.txt  - Contains only YOUR spoken words from July 4th
# ./my-words/2025-07-03.txt  - Contains only YOUR spoken words from July 3rd
```

**Output formats:**
- `raw` (default): Pure text, YOUR words only, ready for word cloud tools
- `words`: YOUR words with statistics headers
- `sentences`: YOUR complete sentences with metadata
- `entries`: YOUR words with timestamps and app context

## MCP Server Integration

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "WisprMCP": {
      "command": "python",
      "args": ["/path/to/WisprMCP/wispr_mcp/mcp/server.py"],
      "cwd": "/path/to/WisprMCP"
    }
  }
}
```

### Available MCP Tools

1. **get_recent_transcripts** - Get most recent transcripts
2. **list_transcripts** - List with date/app filters
3. **search_transcripts** - Search for specific text
4. **get_transcript** - Get specific transcript by ID
5. **get_conversations** - Get grouped conversations
6. **get_conversation** - Get specific conversation
7. **get_app_statistics** - App usage statistics
8. **get_database_statistics** - Overall database stats
9. **export_transcripts** - Export data in various formats
10. **get_dictionary_entries** - Custom dictionary entries

### Example MCP Usage in Claude

```
"Show me my Slack conversations from the last week"
→ Uses list_transcripts with app=Slack and since=1w

"Search for mentions of 'project deadline' in my transcripts"
→ Uses search_transcripts with query="project deadline"

"What are my most used apps for voice transcription?"
→ Uses get_app_statistics sorted by usage

"Export my Obsidian transcripts from last month to JSON"
→ Uses export_transcripts with filters
```

## Library Usage

### Basic Usage

```python
from wispr_mcp import WisprParser, TranscriptEntry, Conversation

# Initialize parser
parser = WisprParser()

# Get recent transcripts
entries = parser.get_entries(limit=10)

# Search for text
transcript = parser.search_text("hello world")

# Get conversations
conversations = parser.get_conversations(limit=5)

# Get statistics
stats = parser.get_statistics()
```

### Advanced Filtering

```python
from datetime import datetime, timedelta
from wispr_mcp.utils.date_parser import DateParser

# Date range filtering
start_date = DateParser.parse_date("1w")  # 1 week ago
end_date = datetime.now()

entries = parser.get_entries(
    start_date=start_date,
    end_date=end_date,
    app="com.tinyspeck.slackmacgap",  # Slack
    status="formatted",
    limit=100
)

# Process entries
for entry in entries:
    print(f"{entry.app_name}: {entry.display_text}")
    print(f"Quality: {entry.quality_score}")
    print(f"Duration: {entry.duration}s")
```

### Working with Conversations

```python
# Get conversations
conversations = parser.get_conversations(limit=10)

for conv in conversations:
    print(f"Conversation: {conv.conversation_id}")
    print(f"App: {conv.app_name}")
    print(f"Duration: {conv.duration}s")
    print(f"Entries: {conv.entry_count}")
    print(f"Summary: {conv.summary}")

    # Export to markdown
    markdown = conv.to_markdown()
    with open(f"conversation_{conv.conversation_id[:8]}.md", "w") as f:
        f.write(markdown)
```

## Database Schema

WisprMCP works with Wispr Flow's SQLite database schema:

### Main Tables

- **History**: Primary transcript entries with ASR, formatted, and edited text
- **Dictionary**: Custom vocabulary entries for speech recognition
- **RemoteNotifications**: Push notifications (typically empty)
- **Notes**: User notes (typically empty)

### Key Fields

- `transcriptEntityId`: Unique transcript identifier
- `asrText`: Raw speech recognition output
- `formattedText`: AI-formatted text
- `editedText`: User-edited text
- `timestamp`: Creation timestamp
- `app`: Application bundle ID
- `duration`: Recording duration in seconds
- `numWords`: Word count
- `conversationId`: Conversation grouping
- `additionalContext`: JSON context data

## Data Privacy and Security

- **Local Access Only**: WisprMCP only accesses your local Wispr Flow database
- **YOUR Words Only**: The `collect` command extracts only YOUR spoken words (transcripts)
- **No File Access**: Does NOT access your Obsidian vault, documents, or personal files
- **No Network Requests**: Zero external dependencies, no data transmission
- **Read-Only Access**: Database is accessed in read-only mode
- **App Context Only**: When you see "Obsidian" it means you were speaking into that app
- **Respect User Privacy**: All processing happens locally on your machine

**What WisprMCP sees:**
- ✅ YOUR voice transcripts from Wispr Flow
- ✅ Which app you were speaking into (e.g., "Obsidian", "Slack")
- ✅ When you spoke and for how long

**What WisprMCP does NOT see:**
- ❌ Your actual Obsidian notes or vault content
- ❌ Your documents, files, or personal data
- ❌ Anything outside the Wispr Flow database

## Architecture

### Project Structure

```
wispr_mcp/
├── core/                      # Core business logic
│   ├── parser.py             # Database access and parsing
│   ├── transcript.py         # Transcript data models
│   └── conversation.py       # Conversation data models
├── utils/                     # Utility functions
│   ├── config.py             # Configuration management
│   └── date_parser.py        # Date parsing utilities
├── cli/                       # Command-line interface
│   ├── main.py               # CLI entry point
│   ├── commands/             # CLI command implementations
│   └── formatters/           # Output formatting
└── mcp/                      # MCP server implementation
    ├── server.py             # JSON-RPC 2.0 server
    └── tools.py              # MCP tool definitions
```

### Design Principles

- **Zero Dependencies**: Pure Python standard library implementation
- **Live Data Access**: Always reads from current database state
- **Graceful Error Handling**: Robust error handling throughout
- **Flexible Filtering**: Comprehensive search and filter options
- **Multiple Interfaces**: Library, CLI, and MCP server from single codebase

## Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/pedram/WisprMCP.git
cd WisprMCP

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black wispr_mcp/
flake8 wispr_mcp/

# Type checking
mypy wispr_mcp/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wispr_mcp

# Run specific test file
pytest tests/test_parser.py
```

## Troubleshooting

### Database Not Found

```bash
# Check if Wispr Flow is installed
ls ~/Library/Application\ Support/Wispr\ Flow/

# Set custom database path
export WISPR_DATABASE_PATH="/path/to/flow.sqlite"

# Verify database access
wispr stats
```

### Permission Issues

```bash
# Check database permissions
ls -la ~/Library/Application\ Support/Wispr\ Flow/flow.sqlite

# Ensure Wispr Flow isn't running exclusively
pkill "Wispr Flow"
```

### CLI Output Issues

```bash
# Disable colors if terminal doesn't support them
export NO_COLOR=1
wispr list

# Force colors
export FORCE_COLOR=1
wispr list --no-color
```

### MCP Server Issues

```bash
# Test MCP server directly
python wispr_mcp/mcp/server.py --debug

# Check Claude Desktop logs
# macOS: ~/Library/Logs/Claude/
# Look for WisprMCP related errors
```

## Performance

- **Database Size**: Handles databases with 100,000+ entries efficiently
- **Memory Usage**: Minimal memory footprint with lazy loading
- **Query Speed**: Optimized queries with strategic indexing
- **CLI Responsiveness**: Fast command execution with pagination

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0 (2025-07-04)
- **NEW**: Added `collect` command for extracting words by day (YYYY-MM-DD.txt files)
- **NEW**: Sane defaults - `wispr list` now defaults to last 2 days instead of all entries
- **IMPROVEMENT**: Fixed timestamp parsing for proper date filtering and display
- **IMPROVEMENT**: Enhanced CLI help with better examples and date format info
- Initial release with core library, complete CLI (7 commands), and MCP server (10 tools)
- Zero external dependencies implementation
- Comprehensive documentation and examples

## Related Projects

- **Wispr Flow**: AI-powered voice transcription app
- **Claude Desktop**: AI assistant with MCP support
- **Model Context Protocol**: Standard for AI tool integration

## Support

- **Issues**: [GitHub Issues](https://github.com/pedram/WisprMCP/issues)
- **Documentation**: This README and inline code documentation
- **Examples**: See `examples/` directory for usage samples

## Quick Reference

### Most Common Commands
```bash
# List recent transcripts (last 2 days)
wispr list

# Collect YOUR spoken words for analysis
wispr collect ./my-words

# Search YOUR transcripts
wispr search "project"

# Show database stats
wispr stats

# Get app usage breakdown
wispr apps
```

### Word Collection (Key Feature)
```bash
# Extract YOUR raw spoken words by day → ./my-words/2025-07-04.txt
wispr collect ./my-words                    # Last 7 days, raw format
wispr collect ./words --since 1m            # Last month
wispr collect ./clean --exclude-apps "ChatGPT"  # Exclude certain apps
```

### MCP Integration
Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "WisprMCP": {
      "command": "python",
      "args": ["/path/to/WisprMCP/mcp_server.py"],
      "cwd": "/path/to/WisprMCP"
    }
  }
}
```