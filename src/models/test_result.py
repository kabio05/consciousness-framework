# This defines what information we keep from each test
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class TestResult:
    trait_id: str          # Which trait was tested
    model_name: str        # Which AI was tested
    score: float           # The final score
    raw_responses: List[str]    # What the AI actually said
    timestamp: datetime    # When we ran the test