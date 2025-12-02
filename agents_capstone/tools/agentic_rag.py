"""
Agentic RAG (Retrieval-Augmented Generation) for Photography Coaching

This module implements a HYBRID approach:
1. Gemini generates creative, photo-specific coaching (dynamic)
2. RAG retrieves authoritative citations from photography literature (grounded)
3. Agent synthesizes: Creative advice + cited sources

WHY AGENTIC RAG vs. PURE RAG?
-------------------------------
Pure RAG: "According to source X, use rule of thirds..."
  - Static, robotic
  - No creativity
  - Just regurgitates documents

Agentic RAG: "Try placing your subject at the left third... This creates 
              visual tension. 📚 Source: Adams, The Camera, 1980"
  - Creative advice from Gemini
  - Grounded with authoritative citations
  - Best of both worlds

HOW IT WORKS:
-------------
1. KnowledgeAgent asks Gemini for coaching
2. Gemini generates creative, photo-specific advice
3. AgenticRAG extracts topics from Gemini's response
4. Retrieves relevant citations matching those topics
5. Returns: Gemini's advice + aligned citations

EXAMPLE:
--------
Gemini says: "Try rule of thirds for better composition"
AgenticRAG:
  - Extracts topic: "rule of thirds"
  - Retrieves: "Rule of thirds: Position subjects at power points [Adams, 1980]"
  - Returns: Gemini advice + citation ✅ ALIGNED

VS. WRONG APPROACH:
-------------------
Gemini says: "Try rule of thirds"
Naive RAG:
  - Uses user query: "how to improve landscape?"
  - Retrieves: "Golden hour lighting is best [Freeman, 2007]"
  - Returns: Composition advice + lighting citation ❌ MISALIGNED
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import json
import os
import re


class AgenticRAG:
    """
    Hybrid RAG that combines Gemini's creativity with grounded citations.
    """
    
    def __init__(self, knowledge_base: Optional[List[Dict]] = None):
        """
        Initialize AgenticRAG with knowledge base and embedding model.
        
        Args:
            knowledge_base: List of dict with keys: text, source, category, topics
                           If None, loads from data/knowledge_sources.py
        
        How sentence-transformers work:
        --------------------------------
        1. Model converts text into 384-dimensional vector (embedding)
        2. Similar concepts have similar vectors (nearby in vector space)
        3. We compute cosine similarity to find semantically related entries
        
        Why 'all-MiniLM-L6-v2'?
        -------------------------
        - Fast: 14,000 sentences/sec on CPU
        - Compact: 80MB model size
        - Accurate: 68.06 on SBERT benchmark
        - Perfect balance for this use case
        """
        # Load knowledge base
        if knowledge_base is None:
            from data.knowledge_sources import PHOTOGRAPHY_KNOWLEDGE
            self.knowledge_base = PHOTOGRAPHY_KNOWLEDGE
        else:
            self.knowledge_base = knowledge_base
        
        print(f"📚 Loaded {len(self.knowledge_base)} knowledge entries")
        
        # Initialize sentence transformer
        # This creates vector embeddings (numeric representations) of text
        print("🔧 Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Check if we have cached embeddings (saves time on restart)
        embeddings_path = os.path.join(
            os.path.dirname(__file__), 
            "../data/embeddings.npy"
        )
        
        if os.path.exists(embeddings_path):
            print("✅ Loading cached embeddings...")
            self.embeddings = np.load(embeddings_path)
        else:
            print("🔄 Generating embeddings (first time only, ~10 seconds)...")
            # Encode all knowledge base entries into vectors
            # This is slow, so we cache it
            texts = [k["text"] for k in self.knowledge_base]
            self.embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # Save for next time
            np.save(embeddings_path, self.embeddings)
            print(f"💾 Cached embeddings to {embeddings_path}")
        
        print(f"✅ AgenticRAG initialized with {len(self.embeddings)} embeddings")
    
    
    def _extract_topics(self, response: str) -> List[str]:
        """
        Extract photography topics from Gemini's response.
        
        This is the KEY to aligned citations. We analyze what Gemini actually
        talked about, then retrieve citations matching THOSE topics.
        
        Args:
            response: Gemini's generated coaching text
        
        Returns:
            List of detected topics (e.g., ["rule of thirds", "golden hour"])
        
        How it works:
        -------------
        1. Define keyword patterns for each topic
        2. Check if any pattern appears in Gemini's response
        3. Return list of matched topics
        4. Use these topics to query RAG for aligned citations
        """
        # Map of topics to their keyword patterns
        # If any keyword appears in response, we detected that topic
        topic_keywords = {
            "rule of thirds": ["rule of thirds", "thirds", "grid", "power point", "intersection"],
            "golden hour": ["golden hour", "magic hour", "sunrise", "sunset", "warm light"],
            "depth of field": ["depth of field", "dof", "bokeh", "blur", "background separation", "shallow", "deep"],
            "exposure": ["exposure", "overexposed", "underexposed", "bright", "dark", "histogram"],
            "iso": ["iso", "noise", "grain", "sensitivity", "high iso", "low iso"],
            "aperture": ["aperture", "f-stop", "f/", "f stop", "wide open", "stopped down"],
            "shutter speed": ["shutter speed", "motion blur", "freeze", "fast shutter", "slow shutter"],
            "leading lines": ["leading lines", "lines", "guide", "eye flow", "diagonal"],
            "lighting": ["lighting", "light", "shadows", "highlights", "contrast"],
            "composition": ["composition", "framing", "frame", "arrange", "placement"],
            "focus": ["focus", "sharp", "sharpness", "blur", "out of focus", "soft"],
            "white balance": ["white balance", "color temperature", "kelvin", "warm", "cool", "color cast"],
            "horizon": ["horizon", "tilt", "level", "straight", "crooked"],
            "centered subject": ["centered", "center", "middle", "symmetry", "symmetrical"],
            "background": ["background", "distraction", "clutter", "busy", "clean background"],
        }
        
        found_topics = []
        response_lower = response.lower()
        
        for topic, keywords in topic_keywords.items():
            # Check if ANY keyword for this topic appears in response
            if any(keyword in response_lower for keyword in keywords):
                found_topics.append(topic)
        
        # Always include general "composition" and "exposure" if no specific topics found
        if not found_topics:
            found_topics = ["composition", "exposure"]
        
        return found_topics
    
    
    def retrieve_grounding(self, query: str, top_k: int = 2) -> List[Dict]:
        """
        Retrieve most relevant knowledge entries for a query.
        
        Args:
            query: Search query (user question OR Gemini's response topics)
            top_k: Number of results to return
        
        Returns:
            List of dicts with: text, source, category, topics, relevance_score
        
        How semantic search works:
        --------------------------
        1. Convert query to vector embedding (same model as knowledge base)
        2. Compute cosine similarity between query and all knowledge entries
        3. Sort by similarity score (highest = most relevant)
        4. Return top_k results
        
        Why this works:
        ---------------
        "rule of thirds" query will match:
          - "Rule of thirds: Position subjects at power points..." (HIGH)
          - "Leading lines guide the eye..." (MEDIUM - related to composition)
          - "ISO sensitivity controls exposure..." (LOW - unrelated)
        
        Vector similarity captures semantic meaning, not just keyword matching.
        """
        # Encode the query into a vector
        query_embedding = self.model.encode([query])
        
        # Compute cosine similarity: dot product of normalized vectors
        # Result: scores from 0 (unrelated) to 1 (identical)
        scores = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # Get indices of top_k highest scores
        top_indices = np.argsort(scores)[-top_k:][::-1]  # [::-1] reverses to descending
        
        # Build results with scores
        results = []
        for idx in top_indices:
            entry = self.knowledge_base[idx].copy()
            entry["relevance_score"] = float(scores[idx])
            results.append(entry)
        
        return results
    
    
    def ground_response(
        self, 
        creative_response: str, 
        user_query: str,
        max_citations: int = 2
    ) -> str:
        """
        Augment Gemini's creative response with grounded citations.
        
        This is the MAIN METHOD that combines Gemini + RAG.
        
        Args:
            creative_response: Gemini's generated coaching advice
            user_query: User's original question (for context)
            max_citations: Maximum number of citations to add
        
        Returns:
            Enhanced response with creative advice + citations
        
        Workflow:
        ---------
        1. Extract topics from Gemini's response (e.g., "rule of thirds")
        2. Retrieve citations matching those topics
        3. Format as: Gemini's advice + "📚 Supporting Resources:" + citations
        4. Ensure citations ALIGN with what Gemini said
        
        Example:
        --------
        Input (Gemini): "Try rule of thirds for better composition"
        Topics extracted: ["rule of thirds", "composition"]
        Retrieved: "Rule of thirds: Position at power points [Adams, 1980]"
        Output: Gemini's text + 📚 citation
        """
        # Step 1: Extract topics from Gemini's response
        topics = self._extract_topics(creative_response)
        print(f"🔍 Detected topics in response: {topics}")
        
        # Step 2: Retrieve citations for each topic
        evidence = []
        seen_sources = set()  # Avoid duplicate sources
        
        for topic in topics:
            # Query RAG with the topic
            results = self.retrieve_grounding(topic, top_k=1)
            
            for result in results:
                # Skip if we already have a citation from this source
                source = result["source"]
                if source not in seen_sources and len(evidence) < max_citations:
                    evidence.append(result)
                    seen_sources.add(source)
        
        # If we found no topic-specific citations, fall back to user query
        if not evidence:
            print("⚠️  No topic-specific citations found, using user query...")
            evidence = self.retrieve_grounding(user_query, top_k=max_citations)
        
        # Step 3: Format final response
        if not evidence:
            # No citations available, return Gemini's response as-is
            return creative_response
        
        # Build citations section
        citations_text = "\n\n📚 **Supporting Resources:**\n"
        for i, entry in enumerate(evidence, 1):
            # Format: • Text excerpt
            #         *Source: Citation*
            citations_text += f"\n• {entry['text'][:200]}..."  # Truncate long entries
            citations_text += f"\n  *Source: {entry['source']}*\n"
        
        # Combine Gemini's creative advice + grounded citations
        grounded_response = creative_response + citations_text
        
        return grounded_response
    
    
    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        categories = {}
        for entry in self.knowledge_base:
            cat = entry["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        all_topics = set()
        for entry in self.knowledge_base:
            all_topics.update(entry["topics"])
        
        return {
            "total_entries": len(self.knowledge_base),
            "categories": categories,
            "unique_topics": len(all_topics),
            "embedding_dimension": self.embeddings.shape[1] if len(self.embeddings) > 0 else 0
        }


# ============ USAGE EXAMPLE ============
if __name__ == "__main__":
    print("\n" + "="*70)
    print("AGENTIC RAG DEMO")
    print("="*70)
    
    # Initialize
    rag = AgenticRAG()
    
    # Show stats
    stats = rag.get_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Unique topics: {stats['unique_topics']}")
    print(f"  Embedding dimensions: {stats['embedding_dimension']}")
    
    # Test 1: Retrieve by topic
    print("\n" + "-"*70)
    print("TEST 1: Retrieve citations for 'rule of thirds'")
    print("-"*70)
    results = rag.retrieve_grounding("rule of thirds", top_k=2)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['text'][:150]}...")
        print(f"   Source: {result['source']}")
        print(f"   Relevance: {result['relevance_score']:.3f}")
    
    # Test 2: Ground a Gemini response
    print("\n" + "-"*70)
    print("TEST 2: Ground Gemini's response with citations")
    print("-"*70)
    
    # Simulate Gemini's creative response
    gemini_response = """
    Looking at your landscape photo, I can see a few areas for improvement:
    
    1. **Composition**: Your subject is centered, which creates a static feel. 
       Try applying the rule of thirds - position your main element at the 
       left or right third of the frame for more visual interest.
    
    2. **Horizon**: The horizon line appears slightly tilted. Make sure to 
       level it using your camera's grid overlay.
    
    3. **Lighting**: Great use of golden hour! The warm tones add mood.
    """
    
    # Ground it with citations
    grounded = rag.ground_response(
        creative_response=gemini_response,
        user_query="How can I improve this landscape photo?",
        max_citations=2
    )
    
    print("\n📝 Original Gemini Response:")
    print(gemini_response)
    
    print("\n✨ Grounded Response (with citations):")
    print(grounded)
    
    print("\n" + "="*70)
    print("✅ Demo complete!")
    print("="*70)
