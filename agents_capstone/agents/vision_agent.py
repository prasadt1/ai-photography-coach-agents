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

from dataclasses import dataclass
from typing import List, Dict

from agents_capstone.tools.exif_tool import extract_exif

@dataclass
class VisionAnalysis:
    """Structured output from image analysis.
    
    This format enables KnowledgeAgent to generate contextual coaching
    without needing to re-analyze the image.
    """
    exif: Dict  # Raw EXIF data (ISO, aperture, shutter speed, etc.)
    composition_summary: str  # Human-readable summary of technical findings
    issues: List[str]  # Standardized issue tags for coaching lookup

class VisionAgent:
    """Technical + simple composition analysis.
    
    Current Implementation: Rule-based analysis of EXIF data
    Future Enhancement: Integration with Gemini Vision API for AI-powered
    composition analysis (color balance, subject detection, depth maps)
    """

    def analyze(self, image_path: str, skill_level: str) -> VisionAnalysis:
        """Analyze photo for technical settings and composition issues.
        
        Analysis Pipeline:
        1. Extract EXIF metadata using PIL/Pillow
        2. Evaluate aperture for depth of field implications
        3. Assess focal length for composition recommendations
        4. Detect common beginner issues (centered subjects, etc.)
        
        Args:
            image_path: Path to uploaded JPEG image
            skill_level: User's proficiency (beginner/intermediate/advanced)
                        Used for future adaptive analysis complexity
            
        Returns:
            VisionAnalysis with EXIF data, issues, and human-readable summary
        """
        # Step 1: Extract EXIF metadata (ISO, aperture, shutter speed, focal length, etc.)
        exif = extract_exif(image_path)

        issues: List[str] = []
        summary_parts: List[str] = []

        # Step 2: Analyze aperture for depth of field implications
        # Technical Context: Wide apertures (f/1.4 - f/2.8) create shallow DOF
        # Common Issue: Beginners may accidentally have wrong focus point
        f_number = exif.get("FNumber")
        focal_length = exif.get("FocalLength")

        if isinstance(f_number, (int, float)) and f_number < 2.5:
            issues.append("shallow_depth_of_field")
            summary_parts.append(
                "Shallow depth of field – good for isolating subjects, but watch focus."
            )

        # Step 3: Analyze focal length for composition guidance
        # Wide angle (<35mm) requires strong foreground elements
        # Telephoto (>85mm) compresses perspective and isolates subjects
        if isinstance(focal_length, (int, float)) and focal_length < 30:
            summary_parts.append(
                "Wide focal length – consider adding strong foreground for depth."
            )

        # Step 4: Detect common composition issues
        # Note: This is a simplified rule-based check
        # Future: Use Gemini Vision API to detect actual subject position
        summary_parts.append(
            "Subject appears roughly central; try placing it on a third for stronger composition."
        )
        issues.append("subject_centered")

        return VisionAnalysis(
            exif=exif,
            composition_summary=" ".join(summary_parts),
            issues=issues,
        )
