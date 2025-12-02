"""
Model Context Protocol (MCP) Server for AI Photography Coach

Exposes photography coaching agents as standardized MCP tools for:
- Claude Desktop integration
- VS Code extensions
- Other MCP-compatible clients

Tools Provided:
1. analyze_photo - Technical analysis and composition assessment
2. coach_on_photo - Personalized coaching with conversation history
3. get_session_history - Retrieve past coaching sessions

Usage:
    python -m agents_capstone.tools.mcp_server

Integration with Claude Desktop:
    Add to ~/Library/Application Support/Claude/claude_desktop_config.json:
    {
      "mcpServers": {
        "photography-coach": {
          "command": "python",
          "args": ["-m", "agents_capstone.tools.mcp_server"]
        }
      }
    }
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional
from dataclasses import asdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from agents_capstone.agents.vision_agent import VisionAgent, VisionAnalysis
from agents_capstone.agents.knowledge_agent import KnowledgeAgent
from agents_capstone.agents.orchestrator import Orchestrator


class MCPServer:
    """MCP Server implementation for Photography Coach agents."""
    
    def __init__(self):
        """Initialize agents and session storage."""
        self.vision_agent = VisionAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.orchestrator = Orchestrator(self.vision_agent, self.knowledge_agent)
        
        # In-memory session storage (could be replaced with persistent storage)
        self.sessions: Dict[str, Dict] = {}
    
    def _get_session(self, user_id: str) -> Dict:
        """Get or create a session for a user."""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "user_id": user_id,
                "skill_level": "intermediate",
                "history": []
            }
        return self.sessions[user_id]
    
    async def handle_analyze_photo(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool: analyze_photo
        
        Analyze a photo's technical settings and composition.
        
        Args:
            image_path (str): Path to the image file
            skill_level (str, optional): User's skill level (beginner/intermediate/advanced)
        
        Returns:
            Dict with:
                - exif: Camera settings and metadata
                - composition_summary: Natural language analysis
                - detected_issues: List of issues with severity and suggestions
                - strengths: Positive aspects of the photo
        """
        image_path = arguments.get("image_path")
        skill_level = arguments.get("skill_level", "intermediate")
        
        if not image_path:
            return {
                "error": "image_path is required",
                "content": [{"type": "text", "text": "Error: No image path provided"}]
            }
        
        if not os.path.exists(image_path):
            return {
                "error": f"Image not found: {image_path}",
                "content": [{"type": "text", "text": f"Error: Image file not found at {image_path}"}]
            }
        
        try:
            # Analyze the photo
            result = self.vision_agent.analyze(image_path, skill_level)
            
            # Format response for MCP
            issues_formatted = []
            for issue in result.detected_issues:
                issues_formatted.append({
                    "type": issue.type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "suggestion": issue.suggestion
                })
            
            response_text = f"""# Photo Analysis Results

## Composition Summary
{result.composition_summary}

## Technical Settings (EXIF)
- Focal Length: {result.exif.get('FocalLength', 'N/A')}
- Aperture: f/{result.exif.get('FNumber', 'N/A')}
- ISO: {result.exif.get('ISO', 'N/A')}
- Shutter Speed: {result.exif.get('ShutterSpeed', 'N/A')}

## Detected Issues ({len(result.detected_issues)})
"""
            for i, issue in enumerate(result.detected_issues, 1):
                response_text += f"\n{i}. **[{issue.severity.upper()}] {issue.type}**\n"
                response_text += f"   - {issue.description}\n"
                response_text += f"   - 💡 {issue.suggestion}\n"
            
            if result.strengths:
                response_text += f"\n## Strengths ({len(result.strengths)})\n"
                for strength in result.strengths:
                    response_text += f"- ✅ {strength}\n"
            
            return {
                "content": [{"type": "text", "text": response_text}],
                "data": {
                    "exif": result.exif,
                    "composition_summary": result.composition_summary,
                    "detected_issues": issues_formatted,
                    "strengths": result.strengths
                }
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "content": [{"type": "text", "text": f"Error analyzing photo: {str(e)}"}]
            }
    
    async def handle_coach_on_photo(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool: coach_on_photo
        
        Get personalized coaching advice on a photo.
        
        Args:
            user_id (str): User identifier for session continuity
            image_path (str, optional): Path to image file (if analyzing new image)
            query (str): User's question or request for coaching
            skill_level (str, optional): User's skill level
        
        Returns:
            Dict with coaching response and session context
        """
        user_id = arguments.get("user_id", "default_user")
        image_path = arguments.get("image_path")
        query = arguments.get("query")
        skill_level = arguments.get("skill_level")
        
        if not query:
            return {
                "error": "query is required",
                "content": [{"type": "text", "text": "Error: Please provide a question or request"}]
            }
        
        try:
            # Get or create session
            session = self._get_session(user_id)
            
            if skill_level:
                session["skill_level"] = skill_level
            
            # Run orchestrator
            result = self.orchestrator.run(
                user_id=user_id,
                image_path=image_path,
                query=query
            )
            
            # Format response
            response_text = f"""# Coaching Response

{result['coach']['text']}
"""
            
            if result.get('vision'):
                response_text += f"\n## Photo Analysis\n{result['vision'].composition_summary}\n"
            
            return {
                "content": [{"type": "text", "text": response_text}],
                "data": {
                    "coach_response": result['coach']['text'],
                    "vision_analysis": result.get('vision'),
                    "session_history_count": len(session.get('history', []))
                }
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "content": [{"type": "text", "text": f"Error providing coaching: {str(e)}"}]
            }
    
    async def handle_get_session_history(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool: get_session_history
        
        Retrieve coaching session history for a user.
        
        Args:
            user_id (str): User identifier
        
        Returns:
            Dict with session history and statistics
        """
        user_id = arguments.get("user_id", "default_user")
        
        session = self._get_session(user_id)
        history = session.get("history", [])
        
        response_text = f"""# Session History for {user_id}

**Skill Level:** {session.get('skill_level', 'intermediate')}
**Total Interactions:** {len(history)}

## Recent Queries
"""
        
        for i, item in enumerate(history[-5:], 1):  # Show last 5
            response_text += f"\n{i}. {item.get('query', 'N/A')}\n"
            issues = item.get('issues', [])
            if issues:
                response_text += f"   Issues: {', '.join(issues)}\n"
        
        return {
            "content": [{"type": "text", "text": response_text}],
            "data": {
                "user_id": user_id,
                "skill_level": session.get('skill_level'),
                "total_interactions": len(history),
                "history": history
            }
        }
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers."""
        handlers = {
            "analyze_photo": self.handle_analyze_photo,
            "coach_on_photo": self.handle_coach_on_photo,
            "get_session_history": self.handle_get_session_history
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return {
                "error": f"Unknown tool: {tool_name}",
                "content": [{"type": "text", "text": f"Error: Tool '{tool_name}' not found"}]
            }
        
        return await handler(arguments)
    
    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Return list of available tools for MCP protocol."""
        return [
            {
                "name": "analyze_photo",
                "description": "Analyze a photo's technical settings and composition. Returns EXIF data, composition summary, detected issues with severity, and strengths.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Path to the image file to analyze"
                        },
                        "skill_level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced"],
                            "description": "User's photography skill level for adaptive analysis",
                            "default": "intermediate"
                        }
                    },
                    "required": ["image_path"]
                }
            },
            {
                "name": "coach_on_photo",
                "description": "Get personalized photography coaching advice. Maintains conversation history and provides contextual feedback.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for session continuity",
                            "default": "default_user"
                        },
                        "image_path": {
                            "type": "string",
                            "description": "Optional: Path to image file if analyzing a new photo"
                        },
                        "query": {
                            "type": "string",
                            "description": "User's question or request for coaching advice"
                        },
                        "skill_level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced"],
                            "description": "User's photography skill level"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_session_history",
                "description": "Retrieve coaching session history and statistics for a user.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User identifier",
                            "default": "default_user"
                        }
                    }
                }
            }
        ]
    
    async def run(self):
        """Run the MCP server on stdin/stdout."""
        print("AI Photography Coach MCP Server starting...", file=sys.stderr)
        print(f"Available tools: {', '.join(t['name'] for t in self.get_tools_list())}", file=sys.stderr)
        
        # MCP protocol: read JSON-RPC messages from stdin
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                request_id = request.get("id")
                
                # Handle different MCP methods
                if method == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": self.get_tools_list()
                        }
                    }
                
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    result = await self.handle_tool_call(tool_name, arguments)
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                
                elif method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": "ai-photography-coach",
                                "version": "1.0.0"
                            }
                        }
                    }
                
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
            
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                if 'request_id' in locals():
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }
                    print(json.dumps(error_response), flush=True)


def main():
    """Entry point for MCP server."""
    # Configure Gemini if API key available
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        print("✓ Gemini API configured", file=sys.stderr)
    else:
        print("⚠ Warning: GOOGLE_API_KEY not set, using fallback analysis", file=sys.stderr)
    
    server = MCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
