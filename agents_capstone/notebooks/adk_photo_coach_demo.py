"""
ADK demo showing sessions & memory for the AI Photography Coach.

Run with: python agents_capstone/notebooks/adk_photo_coach_demo.py
"""

import asyncio
import os

import google.generativeai as genai
from google.genai.types import Content, Part

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

from agents_capstone.tools.knowledge_base import simple_retrieve

MODEL = "gemini-2.5-flash"
APP_NAME = "photo_coach_adk"

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()


def build_instruction():
    return """
You are a photography coach helping a beginner improve composition and exposure.

You are part of a larger system; another component has already done EXIF analysis.
You do NOT see the image, only text, but you must:
- give practical, concrete suggestions
- reference composition principles (rule of thirds, leading lines, foreground interest)
- keep answers under 150 words

Use the conversation history to avoid repeating the same tips.
"""


coach_agent = LlmAgent(
    model=MODEL,
    name="PhotoCoachADK",
    instruction=build_instruction(),
)


async def run_conversation():
    runner = Runner(
        agent=coach_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    user_id = "adk_demo_user"
    session_id = "adk_demo_session"

    # Turn 1
    print("=== Turn 1 ===")
    msg1 = Content(
        role="user",
        parts=[
            Part(
                text=(
                    "The EXIF says: 24mm, f/3.5, ISO 800, 1/60s. "
                    "It's a wide landscape but it looks flat. How can I improve the composition?"
                )
            )
        ],
    )
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=msg1,
    ):
        if event.response:
            print(event.response.text)

    # Turn 2 (same session, follow-up)
    print("\n=== Turn 2 (follow‑up in same session) ===")
    msg2 = Content(
        role="user",
        parts=[
            Part(
                text=(
                    "Thanks! For the same scene at sunset, what should I change first: "
                    "the foreground or the horizon position?"
                )
            )
        ],
    )
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=msg2,
    ):
        if event.response:
            print(event.response.text)


if __name__ == "__main__":
    asyncio.run(run_conversation())
