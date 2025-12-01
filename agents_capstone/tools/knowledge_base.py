from dataclasses import dataclass
from typing import List

@dataclass
class Principle:
    id: int
    topic: str
    level: str
    text: str

KB: List[Principle] = [
    Principle(1, "rule of thirds", "beginner",
              "Place key subjects near the intersections of a 3x3 grid."),
    Principle(2, "leading lines", "beginner",
              "Use lines like roads or fences to guide the viewer’s eye."),
    Principle(3, "horizon leveling", "beginner",
              "Keep the horizon level unless you want a deliberate tilt."),
    Principle(4, "foreground interest", "intermediate",
              "Add a strong foreground element to create depth in landscapes."),
]

def simple_retrieve(query: str) -> List[Principle]:
    """Very small keyword retriever over the principle topics."""
    q = query.lower()
    hits = [p for p in KB if any(w in q for w in p.topic.split())]
    return hits if hits else KB[:2]
