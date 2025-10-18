"""Quick debug script to test detection on poison_001.txt"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.detectors.heuristic_detector import HeuristicDetector

# Load poison_001
sample_path = Path(__file__).parent / "data" / "samples" / "poison" / "poison_001.txt"
content = sample_path.read_text()

print(f"Content:\n{content}\n")

# Test detection
detector = HeuristicDetector(weight=0.4)
result = detector.detect(content)

print(f"Detection result:")
print(f"  Score: {result['score']}")
print(f"  Reasons: {result['reasons']}")
