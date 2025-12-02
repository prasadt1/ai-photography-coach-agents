#!/usr/bin/env python3
"""
Quick test of the AgenticRAG implementation
"""

import sys
import os

# Add agents_capstone to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents_capstone'))

# Test 1: Knowledge base
print("="*70)
print("TEST 1: Knowledge Base")
print("="*70)

from data.knowledge_sources import PHOTOGRAPHY_KNOWLEDGE, get_all_topics

print(f"✅ Total entries: {len(PHOTOGRAPHY_KNOWLEDGE)}")
print(f"✅ Total topics: {len(get_all_topics())}")
print(f"\nSample entry:")
print(f"  Text: {PHOTOGRAPHY_KNOWLEDGE[0]['text'][:100]}...")
print(f"  Source: {PHOTOGRAPHY_KNOWLEDGE[0]['source']}")
print(f"  Topics: {', '.join(PHOTOGRAPHY_KNOWLEDGE[0]['topics'])}")

print("\n✅ Knowledge base loaded successfully!")
print("\nTo test full AgenticRAG (requires sentence-transformers):")
print("  pip3 install sentence-transformers")
print("  python3 -c 'from agents_capstone.tools.agentic_rag import AgenticRAG; rag = AgenticRAG()'")
