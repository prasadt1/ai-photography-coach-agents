from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import google.generativeai as genai
from agents_capstone.tools.knowledge_base import simple_retrieve, Principle

@dataclass
class CoachingResponse:
    text: str
    principles: List[Principle]
    issues: List[str]
    exercise: str

class KnowledgeAgent:
    """Turns analysis + question + history into coaching text using LLM."""

    def coach(
        self,
        query: str,
        vision_analysis: Optional[object],
        session: dict,
    ) -> CoachingResponse:
        """Generate coaching response using LLM with conversation context."""
        issues: List[str] = []
        if vision_analysis is not None:
            issues = list(getattr(vision_analysis, "issues", []))

        # Build coaching prompt with conversation history
        history_context = self._build_history_context(session)
        
        # Retrieve relevant principles
        retrieval_query = query + " " + " ".join(issues)
        principles = simple_retrieve(retrieval_query)
        
        # Get dynamic response from LLM
        coaching_text = self._get_llm_coaching(
            query=query,
            issues=issues,
            history=history_context,
            principles=principles,
        )

        # Generate exercise based on issues
        exercise = self._generate_exercise(issues)

        return CoachingResponse(
            text=coaching_text,
            principles=principles,
            issues=issues,
            exercise=exercise,
        )

    def _build_history_context(self, session: Dict[str, Any]) -> str:
        """Build context string from conversation history."""
        history = session.get("history", [])
        if not history:
            return "This is the start of the conversation."
        
        context_lines = []
        for i, entry in enumerate(history[-3:]):  # Last 3 turns for context
            query = entry.get("query", "")
            if query:
                context_lines.append(f"- Previous question {i+1}: {query}")
        
        return "\n".join(context_lines) if context_lines else "This is the start of the conversation."

    def _get_llm_coaching(
        self,
        query: str,
        issues: List[str],
        history: str,
        principles: List[Principle],
    ) -> str:
        """Get coaching response from Gemini LLM."""
        try:
            # Build principles context
            principles_text = "\n".join([
                f"- {p.title}: {p.description}" for p in principles[:3]
            ]) if principles else "No specific principles found."

            prompt = f"""You are an expert photography coach providing personalized guidance.

User's Current Question: {query}

Detected Issues in Photo:
{chr(10).join(f"- {issue}" for issue in issues) if issues else "- No issues detected"}

Photography Principles to Consider:
{principles_text}

Conversation Context (Previous Questions):
{history}

Provide helpful, specific photography coaching that:
1. Directly addresses the user's current question
2. References any detected issues in the photo
3. Gives actionable advice they can apply immediately
4. Builds on previous conversation context if applicable
5. Stays focused and concise (3-4 sentences)

Respond as a friendly photography coach, not as a template."""

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback if LLM fails
            return self._generate_fallback_response(query, issues)

    def _generate_fallback_response(self, query: str, issues: List[str]) -> str:
        """Generate fallback response if LLM is unavailable."""
        response = f"Based on your question about {query}:\n\n"
        
        if "composition" in query.lower():
            response += "For composition: "
            if "subject_centered" in issues:
                response += "Try moving your main subject to the rule of thirds. "
            response += "Check your horizon line and use leading lines to guide the viewer."
        elif "lighting" in query.lower():
            response += "Lighting is key to great photos. Look for directional light, avoid harsh shadows, and consider the time of day."
        elif "iso" in query.lower() or "settings" in query.lower():
            response += "Adjust ISO based on available light - lower ISO for bright conditions, higher for low light. Balance with aperture and shutter speed."
        elif "about" in query.lower() or "subject" in query.lower():
            response += "Your photo shows interesting elements. Focus on what draws your eye most, and frame to emphasize that."
        else:
            response += "Great question about photography. Keep practicing and experimenting with different perspectives and settings."
        
        return response

    def _generate_exercise(self, issues: List[str]) -> str:
        """Generate a practice exercise based on detected issues."""
        if "subject_centered" in issues:
            return "Exercise: Take 10 photos of the same scene. For each frame, place the subject on a different position using the rule of thirds. Review which feels most compelling."
        elif "shallow_depth_of_field" in issues:
            return "Exercise: Practice focus placement with a wide aperture. Take shots with focus on different elements to master depth control."
        else:
            return "Exercise: Spend 30 minutes taking photos of one subject from different angles, distances, and compositions. Note what works best."
