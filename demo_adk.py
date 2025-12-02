"""
ADK Deployment Demo - Google Vertex AI Agent Engine

This script demonstrates how the photography coach agents are packaged
as ADK (Agent Development Kit) tools for production deployment on 
Google Cloud's Vertex AI Agent Engine.

Usage:
    python3 demo_adk.py

Features:
- Formal JSON schemas for input/output validation
- Structured error handling
- Production-ready tool definitions
- Compatible with ADK Runner / Vertex AI
"""

import os
import json
from typing import Dict, Any

# Configure API key
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', 'your-api-key-here')

# Import ADK tools
from agents_capstone.adk_tools import (
    analyze_photo_tool,
    coach_on_photo_tool,
    TOOLS  # Full ADK tool registry
)

def demo_adk_tools():
    """Demonstrate ADK tool usage"""
    
    print("=" * 80)
    print("ADK TOOL DEMONSTRATION")
    print("Showing Google Vertex AI Agent Engine Compatible Tools")
    print("=" * 80)
    print()
    
    # Show available tools
    print("📦 AVAILABLE ADK TOOLS:")
    for i, tool in enumerate(TOOLS, 1):
        print(f"{i}. {tool['name']}")
        print(f"   Description: {tool['description']}")
        print(f"   Input Schema: {list(tool['input_schema']['properties'].keys())}")
        print()
    
    # Demo 1: Analyze Photo Tool
    print("-" * 80)
    print("DEMO 1: analyze_photo_tool")
    print("-" * 80)
    
    test_image = "agents_capstone/assets/test_bicycle.jpg"
    
    if os.path.exists(test_image):
        print(f"Analyzing: {test_image}")
        print()
        
        try:
            result = analyze_photo_tool(
                image_path=test_image,
                include_exif=True
            )
            
            print("✅ ANALYSIS RESULT:")
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"⚠️  Analysis failed: {e}")
    else:
        print(f"⚠️  Test image not found: {test_image}")
        print("   Showing tool signature instead:")
        tool_def = next(t for t in TOOLS if t['name'] == 'analyze_photo')
        print(json.dumps(tool_def, indent=2))
    
    print()
    
    # Demo 2: Coach on Photo Tool
    print("-" * 80)
    print("DEMO 2: coach_on_photo_tool")
    print("-" * 80)
    
    if os.path.exists(test_image):
        print(f"Getting coaching for: {test_image}")
        print(f"Query: 'How can I improve the composition?'")
        print()
        
        try:
            result = coach_on_photo_tool(
                image_path=test_image,
                query="How can I improve the composition?",
                user_id="demo_user"
            )
            
            print("✅ COACHING RESULT:")
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"⚠️  Coaching failed: {e}")
    else:
        print(f"⚠️  Test image not found: {test_image}")
        print("   Showing tool signature instead:")
        tool_def = next(t for t in TOOLS if t['name'] == 'coach_on_photo')
        print(json.dumps(tool_def, indent=2))
    
    print()
    print("=" * 80)
    print("✅ ADK TOOL DEMO COMPLETE")
    print()
    print("DEPLOYMENT NOTES:")
    print("- These tools have formal JSON schemas for Vertex AI")
    print("- Input/output validation built-in")
    print("- Error handling follows ADK best practices")
    print("- Compatible with ADK Runner and Agent Engine")
    print("=" * 80)


if __name__ == "__main__":
    demo_adk_tools()
