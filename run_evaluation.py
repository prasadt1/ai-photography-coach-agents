#!/usr/bin/env python3
"""
Standalone evaluation runner for AI Photography Coach.

This script can be run from any directory and will find the project root automatically.

Usage:
    python3 run_evaluation.py [--help]

Or from agents_capstone/:
    cd agents_capstone && python3 -m run_evaluation
"""
import sys
import os
from pathlib import Path

# Auto-detect project root (2 levels up from this script)
script_dir = Path(__file__).parent
project_root = script_dir

if project_root not in sys.path:
    sys.path.insert(0, str(project_root))

# Now we can import
from agents_capstone.evaluate import evaluate_sample

def main():
    """Run evaluation with demo prompts."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run evaluation on AI Photography Coach"
    )
    parser.add_argument(
        "--image",
        default="tmp_uploaded.jpg",
        help="Path to test image (default: tmp_uploaded.jpg)"
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Output directory for reports (default: reports)"
    )
    parser.add_argument(
        "--use-llm-judge",
        action="store_true",
        default=True,
        help="Use LLM-as-Judge for scoring (default: True)"
    )
    parser.add_argument(
        "--no-llm-judge",
        action="store_true",
        help="Disable LLM-as-Judge, use local heuristics only"
    )
    
    args = parser.parse_args()
    
    if args.no_llm_judge:
        args.use_llm_judge = False
    
    # Sample test prompts
    test_prompts = [
        "How can I improve the composition of this photo?",
        "What camera settings should I use for a sunset shot?",
        "Explain the rule of thirds and how to apply it.",
        "What is ISO and how does it affect image quality?",
        "How can I create better depth of field in this shot?",
    ]
    
    # Check if test image exists
    image_path = Path(args.image)
    
    # Try multiple locations
    if not image_path.exists():
        for alt_path in [
            Path(project_root) / "tmp_uploaded.jpg",
            project_root / "agents_capstone" / "tmp_uploaded.jpg",
        ]:
            if alt_path.exists():
                image_path = alt_path
                break
        print(f"❌ Test image not found: {image_path}")
        print("\nTo run evaluation:")
        print("  1. Upload a photo via the Streamlit app first:")
        print("     python3 -m streamlit run agents_capstone/app_streamlit.py")
        print("  2. Then run this script:")
        print("     python3 run_evaluation.py")
        sys.exit(1)
    
    print(f"Running evaluation on {image_path}")
    print(f"Output directory: {args.output_dir}")
    print(f"LLM-as-Judge: {'enabled' if args.use_llm_judge else 'disabled (heuristics only)'}")
    print(f"\nTest prompts ({len(test_prompts)}):")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"  {i}. {prompt}")
    print()
    
    # Run evaluation
    summary = evaluate_sample(
        image_path=str(image_path),
        prompts=test_prompts,
        out_dir=args.output_dir,
        use_llm_judge=args.use_llm_judge
    )
    
    # Print summary
    print(f"\n📊 Evaluation Results:")
    print(f"  Avg Overall Score: {summary['avg_overall_score']}/10")
    print(f"  Avg Latency: {summary['avg_latency_sec']:.2f}s")
    print(f"  Prompts Evaluated: {summary['num_prompts']}")
    print(f"\n✓ Reports saved to {args.output_dir}/")
    
    # Show file locations
    output_path = Path(args.output_dir)
    if output_path.exists():
        print(f"\nGenerated files:")
        for f in sorted(output_path.glob("evaluation_*")):
            print(f"  • {f.name}")

if __name__ == "__main__":
    main()
