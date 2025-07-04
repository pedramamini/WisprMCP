"""
MCP tools for WisprMCP server.
"""

from typing import Dict, Any, List, Optional
import json

from ..core.parser import WisprParser
from ..utils.date_parser import DateParser


class WisprTools:
    """MCP tools for Wispr Flow database access."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.parser = WisprParser(db_path)
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get the schema for all available tools."""
        return [
            {
                "name": "get_recent_transcripts",
                "description": "Get the most recent transcript entries regardless of date",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of transcripts to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "app": {
                            "type": "string",
                            "description": "Filter by app (bundle ID or name like 'Slack', 'Obsidian')"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status (formatted, empty, no_audio, etc.)"
                        },
                        "include_archived": {
                            "type": "boolean",
                            "description": "Include archived entries",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "list_transcripts",
                "description": "List transcript entries with date and app filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "since": {
                            "type": "string",
                            "description": "Show entries since this date/time (e.g. '3d', '1w', '2024-01-01')"
                        },
                        "until": {
                            "type": "string",
                            "description": "Show entries until this date/time"
                        },
                        "app": {
                            "type": "string",
                            "description": "Filter by app (bundle ID or name)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of entries",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "include_archived": {
                            "type": "boolean",
                            "description": "Include archived entries",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "search_transcripts",
                "description": "Search transcript entries for specific text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Text to search for"
                        },
                        "since": {
                            "type": "string",
                            "description": "Search entries since this date/time"
                        },
                        "until": {
                            "type": "string",
                            "description": "Search entries until this date/time"
                        },
                        "app": {
                            "type": "string",
                            "description": "Filter by app"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_transcript",
                "description": "Get a specific transcript entry by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "transcript_id": {
                            "type": "string",
                            "description": "Transcript ID (full UUID or first 8 characters)"
                        },
                        "include_context": {
                            "type": "boolean",
                            "description": "Include additional context information",
                            "default": False
                        }
                    },
                    "required": ["transcript_id"]
                }
            },
            {
                "name": "get_conversations",
                "description": "Get conversations (grouped transcript entries)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "since": {
                            "type": "string",
                            "description": "Show conversations since this date/time"
                        },
                        "until": {
                            "type": "string",
                            "description": "Show conversations until this date/time"
                        },
                        "app": {
                            "type": "string",
                            "description": "Filter by app"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of conversations",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    }
                }
            },
            {
                "name": "get_conversation",
                "description": "Get a specific conversation by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {
                            "type": "string",
                            "description": "Conversation ID"
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format (json or markdown)",
                            "enum": ["json", "markdown"],
                            "default": "json"
                        }
                    },
                    "required": ["conversation_id"]
                }
            },
            {
                "name": "get_app_statistics",
                "description": "Get usage statistics for apps",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of apps to return",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Sort apps by field",
                            "enum": ["entries", "words", "duration", "latency", "last_used"],
                            "default": "entries"
                        },
                        "min_entries": {
                            "type": "integer",
                            "description": "Minimum number of entries to include app",
                            "default": 1,
                            "minimum": 1
                        }
                    }
                }
            },
            {
                "name": "get_database_statistics",
                "description": "Get overall database statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "since": {
                            "type": "string",
                            "description": "Calculate stats since this date/time"
                        },
                        "until": {
                            "type": "string",
                            "description": "Calculate stats until this date/time"
                        },
                        "app": {
                            "type": "string",
                            "description": "Filter by app"
                        }
                    }
                }
            },
            {
                "name": "export_transcripts",
                "description": "Export transcript data in various formats",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "Export format",
                            "enum": ["json", "csv", "markdown", "text"],
                            "default": "json"
                        },
                        "since": {
                            "type": "string",
                            "description": "Export entries since this date/time"
                        },
                        "until": {
                            "type": "string",
                            "description": "Export entries until this date/time"
                        },
                        "app": {
                            "type": "string",
                            "description": "Filter by app"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of entries to export",
                            "minimum": 1,
                            "maximum": 1000
                        },
                        "group_by_conversation": {
                            "type": "boolean",
                            "description": "Group entries by conversation",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "get_dictionary_entries",
                "description": "Get custom dictionary entries used for speech recognition corrections",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        try:
            if tool_name == "get_recent_transcripts":
                return self._get_recent_transcripts(**arguments)
            elif tool_name == "list_transcripts":
                return self._list_transcripts(**arguments)
            elif tool_name == "search_transcripts":
                return self._search_transcripts(**arguments)
            elif tool_name == "get_transcript":
                return self._get_transcript(**arguments)
            elif tool_name == "get_conversations":
                return self._get_conversations(**arguments)
            elif tool_name == "get_conversation":
                return self._get_conversation(**arguments)
            elif tool_name == "get_app_statistics":
                return self._get_app_statistics(**arguments)
            elif tool_name == "get_database_statistics":
                return self._get_database_statistics(**arguments)
            elif tool_name == "export_transcripts":
                return self._export_transcripts(**arguments)
            elif tool_name == "get_dictionary_entries":
                return self._get_dictionary_entries(**arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def _resolve_app_filter(self, app: Optional[str]) -> Optional[str]:
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
    
    def _get_recent_transcripts(self, limit: int = 10, app: Optional[str] = None, 
                              status: Optional[str] = None, include_archived: bool = False) -> Dict[str, Any]:
        """Get recent transcripts."""
        app_filter = self._resolve_app_filter(app)
        
        entries = self.parser.get_entries(
            limit=limit,
            app=app_filter,
            status=status,
            include_archived=include_archived
        )
        
        return {
            "transcripts": [entry.to_dict() for entry in entries],
            "count": len(entries)
        }
    
    def _list_transcripts(self, since: Optional[str] = None, until: Optional[str] = None,
                         app: Optional[str] = None, status: Optional[str] = None,
                         limit: int = 20, include_archived: bool = False) -> Dict[str, Any]:
        """List transcripts with filters."""
        start_date = DateParser.parse_date(since) if since else None
        end_date = DateParser.parse_date(until) if until else None
        app_filter = self._resolve_app_filter(app)
        
        if since and not start_date:
            return {"error": f"Invalid date format: {since}"}
        if until and not end_date:
            return {"error": f"Invalid date format: {until}"}
        
        entries = self.parser.get_entries(
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            app=app_filter,
            status=status,
            include_archived=include_archived
        )
        
        return {
            "transcripts": [entry.to_dict() for entry in entries],
            "count": len(entries),
            "filters": {
                "since": since,
                "until": until,
                "app": app,
                "status": status
            }
        }
    
    def _search_transcripts(self, query: str, since: Optional[str] = None,
                           until: Optional[str] = None, app: Optional[str] = None,
                           limit: int = 50) -> Dict[str, Any]:
        """Search transcripts."""
        start_date = DateParser.parse_date(since) if since else None
        end_date = DateParser.parse_date(until) if until else None
        app_filter = self._resolve_app_filter(app)
        
        if since and not start_date:
            return {"error": f"Invalid date format: {since}"}
        if until and not end_date:
            return {"error": f"Invalid date format: {until}"}
        
        transcript = self.parser.search_text(
            query,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            app=app_filter
        )
        
        return {
            "transcripts": [entry.to_dict() for entry in transcript.entries],
            "count": len(transcript.entries),
            "query": query,
            "total_duration": transcript.total_duration,
            "total_words": transcript.total_words
        }
    
    def _get_transcript(self, transcript_id: str, include_context: bool = False) -> Dict[str, Any]:
        """Get specific transcript."""
        entry = self.parser.get_entry_by_id(transcript_id)
        
        if not entry:
            # Try partial ID search
            entries = self.parser.get_entries(limit=1000)
            matches = [e for e in entries if e.transcript_id.startswith(transcript_id)]
            
            if len(matches) == 1:
                entry = matches[0]
            elif len(matches) > 1:
                return {
                    "error": f"Multiple matches found for '{transcript_id}'",
                    "matches": [{"id": m.transcript_id, "app": m.app_name, "text": m.display_text[:50]} for m in matches[:10]]
                }
            else:
                return {"error": f"Transcript not found: {transcript_id}"}
        
        result = entry.to_dict()
        if include_context and entry.additional_context:
            result["additional_context"] = entry.additional_context
        
        return result
    
    def _get_conversations(self, since: Optional[str] = None, until: Optional[str] = None,
                          app: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Get conversations."""
        start_date = DateParser.parse_date(since) if since else None
        end_date = DateParser.parse_date(until) if until else None
        app_filter = self._resolve_app_filter(app)
        
        if since and not start_date:
            return {"error": f"Invalid date format: {since}"}
        if until and not end_date:
            return {"error": f"Invalid date format: {until}"}
        
        conversations = self.parser.get_conversations(
            limit=limit * 10,  # Get more entries to group into conversations
            start_date=start_date,
            end_date=end_date,
            app=app_filter
        )
        
        # Limit conversations
        conversations = conversations[:limit]
        
        return {
            "conversations": [conv.to_dict() for conv in conversations],
            "count": len(conversations)
        }
    
    def _get_conversation(self, conversation_id: str, format: str = "json") -> Dict[str, Any]:
        """Get specific conversation."""
        conversation = self.parser.get_conversation_by_id(conversation_id)
        
        if not conversation:
            return {"error": f"Conversation not found: {conversation_id}"}
        
        if format == "markdown":
            return {"conversation": conversation.to_markdown()}
        else:
            return conversation.to_dict()
    
    def _get_app_statistics(self, limit: int = 20, sort_by: str = "entries",
                           min_entries: int = 1) -> Dict[str, Any]:
        """Get app statistics."""
        apps = self.parser.get_apps()
        
        # Filter by minimum entries
        apps = [app for app in apps if app["total_entries"] >= min_entries]
        
        # Sort apps
        sort_key_map = {
            "entries": "total_entries",
            "words": "total_words",
            "duration": "total_duration",
            "latency": "avg_latency",
            "last_used": "last_used"
        }
        
        sort_key = sort_key_map.get(sort_by, "total_entries")
        apps.sort(key=lambda x: x[sort_key] or 0, reverse=True)
        
        # Limit results
        apps = apps[:limit]
        
        return {
            "apps": apps,
            "count": len(apps),
            "sort_by": sort_by
        }
    
    def _get_database_statistics(self, since: Optional[str] = None,
                               until: Optional[str] = None, app: Optional[str] = None) -> Dict[str, Any]:
        """Get database statistics."""
        start_date = DateParser.parse_date(since) if since else None
        end_date = DateParser.parse_date(until) if until else None
        app_filter = self._resolve_app_filter(app)
        
        if since and not start_date:
            return {"error": f"Invalid date format: {since}"}
        if until and not end_date:
            return {"error": f"Invalid date format: {until}"}
        
        if start_date or end_date or app_filter:
            # Get filtered statistics
            entries = self.parser.get_entries(
                start_date=start_date,
                end_date=end_date,
                app=app_filter,
                include_archived=True
            )
            
            total_entries = len(entries)
            active_entries = len([e for e in entries if not e.is_archived])
            
            total_duration = sum(e.duration or 0 for e in entries)
            total_words = sum(e.num_words or 0 for e in entries)
            
            valid_entries = [e for e in entries if e.duration is not None and e.num_words is not None]
            avg_duration = sum(e.duration for e in valid_entries) / len(valid_entries) if valid_entries else 0
            avg_words = sum(e.num_words for e in valid_entries) / len(valid_entries) if valid_entries else 0
            
            status_breakdown = {}
            for entry in entries:
                status = entry.status or "unknown"
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "archived_entries": total_entries - active_entries,
                "total_duration": total_duration,
                "total_words": total_words,
                "avg_duration": avg_duration,
                "avg_words": avg_words,
                "status_breakdown": status_breakdown,
                "filtered": True
            }
        else:
            # Get overall statistics
            return self.parser.get_statistics()
    
    def _export_transcripts(self, format: str = "json", since: Optional[str] = None,
                           until: Optional[str] = None, app: Optional[str] = None,
                           limit: Optional[int] = None, group_by_conversation: bool = False) -> Dict[str, Any]:
        """Export transcripts."""
        start_date = DateParser.parse_date(since) if since else None
        end_date = DateParser.parse_date(until) if until else None
        app_filter = self._resolve_app_filter(app)
        
        if since and not start_date:
            return {"error": f"Invalid date format: {since}"}
        if until and not end_date:
            return {"error": f"Invalid date format: {until}"}
        
        if group_by_conversation:
            conversations = self.parser.get_conversations(
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                app=app_filter
            )
            data = [conv.to_dict() for conv in conversations]
        else:
            entries = self.parser.get_entries(
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                app=app_filter
            )
            data = [entry.to_dict() for entry in entries]
        
        if format == "json":
            export_data = {
                "format": "wispr_mcp_export",
                "version": "1.0",
                "count": len(data),
                "grouped_by_conversation": group_by_conversation,
                "data": data
            }
            return {"export": json.dumps(export_data, indent=2, default=str)}
        else:
            return {"error": f"Format '{format}' not supported in MCP mode. Use 'json' format."}
    
    def _get_dictionary_entries(self) -> Dict[str, Any]:
        """Get dictionary entries."""
        entries = self.parser.get_dictionary_entries()
        
        return {
            "dictionary_entries": entries,
            "count": len(entries)
        }