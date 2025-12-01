"""
Orchestrator Agent: Coordinates multi-agent interactions and manages session state.

This is the central coordination layer that:
1. Routes requests between VisionAgent and KnowledgeAgent
2. Maintains conversation history and user context
3. Provides persistent memory via SQLite (ADK-compatible adapter pattern)
4. Implements context compaction to prevent token overflow in long conversations

Design Decision: Orchestrator pattern chosen over direct agent-to-agent communication
to maintain clear separation of concerns and enable future scaling with additional agents.
"""

from dataclasses import asdict
from typing import Optional, Dict, Any

from agents_capstone.agents.vision_agent import VisionAgent, VisionAnalysis
from agents_capstone.agents.knowledge_agent import KnowledgeAgent, CoachingResponse
from agents_capstone.agents import SESSION_STORE
from agents_capstone.tools import adk_adapter as memory
from agents_capstone.tools.context import compact_context
import logging

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates agents and tracks session state.

    Adds persistent memory integration and simple context compaction.
    
    Architecture Pattern: This uses the Adapter pattern for memory operations,
    allowing easy migration from SQLite to Google Cloud ADK when deploying.
    """

    def __init__(self, vision_agent: VisionAgent, knowledge_agent: KnowledgeAgent):
        """Initialize orchestrator with specialized agent instances.
        
        Args:
            vision_agent: Handles image analysis and EXIF extraction
            knowledge_agent: Provides LLM-powered coaching responses
        """
        self.vision_agent = vision_agent
        self.knowledge_agent = knowledge_agent

    def _get_session(self, user_id: str) -> Dict[str, Any]:
        """Retrieve or initialize user session with persistent memory.
        
        Session Lifecycle:
        1. Check SQLite for persisted session (survives app restarts)
        2. If found, hydrate in-memory SESSION_STORE
        3. If not found, create new session with default values
        
        Args:
            user_id: Unique identifier for user session
            
        Returns:
            Dict containing skill_level, conversation history, and metadata
        """
        # Try to load persisted session first (ADK-compatible memory adapter)
        persisted = memory.get_value(user_id, "session")
        if persisted is not None:
            SESSION_STORE[user_id] = persisted

        # Initialize new session if user is first-time visitor
        if user_id not in SESSION_STORE:
            SESSION_STORE[user_id] = {
                "skill_level": "beginner",  # Default skill level for personalization
                "history": [],  # Conversation history for context
            }
        return SESSION_STORE[user_id]

    def _persist_session(self, user_id: str) -> None:
        """Persist session to SQLite for long-term memory.
        
        Memory Strategy: Uses ADK-compatible adapter pattern so this code
        can be migrated to Google Cloud Memory Store without changes.
        
        Args:
            user_id: User session to persist
        """
        try:
            memory.set_value(user_id, "session", SESSION_STORE.get(user_id, {}))
        except Exception as e:
            logger.exception("Failed to persist session: %s", e)

    def run(
        self,
        user_id: str,
        image_path: Optional[str],
        query: str,
    ) -> Dict[str, Any]:
        """Main orchestration method - coordinates all agent interactions.
        
        Execution Flow:
        1. Load/restore user session (with persistent memory)
        2. Run VisionAgent if new image uploaded (EXIF + composition analysis)
        3. Run KnowledgeAgent with vision results + conversation history
        4. Update conversation history
        5. Compact context if history exceeds 6 turns (prevents token overflow)
        6. Persist session to SQLite
        7. Return combined results
        
        Args:
            user_id: Unique session identifier
            image_path: Optional path to uploaded photo
            query: User's question or request
            
        Returns:
            Dict with vision analysis, coaching response, and session state
        """
        # Step 1: Restore session state (includes conversation history)
        session = self._get_session(user_id)
        skill_level = session.get("skill_level", "beginner")

        # Step 2: Run VisionAgent if new image provided
        # Design: Vision analysis only runs when needed, not on every query
        vision_result: Optional[VisionAnalysis] = None
        if image_path:
            vision_result = self.vision_agent.analyze(image_path, skill_level)

        # Step 3: Run KnowledgeAgent with all available context
        # This agent has access to: query, vision results, and conversation history
        coach_result: CoachingResponse = self.knowledge_agent.coach(
            query=query,
            vision_analysis=vision_result,
            session=session,
        )

        # Step 4: Update conversation history for future context
        # Each turn stores the query and detected issues for continuity
        session.setdefault("history", []).append(
            {
                "query": query,
                "issues": vision_result.issues if vision_result else [],
            }
        )

        # Step 5: Context compaction to handle long conversations
        # Problem: Long histories exceed LLM token limits (e.g., 50+ turn conversations)
        # Solution: After 6 turns, compact history into summary while preserving recent context
        try:
            if len(session.get("history", [])) > 6:
                summary = compact_context(session.get("history", []), max_sentences=3)
                session["compact_summary"] = summary
        except Exception:
            logger.exception("Context compaction failed")

        # Step 6: Persist session to SQLite (enables session restoration across app restarts)
        self._persist_session(user_id)

        # Step 7: Combine all results for UI rendering
        # Format: Structured dict that Streamlit can easily display
        combined: Dict[str, Any] = {
            "vision": asdict(vision_result) if vision_result else None,
            "coach": {
                "text": coach_result.text,
                "issues": coach_result.issues,
                "exercise": coach_result.exercise,
                "principles": [asdict(p) for p in coach_result.principles],
            },
            "session": session,  # Includes history for debugging/observability
        }
        return combined
