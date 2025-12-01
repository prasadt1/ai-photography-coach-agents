from dataclasses import dataclass
from typing import List, Dict

from agents_capstone.tools.exif_tool import extract_exif

@dataclass
class VisionAnalysis:
    exif: Dict
    composition_summary: str
    issues: List[str]

class VisionAgent:
    """Technical + simple composition analysis."""

    def analyze(self, image_path: str, skill_level: str) -> VisionAnalysis:
        exif = extract_exif(image_path)

        issues: List[str] = []
        summary_parts: List[str] = []

        f_number = exif.get("FNumber")
        focal_length = exif.get("FocalLength")

        if isinstance(f_number, (int, float)) and f_number < 2.5:
            issues.append("shallow_depth_of_field")
            summary_parts.append(
                "Shallow depth of field – good for isolating subjects, but watch focus."
            )

        if isinstance(focal_length, (int, float)) and focal_length < 30:
            summary_parts.append(
                "Wide focal length – consider adding strong foreground for depth."
            )

        summary_parts.append(
            "Subject appears roughly central; try placing it on a third for stronger composition."
        )
        issues.append("subject_centered")

        return VisionAnalysis(
            exif=exif,
            composition_summary=" ".join(summary_parts),
            issues=issues,
        )
