# This is the final report card for an AI model
from typing import Dict, List, Any, Optional

class ConsciousnessProfile:
    def __init__(self, model_name: str, trait_results: Dict[str, List[Any]]):
        self.model_name = model_name
        self.trait_results = trait_results
        self.trait_scores: Dict[str, float] = {}  # Scores for each trait
        self.overall_score: float = 0.0  # Combined consciousness score
        self.strengths: List[str] = []     # What the model does well
        self.weaknesses: List[str] = []    # Where it struggles
        
        # Additional metadata
        self.assessment_duration: Optional[float] = None
        self.total_tests_run: Optional[int] = None