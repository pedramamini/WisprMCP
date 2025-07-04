"""
MCP server implementation for WisprMCP.
"""

import json
import sys
import asyncio
from typing import Dict, Any, List, Optional
import argparse

try:
    from .tools import WisprTools
except ImportError:
    # Handle running as standalone script
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from wispr_mcp.mcp.tools import WisprTools


class MCPServer:
    """JSON-RPC 2.0 STDIO server for MCP protocol."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.tools = WisprTools(db_path)
        self.request_id = 0
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming JSON-RPC request."""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            if method == "initialize":
                return self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return self._handle_tools_call(request_id, params)
            elif method == "ping":
                return self._handle_ping(request_id)
            else:
                return self._error_response(request_id, -32601, f"Method not found: {method}")
        
        except Exception as e:
            return self._error_response(request_id, -32603, f"Internal error: {str(e)}")
    
    def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {},
                    "logging": {}
                },
                "serverInfo": {
                    "name": "wispr-mcp",
                    "version": "0.1.0"
                }
            }
        }
    
    def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
        tools_schema = self.tools.get_tools_schema()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools_schema
            }
        }
    
    def _handle_tools_call(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return self._error_response(request_id, -32602, "Missing tool name")
        
        result = self.tools.execute_tool(tool_name, arguments)
        
        if "error" in result:
            return self._error_response(request_id, -32603, result["error"])
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str)
                    }
                ]
            }
        }
    
    def _handle_ping(self, request_id: Any) -> Dict[str, Any]:
        """Handle ping request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {}
        }
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    async def run(self) -> None:
        """Run the MCP server."""
        while True:
            try:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse JSON-RPC request
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    error_response = self._error_response(None, -32700, f"Parse error: {str(e)}")
                    print(json.dumps(error_response), flush=True)
                    continue
                
                # Handle request
                response = await self.handle_request(request)
                
                if response:
                    print(json.dumps(response), flush=True)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                error_response = self._error_response(None, -32603, f"Server error: {str(e)}")
                print(json.dumps(error_response), flush=True)


async def main():
    """Main entry point for MCP server."""
    parser = argparse.ArgumentParser(description="WisprMCP JSON-RPC server")
    parser.add_argument("--db-path", help="Path to Wispr Flow database")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    try:
        server = MCPServer(args.db_path)
        await server.run()
    except FileNotFoundError as e:
        error_msg = f"Database not found: {e}"
        if args.debug:
            import traceback
            error_msg += f"\n{traceback.format_exc()}"
        
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": error_msg
            }
        }
        print(json.dumps(error_response), flush=True)
        sys.exit(1)
    except Exception as e:
        error_msg = f"Server startup failed: {e}"
        if args.debug:
            import traceback
            error_msg += f"\n{traceback.format_exc()}"
        
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": error_msg
            }
        }
        print(json.dumps(error_response), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())