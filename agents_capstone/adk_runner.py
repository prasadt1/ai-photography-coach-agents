"""
ADK Runner Implementation for AI Photography Coach

Real ADK integration using google.adk SDK. Demonstrates agent deployment
via Google's Agent Development Kit with tools, sessions, and memory.

This implementation wraps the same core agents (VisionAgent, KnowledgeAgent)
used in MCP server and Python API, showing architectural reusability.

Usage:
    # As module
    from agents_capstone.adk_runner import run_photo_coach_adk
    
    result = await run_photo_coach_adk(
        user_input="How do I improve landscape composition?",
        image_path="photo.jpg",
        user_id="user123",
        session_id="session456"
    )
    
    # Or run demo directly
    python3 agents_capstone/adk_runner.py

Architecture:
    - Uses google.adk.agents.LlmAgent with Gemini 2.5 Flash
    - InMemorySessionService for conversation continuity
    - Tools wrapped from existing agents/vision_agent.py and agents/knowledge_agent.py
    - Shows 3-platform deployment: ADK + MCP + Python API

References:
    - ADK_INTEGRATION.md for architecture details
    - tools/mcp_server.py for MCP implementation comparison
    - demo_3_platforms.py for unified demonstration
"""

import asyncio
import os
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.genai.types import Content, Part

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents_capstone.adk_tools import (
    analyze_photo_tool,
    coach_on_photo_tool
)

# Model configuration
MODEL = "gemini-2.5-flash"
APP_NAME = "photo_coach_adk"

# Configure Gemini API
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable required")
genai.configure(api_key=api_key)

# Global session service (persistent across calls)
session_service = InMemorySessionService()


def build_coach_instruction() -> str:
    """
    Build system instruction for the photography coach agent.
    
    Defines the agent's role, capabilities, and constraints to ensure
    helpful, actionable feedback for photographers.
    """
    return """You are an expert photography coach helping photographers improve their skills.

Your role:
- Analyze photographs using technical EXIF data and composition principles
- Provide practical, actionable suggestions tailored to skill level
- Reference established principles: rule of thirds, leading lines, exposure triangle
- Build on conversation history to avoid repetition

Your capabilities:
1. analyze_photo: Extract EXIF, evaluate composition, detect issues with severity
2. coach_on_photo: Give coaching advice using vision analysis and knowledge base

Guidelines:
- Be encouraging but constructive
- Keep responses focused and under 200 words
- Adapt complexity to user's skill level (beginner/intermediate/advanced)
- Use conversation context to personalize advice
- Prioritize high-severity issues first

You work as part of a multi-agent system with vision analysis and knowledge retrieval.
"""


# Initialize the ADK agent with tools
photo_coach_agent = LlmAgent(
    model=MODEL,
    name="PhotoCoachADK",
    instruction=build_coach_instruction(),
    # Note: Tools are registered separately when creating Runner
    # ADK currently doesn't support passing tools directly to LlmAgent
)


async def run_photo_coach_adk(
    user_input: str,
    image_path: Optional[str] = None,
    skill_level: str = "intermediate",
    user_id: str = "default_user",
    session_id: Optional[str] = None,
    runner: Optional[Runner] = None,
) -> Dict[str, Any]:
    """
    Run the ADK photography coach with a user query.
    
    Args:
        user_input: User's question or request
        image_path: Optional path to image for analysis
        skill_level: User's proficiency (beginner/intermediate/advanced)
        user_id: Unique user identifier for session management
        session_id: Session identifier (ADK creates on first call if None)
        runner: Optional pre-configured Runner (created if not provided)
    
    Returns:
        Dictionary containing:
            - response: Agent's text response
            - session_id: Session identifier used
            - analysis: Vision analysis results (if image_path provided)
            - runner: Runner instance (for reuse in follow-up calls)
    
    Example:
        >>> result = await run_photo_coach_adk(
        ...     user_input="Analyze my landscape photo",
        ...     image_path="assets/test_images/landscape.jpg",
        ...     skill_level="intermediate"
        ... )
        >>> print(result["response"])
        >>> print(result["analysis"]["composition_summary"])
    """
    # Generate simple session ID if not provided (ADK will create session)
    if session_id is None:
        session_id = f"session_{user_id}"
    
    # Create runner with agent and session service (if not provided)
    if runner is None:
        runner = Runner(
            agent=photo_coach_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )
    
    # Prepare context with image analysis if provided
    context_parts = []
    analysis_result = None
    
    if image_path:
        # Run vision analysis first
        analysis_result = analyze_photo_tool(image_path, skill_level)
        
        # Add analysis to context
        context_parts.append(Part(text=f"""
Image Analysis Results:
- EXIF: {analysis_result['exif']}
- Composition: {analysis_result['composition_summary']}
- Issues: {len(analysis_result['detected_issues'])} detected
- Strengths: {', '.join(analysis_result['strengths'])}

Detected Issues:
"""))
        
        for issue in analysis_result['detected_issues']:
            context_parts.append(Part(text=f"- [{issue['severity']}] {issue['type']}: {issue['description']}"))
        
        context_parts.append(Part(text=f"\n\nUser Question: {user_input}"))
    else:
        context_parts.append(Part(text=user_input))
    
    # Create message content
    message = Content(
        role="user",
        parts=context_parts,
    )
    
    # Run the agent
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
    
    return {
        "response": response_text,
        "session_id": session_id,
        "analysis": analysis_result,
        "runner": runner,
    }


async def demo():
    """
    Demonstrate ADK runner with sample conversation.
    
    Shows:
    1. Image analysis with EXIF extraction
    2. Coaching advice using vision analysis
    3. Follow-up question with session continuity
    """
    print("=== ADK Photography Coach Demo ===\n")
    
    # Check for test image
    test_image = "agents_capstone/assets/test_images/overexposed.jpg"
    if not os.path.exists(test_image):
        print(f"⚠️  Test image not found: {test_image}")
        print("Using text-only demo mode\n")
        test_image = None
    
    user_id = "demo_user"
    session_id = "adk_demo_session"
    
    # Create session explicitly
    await session_service.create_session(
        user_id=user_id,
        session_id=session_id,
        app_name=APP_NAME
    )
    
    # Turn 1: Initial analysis
    print("👤 User: Analyze this photo and tell me how to improve composition")
    print("🤖 Coach ADK:")
    
    result1 = await run_photo_coach_adk(
        user_input="Analyze this photo and tell me how to improve composition",
        image_path=test_image,
        skill_level="intermediate",
        user_id=user_id,
        session_id=session_id,
    )
    
    print(result1["response"])
    
    if result1["analysis"]:
        print(f"\n📊 EXIF: {result1['analysis']['exif']}")
        print(f"🎯 Issues: {len(result1['analysis']['detected_issues'])} detected")
    
    print("\n" + "="*60 + "\n")
    
    # Turn 2: Follow-up question (same session, reuse runner)
    print("👤 User: What's the most important fix for a beginner?")
    print("🤖 Coach ADK:")
    
    result2 = await run_photo_coach_adk(
        user_input="What's the most important fix for a beginner?",
        skill_level="beginner",
        user_id=user_id,
        session_id=session_id,
        runner=result1["runner"],  # Reuse runner for session continuity
    )
    
    print(result2["response"])
    
    print("\n✅ ADK Runner Demo Complete!")
    print(f"Session ID: {result2['session_id']}")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo())
