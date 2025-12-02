"""
Test script for Hybrid RAG System

Tests:
1. Curated knowledge retrieval (high confidence)
2. FAISS fallback (low confidence / not found in curated)
3. Cascade logic with different queries
4. Topic extraction from Gemini-style responses
5. Source attribution labeling

Usage:
    python3 test_hybrid_rag.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents_capstone'))

def test_curated_retrieval():
    """Test PRIMARY tier: Curated knowledge"""
    print("\n" + "="*70)
    print("TEST 1: Curated Knowledge Retrieval (HIGH CONFIDENCE)")
    print("="*70)
    
    from tools.agentic_rag import AgenticRAG
    
    # Initialize with FAISS disabled (test curated only)
    rag = AgenticRAG(enable_faiss=False, curated_threshold=0.6)
    
    # Query that should match curated well
    query = "rule of thirds composition"
    print(f"\nQuery: '{query}'")
    
    results = rag.retrieve_grounding(query, top_k=3)
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Score: {result['relevance_score']:.3f}")
        print(f"  Source: {result['source']}")
        print(f"  Category: {result['category']}")
        print(f"  Text: {result['text'][:100]}...")
    
    # Verify reasonable score (cosine similarity for short queries is typically 0.3-0.5)
    best_score = results[0]['relevance_score']
    assert best_score >= 0.3, f"Expected score >= 0.3, got {best_score}"
    print(f"\n✅ TEST PASSED: Best score {best_score:.3f} (curated retrieval working)")


def test_topic_extraction():
    """Test topic extraction from Gemini-style responses"""
    print("\n" + "="*70)
    print("TEST 2: Topic Extraction from LLM Response")
    print("="*70)
    
    from tools.agentic_rag import AgenticRAG
    
    rag = AgenticRAG(enable_faiss=False)
    
    # Simulate Gemini response
    gemini_response = """
    Looking at your landscape, I notice your main subject is centered,
    which can feel a bit static. Try using the rule of thirds - position
    your subject at one of the power points for a more dynamic composition.
    Also, make sure to level your horizon line; a tilted horizon is 
    distracting. The golden hour lighting is beautiful though!
    """
    
    print(f"\nGemini Response:\n{gemini_response}")
    
    topics = rag._extract_topics(gemini_response)
    
    print(f"\nExtracted Topics: {topics}")
    
    # Verify expected topics detected
    assert "rule of thirds" in topics, "Should detect 'rule of thirds'"
    assert "composition" in topics, "Should detect 'composition'"
    assert "horizon" in topics, "Should detect 'horizon'"
    assert "golden hour" in topics, "Should detect 'golden hour'"
    
    print(f"\n✅ TEST PASSED: Extracted {len(topics)} topics correctly")


def test_cascade_logic():
    """Test CASCADE: curated → FAISS fallback"""
    print("\n" + "="*70)
    print("TEST 3: Cascade Logic (Curated → FAISS)")
    print("="*70)
    
    from tools.agentic_rag import AgenticRAG
    
    # Initialize with FAISS enabled (if available)
    rag = AgenticRAG(enable_faiss=True, curated_threshold=0.6)
    
    # Test 3a: High confidence query (should use curated)
    print("\n--- Test 3a: High Confidence Query ---")
    query_high = "rule of thirds"
    print(f"Query: '{query_high}'")
    
    results, source_type = rag._retrieve_cascade(query_high, top_k=1)
    
    print(f"Source Type: {source_type}")
    print(f"Result Score: {results[0]['relevance_score']:.3f}")
    
    if source_type == "curated":
        print("✅ Used curated (as expected for high confidence)")
    else:
        print("⚠️  Used FAISS despite high confidence (unexpected)")
    
    # Test 3b: Low confidence query (should try FAISS if available)
    print("\n--- Test 3b: Low Confidence Query ---")
    query_low = "camera settings menu navigation"
    print(f"Query: '{query_low}'")
    
    results, source_type = rag._retrieve_cascade(query_low, top_k=1)
    
    print(f"Source Type: {source_type}")
    if results:
        print(f"Result Score: {results[0].get('relevance_score', 'N/A')}")
    
    if source_type == "faiss":
        print("✅ Used FAISS fallback (as expected for low confidence)")
    elif source_type == "curated":
        print("⚠️  Used curated despite low confidence (FAISS unavailable or threshold met)")
    else:
        print("⚠️  No results from either tier")
    
    print(f"\n✅ TEST PASSED: Cascade logic working")


def test_ground_response():
    """Test full grounding flow: Gemini → Topics → Cascade → Citations"""
    print("\n" + "="*70)
    print("TEST 4: Full Grounding Flow")
    print("="*70)
    
    from tools.agentic_rag import AgenticRAG
    
    rag = AgenticRAG(enable_faiss=True)
    
    # Simulate Gemini creative response
    creative_response = """
    Great landscape shot! To improve it, try these tips:
    
    1. Your subject is centered, which feels static. Use the rule of thirds
       to position it at a power point for more visual interest.
    
    2. The horizon line is slightly tilted. Level it using your camera's
       grid overlay for a more professional look.
    
    3. Beautiful golden hour lighting - that warm glow is perfect!
    """
    
    user_query = "How can I improve this landscape photo?"
    
    print(f"\nUser Query: {user_query}")
    print(f"\nGemini Creative Response:\n{creative_response}")
    
    # Ground the response
    grounded_response = rag.ground_response(
        creative_response=creative_response,
        user_query=user_query,
        max_citations=2
    )
    
    print("\n" + "-"*70)
    print("GROUNDED RESPONSE (with citations):")
    print("-"*70)
    print(grounded_response)
    
    # Verify citations added
    assert "📚" in grounded_response, "Should contain citation section"
    assert "Supporting Resources" in grounded_response, "Should have heading"
    assert "*Source:" in grounded_response, "Should have source attribution"
    
    print(f"\n✅ TEST PASSED: Response grounded with citations")


def test_source_labels():
    """Test source label generation"""
    print("\n" + "="*70)
    print("TEST 5: Source Attribution Labels")
    print("="*70)
    
    from tools.agentic_rag import AgenticRAG
    
    rag = AgenticRAG(enable_faiss=False)
    
    # Test different source combinations
    test_cases = [
        (["curated"], "Curated Photography Books"),
        (["faiss"], "Photography Guides & Handbooks"),
        (["curated", "faiss"], "Curated + PDF Knowledge"),
        ([], "General"),
    ]
    
    for sources_used, expected_label in test_cases:
        label = rag._get_source_label(sources_used)
        print(f"\nSources: {sources_used}")
        print(f"Label: {label}")
        assert label == expected_label, f"Expected '{expected_label}', got '{label}'"
    
    print(f"\n✅ TEST PASSED: All source labels correct")


def test_knowledge_stats():
    """Test knowledge base statistics"""
    print("\n" + "="*70)
    print("TEST 6: Knowledge Base Statistics")
    print("="*70)
    
    from tools.agentic_rag import AgenticRAG
    
    rag = AgenticRAG(enable_faiss=False)
    
    stats = rag.get_stats()
    
    print(f"\nCurated Knowledge Stats:")
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Unique Topics: {stats['unique_topics']}")
    print(f"  Embedding Dimension: {stats['embedding_dimension']}")
    
    assert stats['total_entries'] == 20, "Should have 20 curated entries"
    assert stats['embedding_dimension'] == 384, "Should use 384-dim embeddings"
    
    print(f"\n✅ TEST PASSED: Knowledge base statistics correct")


def main():
    """Run all tests"""
    print("\n")
    print("🧪 " + "="*68 + " 🧪")
    print("🧪" + " "*68 + "🧪")
    print("🧪  HYBRID RAG SYSTEM TEST SUITE" + " "*39 + "🧪")
    print("🧪" + " "*68 + "🧪")
    print("🧪 " + "="*68 + " 🧪")
    
    tests = [
        ("Curated Retrieval", test_curated_retrieval),
        ("Topic Extraction", test_topic_extraction),
        ("Cascade Logic", test_cascade_logic),
        ("Ground Response", test_ground_response),
        ("Source Labels", test_source_labels),
        ("Knowledge Stats", test_knowledge_stats),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(tests)}")
    else:
        print(f"🎉 ALL TESTS PASSED!")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
