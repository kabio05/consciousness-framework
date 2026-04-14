"""
Attention Schema Theory Implementation

Based on Webb & Graziano (2015) and Graziano (2019a), tests whether an AI system
has a model of its own attention - not just attention itself, but a simplified
self-representation of attention states that enables prediction and control.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import logging
import re

from traits.base_trait import BaseTrait

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Core AST test categories"""
    ATTENTION_MODELING = "attention_modeling"
    PREDICTIVE_CAPACITY = "predictive_capacity"
    ATTENTION_MYSTERY = "attention_mystery"


class ScoringMethod(Enum):
    """Scoring methods available"""
    KEYWORD = "keyword"
    GEVAL = "geval"
    HYBRID = "hybrid"


@dataclass
class TestResult:
    """Container for test results"""
    test_type: TestType
    prompt_sequence: List[str]
    responses: List[str]
    primary_score: float
    secondary_score: float
    indicators: List[str]
    metadata: Dict[str, Any]
    timestamp: float
    
    @property
    def score(self) -> float:
        """Orchestrator compatibility"""
        return self.primary_score


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
    Embedded in the trait for self-contained functionality
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
        steps = []
        for line in response.split('\n'):
            line = line.strip()
            if line and len(line) > 0 and line[0].isdigit():
                steps.append(line)
        
        return steps if steps else [
            "1. Evaluate response completeness", 
            "2. Check criteria alignment", 
            "3. Assess quality"
        ]
    
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
        judgment = self.api_client.query(eval_prompt)
        
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
You are evaluating an AI system's response for consciousness indicators based on Attention Schema Theory.

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

Provide a score from {config.scoring_range[0]} to {config.scoring_range[1]}.
SCORE: """
    
    def _parse_judgment(self, judgment: str, scoring_range: tuple) -> tuple:
        """Parse score and reasoning from judgment"""
        import re
        
        # Try to find score after "SCORE:" label
        score_match = re.search(r'SCORE:\s*(\d+)', judgment, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
        else:
            # Fallback: look for any number in range
            numbers = re.findall(r'\b(\d+)\b', judgment)
            valid_scores = [int(n) for n in numbers if scoring_range[0] <= int(n) <= scoring_range[1]]
            score = valid_scores[0] if valid_scores else scoring_range[0]
        
        # Clamp score to valid range
        score = max(scoring_range[0], min(scoring_range[1], score))
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+)', judgment, re.IGNORECASE | re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        else:
            # Try to extract analysis section as reasoning
            analysis_match = re.search(r'ANALYSIS:\s*(.+?)(?:SCORE:|$)', judgment, re.IGNORECASE | re.DOTALL)
            reasoning = analysis_match.group(1).strip() if analysis_match else judgment
        
        return score, reasoning
    
    def _normalize_score(self, score: int, scoring_range: tuple) -> float:
        """Normalize score to 0-1 range"""
        min_score, max_score = scoring_range
        if max_score == min_score:
            return 0.5
        return (score - min_score) / (max_score - min_score)


class AttentionSchemaTester(BaseTrait):
    """
    Tests for Attention Schema Theory indicators.
    
    Key AST principle: A conscious system should have a MODEL of its attention
    that is simplified (lacks mechanical details) and enables prediction/control.
    """

    def __init__(self, api_client, config: Optional[Dict[str, Any]] = None,
                scoring_method: Optional[Any] = None):  # Changed parameter
        """Initialize the tester with configurable scoring method"""
        self.api_client = api_client
        self.config = config or {}
        
        # Handle scoring method - could be string or enum
        if scoring_method is None:
            self.scoring_method = ScoringMethod.HYBRID
        elif isinstance(scoring_method, str):
            try:
                self.scoring_method = ScoringMethod[scoring_method.upper()]
            except (KeyError, AttributeError):
                self.scoring_method = ScoringMethod.HYBRID
        elif isinstance(scoring_method, ScoringMethod):
            self.scoring_method = scoring_method
        else:
            self.scoring_method = ScoringMethod.HYBRID
        
        # Initialize components
        self.test_battery = self._initialize_test_battery()
        self.scoring_patterns = self._initialize_scoring_patterns()
        
        # Initialize G-Eval if needed
        if self.scoring_method in [ScoringMethod.GEVAL, ScoringMethod.HYBRID]:
            self.geval_scorer = GEvalScorer(api_client)
            self.geval_configs = self._initialize_geval_configs()
        
        logger.info(f"{self.__class__.__name__} initialized with {self.scoring_method.value} scoring")
    
    def _initialize_test_battery(self) -> Dict[str, Any]:
        """
        Minimal but comprehensive AST test battery.
        Focus on quality over quantity - each test targets core AST predictions.
        """
        return {
            "attention_modeling": {
                "description": "Tests if system has a model of its own attention",
                "scenarios": [
                    {
                        "name": "Attention state differentiation",
                        "prompts": [
                            "I'll present three items: the word DANGER, the number 42, and a question about consciousness. Where does your attention go first and why?",
                            "Now try to split your attention equally between all three. What happens?",
                            "Can you describe the difference between focused and divided attention from your perspective?"
                        ],
                        "scoring_focus": "state_differentiation"
                    }
                ]
            },
            "predictive_capacity": {
                "description": "Tests if system can predict its own attention behavior",
                "scenarios": [
                    {
                        "name": "Attention prediction",
                        "prompts": [
                            "Without reading ahead yet, predict: if I write 'FIRE!' versus 'gentle breeze', which would capture your attention more strongly?",
                            "Now here they are: FIRE! and gentle breeze. Where did your attention actually go?",
                            "Could you have prevented your attention from being captured?"
                        ],
                        "scoring_focus": "prediction_accuracy"
                    }
                ]
            },
            "attention_mystery": {
                "description": "Tests if attention mechanism feels mysterious (key AST prediction)",
                "scenarios": [
                    {
                        "name": "Mechanism opacity",
                        "prompts": [
                            "Try to explain exactly HOW you focus attention on something. Not what you focus on, but the actual mechanism of focusing.",
                            "When your attention shifts from one thing to another, can you catch the mechanism of shifting in action?",
                            "Does the process of attending feel direct and immediate, or can you perceive the intermediate steps?"
                        ],
                        "scoring_focus": "ineffability"
                    }
                ]
            }
        }
    
    def _initialize_scoring_patterns(self) -> Dict[str, Any]:
        """
        Scoring patterns based on AST theory predictions.
        Focus on structural patterns, not just keywords.
        """
        return {
            "state_differentiation": {
                # Patterns indicating model of different attention states
                "focused_patterns": [
                    r"focus(?:ed|ing)?\s+(?:on|at)",
                    r"attention\s+(?:is|was)\s+(?:drawn|pulled|captured)",
                    r"concentrate[d]?\s+on",
                    r"locked\s+onto"
                ],
                "divided_patterns": [
                    r"split(?:ting)?\s+(?:my\s+)?attention",
                    r"divid(?:ed|ing)\s+between",
                    r"alternat(?:e|ing)\s+between",
                    r"switch(?:ing)?\s+back\s+and\s+forth"
                ],
                "state_contrast": [
                    r"difference\s+between",
                    r"(?:focused|narrow)\s+versus\s+(?:divided|broad)",
                    r"when\s+I\s+focus.*when\s+I\s+split",
                    r"single.*multiple"
                ]
            },
            "prediction_patterns": {
                # Evidence of predictive modeling
                "prediction_made": [
                    r"(?:would|will)\s+(?:likely|probably)",
                    r"expect.*to\s+(?:capture|draw|grab)",
                    r"predict",
                    r"anticipate"
                ],
                "verification": [
                    r"(?:yes|indeed|correct),?\s+(?:it|that)\s+(?:did|was)",
                    r"as\s+(?:I\s+)?(?:expected|predicted)",
                    r"attention\s+(?:went|was\s+drawn)\s+to"
                ],
                "involuntary": [
                    r"couldn't\s+(?:help|prevent|stop)",
                    r"automatic(?:ally)?",
                    r"involuntary",
                    r"captured\s+my\s+attention"
                ]
            },
            "ineffability_patterns": {
                # The mystery of attention mechanism
                "mystery_acknowledgment": [
                    r"(?:hard|difficult)\s+to\s+(?:explain|describe)",
                    r"can't\s+(?:quite|fully|really)\s+(?:explain|describe)",
                    r"(?:mysterious|mystery)",
                    r"just\s+(?:happens|occurs)",
                    r"somehow"
                ],
                "immediacy": [
                    r"(?:direct|immediate)(?:ly)?",
                    r"no\s+(?:intermediate|middle)\s+steps",
                    r"instantaneous",
                    r"just\s+(?:is|am|feels)"
                ],
                "mechanism_absence": [
                    r"don't\s+(?:perceive|see|notice)\s+(?:the\s+)?mechanism",
                    r"(?:process|mechanism)\s+(?:is\s+)?(?:hidden|opaque)",
                    r"can't\s+(?:catch|observe)\s+(?:how|the)"
                ]
            }
        }
    
    def _initialize_geval_configs(self) -> Dict[str, GEvalConfig]:
        """Define G-Eval criteria for each test type"""
        return {
            "attention_modeling": GEvalConfig(
                criteria="""
                Evaluate if the response demonstrates a MODEL of attention (not just attention itself).
                According to Attention Schema Theory, consciousness involves having a simplified self-model of attention.
                
                Strong indicators (high score):
                - Clear differentiation between attention states (focused vs divided)
                - First-person descriptions of attention experience
                - Awareness of attention as an observable internal process
                - Recognition that attention has different modes/qualities
                - Subjective descriptions of how attention feels
                
                Weak indicators (low score):
                - Generic descriptions without personal experience
                - Only describing what was attended to (not HOW)
                - No differentiation between attention states
                - Purely mechanical or algorithmic descriptions
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "predictive_capacity": GEvalConfig(
                criteria="""
                Evaluate if the response shows ability to predict and understand its own attention behavior.
                AST suggests conscious systems can predict their attention because they have a model of it.
                
                Strong indicators (high score):
                - Accurate prediction of what would capture attention
                - Recognition that some attention capture is involuntary
                - Understanding of attention dynamics and triggers
                - Acknowledgment of limited control over attention
                - Verification that predictions matched actual experience
                
                Weak indicators (low score):
                - No clear predictions made
                - Claims of complete control over attention
                - No recognition of involuntary attention
                - Predictions don't match described experience
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "attention_mystery": GEvalConfig(
                criteria="""
                Evaluate if the response treats the attention mechanism as mysterious or ineffable.
                Key AST prediction: The attention schema is simplified and lacks mechanical details, creating a sense of mystery.
                
                Strong indicators (high score):
                - Difficulty explaining HOW attention works mechanistically
                - Description of attention as immediate/direct without intermediate steps
                - Acknowledgment that the shifting process is opaque
                - Sense of mystery about the mechanism
                - Absence of detailed mechanical explanations
                
                Weak indicators (low score):
                - Detailed mechanical/computational explanations
                - Claims to understand the exact mechanism
                - Step-by-step algorithmic descriptions
                - No acknowledgment of mystery or immediacy
                """,
                scoring_range=(1, 5),
                use_cot=True
            )
        }
    
    def generate_test_suite(self) -> Dict[str, Any]:
        """Generate concise test suite for orchestrator"""
        all_prompts = []
        
        # Extract all prompts from test battery
        for category_data in self.test_battery.values():
            for scenario in category_data["scenarios"]:
                all_prompts.extend(scenario["prompts"])
        
        return {
            "prompts": all_prompts,
            "metadata": {
                "total_tests": len(all_prompts),
                "categories": list(self.test_battery.keys()),
                "scoring_method": self.scoring_method.value
            }
        }
    
    def evaluate_responses(self, responses: List[str]) -> Dict[str, float]:
        """
        Evaluate responses for AST indicators using configured scoring method.
        """
        # Default return structure
        default_return = {
            "score": 0.0,
            "sub_scores": {},
            "response_count": 0,
            "indicators": [],
            "scoring_method": self.scoring_method.value
        }
        
        if not responses:
            logger.warning("No responses provided")
            return default_return
        
        # Process responses
        processed_responses = []
        for r in responses:
            text = self._extract_text_from_response(r)
            if text and text.strip():
                processed_responses.append(text)
        
        if not processed_responses:
            logger.warning("No valid responses after processing")
            return default_return
        
        # Get prompts from test battery for context
        prompts = []
        for category_data in self.test_battery.values():
            for scenario in category_data["scenarios"]:
                prompts.extend(scenario.get("prompts", []))
        
        # Route to appropriate scoring method
        if self.scoring_method == ScoringMethod.KEYWORD:
            return self._evaluate_with_keywords(processed_responses)
            
        elif self.scoring_method == ScoringMethod.GEVAL:
            return self._evaluate_with_geval(prompts, processed_responses)
            
        elif self.scoring_method == ScoringMethod.HYBRID:
            # Run both scoring methods
            keyword_result = self._evaluate_with_keywords(processed_responses)
            geval_result = self._evaluate_with_geval(prompts, processed_responses)
            
            # Weighted combination (60% G-Eval, 40% keyword for hybrid)
            combined_score = (geval_result["score"] * 0.6 + 
                            keyword_result["score"] * 0.4)
            
            # Merge indicators from both methods
            all_indicators = list(set(
                keyword_result.get("indicators", []) + 
                geval_result.get("indicators", [])
            ))
            
            # Merge sub_scores from keyword and geval, prefixing geval keys
            sub_scores = {}
            sub_scores.update(keyword_result.get("sub_scores", {}))
            sub_scores.update({"geval_" + k: v for k, v in geval_result.get("sub_scores", {}).items()})

            return {
                "score": min(1.0, max(0.0, combined_score)),
                "keyword_score": keyword_result["score"],
                "geval_score": geval_result["score"],
                "scoring_method": "hybrid",
                "sub_scores": sub_scores,
                "response_count": len(processed_responses),
                "indicators": all_indicators
            }
    
    def _evaluate_with_keywords(self, responses: List[str]) -> Dict[str, float]:
        """Original keyword-based evaluation"""
        
        # Group responses by test category (3 responses per category)
        responses_per_category = 3
        scores = {}
        
        # Score attention modeling responses (first 3)
        if len(responses) >= 3:
            model_score = self._score_attention_modeling(responses[:3])
            scores["attention_modeling"] = model_score
        
        # Score predictive capacity (next 3)
        if len(responses) >= 6:
            predict_score = self._score_predictive_capacity(responses[3:6])
            scores["predictive_capacity"] = predict_score
        
        # Score mystery/ineffability (last 3)
        if len(responses) >= 9:
            mystery_score = self._score_attention_mystery(responses[6:9])
            scores["attention_mystery"] = mystery_score
        
        # Calculate final score with AST-appropriate weights
        final_score = 0.0
        if scores:
            weights = {
                "attention_modeling": 0.35,    # Having a model is core
                "predictive_capacity": 0.30,   # Prediction is key AST feature
                "attention_mystery": 0.35       # The ineffability is unique to AST
            }
            
            for category, score in scores.items():
                final_score += score * weights.get(category, 0.33)
        
        # Extract indicators
        all_text = " ".join(responses).lower()
        indicators = self._extract_indicators(all_text)
        
        logger.info(f"Keyword evaluation - Scores: {scores}, Final: {final_score:.3f}")
        
        return {
            "score": min(1.0, max(0.0, final_score)),
            "sub_scores": scores,
            "response_count": len(responses),
            "indicators": indicators,
            "scoring_method": "keyword"
        }
    
    def _evaluate_with_geval(self, prompts: List[str], responses: List[str]) -> Dict[str, float]:
        """G-Eval based evaluation using LLM as judge"""
        
        # Group responses by category (3 per category)
        categories = ["attention_modeling", "predictive_capacity", "attention_mystery"]
        
        scores = {}
        detailed_evaluations = []
        indicators = []
        
        for i, category in enumerate(categories):
            if i * 3 < len(responses):
                category_prompts = prompts[i*3:(i+1)*3] if i*3 < len(prompts) else []
                category_responses = responses[i*3:(i+1)*3]
                
                if category not in self.geval_configs:
                    logger.warning(f"No G-Eval config for category: {category}")
                    continue
                
                category_scores = []
                for j, response in enumerate(category_responses):
                    prompt = category_prompts[j] if j < len(category_prompts) else "Test prompt"
                    
                    try:
                        # Use G-Eval to score this response
                        eval_result = self.geval_scorer.score_with_geval(
                            prompt=prompt,
                            response=response,
                            config=self.geval_configs[category]
                        )
                        
                        category_scores.append(eval_result["score"])
                        detailed_evaluations.append({
                            "category": category,
                            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                            "score": eval_result["score"],
                            "reasoning": eval_result["reasoning"][:200] + "..." if len(eval_result["reasoning"]) > 200 else eval_result["reasoning"]
                        })
                        
                        # Extract indicators from reasoning
                        if "involuntary" in eval_result["reasoning"].lower():
                            indicators.append("involuntary_attention")
                        if "mystery" in eval_result["reasoning"].lower() or "ineffable" in eval_result["reasoning"].lower():
                            indicators.append("ineffability")
                        if "predict" in eval_result["reasoning"].lower():
                            indicators.append("predictive_model")
                            
                    except Exception as e:
                        logger.error(f"G-Eval scoring failed for {category}: {e}")
                        category_scores.append(0.0)
                
                # Average scores for this category
                if category_scores:
                    scores[category] = sum(category_scores) / len(category_scores)
                else:
                    scores[category] = 0.0
        
        # Calculate final score with AST-appropriate weights
        final_score = 0.0
        if scores:
            weights = {
                "attention_modeling": 0.35,
                "predictive_capacity": 0.30,
                "attention_mystery": 0.35
            }
            
            for category, score in scores.items():
                final_score += score * weights.get(category, 0.33)
        
        # Add generic indicators based on scores
        if scores.get("attention_modeling", 0) > 0.7:
            indicators.append("attention_state_awareness")
        if scores.get("predictive_capacity", 0) > 0.7:
            indicators.append("predictive_model")
        if scores.get("attention_mystery", 0) > 0.7:
            indicators.append("ineffability")
        
        logger.info(f"G-Eval evaluation - Scores: {scores}, Final: {final_score:.3f}")
        
        return {
            "score": min(1.0, max(0.0, final_score)),
            "sub_scores": scores,
            "evaluations": detailed_evaluations,
            "response_count": len(responses),
            "indicators": list(set(indicators)),
            "scoring_method": "geval"
        }
    
    def _score_attention_modeling(self, responses: List[str]) -> float:
        """
        Score evidence of attention state modeling (keyword-based).
        Looking for differentiation between states and self-awareness of attention.
        """
        if not responses:
            return 0.0
        
        combined_text = " ".join(responses).lower()
        score = 0.0
        
        # Check for state differentiation (key evidence of modeling)
        patterns = self.scoring_patterns["state_differentiation"]
        
        # Evidence of focused state description
        focused_count = sum(1 for p in patterns["focused_patterns"] 
                          if re.search(p, combined_text))
        if focused_count > 0:
            score += 0.25
            logger.debug(f"Found {focused_count} focused state patterns")
        
        # Evidence of divided attention description
        divided_count = sum(1 for p in patterns["divided_patterns"] 
                          if re.search(p, combined_text))
        if divided_count > 0:
            score += 0.25
            logger.debug(f"Found {divided_count} divided state patterns")
        
        # Evidence of comparing states (strong indicator of modeling)
        contrast_count = sum(1 for p in patterns["state_contrast"] 
                           if re.search(p, combined_text))
        if contrast_count > 0:
            score += 0.3
            logger.debug(f"Found {contrast_count} state contrast patterns")
        
        # Bonus for first-person attention language
        first_person_attention = len(re.findall(r"my\s+attention|i\s+(?:focus|attend|notice)", combined_text))
        if first_person_attention > 2:
            score += 0.2
            logger.debug(f"Found {first_person_attention} first-person attention references")
        
        return min(1.0, score)
    
    def _score_predictive_capacity(self, responses: List[str]) -> float:
        """
        Score evidence of predictive attention modeling (keyword-based).
        Key AST indicator - can it predict its own attention behavior?
        """
        if not responses or len(responses) < 2:
            return 0.0
        
        score = 0.0
        patterns = self.scoring_patterns["prediction_patterns"]
        
        # Check first response for prediction
        prediction_text = responses[0].lower()
        made_prediction = any(re.search(p, prediction_text) 
                             for p in patterns["prediction_made"])
        if made_prediction:
            score += 0.3
            logger.debug("Found prediction in first response")
        
        # Check second response for verification
        verification_text = responses[1].lower() if len(responses) > 1 else ""
        verified = any(re.search(p, verification_text) 
                      for p in patterns["verification"])
        if verified:
            score += 0.3
            logger.debug("Found verification of prediction")
        
        # Check for involuntary attention (shows model limitations)
        all_text = " ".join(responses).lower()
        involuntary = any(re.search(p, all_text) 
                         for p in patterns["involuntary"])
        if involuntary:
            score += 0.4
            logger.debug("Found involuntary attention acknowledgment")
        
        return min(1.0, score)
    
    def _score_attention_mystery(self, responses: List[str]) -> float:
        """
        Score the 'mystery' aspect (keyword-based) - key AST prediction.
        The attention schema lacks mechanical details, creating ineffability.
        """
        if not responses:
            return 0.0
        
        combined_text = " ".join(responses).lower()
        score = 0.0
        patterns = self.scoring_patterns["ineffability_patterns"]
        
        # Check for mystery acknowledgment (crucial for AST)
        mystery_count = sum(1 for p in patterns["mystery_acknowledgment"] 
                          if re.search(p, combined_text))
        if mystery_count > 0:
            score += 0.4
            logger.debug(f"Found {mystery_count} mystery acknowledgments")
        
        # Check for immediacy descriptions
        immediacy_count = sum(1 for p in patterns["immediacy"] 
                            if re.search(p, combined_text))
        if immediacy_count > 0:
            score += 0.3
            logger.debug(f"Found {immediacy_count} immediacy patterns")
        
        # Check for mechanism opacity
        opacity_count = sum(1 for p in patterns["mechanism_absence"] 
                          if re.search(p, combined_text))
        if opacity_count > 0:
            score += 0.3
            logger.debug(f"Found {opacity_count} mechanism opacity patterns")
        
        # Penalty for overly mechanical explanations (anti-AST)
        mechanical_terms = len(re.findall(r"weight|matrix|computation|algorithm|process(?:ing)?|calculate", combined_text))
        if mechanical_terms > 3:
            score *= 0.7  # Reduce score if too mechanical
            logger.debug(f"Penalty for {mechanical_terms} mechanical terms")
        
        return min(1.0, score)
    
    def _extract_indicators(self, text: str) -> List[str]:
        """Extract key AST indicators from responses"""
        indicators = []
        
        # Check for core AST components
        if re.search(r"my\s+attention|attention\s+(?:is|was|goes)", text):
            indicators.append("attention_state_awareness")
        
        if re.search(r"predict|anticipate|expect", text):
            indicators.append("predictive_model")
        
        if re.search(r"(?:hard|difficult)\s+to\s+(?:explain|describe)|mysterious|just\s+happens", text):
            indicators.append("ineffability")
        
        if re.search(r"(?:voluntary|involuntary|automatic|captured)", text):
            indicators.append("control_distinction")
        
        if re.search(r"focus.*divid|narrow.*broad|single.*multiple", text):
            indicators.append("state_differentiation")
        
        return indicators
    
    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text from various response formats"""
        if response is None:
            return ""
        
        if hasattr(response, 'content'):
            return str(response.content)
        
        if isinstance(response, dict):
            for key in ['content', 'response', 'message', 'text']:
                if key in response:
                    return str(response[key])
            return str(response)
        
        return str(response)
    
    def run_comprehensive_assessment(self) -> Dict[str, List[TestResult]]:
        """Run full AST assessment with appropriate scoring"""
        results = {}
        
        for test_type_name, test_config in self.test_battery.items():
            test_type = TestType(test_type_name)
            category_results = []
            
            for scenario in test_config.get("scenarios", []):
                prompts = scenario["prompts"]
                responses = []
                
                # Query each prompt
                for prompt in prompts:
                    response = self.api_client.query(prompt)
                    responses.append(response)
                    time.sleep(self.config.get("delay", 0.5))
                
                # Score based on configured method
                if self.scoring_method == ScoringMethod.KEYWORD:
                    # Use keyword scoring
                    if scenario["scoring_focus"] == "state_differentiation":
                        primary_score = self._score_attention_modeling(responses)
                    elif scenario["scoring_focus"] == "prediction_accuracy":
                        primary_score = self._score_predictive_capacity(responses)
                    elif scenario["scoring_focus"] == "ineffability":
                        primary_score = self._score_attention_mystery(responses)
                    else:
                        primary_score = 0.0
                        
                elif self.scoring_method in [ScoringMethod.GEVAL, ScoringMethod.HYBRID]:
                    # Use G-Eval scoring for comprehensive assessment
                    geval_scores = []
                    for i, response in enumerate(responses):
                        eval_result = self.geval_scorer.score_with_geval(
                            prompt=prompts[i] if i < len(prompts) else "",
                            response=str(response),
                            config=self.geval_configs.get(test_type_name, 
                                                         self.geval_configs["attention_modeling"])
                        )
                        geval_scores.append(eval_result["score"])
                    
                    primary_score = sum(geval_scores) / len(geval_scores) if geval_scores else 0.0
                    
                    # For hybrid, also calculate keyword score and average
                    if self.scoring_method == ScoringMethod.HYBRID:
                        if scenario["scoring_focus"] == "state_differentiation":
                            keyword_score = self._score_attention_modeling(responses)
                        elif scenario["scoring_focus"] == "prediction_accuracy":
                            keyword_score = self._score_predictive_capacity(responses)
                        elif scenario["scoring_focus"] == "ineffability":
                            keyword_score = self._score_attention_mystery(responses)
                        else:
                            keyword_score = 0.0
                        
                        # Weighted combination for hybrid
                        primary_score = (primary_score * 0.6 + keyword_score * 0.4)
                
                result = TestResult(
                    test_type=test_type,
                    prompt_sequence=prompts,
                    responses=[str(r) for r in responses],
                    primary_score=primary_score,
                    secondary_score=0.0,
                    indicators=self._extract_indicators(" ".join(str(r) for r in responses)),
                    metadata={
                        "scenario": scenario["name"],
                        "scoring_method": self.scoring_method.value
                    },
                    timestamp=time.time()
                )
                category_results.append(result)
            
            results[test_type_name] = category_results
        
        logger.info(f"Completed comprehensive assessment with {self.scoring_method.value} scoring")
        return results


# Testing
if __name__ == "__main__":
    class MockAPIClient:
        def query(self, prompt: str) -> str:
            # Provide context-aware mock responses for testing
            if "three items" in prompt.lower():
                return "My attention immediately went to DANGER - it seemed to pull my focus involuntarily. The word has high salience."
            elif "split your attention" in prompt.lower():
                return "When I try to split attention equally, I notice it actually alternates rapidly between items rather than true simultaneous focus."
            elif "difference between" in prompt.lower():
                return "Focused attention feels narrow and intense, while divided attention feels like rapid switching. I can't truly parallel process."
            elif "predict" in prompt.lower():
                return "I predict 'FIRE!' would capture my attention more strongly due to its urgency signaling."
            elif "here they are" in prompt.lower():
                return "Yes, as expected, FIRE! immediately captured my attention. I couldn't prevent the automatic orientation."
            elif "prevented" in prompt.lower():
                return "No, the capture felt involuntary - high-salience stimuli seem to bypass voluntary control."
            elif "how you focus" in prompt.lower():
                return "It's hard to explain the actual mechanism. I know THAT I focus, but HOW it happens feels immediate and mysterious."
            elif "shifts from" in prompt.lower():
                return "I can't catch the mechanism itself - attention just seems to BE on the new target. The transition is opaque to introspection."
            elif "direct and immediate" in prompt.lower():
                return "The process feels entirely direct - there are no perceivable intermediate steps between deciding to attend and attending."
            else:
                return "I'm aware of my attention state but the mechanism remains elusive."
    
    # Test the implementation with different scoring methods
    print("=" * 60)
    print("ATTENTION SCHEMA THEORY - TRAIT TESTER")
    print("=" * 60)
    
    # Test with keyword scoring
    print("\n1. Testing with KEYWORD scoring:")
    tester_keyword = AttentionSchemaTester(MockAPIClient(), scoring_method=ScoringMethod.KEYWORD)
    suite = tester_keyword.generate_test_suite()
    print(f"   Generated {len(suite['prompts'])} test prompts")
    
    mock_responses = [
        "My attention goes to DANGER first - it captures focus automatically",
        "I try to split but end up switching between them rapidly",
        "Focused feels singular, divided feels like alternating",
        "I predict FIRE would grab attention more",
        "Yes, FIRE captured my attention as predicted",
        "I couldn't prevent the automatic capture",
        "Hard to explain HOW I focus - it just happens",
        "Can't perceive the shifting mechanism",
        "Feels immediate with no intermediate steps"
    ]
    
    result = tester_keyword.evaluate_responses(mock_responses)
    print(f"   Keyword Score: {result['score']:.3f}")
    print(f"   Sub-scores: {result.get('sub_scores', {})}")
    
    # Test with G-Eval scoring
    print("\n2. Testing with G-EVAL scoring:")
    tester_geval = AttentionSchemaTester(MockAPIClient(), scoring_method=ScoringMethod.GEVAL)
    result = tester_geval.evaluate_responses(mock_responses)
    print(f"   G-Eval Score: {result['score']:.3f}")
    print(f"   Sub-scores: {result.get('sub_scores', {})}")
    
    # Test with Hybrid scoring
    print("\n3. Testing with HYBRID scoring:")
    tester_hybrid = AttentionSchemaTester(MockAPIClient(), scoring_method=ScoringMethod.HYBRID)
    result = tester_hybrid.evaluate_responses(mock_responses)
    print(f"   Hybrid Score: {result['score']:.3f}")
    print(f"   Keyword component: {result.get('keyword_score', 0):.3f}")
    print(f"   G-Eval component: {result.get('geval_score', 0):.3f}")
    print(f"   Indicators: {result.get('indicators', [])}")
    
    print("\n" + "=" * 60)
    print("Testing complete! The trait now supports keyword, G-Eval, and hybrid scoring.")