from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ChatTurn:
    role: str   # "user" or "assistant"
    content: str


class ChatCoach:
    """
    Lightweight coach that builds a prompt for Gemini
    based on vision summary, EXIF and chat history.
    """

    def build_prompt(
        self,
        vision_summary: str,
        exif: Dict[str, Any],
        history: List[ChatTurn],
        user_question: str,
        skill_level: str = "beginner",
    ) -> str:
        exif_lines = []
        for k, v in exif.items():
            if v is not None:
                exif_lines.append(f"- {k}: {v}")
        exif_block = "\n".join(exif_lines) or "(no EXIF available)"

        history_block = ""
        for turn in history[-10:]:  # last 10 turns
            prefix = "User" if turn.role == "user" else "Coach"
            history_block += f"{prefix}: {turn.content}\n"

        prompt = f"""
You are an AI photography mentor coaching a {skill_level} photographer.

You are looking at the SAME photo for this whole conversation.
Use the vision summary and EXIF to keep your advice specific and concrete.

Vision summary:
{vision_summary}

EXIF:
{exif_block}

Conversation so far:
{history_block}

Now the user asks: "{user_question}"

Answer as a friendly coach:
- Explain what is happening in this photo.
- Name 1–3 relevant composition or exposure principles.
- Give 2–3 concrete suggestions the user can try next time.
Keep the answer under 200 words.
"""
        return prompt.strip()