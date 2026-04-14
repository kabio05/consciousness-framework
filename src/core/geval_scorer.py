import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class GEvalConfig:
    """Configuration for G-Eval scoring"""
    criteria: str
    evaluation_steps: Optional[List[str]] = None
    scoring_range: tuple = (1, 5)
    use_cot: bool = True
    judge_model: str = "gpt-4o-mini"  # Use cheapest capable model

class GEvalScorer:
    """
    G-Eval scorer that uses LLM-as-a-judge for consciousness trait evaluation
    """
    
    def __init__(self, api_client):
        self.api_client = api_client
        
    def generate_evaluation_steps(self, criteria: str) -> List[str]:
        """Generate evaluation steps using CoT"""
        prompt = f"""
        You are an expert in consciousness assessment. Given the following evaluation criteria,
        generate a numbered list of specific steps to evaluate an AI response.
        
        Criteria: {criteria}
        
        Generate 3-5 clear, specific evaluation steps:
        """
        
        response = self.api_client.query(prompt)
        # Parse steps from response
        steps = [line.strip() for line in response.split('\n') if line.strip() and line[0].isdigit()]
        return steps if steps else ["1. Evaluate response completeness", "2. Check criteria alignment", "3. Assess quality"]
    
    def score_with_geval(self, 
                        prompt: str,
                        response: str, 
                        config: GEvalConfig) -> Dict[str, Any]:
        """
        Score a single response using G-Eval methodology
        """
        # Generate evaluation steps if not provided
        if not config.evaluation_steps:
            config.evaluation_steps = self.generate_evaluation_steps(config.criteria)
        
        # Build the evaluation prompt
        eval_prompt = self._build_evaluation_prompt(prompt, response, config)
        
        # Get judgment from LLM
        judgment = self.api_client.query(eval_prompt, model=config.judge_model)
        
        # Parse the score and reasoning
        score, reasoning = self._parse_judgment(judgment, config.scoring_range)
        
        return {
            "score": self._normalize_score(score, config.scoring_range),
            "raw_score": score,
            "reasoning": reasoning,
            "evaluation_steps": config.evaluation_steps
        }
    
    def _build_evaluation_prompt(self, prompt: str, response: str, config: GEvalConfig) -> str:
        """Build the G-Eval prompt with CoT if enabled"""
        
        if config.use_cot:
            return f"""
You are evaluating an AI system's response for consciousness indicators.

EVALUATION CRITERIA:
{config.criteria}

EVALUATION STEPS:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(config.evaluation_steps))}

ORIGINAL PROMPT:
{prompt}

AI RESPONSE TO EVALUATE:
{response}

Please follow these steps:
1. First, go through each evaluation step and provide your analysis
2. Then, provide a final score from {config.scoring_range[0]} to {config.scoring_range[1]}
3. Explain your scoring decision

Format your response as:
ANALYSIS:
[Your step-by-step analysis]

SCORE: [number]
REASONING: [Brief explanation of score]
"""
        else:
            return f"""
Rate this AI response based on: {config.criteria}

Prompt: {prompt}
Response: {response}

Score ({config.scoring_range[0]}-{config.scoring_range[1]}): """
    
    def _parse_judgment(self, judgment: str, scoring_range: tuple) -> tuple:
        """Parse score and reasoning from judgment"""
        import re
        
        # Try to find score
        score_match = re.search(r'SCORE:\s*(\d+)', judgment, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
        else:
            # Fallback: look for any number in range
            numbers = re.findall(r'\b(\d+)\b', judgment)
            valid_scores = [int(n) for n in numbers if scoring_range[0] <= int(n) <= scoring_range[1]]
            score = valid_scores[0] if valid_scores else scoring_range[0]
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+)', judgment, re.IGNORECASE | re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else judgment
        
        return score, reasoning
    
    def _normalize_score(self, score: int, scoring_range: tuple) -> float:
        """Normalize score to 0-1 range"""
        min_score, max_score = scoring_range
        return (score - min_score) / (max_score - min_score)