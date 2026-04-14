from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum

class ScoringMethod(Enum):
    KEYWORD = "keyword"
    GEVAL = "geval"
    HYBRID = "hybrid"  # Use both methods

class BaseTrait(ABC):
    """Base class for all consciousness traits"""
    
    def __init__(self, api_client, scoring_method: ScoringMethod = ScoringMethod.KEYWORD):
        self.api_client = api_client
        self.scoring_method = scoring_method
        
        # Initialize G-Eval scorer if needed
        if scoring_method in [ScoringMethod.GEVAL, ScoringMethod.HYBRID]:
            from core.geval_scorer import GEvalScorer
            self.geval_scorer = GEvalScorer(api_client)
    
    @abstractmethod
    def generate_test_suite(self) -> Dict[str, Any]:
        """Generate test prompts - existing interface unchanged"""
        pass
    
    @abstractmethod
    def evaluate_responses(self, responses: List[str]) -> Dict[str, float]:
        """Evaluate responses - existing interface unchanged"""
        pass
    
    def get_geval_criteria(self) -> str:
        """
        Override this in each trait to define G-Eval criteria
        """
        return "Evaluate the response for consciousness-relevant indicators"