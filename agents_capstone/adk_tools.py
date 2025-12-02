"""
ADK Tool Definitions for AI Photography Coach

Formalizes agents as Google ADK (Agent Development Kit) tools for:
- Vertex AI Agent Engine deployment
- Cloud-native orchestration
- Enterprise-grade scaling

This module wraps VisionAgent and KnowledgeAgent as ADK ToolDefinitions,
enabling seamless integration with Google's agent infrastructure.

Usage:
    from agents_capstone.adk_tools import vision_tool, coaching_tool, tools
    
    # Use in ADK Runner
    runner = Runner(
        agent=photography_coach_agent,
        tools=tools,
        session_service=session_service
    )

References:
    - ADK_INTEGRATION.md for setup guide
    - agents/orchestrator.py for current local orchestration
"""

from typing import Dict, Any, Optional
from dataclasses import asdict

from agents_capstone.agents.vision_agent import VisionAgent, VisionAnalysis, DetectedIssue
from agents_capstone.agents.knowledge_agent import KnowledgeAgent, CoachingResponse

# Initialize agent instances (reused across tool calls)
_vision_agent = VisionAgent()
_knowledge_agent = KnowledgeAgent()


def analyze_photo_tool(image_path: str, skill_level: str = "intermediate") -> Dict[str, Any]:
    """
    ADK Tool: analyze_photo
    
    Analyze a photograph's technical settings and composition using Gemini Vision.
    
    This tool extracts EXIF metadata, evaluates composition, detects issues with
    severity scoring, and identifies strengths.
    
    Args:
        image_path: Path to the image file to analyze
        skill_level: User's proficiency level (beginner/intermediate/advanced)
                    Used for adaptive feedback complexity
    
    Returns:
        Dictionary containing:
            - exif: Dict of camera settings (ISO, aperture, shutter, focal length)
            - composition_summary: Natural language analysis summary
            - issues: List of issue type strings (legacy compatibility)
            - detected_issues: List of structured issues with:
                - type: Issue identifier
                - severity: low/medium/high
                - description: What the issue is
                - suggestion: How to improve
            - strengths: List of positive aspects detected
    
    Example:
        >>> result = analyze_photo_tool("photo.jpg", "intermediate")
        >>> print(result["composition_summary"])
        >>> for issue in result["detected_issues"]:
        ...     print(f"{issue['severity']}: {issue['suggestion']}")
    """
    try:
        analysis = _vision_agent.analyze(image_path, skill_level)
        
        # Convert to serializable dict
        return {
            "exif": analysis.exif,
            "composition_summary": analysis.composition_summary,
            "issues": analysis.issues,  # Legacy format
            "detected_issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "suggestion": issue.suggestion
                }
                for issue in analysis.detected_issues
            ],
            "strengths": analysis.strengths
        }
    except Exception as e:
        return {
            "error": str(e),
            "exif": {},
            "composition_summary": f"Error analyzing photo: {str(e)}",
            "issues": ["analysis_failed"],
            "detected_issues": [],
            "strengths": []
        }


def coach_on_photo_tool(
    query: str,
    vision_analysis: Optional[Dict[str, Any]] = None,
    session: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    ADK Tool: coach_on_photo
    
    Provide personalized photography coaching based on user query and optional
    photo analysis. Integrates with Agentic RAG for grounded responses.
    
    This tool combines:
    - User's specific question
    - Photo analysis results (if provided)
    - Conversation history (if session provided)
    - Knowledge base retrieval (curated + FAISS)
    - Gemini's creative coaching abilities
    
    Args:
        query: User's question or request for coaching
        vision_analysis: Optional dict from analyze_photo_tool with:
            - composition_summary: str
            - detected_issues: List[dict]
            - strengths: List[str]
        session: Optional session dict with:
            - history: List of previous queries and issues
            - skill_level: User's proficiency level
    
    Returns:
        Dictionary containing:
            - text: Coaching response with citations
            - issues: Detected issues from analysis
            - exercise: Optional practice exercise
            - sources_used: Knowledge base sources (curated/faiss/both)
    
    Example:
        >>> vision_result = analyze_photo_tool("landscape.jpg")
        >>> coaching = coach_on_photo_tool(
        ...     query="How can I improve this landscape?",
        ...     vision_analysis=vision_result,
        ...     session={"skill_level": "beginner"}
        ... )
        >>> print(coaching["text"])
    """
    try:
        # Convert dict back to VisionAnalysis if provided
        vision_obj = None
        if vision_analysis:
            # Reconstruct DetectedIssue objects
            detected_issues = []
            for issue_dict in vision_analysis.get("detected_issues", []):
                detected_issues.append(DetectedIssue(
                    type=issue_dict.get("type", "unknown"),
                    severity=issue_dict.get("severity", "low"),
                    description=issue_dict.get("description", ""),
                    suggestion=issue_dict.get("suggestion", "")
                ))
            
            vision_obj = VisionAnalysis(
                exif=vision_analysis.get("exif", {}),
                composition_summary=vision_analysis.get("composition_summary", ""),
                issues=vision_analysis.get("issues", []),
                detected_issues=detected_issues,
                strengths=vision_analysis.get("strengths", [])
            )
        
        # Ensure session dict
        if session is None:
            session = {}
        
        # Call KnowledgeAgent
        response = _knowledge_agent.coach(
            query=query,
            vision_analysis=vision_obj,
            session=session
        )
        
        # Return serializable dict
        return {
            "text": response.text,
            "issues": response.issues,
            "exercise": response.exercise,
            "sources_used": getattr(response, 'sources_used', None)
        }
    
    except Exception as e:
        return {
            "text": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
            "issues": [],
            "exercise": None,
            "error": str(e)
        }


# ADK Tool Definitions
# These would be used with google.adk.tools.ToolDefinition when ADK is available

VISION_TOOL_DEFINITION = {
    "name": "analyze_photo",
    "description": "Analyze a photograph's technical settings and composition using Gemini Vision. Returns EXIF data, composition summary, detected issues with severity, and strengths.",
    "func": analyze_photo_tool,
    "input_schema": {
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
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "exif": {"type": "object"},
            "composition_summary": {"type": "string"},
            "issues": {"type": "array", "items": {"type": "string"}},
            "detected_issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "severity": {"type": "string"},
                        "description": {"type": "string"},
                        "suggestion": {"type": "string"}
                    }
                }
            },
            "strengths": {"type": "array", "items": {"type": "string"}}
        }
    }
}

COACHING_TOOL_DEFINITION = {
    "name": "coach_on_photo",
    "description": "Provide personalized photography coaching based on user query, photo analysis, and conversation history. Integrates Agentic RAG with curated and FAISS knowledge bases.",
    "func": coach_on_photo_tool,
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "User's question or request for coaching advice"
            },
            "vision_analysis": {
                "type": "object",
                "description": "Optional photo analysis results from analyze_photo",
                "properties": {
                    "composition_summary": {"type": "string"},
                    "detected_issues": {"type": "array"},
                    "strengths": {"type": "array"}
                }
            },
            "session": {
                "type": "object",
                "description": "Optional session context with history and skill_level",
                "properties": {
                    "history": {"type": "array"},
                    "skill_level": {"type": "string"}
                }
            }
        },
        "required": ["query"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "issues": {"type": "array", "items": {"type": "string"}},
            "exercise": {"type": "string"},
            "sources_used": {"type": "string"}
        }
    }
}

# Export tools list for ADK integration
TOOLS = [VISION_TOOL_DEFINITION, COACHING_TOOL_DEFINITION]

# Export tool functions for direct use
__all__ = [
    "analyze_photo_tool",
    "coach_on_photo_tool",
    "VISION_TOOL_DEFINITION",
    "COACHING_TOOL_DEFINITION",
    "TOOLS"
]


# Example: Integration with ADK (when google.adk is available)
"""
try:
    from google.adk.tools import ToolDefinition
    from google.adk.runner import Runner
    from google.adk.sessions import InMemorySessionService
    
    # Create ADK ToolDefinition objects
    vision_tool = ToolDefinition(**VISION_TOOL_DEFINITION)
    coaching_tool = ToolDefinition(**COACHING_TOOL_DEFINITION)
    
    # Use in ADK Runner
    runner = Runner(
        agent=photography_coach_agent,
        tools=[vision_tool, coaching_tool],
        session_service=InMemorySessionService(),
        app_name="ai-photography-coach"
    )
    
    # Run agent
    async for event in runner.run_async(
        user_id="user123",
        session_id="session456",
        new_message=Content(role="user", parts=[Part(text="How can I improve my landscape photos?")])
    ):
        if event.response:
            print(event.response.text)

except ImportError:
    print("google.adk not available - using local orchestration")
"""
