"""
Context Compaction Tool: Prevents token overflow in long conversations.

Problem: LLMs have token limits (e.g., Gemini 1.5 Flash: 32K tokens)
Long conversations (50+ turns) can exceed these limits, causing API errors.

Solution: Compact conversation history into concise summary
Strategy:
1. Keep last 3 turns verbatim (most relevant context)
2. Summarize earlier turns into key points
3. Extract important keywords and user intents

Current Implementation: Simple heuristic summarization
Production Enhancement: Could use LLM for semantic summaries

Design Trade-off: Speed vs. Quality
- Heuristic: Fast, no API cost, but may miss nuance
- LLM-based: Better summaries, but adds latency and cost
The heuristic approach works well for demo purposes. Production deployments
might benefit from LLM-based summarization depending on conversation complexity.
"""

from typing import List, Dict

def compact_context(history: List[Dict[str, str]], max_sentences: int = 3) -> str:
    """Return a short summary string for the provided chat history.
    
    Compaction Strategy:
    1. Focus on last 6 messages (3 user+assistant turns)
    2. Extract assistant responses (most informative)
    3. Collect user questions (shows intent progression)
    4. Limit to max_sentences to control summary length

    Args:
        history: List of dicts with keys 'role' and 'content'
        max_sentences: Maximum sentences to extract from assistant responses
        
    Returns:
        Compact summary string preserving key information
        
    The Orchestrator calls this when history exceeds 6 turns
    """
    if not history:
        return ""

    # Step 1: Take last 6 messages (3 turns) - most relevant recent context
    relevant = history[-6:]
    
    # Step 2: Separate user and assistant messages
    # Assistant content = coaching responses (most informative)
    # User content = questions/intents (shows conversation flow)
    assistant_texts = [m["content"] for m in relevant if m.get("role") == "assistant"]
    user_texts = [m["content"] for m in relevant if m.get("role") == "user"]

    # Step 3: Build summary from key components
    summary_parts = []
    
    if assistant_texts:
        # Extract first N sentences from assistant responses
        # Heuristic: First sentences often contain main points
        sents = []
        for t in assistant_texts:
            for s in t.split("."):
                s = s.strip()
                if s:
                    sents.append(s)
        # Limit to max_sentences to control summary length
        for s in sents[:max_sentences]:
            summary_parts.append(s + ".")

    if user_texts:
        # Preserve user question progression to maintain context flow
        summary_parts.append("Recent user questions: " + "; ".join(user_texts))

    # Step 4: Join all parts into compact summary string
    return " ".join(summary_parts)
