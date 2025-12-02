#!/bin/bash
# Launcher script for AI Photography Coach MCP Server
#
# Usage:
#   ./run_mcp_server.sh
#
# For Claude Desktop integration, add to:
#   ~/Library/Application Support/Claude/claude_desktop_config.json
#
# {
#   "mcpServers": {
#     "photography-coach": {
#       "command": "/path/to/ai-photography-coach-agents/run_mcp_server.sh"
#     }
#   }
# }

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Set GOOGLE_API_KEY if not already set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠ Warning: GOOGLE_API_KEY not set. Using fallback analysis." >&2
    echo "   Set it with: export GOOGLE_API_KEY='your-key-here'" >&2
fi

# Run MCP server
cd "$SCRIPT_DIR"
exec python3 -m agents_capstone.tools.mcp_server
