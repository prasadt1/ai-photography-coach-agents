from typing import List, Dict

# Very small, local context compactor. For the capstone we implement a simple
# heuristic summarizer that extracts sentences and important keywords from
# recent chat history. In a production system you'd use an LLM call.

def compact_context(history: List[Dict[str, str]], max_sentences: int = 3) -> str:
    """Return a short summary string for the provided chat history.

    history: list of dicts with keys 'role' and 'content'. We take the last
    N user+assistant turns and create a short summary.
    """
    if not history:
        return ""

    # Take last 6 messages (3 turns) by default
    relevant = history[-6:]
    # Collect important lines: prefer assistant content
    assistant_texts = [m["content"] for m in relevant if m.get("role") == "assistant"]
    user_texts = [m["content"] for m in relevant if m.get("role") == "user"]

    # Simple heuristics: pick first 1-2 assistant sentences and user intents
    summary_parts = []
    if assistant_texts:
        # split into sentences by period
        sents = []
        for t in assistant_texts:
            for s in t.split("."):
                s = s.strip()
                if s:
                    sents.append(s)
        # take up to max_sentences
        for s in sents[:max_sentences]:
            summary_parts.append(s + ".")

    if user_texts:
        summary_parts.append("Recent user questions: " + "; ".join(user_texts))

    return " ".join(summary_parts)
