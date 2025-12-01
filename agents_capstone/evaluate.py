"""Evaluation harness for the AI Photography Coach.

Runs synthetic test prompts and scores responses using:
1. LLM-as-Judge (relevance, completeness, accuracy)
2. Local heuristics (response length, includes technical terms)
3. Latency and error tracking

Outputs:
- CSV report with scores for each response
- HTML summary with charts and aggregates
- JSON detailed logs for debugging
"""
import json
import time
import csv
import os
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Handle imports from both project root and agents_capstone/ directory
if "agents_capstone" not in sys.modules:
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

import google.generativeai as genai

# Configure Gemini API for LLM-as-Judge scoring
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

from agents_capstone.agents.orchestrator import Orchestrator
from agents_capstone.agents.vision_agent import VisionAgent
from agents_capstone.agents.knowledge_agent import KnowledgeAgent

# Scoring rubric
SCORING_RUBRIC = """
You are an expert photography instructor evaluating an AI coach's response.

Score the following response on a scale of 1-10 for each criterion:

**Relevance (1-10):** How well does the response address the user's question?
**Completeness (1-10):** Does it provide sufficient detail and context?
**Accuracy (1-10):** Is the technical advice correct and grounded?
**Actionability (1-10):** Can the user act on this advice immediately?

Response to score:
"{response}"

Provide a JSON object with keys: relevance, completeness, accuracy, actionability, and a brief explanation.
"""


def score_response_with_llm(response: str, llm_model: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """Use LLM-as-Judge to score a coaching response."""
    try:
        model = genai.GenerativeModel(llm_model)
        prompt = SCORING_RUBRIC.format(response=response)
        result = model.generate_content(prompt)
        text = result.text
        
        # Try to parse JSON from response
        try:
            # Find JSON in response (may be wrapped in markdown code blocks)
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
            elif "{" in text:
                json_str = text[text.index("{"):text.rindex("}")+1]
            else:
                json_str = text
            
            scores = json.loads(json_str)
            return {
                "relevance": scores.get("relevance", 0),
                "completeness": scores.get("completeness", 0),
                "accuracy": scores.get("accuracy", 0),
                "actionability": scores.get("actionability", 0),
                "explanation": scores.get("explanation", ""),
                "raw_response": text,
            }
        except json.JSONDecodeError:
            return {
                "relevance": 0,
                "completeness": 0,
                "accuracy": 0,
                "actionability": 0,
                "explanation": f"Failed to parse LLM scoring: {text[:100]}",
                "raw_response": text,
            }
    except Exception as e:
        return {
            "relevance": 0,
            "completeness": 0,
            "accuracy": 0,
            "actionability": 0,
            "explanation": f"LLM scoring error: {str(e)}",
            "raw_response": "",
        }


def score_response_heuristic(response: str) -> Dict[str, Any]:
    """Apply simple heuristic scoring (length, tech terms, etc.)."""
    if not response:
        return {"length_score": 0, "tech_score": 0}
    
    # Length heuristic: 100-500 chars is good
    length = len(response)
    if 100 <= length <= 500:
        length_score = 8
    elif length > 500:
        length_score = 6  # Too verbose
    elif length < 50:
        length_score = 3  # Too short
    else:
        length_score = 5
    
    # Tech term heuristic: includes photography-specific vocabulary
    tech_terms = [
        "composition", "exposure", "iso", "aperture", "focal length",
        "shutter speed", "depth of field", "bokeh", "rule of thirds",
        "leading lines", "contrast", "dynamic range", "white balance",
        "histogram", "metering", "autofocus"
    ]
    tech_count = sum(1 for term in tech_terms if term.lower() in response.lower())
    tech_score = min(10, tech_count * 2)  # Up to 10
    
    return {
        "length_score": length_score,
        "tech_score": tech_score,
        "response_length": length,
        "tech_terms_found": tech_count,
    }


def evaluate_sample(
    image_path: str,
    prompts: List[str],
    out_dir: str = "reports",
    use_llm_judge: bool = True,
) -> Dict[str, Any]:
    """Run evaluation on a set of test prompts.
    
    Args:
        image_path: Path to test image
        prompts: List of test prompts
        out_dir: Output directory for reports
        use_llm_judge: Whether to use LLM-as-Judge scoring
    
    Returns:
        Dictionary with results summary
    """
    os.makedirs(out_dir, exist_ok=True)
    
    vision = VisionAgent()
    know = KnowledgeAgent()
    orch = Orchestrator(vision, know)
    
    results = []
    
    print(f"Running evaluation on {len(prompts)} prompts...")
    for i, prompt in enumerate(prompts, 1):
        print(f"  [{i}/{len(prompts)}] {prompt[:50]}...")
        t0 = time.time()
        
        try:
            # Use unique user_id per prompt to avoid cross-contamination
            res = orch.run(user_id=f"eval_user_{i}", image_path=image_path, query=prompt)
            latency = time.time() - t0
            coach_text = res.get("coach", {}).get("text", "")
            vision_summary = res.get("vision", {}).get("composition_summary", "") if res.get("vision") else ""
            
            # Debug: Check if we got a fallback response
            if coach_text.startswith("Based on your question about"):
                print(f"    ⚠️  WARNING: Got fallback response (Gemini API may have failed)")
            
            # Score with LLM if available
            llm_scores = {}
            if use_llm_judge and coach_text:
                llm_scores = score_response_with_llm(coach_text)
            
            # Score with heuristics
            heuristic_scores = score_response_heuristic(coach_text)
            
            # Combine scores
            overall_score = 0
            if llm_scores:
                overall_score = (
                    llm_scores.get("relevance", 0) +
                    llm_scores.get("completeness", 0) +
                    llm_scores.get("accuracy", 0) +
                    llm_scores.get("actionability", 0)
                ) / 4
            else:
                overall_score = (heuristic_scores.get("length_score", 0) + heuristic_scores.get("tech_score", 0)) / 2
            
            result = {
                "prompt": prompt,
                "coach_response": coach_text,
                "vision_summary": vision_summary,
                "latency_sec": round(latency, 3),
                "overall_score": round(overall_score, 2),
                "llm_scores": llm_scores,
                "heuristic_scores": heuristic_scores,
                "status": "success",
            }
        except Exception as e:
            result = {
                "prompt": prompt,
                "coach_response": "",
                "vision_summary": "",
                "latency_sec": round(time.time() - t0, 3),
                "overall_score": 0,
                "llm_scores": {},
                "heuristic_scores": {},
                "status": "error",
                "error": str(e),
            }
        
        results.append(result)
    
    # Write reports
    json_path = os.path.join(out_dir, "evaluation_detailed.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✓ Detailed report: {json_path}")
    
    # Write CSV summary
    csv_path = os.path.join(out_dir, "evaluation_summary.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Prompt", "Overall Score", "Latency (s)",
            "Relevance", "Completeness", "Accuracy", "Actionability",
            "Length Score", "Tech Score", "Status"
        ])
        for r in results:
            writer.writerow([
                r["prompt"],
                r["overall_score"],
                r["latency_sec"],
                r["llm_scores"].get("relevance", "-"),
                r["llm_scores"].get("completeness", "-"),
                r["llm_scores"].get("accuracy", "-"),
                r["llm_scores"].get("actionability", "-"),
                r["heuristic_scores"].get("length_score", "-"),
                r["heuristic_scores"].get("tech_score", "-"),
                r["status"],
            ])
    print(f"✓ CSV summary: {csv_path}")
    
    # Generate HTML report
    html_path = os.path.join(out_dir, "evaluation_report.html")
    avg_score = sum(r["overall_score"] for r in results) / len(results) if results else 0
    avg_latency = sum(r["latency_sec"] for r in results) / len(results) if results else 0
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Photography Coach - Evaluation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2em; background: #f5f5f5; }}
            h1 {{ color: #333; }}
            .summary {{ background: white; padding: 1em; border-radius: 5px; margin: 1em 0; }}
            .metric {{ display: inline-block; margin: 1em 2em 1em 0; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
            .metric-label {{ font-size: 12px; color: #666; }}
            table {{ width: 100%; border-collapse: collapse; background: white; }}
            th {{ background: #0066cc; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            tr:hover {{ background: #f9f9f9; }}
            .score-good {{ color: #28a745; font-weight: bold; }}
            .score-fair {{ color: #ffc107; font-weight: bold; }}
            .score-poor {{ color: #dc3545; font-weight: bold; }}
            .error {{ color: #dc3545; }}
            .response-text {{ max-width: 400px; word-wrap: break-word; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h1>AI Photography Coach - Evaluation Report</h1>
        <div class="summary">
            <h2>Summary Metrics</h2>
            <div class="metric">
                <div class="metric-value">{avg_score:.2f}</div>
                <div class="metric-label">Avg Overall Score (0-10)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(results)}</div>
                <div class="metric-label">Prompts Evaluated</div>
            </div>
            <div class="metric">
                <div class="metric-value">{avg_latency:.2f}s</div>
                <div class="metric-label">Avg Latency</div>
            </div>
        </div>
        <h2>Results</h2>
        <table>
            <tr>
                <th>Prompt</th>
                <th>Overall Score</th>
                <th>Relevance</th>
                <th>Latency (s)</th>
                <th>Response Preview</th>
            </tr>
    """
    
    for r in results:
        import html as html_module
        score_class = "score-good" if r["overall_score"] >= 7 else "score-fair" if r["overall_score"] >= 4 else "score-poor"
        relevance = r["llm_scores"].get("relevance", "-")
        response_preview = r["coach_response"][:100] + "..." if len(r["coach_response"]) > 100 else r["coach_response"]
        
        # Escape HTML entities to prevent encoding issues
        prompt_escaped = html_module.escape(r["prompt"])
        preview_escaped = html_module.escape(response_preview)
        
        html_content += f"""
            <tr>
                <td>{prompt_escaped}</td>
                <td class="{score_class}">{r["overall_score"]}</td>
                <td>{relevance}</td>
                <td>{r["latency_sec"]}</td>
                <td class="response-text">{preview_escaped}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ HTML report: {html_path}")
    
    return {
        "num_prompts": len(results),
        "avg_overall_score": round(avg_score, 2),
        "avg_latency_sec": round(avg_latency, 2),
        "results": results,
    }


if __name__ == "__main__":
    # Sample evaluation
    sample_prompts = [
        "How can I improve the composition of this photo?",
        "What is ISO and how does it affect image quality?",
        "How should I use the rule of thirds in this scene?",
        "What camera settings would you recommend for this lighting?",
        "How can I create better depth of field in this shot?",
    ]
    
    # Check if a test image exists
    test_image = "tmp_uploaded.jpg"
    if os.path.exists(test_image):
        print(f"Running evaluation on {test_image}...")
        summary = evaluate_sample(test_image, sample_prompts, use_llm_judge=True)
        print(f"\nEvaluation Summary:")
        print(f"  Avg Overall Score: {summary['avg_overall_score']}/10")
        print(f"  Avg Latency: {summary['avg_latency_sec']:.2f}s")
        print(f"  Prompts Evaluated: {summary['num_prompts']}")
    else:
        print(f"Test image not found: {test_image}")
        print("To run evaluation, upload a photo via the Streamlit app first.")
