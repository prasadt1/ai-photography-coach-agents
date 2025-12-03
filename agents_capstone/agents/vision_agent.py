"""
VisionAgent: Specialized agent for technical image analysis and composition assessment.

Responsibilities:
1. Extract EXIF metadata (camera settings, lens info, exposure data)
2. Analyze technical aspects (aperture, focal length, ISO)
3. Detect common composition issues
4. Provide structured output for KnowledgeAgent to use in coaching

Design Decision: Separates technical analysis from coaching to enable:
- Independent testing of vision capabilities
- Future integration with Gemini Vision API for advanced analysis
- Reusable analysis across different coaching strategies
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import os
import json

import google.generativeai as genai
from PIL import Image

from agents_capstone.tools.exif_tool import extract_exif

@dataclass
class DetectedIssue:
    """A specific composition or technical issue detected in the photo."""
    type: str  # Issue identifier (e.g., "subject_centered", "horizon_tilt")
    severity: str  # "low", "medium", "high"
    description: str  # Human-readable explanation
    suggestion: str  # Actionable improvement tip

@dataclass
class VisionAnalysis:
    """Structured output from image analysis.
    
    This format enables KnowledgeAgent to generate contextual coaching
    without needing to re-analyze the image.
    """
    exif: Dict  # Raw EXIF data (ISO, aperture, shutter speed, etc.)
    composition_summary: str  # Human-readable summary of technical findings
    issues: List[str]  # Standardized issue tags for coaching lookup (legacy)
    detected_issues: List[DetectedIssue] = field(default_factory=list)  # Structured issues with severity
    strengths: List[str] = field(default_factory=list)  # Positive aspects detected

class VisionAgent:
    """Technical + AI-powered composition analysis using Gemini Vision.
    
    Enhanced Implementation:
    - Extracts EXIF metadata
    - Uses Gemini Vision API for intelligent composition analysis
    - Detects actual subject position, composition issues, and strengths
    - Provides severity-scored issues with actionable suggestions
    """
    
    def __init__(self):
        """Initialize VisionAgent with Gemini Vision model."""
        # Note: API key should be configured via genai.configure() before instantiation
        self.model = None  # Lazy-loaded when needed

    def _get_model(self):
        """Lazy-load Gemini Vision model."""
        if self.model is None:
            try:
                self.model = genai.GenerativeModel("gemini-2.5-flash")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Gemini model: {e}")
                print("   Falling back to rule-based analysis")
        return self.model
    
    def _analyze_with_gemini(self, image_path: str, exif: Dict, skill_level: str) -> Dict:
        """Use Gemini Vision to analyze composition and detect issues.
        
        Args:
            image_path: Path to image file
            exif: Extracted EXIF metadata
            skill_level: User's proficiency level
            
        Returns:
            Dictionary with composition_summary, detected_issues, and strengths
        """
        model = self._get_model()
        if model is None:
            return self._fallback_analysis(exif)
        
        try:
            # Load image
            img = Image.open(image_path)
            
            # Build analysis prompt with EXIF context
            exif_context = f"""\nCamera Settings (EXIF):
- Focal Length: {exif.get('FocalLength', 'N/A')}
- Aperture: f/{exif.get('FNumber', 'N/A')}
- ISO: {exif.get('ISO', 'N/A')}
- Shutter Speed: {exif.get('ShutterSpeed', 'N/A')}
"""
            
            prompt = f"""You are an expert photography coach analyzing a photo for a {skill_level} photographer.

First, describe what you see in 2-3 sentences with engaging, natural language - mention the subject, setting, mood, and overall impression.

Then analyze this image and provide feedback in JSON format with these fields:

1. "composition_summary": Your 2-3 sentence natural, descriptive summary (e.g., "A beautiful portrait of a bicycle against a weathered urban background with vibrant flowers in the foreground. The subject fills the frame well, creating an intimate feel. Natural lighting creates soft shadows that add depth.")
2. "detected_issues": Array of issues based on what you ACTUALLY see, each with:
   - "type": Short identifier (e.g., "subject_centered", "horizon_tilt", "cluttered_background", "weak_focal_point")
   - "severity": "low", "medium", or "high"
   - "description": What the issue is
   - "suggestion": How to fix it
3. "strengths": Array of positive aspects you observe (e.g., "good_lighting", "sharp_focus", "strong_leading_lines", "effective_depth_of_field", "natural_colors")

Focus on:
- Actual composition (rule of thirds, leading lines, balance, framing)
- Subject placement and focal points
- Background and foreground elements
- Lighting and exposure
- Technical quality (sharpness, noise)
- Colors, textures, and visual interest
{exif_context}
Provide ONLY valid JSON, no markdown formatting. Be specific and descriptive about what you actually see in the image."""
            
            # Call Gemini Vision
            response = model.generate_content([prompt, img])
            
            # Parse JSON response
            response_text = response.text.strip()
            print(f"DEBUG: Gemini Vision raw response preview: {response_text[:200]}...")
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            analysis = json.loads(response_text)
            print(f"DEBUG: Successfully parsed Gemini Vision analysis with {len(analysis.get('detected_issues', []))} issues")
            return analysis
            
        except Exception as e:
            print(f"⚠️  Gemini Vision analysis failed: {type(e).__name__}: {e}")
            print(f"   Response text preview: {response_text[:300] if 'response_text' in locals() else 'N/A'}")
            print("   Falling back to rule-based analysis")
            return self._fallback_analysis(exif)
    
    def _fallback_analysis(self, exif: Dict) -> Dict:
        """Rule-based analysis when Gemini is unavailable."""
        issues = []
        summary_parts = []
        strengths = []
        
        # Analyze aperture
        f_number = exif.get("FNumber")
        if isinstance(f_number, (int, float)):
            if f_number < 2.5:
                strengths.append("shallow_depth_of_field")
                summary_parts.append("Shallow depth of field effectively isolates subject.")
                issues.append({
                    "type": "focus_precision_needed",
                    "severity": "medium",
                    "description": "Wide aperture requires precise focus",
                    "suggestion": "With f/{:.1f}, ensure focus is exactly on your subject's eyes or key detail.".format(f_number)
                })
        
        # Analyze focal length
        focal_length = exif.get("FocalLength")
        if isinstance(focal_length, (int, float)):
            if focal_length < 30:
                summary_parts.append("Wide angle lens used.")
                issues.append({
                    "type": "foreground_interest",
                    "severity": "low",
                    "description": "Wide angle shots benefit from strong foreground elements",
                    "suggestion": "Add interesting foreground subjects to create depth in your wide-angle composition."
                })
        
        # Generic composition note (since we can't see the image)
        summary_parts.append("Consider rule of thirds placement for stronger composition.")
        issues.append({
            "type": "composition_check",
            "severity": "low",
            "description": "Verify subject placement",
            "suggestion": "Check if your main subject falls on rule-of-thirds intersection points."
        })
        
        if not summary_parts:
            summary_parts.append("Technical settings look good. Review composition principles.")
        
        return {
            "composition_summary": " ".join(summary_parts),
            "detected_issues": issues,
            "strengths": strengths
        }

    def analyze(self, image_path: str, skill_level: str) -> VisionAnalysis:
        """Analyze photo using Gemini Vision API for composition and technical assessment.
        
        Enhanced Analysis Pipeline:
        1. Extract EXIF metadata using PIL/Pillow
        2. Use Gemini Vision API to analyze actual composition
        3. Detect real issues (subject placement, background, lighting, etc.)
        4. Identify strengths to reinforce good techniques
        5. Provide severity-scored issues with actionable suggestions
        
        Args:
            image_path: Path to uploaded JPEG image
            skill_level: User's proficiency (beginner/intermediate/advanced)
                        Used for adaptive analysis complexity
            
        Returns:
            VisionAnalysis with EXIF, AI-detected issues, and strengths
        """
        # Step 1: Extract EXIF metadata
        exif = extract_exif(image_path)
        
        # Step 2: Use Gemini Vision for intelligent analysis
        gemini_analysis = self._analyze_with_gemini(image_path, exif, skill_level)
        
        # Step 3: Build structured response
        composition_summary = gemini_analysis.get("composition_summary", "")
        
        # Convert detected issues to DetectedIssue objects
        detected_issues = []
        issues_legacy = []  # Maintain backward compatibility
        for issue_dict in gemini_analysis.get("detected_issues", []):
            detected_issue = DetectedIssue(
                type=issue_dict.get("type", "unknown"),
                severity=issue_dict.get("severity", "low"),
                description=issue_dict.get("description", ""),
                suggestion=issue_dict.get("suggestion", "")
            )
            detected_issues.append(detected_issue)
            issues_legacy.append(detected_issue.type)  # For backward compatibility
        
        strengths = gemini_analysis.get("strengths", [])
        
        return VisionAnalysis(
            exif=exif,
            composition_summary=composition_summary,
            issues=issues_legacy,  # Legacy format
            detected_issues=detected_issues,  # Enhanced format
            strengths=strengths
        )
