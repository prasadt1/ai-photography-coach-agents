"""Quick test to verify KnowledgeAgent returns citations"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env file (never hardcode keys!)
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment. Add to .env file.")

genai.configure(api_key=api_key)

# Import the agent
from agents_capstone.agents.knowledge_agent import KnowledgeAgent

# Create test session
session = {
    "session_id": "test-123",
    "history": []
}

# Mock vision analysis with issues
class MockAnalysis:
    issues = ["Horizon not level", "Subject not centered"]

# Create agent and get response
agent = KnowledgeAgent()
print("=" * 80)
print("Testing KnowledgeAgent.coach() with query about composition...")
print("=" * 80)

response = agent.coach(
    query="How can I improve the composition of this photo?",
    vision_analysis=MockAnalysis(),
    session=session
)

print("\n📝 RESPONSE TEXT:")
print("-" * 80)
print(response.text)
print("-" * 80)

# Check for citations
has_citations = "📚" in response.text or "Supporting Resources" in response.text
print(f"\n✓ Has citations: {has_citations}")

if not has_citations:
    print("\n⚠️  WARNING: No citations found in response!")
    print("This means AgenticRAG is not working or not being called.")
else:
    print("\n✅ Citations present - AgenticRAG working correctly!")
