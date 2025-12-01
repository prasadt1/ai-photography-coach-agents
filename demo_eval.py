#!/usr/bin/env python3
"""
Demo evaluation - simplest way to run evaluation.

Just upload an image via Streamlit app, then run this from any directory.

Usage:
    python3 demo_eval.py
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Run evaluation with auto-detection."""
    project_root = Path(__file__).parent
    
    # Try to run quick_eval.py
    quick_eval = project_root / "agents_capstone" / "quick_eval.py"
    
    if quick_eval.exists():
        print("🚀 Running evaluation...")
        result = subprocess.run([sys.executable, str(quick_eval)])
        sys.exit(result.returncode)
    else:
        print("❌ quick_eval.py not found")
        sys.exit(1)

if __name__ == "__main__":
    main()
