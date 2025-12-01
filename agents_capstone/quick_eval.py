#!/usr/bin/env python3
"""
Quick evaluation runner - can be used from agents_capstone/ directory.

Usage from agents_capstone/:
    python3 quick_eval.py

Usage from project root:
    python3 agents_capstone/quick_eval.py
"""
import sys
from pathlib import Path

# Auto-detect project root
current = Path(__file__).parent
if current.name == "agents_capstone":
    project_root = current.parent
else:
    project_root = current

sys.path.insert(0, str(project_root))

from agents_capstone.evaluate import evaluate_sample

def main():
    """Run a quick evaluation."""
    import os
    
    # Test prompts
    prompts = [
        "How can I improve the composition of this photo?",
        "What camera settings should I use for a sunset shot?",
        "Explain the rule of thirds and how to apply it.",
    ]
    
    # Find test image (try multiple locations)
    test_image = None
    for path_candidate in [
        "tmp_uploaded.jpg",
        "../tmp_uploaded.jpg",
        "agents_capstone/tmp_uploaded.jpg",
        str(project_root / "tmp_uploaded.jpg"),
        str(project_root / "agents_capstone" / "tmp_uploaded.jpg"),
    ]:
        if Path(path_candidate).exists():
            test_image = str(path_candidate)
            break
    
    if not test_image:
        print("❌ No test image found.")
        print("\nFirst, upload a photo via the Streamlit app:")
        print("  export GOOGLE_API_KEY='your_key'")
        print("  export PYTHONPATH=$PWD:$PYTHONPATH")
        print("  python3 -m streamlit run agents_capstone/app_streamlit.py")
        print("\nThen run this script again.")
        sys.exit(1)
    
    print(f"📸 Evaluating on: {test_image}")
    print(f"🎯 Running {len(prompts)} test prompts...")
    print()
    
    # Set up output directory
    os.makedirs("reports", exist_ok=True)
    
    # Run evaluation
    try:
        summary = evaluate_sample(
            image_path=test_image,
            prompts=prompts,
            out_dir="reports",
            use_llm_judge=True
        )
        
        print(f"\n✅ Evaluation complete!")
        print(f"   Score: {summary['avg_overall_score']}/10")
        print(f"   Latency: {summary['avg_latency_sec']:.2f}s")
        print(f"   Reports: ./reports/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
