"""Test exercise generation with different issues"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

from agents_capstone.agents.knowledge_agent import KnowledgeAgent

agent = KnowledgeAgent()

# Test different issue scenarios
test_cases = [
    ["Horizon not level", "Subject centered"],
    ["Weak focal point", "Cluttered background"],
    ["Shallow depth of field", "Subject cropped"],
    ["Poor lighting", "Underexposed"],
]

print("=" * 80)
print("TESTING DYNAMIC EXERCISE GENERATION")
print("=" * 80)

for i, issues in enumerate(test_cases, 1):
    print(f"\n{i}. Issues: {', '.join(issues)}")
    exercise = agent._generate_exercise(issues)
    print(f"   Exercise: {exercise}")
    print()

print("=" * 80)
print("✅ Each exercise should be DIFFERENT and issue-specific")
print("=" * 80)
