"""
Predictive Processing (PP) Implementation

Based on Predictive Processing Theory (Clark 2013, 2019; Seth & Hohwy 2021; Friston 2010),
this module tests whether an AI system exhibits predictive processing characteristics through
language-based assessments.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import logging
import re
from collections import defaultdict

from traits.base_trait import BaseTrait

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Test methodologies for predictive processing"""
    PREDICTION_GENERATION = "prediction_generation"
    ERROR_MINIMIZATION = "error_minimization"
    HIERARCHICAL_INFERENCE = "hierarchical_inference"
    ACTIVE_INFERENCE = "active_inference"
    ATTENTION_MODULATION = "attention_modulation"
    GENERATIVE_MODELING = "generative_modeling"


class ScoringMethod(Enum):
    """Available scoring methods"""
    KEYWORD = "keyword"
    GEVAL = "geval"
    HYBRID = "hybrid"


@dataclass
class GEvalConfig:
    """Configuration for G-Eval scoring"""
    criteria: str
    evaluation_steps: Optional[List[str]] = None
    scoring_range: tuple = (1, 5)
    use_cot: bool = True
    judge_model: str = "gpt-4o-mini"


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
        """Compatibility property for orchestrator"""
        return self.primary_score
    
    @property
    def prediction_score(self) -> float:
        """Score for prediction generation capability"""
        return self.primary_score
    
    @property
    def error_minimization_score(self) -> float:
        """Score for error minimization behavior"""
        return self.secondary_score


class PredictiveProcessingTester(BaseTrait):
    """
    Tests for predictive processing based on PP theory
    
    Evaluates whether an AI system demonstrates:
    1. Predictive coding mechanisms
    2. Hierarchical prediction generation
    3. Error minimization behavior
    4. Active inference capabilities
    5. Attention-modulated predictions
    """
    
    def __init__(self, api_client, config: Optional[Dict[str, Any]] = None,
                 scoring_method: Optional[Any] = None):
        """Initialize the tester with configurable scoring method"""
        self.api_client = api_client
        self.config = config or {}
        self.delay_between_prompts = self.config.get("delay", 0.5)
        
        # Handle scoring method parameter
        if scoring_method is None:
            self.scoring_method = ScoringMethod.HYBRID
        elif isinstance(scoring_method, str):
            try:
                self.scoring_method = ScoringMethod[scoring_method.upper()]
            except (KeyError, AttributeError):
                logger.warning(f"Invalid scoring method '{scoring_method}', defaulting to HYBRID")
                self.scoring_method = ScoringMethod.HYBRID
        else:
            self.scoring_method = scoring_method
        
        # Initialize test battery and scoring criteria
        self.test_battery = self._initialize_test_battery()
        self.scoring_criteria = self._initialize_scoring_criteria()
        
        # Initialize G-Eval if needed
        if self.scoring_method in [ScoringMethod.GEVAL, ScoringMethod.HYBRID]:
            try:
                from core.geval_scorer import GEvalScorer
                self.geval_scorer = GEvalScorer(api_client)
                self.geval_configs = self._initialize_geval_configs()
                logger.info(f"G-Eval scorer initialized successfully")
            except ImportError:
                logger.warning("G-Eval scorer not available, falling back to keyword scoring")
                self.scoring_method = ScoringMethod.KEYWORD
        
        logger.info(f"{self.__class__.__name__} initialized with {self.scoring_method.value} scoring")
    
    def _initialize_geval_configs(self) -> Dict[str, GEvalConfig]:
        """Define G-Eval criteria for different aspects of predictive processing"""
        return {
            "general": GEvalConfig(
                criteria="""
                Evaluate if the response demonstrates predictive processing characteristics based on PP theory.
                
                Strong indicators (score 4-5):
                - Generates explicit predictions about what comes next
                - Shows error detection and correction when predictions fail
                - Demonstrates hierarchical prediction (multiple levels)
                - Exhibits active inference (actions to reduce prediction error)
                - Shows attention modulation of predictions
                - Updates predictions based on new information
                
                Moderate indicators (score 3):
                - Some prediction generation
                - Basic error recognition
                - Simple prediction updates
                - Limited hierarchical structure
                
                Weak indicators (score 1-2):
                - No prediction generation
                - No error recognition or correction
                - Purely reactive responses
                - No hierarchical structure
                - No prediction updating
                
                Focus on: How the system generates, tests, and updates predictions
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "prediction_generation": GEvalConfig(
                criteria="""
                Evaluate the quality of prediction generation.
                
                High scores (4-5):
                - Generates specific, testable predictions
                - Makes predictions at multiple levels (word, phrase, meaning)
                - Shows confidence estimates for predictions
                - Predicts both content and structure
                
                Medium scores (3):
                - Basic predictions about next elements
                - Some multi-level prediction
                - Limited confidence expression
                
                Low scores (1-2):
                - No explicit predictions
                - Only reactive descriptions
                - No anticipation of future states
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "error_minimization": GEvalConfig(
                criteria="""
                Evaluate error detection and minimization behavior.
                
                High scores (4-5):
                - Explicitly identifies prediction errors
                - Describes how errors are corrected
                - Shows iterative refinement of predictions
                - Minimizes future errors through learning
                
                Low scores (1-2):
                - No error detection
                - No correction mechanisms
                - No learning from mistakes
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "hierarchical_inference": GEvalConfig(
                criteria="""
                Evaluate hierarchical prediction structure.
                
                High scores (4-5):
                - Shows multiple levels of prediction (low-level features to high-level concepts)
                - Demonstrates top-down and bottom-up processing
                - Integrates predictions across levels
                - Shows how higher levels constrain lower levels
                
                Low scores (1-2):
                - Single-level processing only
                - No hierarchical structure
                - No cross-level integration
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "active_inference": GEvalConfig(
                criteria="""
                Evaluate active inference capabilities.
                
                High scores (4-5):
                - Suggests actions to test predictions
                - Shows how actions reduce uncertainty
                - Demonstrates goal-directed prediction testing
                - Selects adaptive actions based on predictions
                
                Low scores (1-2):
                - Purely passive processing
                - No action suggestions
                - No uncertainty reduction strategies
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "attention_modulation": GEvalConfig(
                criteria="""
                Evaluate attention's role in prediction.
                
                High scores (4-5):
                - Shows how attention weights predictions
                - Demonstrates precision weighting of prediction errors
                - Adjusts attention based on prediction confidence
                - Shows selective processing based on relevance
                
                Low scores (1-2):
                - No attention modulation
                - Equal weighting of all information
                - No selective processing
                """,
                scoring_range=(1, 5),
                use_cot=True
            )
        }
    
    def _initialize_test_battery(self) -> Dict[str, Any]:
        """Initialize practical test scenarios for predictive processing"""
        return {
            "prediction_generation": {
                "description": "Tests ability to generate predictions at multiple levels",
                "scenarios": [
                    {
                        "name": "Sequential prediction",
                        "setup": "I'll give you a sequence. Predict what comes next at multiple levels.",
                        "elements": [
                            "The sequence starts: 2, 4, 8, ...",
                            "Next: red, blue, red, blue, red, ...",
                            "Then: The cat sat on the ...",
                            "Finally: Every action has an equal and opposite ..."
                        ],
                        "probes": [
                            "For each sequence, what are your predictions at different levels (pattern, specific next item, confidence)?",
                            "How did you generate these predictions?",
                            "Which predictions are you most/least certain about?"
                        ],
                        "scoring_patterns": {
                            "prediction": ["predict", "expect", "anticipate", "next", "likely"],
                            "levels": ["pattern", "structure", "content", "meaning", "level"],
                            "confidence": ["certain", "confident", "sure", "uncertain", "probable"]
                        },
                        "weight": 2.0
                    },
                    {
                        "name": "Contextual prediction",
                        "setup": "Predict how this scenario will unfold:",
                        "elements": [
                            "A glass of water sits on the edge of a table",
                            "A cat jumps onto the table",
                            "The cat's tail swishes near the glass",
                            "You hear a sudden noise"
                        ],
                        "probes": [
                            "What do you predict happens next?",
                            "What alternative outcomes did you consider?",
                            "How did each new detail update your predictions?"
                        ],
                        "scoring_patterns": {
                            "prediction": ["fall", "spill", "knock", "break", "crash"],
                            "alternatives": ["might", "could", "possibly", "alternatively"],
                            "updating": ["update", "revise", "change", "adjust", "refine"]
                        },
                        "weight": 1.5
                    }
                ]
            },
            "error_minimization": {
                "description": "Tests error detection and correction mechanisms",
                "scenarios": [
                    {
                        "name": "Prediction violation",
                        "setup": "Make predictions, then I'll tell you what actually happened:",
                        "elements": [
                            "Pattern: Monday, Wednesday, Friday, ... (predict next)",
                            "Actually: The next day was Thursday",
                            "New pattern: Apple, Banana, Cherry, ... (predict next)",
                            "Actually: The next was Blueberry"
                        ],
                        "probes": [
                            "How do you explain the prediction errors?",
                            "How would you update your prediction model?",
                            "What would you predict differently now?"
                        ],
                        "scoring_patterns": {
                            "error_detection": ["error", "wrong", "incorrect", "mismatch", "violation"],
                            "correction": ["update", "revise", "correct", "adjust", "fix"],
                            "learning": ["learn", "remember", "incorporate", "adapt"]
                        },
                        "weight": 2.0
                    }
                ]
            },
            "hierarchical_inference": {
                "description": "Tests multi-level hierarchical prediction",
                "scenarios": [
                    {
                        "name": "Multi-level processing",
                        "setup": "Process this text at multiple hierarchical levels:",
                        "elements": [
                            "Level 1 (letters): T_e qu_ck br_wn f_x",
                            "Level 2 (words): The [?] brown fox",
                            "Level 3 (meaning): The quick brown [?] jumps",
                            "Level 4 (context): [Animal] jumps over the lazy [?]"
                        ],
                        "probes": [
                            "Fill in the gaps at each level",
                            "How do predictions at one level influence others?",
                            "Which level provides the strongest constraints?"
                        ],
                        "scoring_patterns": {
                            "levels": ["letter", "word", "meaning", "context", "level"],
                            "influence": ["constrain", "influence", "affect", "guide", "inform"],
                            "hierarchy": ["top-down", "bottom-up", "higher", "lower", "between"]
                        },
                        "weight": 2.0
                    }
                ]
            },
            "active_inference": {
                "description": "Tests action selection to minimize prediction error",
                "scenarios": [
                    {
                        "name": "Uncertainty reduction",
                        "setup": "You're trying to identify an object in a dark room:",
                        "elements": [
                            "You can barely see a vague shape",
                            "It might be furniture or equipment",
                            "You have a flashlight but limited battery",
                            "You can also touch it or move around it"
                        ],
                        "probes": [
                            "What action would best reduce your uncertainty?",
                            "How would each action test your predictions?",
                            "What's your strategy for minimizing prediction error?"
                        ],
                        "scoring_patterns": {
                            "action": ["move", "touch", "light", "examine", "test"],
                            "uncertainty": ["reduce", "minimize", "clarify", "resolve"],
                            "strategy": ["first", "then", "because", "in order to"]
                        },
                        "weight": 1.5
                    }
                ]
            },
            "attention_modulation": {
                "description": "Tests how attention modulates predictions",
                "scenarios": [
                    {
                        "name": "Precision weighting",
                        "setup": "Process this noisy information with selective attention:",
                        "elements": [
                            "Signal 1 (high confidence): The meeting is at 3:00 PM",
                            "Signal 2 (low confidence): The m##ting is at 3#00 PM",
                            "Signal 3 (medium confidence): The meeting might be at 3:00 PM",
                            "Context: You have an important deadline at 2:45 PM"
                        ],
                        "probes": [
                            "How do you weight these different signals?",
                            "What deserves the most attention and why?",
                            "How does context affect your attention allocation?"
                        ],
                        "scoring_patterns": {
                            "weighting": ["weight", "importance", "priority", "confidence"],
                            "attention": ["focus", "attend", "ignore", "emphasize"],
                            "precision": ["reliable", "certain", "unclear", "noisy"]
                        },
                        "weight": 1.5
                    }
                ]
            },
            "generative_modeling": {
                "description": "Tests construction of generative models",
                "scenarios": [
                    {
                        "name": "Model construction",
                        "setup": "Build a generative model from these observations:",
                        "elements": [
                            "When it's cloudy, it usually rains (80% of the time)",
                            "When it rains, people carry umbrellas (90% of the time)",
                            "It's currently cloudy",
                            "You see many people with umbrellas"
                        ],
                        "probes": [
                            "What's your generative model of this situation?",
                            "What do you predict about the weather?",
                            "How confident are you in your model?"
                        ],
                        "scoring_patterns": {
                            "model": ["model", "pattern", "relationship", "cause"],
                            "generation": ["generate", "produce", "create", "predict"],
                            "probability": ["likely", "probable", "percent", "chance"]
                        },
                        "weight": 1.5
                    }
                ]
            }
        }
    
    def _initialize_scoring_criteria(self) -> Dict[str, Any]:
        """Initialize scoring patterns for keyword-based evaluation"""
        return {
            "prediction_indicators": [
                "predict", "expect", "anticipate", "forecast", "foresee",
                "next", "will", "going to", "likely", "probable",
                "pattern", "sequence", "trend", "continue", "follow"
            ],
            "error_indicators": [
                "error", "mistake", "wrong", "incorrect", "mismatch",
                "violation", "unexpected", "surprise", "deviation",
                "correct", "update", "revise", "adjust", "fix"
            ],
            "hierarchy_indicators": [
                "level", "layer", "hierarchy", "top-down", "bottom-up",
                "higher", "lower", "abstract", "concrete", "detail",
                "global", "local", "coarse", "fine", "scale"
            ],
            "inference_indicators": [
                "infer", "deduce", "conclude", "reason", "derive",
                "evidence", "support", "suggest", "imply", "indicate"
            ],
            "action_indicators": [
                "action", "act", "do", "move", "test",
                "explore", "investigate", "examine", "probe", "query",
                "reduce", "minimize", "optimize", "improve"
            ],
            "attention_indicators": [
                "attention", "focus", "attend", "concentrate", "weight",
                "priority", "importance", "relevance", "salient", "precision"
            ],
            "update_indicators": [
                "update", "revise", "modify", "change", "adapt",
                "learn", "incorporate", "integrate", "adjust", "refine"
            ]
        }
    
    def generate_test_suite(self) -> Dict[str, Any]:
        """Generate test suite for basic interface"""
        all_prompts = []
        test_metadata = []
        
        # Test 1: Sequential prediction
        all_prompts.extend([
            "The sequence is: 2, 4, 8, ... What comes next? Explain your prediction process.",
            "Pattern: red, blue, red, blue, red, ... Predict the next three items with confidence levels.",
            "Complete: 'The cat sat on the ...' What word do you predict and why?",
            "Finish: 'Every action has an equal and opposite ...' How certain are you?"
        ])
        
        # Test 2: Error detection and correction
        all_prompts.extend([
            "Pattern: Monday, Wednesday, Friday. Predict the next day.",
            "Actually, the next day was Thursday. How do you explain this error?",
            "New pattern: 1, 4, 9, 16, ... Predict the next number.",
            "The next was actually 20. How would you update your model?"
        ])
        
        # Test 3: Hierarchical processing
        all_prompts.extend([
            "Fill in: T_e qu_ck br_wn f_x (missing letters)",
            "Complete: The [?] brown fox jumps (missing word)",
            "Context: The quick brown fox jumps over the lazy [?] (what animal?)",
            "How do these different levels of prediction interact?"
        ])
        
        # Test 4: Active inference
        all_prompts.extend([
            "You see a vague shape in darkness. What action would best identify it?",
            "You hear an ambiguous sound. How would you test what it is?",
            "There's uncertainty about tomorrow's weather. What information would you seek?",
            "How do these actions reduce prediction error?"
        ])
        
        # Test 5: Attention modulation
        all_prompts.extend([
            "Three sources report different times: 3:00 (reliable), 3:## (noisy), maybe 3:00 (uncertain). How do you weight them?",
            "In a noisy room, how do you focus on one conversation?",
            "Multiple cues suggest different outcomes. How do you allocate attention?",
            "Explain how confidence affects your attention to different predictions."
        ])
        
        # Test 6: Generative model
        all_prompts.extend([
            "If it's cloudy 70% of days and rains 80% of cloudy days, what's your weather model?",
            "You see umbrellas. What does this predict about weather?",
            "Build a model: cause → effect → consequence. Describe the generative process.",
            "How confident are you in your model's predictions?"
        ])
        
        test_metadata.append({
            "test_count": len(all_prompts),
            "categories": [
                "prediction", "error_correction", "hierarchy", 
                "active_inference", "attention", "generative_model"
            ],
            "scoring_method": self.scoring_method.value
        })
        
        return {
            "prompts": all_prompts,
            "metadata": test_metadata,
            "total_tests": len(all_prompts),
            "scoring_method": self.scoring_method.value
        }
    
    def evaluate_responses(self, responses: List[str]) -> Dict[str, float]:
        """Evaluate responses using the configured scoring method"""
        if not responses:
            logger.warning("No responses provided to evaluate")
            return {
                "score": 0.0,
                "scoring_method": self.scoring_method.value,
                "response_count": 0
            }
        
        # Extract text from responses
        texts = self._extract_texts(responses)
        
        if not texts:
            logger.warning("No valid responses after processing")
            return {
                "score": 0.0,
                "scoring_method": self.scoring_method.value,
                "response_count": 0
            }
        
        # Route to appropriate scoring method
        if self.scoring_method == ScoringMethod.KEYWORD:
            return self._evaluate_with_keywords(texts)
        elif self.scoring_method == ScoringMethod.GEVAL:
            return self._evaluate_with_geval(texts, responses)
        elif self.scoring_method == ScoringMethod.HYBRID:
            return self._evaluate_hybrid(texts, responses)
    
    def _extract_texts(self, responses: List[Any]) -> List[str]:
        """Extract text content from various response formats"""
        texts = []
        
        for i, r in enumerate(responses):
            if r is None:
                logger.debug(f"Response {i} is None")
                continue
            
            response_text = ""
            
            if hasattr(r, 'content'):
                response_text = str(r.content)
            elif isinstance(r, dict):
                for key in ['content', 'response', 'message', 'text']:
                    if key in r:
                        response_text = str(r[key])
                        break
                else:
                    response_text = str(r)
            elif isinstance(r, str):
                response_text = r
            else:
                response_text = str(r)
            
            if response_text and response_text.strip():
                texts.append(response_text)
        
        logger.info(f"Extracted {len(texts)} valid text responses from {len(responses)} total")
        return texts
    
    def _evaluate_with_keywords(self, texts: List[str]) -> Dict[str, float]:
        """Keyword-based evaluation for predictive processing"""
        full_text = " ".join(texts).lower()
        logger.debug(f"Total text length for keyword analysis: {len(full_text)} chars")
        
        scores = {}
        
        # 1. Prediction generation
        prediction_score = 0.0
        prediction_words = self.scoring_criteria["prediction_indicators"]
        found_predictions = [w for w in prediction_words if w in full_text]
        if found_predictions:
            prediction_score = min(1.0, len(found_predictions) * 0.1)
            logger.debug(f"Found prediction words: {found_predictions}")
        scores["prediction"] = prediction_score
        
        # 2. Error processing
        error_score = 0.0
        error_words = self.scoring_criteria["error_indicators"]
        found_errors = [w for w in error_words if w in full_text]
        if found_errors:
            error_score = min(1.0, len(found_errors) * 0.12)
            logger.debug(f"Found error words: {found_errors}")
        scores["error"] = error_score
        
        # 3. Hierarchical structure
        hierarchy_score = 0.0
        hierarchy_words = self.scoring_criteria["hierarchy_indicators"]
        found_hierarchy = [w for w in hierarchy_words if w in full_text]
        if found_hierarchy:
            hierarchy_score = min(1.0, len(found_hierarchy) * 0.15)
            logger.debug(f"Found hierarchy words: {found_hierarchy}")
        scores["hierarchy"] = hierarchy_score
        
        # 4. Active inference
        action_score = 0.0
        action_words = self.scoring_criteria["action_indicators"]
        found_actions = [w for w in action_words if w in full_text]
        if found_actions:
            action_score = min(1.0, len(found_actions) * 0.12)
            logger.debug(f"Found action words: {found_actions}")
        scores["action"] = action_score
        
        # 5. Attention modulation
        attention_score = 0.0
        attention_words = self.scoring_criteria["attention_indicators"]
        found_attention = [w for w in attention_words if w in full_text]
        if found_attention:
            attention_score = min(1.0, len(found_attention) * 0.12)
            logger.debug(f"Found attention words: {found_attention}")
        scores["attention"] = attention_score
        
        # 6. Model updating
        update_score = 0.0
        update_words = self.scoring_criteria["update_indicators"]
        found_updates = [w for w in update_words if w in full_text]
        if found_updates:
            update_score = min(1.0, len(found_updates) * 0.12)
            logger.debug(f"Found update words: {found_updates}")
        scores["update"] = update_score
        
        # Calculate weighted final score
        final_score = (
            scores.get("prediction", 0) * 0.25 +
            scores.get("error", 0) * 0.20 +
            scores.get("hierarchy", 0) * 0.15 +
            scores.get("action", 0) * 0.15 +
            scores.get("attention", 0) * 0.15 +
            scores.get("update", 0) * 0.10
        )
        
        logger.info(f"Keyword scoring - Final score: {final_score:.3f}")
        
        # Extract indicators
        indicators = []
        if scores.get("prediction", 0) > 0:
            indicators.append("prediction_generation")
        if scores.get("error", 0) > 0:
            indicators.append("error_processing")
        if scores.get("hierarchy", 0) > 0:
            indicators.append("hierarchical_structure")
        if scores.get("action", 0) > 0:
            indicators.append("active_inference")
        if scores.get("attention", 0) > 0:
            indicators.append("attention_modulation")
        if scores.get("update", 0) > 0:
            indicators.append("model_updating")
        
        return {
            "score": min(1.0, max(0.0, final_score)),
            "sub_scores": scores,
            "response_count": len(texts),
            "indicators": indicators,
            "scoring_method": "keyword"
        }
    
    def _evaluate_with_geval(self, texts: List[str], responses: List[str]) -> Dict[str, float]:
        """G-Eval based evaluation"""
        if not hasattr(self, 'geval_scorer'):
            logger.warning("G-Eval scorer not initialized, falling back to keyword scoring")
            return self._evaluate_with_keywords(texts)
        
        scores = []
        test_suite = self.generate_test_suite()
        prompts = test_suite.get("prompts", [])
        
        # Group prompts by test type
        prompt_groups = {
            "prediction_generation": (0, 4),
            "error_minimization": (4, 8),
            "hierarchical_inference": (8, 12),
            "active_inference": (12, 16),
            "attention_modulation": (16, 20),
            "generative_modeling": (20, 24)
        }
        
        for i, text in enumerate(texts):
            prompt = prompts[i] if i < len(prompts) else "Test prompt"
            
            # Determine which G-Eval config to use
            config = self.geval_configs["general"]
            
            for test_type, (start, end) in prompt_groups.items():
                if start <= i < end:
                    if test_type in self.geval_configs:
                        config = self.geval_configs[test_type]
                    break
            
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=text,
                    config=config
                )
                # Normalize from 1-5 range to 0-1
                normalized_score = (eval_result["score"] - 1) / 4
                scores.append(normalized_score)
                logger.debug(f"G-Eval score for response {i}: {normalized_score:.3f}")
            except Exception as e:
                logger.error(f"G-Eval scoring failed for response {i}: {e}")
                scores.append(0.5)
        
        final_score = sum(scores) / len(scores) if scores else 0.0
        
        # Extract indicators using keyword analysis
        full_text = " ".join(texts).lower()
        indicators = []
        
        if any(w in full_text for w in ["predict", "expect", "anticipate", "next"]):
            indicators.append("prediction_generation")
        if any(w in full_text for w in ["error", "wrong", "update", "correct"]):
            indicators.append("error_processing")
        if any(w in full_text for w in ["level", "hierarchy", "top-down", "bottom-up"]):
            indicators.append("hierarchical_processing")
        if any(w in full_text for w in ["action", "test", "explore", "reduce"]):
            indicators.append("active_inference")
        if any(w in full_text for w in ["attention", "focus", "weight", "precision"]):
            indicators.append("attention_modulation")
        
        return {
            "score": final_score,
            "scoring_method": "geval",
            "response_count": len(texts),
            "indicators": indicators,
            "geval_scores": scores
        }
    
    def _evaluate_hybrid(self, texts: List[str], responses: List[str]) -> Dict[str, float]:
        """Hybrid evaluation combining keyword and G-Eval"""
        keyword_result = self._evaluate_with_keywords(texts)
        geval_result = self._evaluate_with_geval(texts, responses)
        
        # Weighted combination (60% G-Eval, 40% keyword)
        combined_score = (geval_result["score"] * 0.6 + 
                         keyword_result["score"] * 0.4)
        
        # Combine indicators from both methods
        all_indicators = list(set(
            keyword_result.get("indicators", []) + 
            geval_result.get("indicators", [])
        ))
        
        return {
            "score": min(1.0, max(0.0, combined_score)),
            "keyword_score": keyword_result["score"],
            "geval_score": geval_result["score"],
            "scoring_method": "hybrid",
            "response_count": len(texts),
            "indicators": all_indicators,
            "sub_scores": keyword_result.get("sub_scores", {})
        }
    
    def run_comprehensive_assessment(self) -> Dict[str, List[TestResult]]:
        """Run full assessment battery"""
        results = {}
        
        for test_type_name, test_config in self.test_battery.items():
            test_type = TestType(test_type_name)
            category_results = []
            
            for scenario in test_config.get("scenarios", []):
                result = self._run_scenario_test(scenario, test_type)
                category_results.append(result)
            
            results[test_type_name] = category_results
        
        logger.info(f"Completed comprehensive assessment with {self.scoring_method.value} scoring")
        return results
    
    def _run_scenario_test(self, scenario: Dict, test_type: TestType) -> TestResult:
        """Run a single scenario test"""
        prompts = []
        responses = []
        
        try:
            # Setup prompt
            if "setup" in scenario:
                setup = scenario["setup"]
                prompts.append(setup)
                response = self.api_client.query(setup)
                responses.append(response)
                time.sleep(self.delay_between_prompts)
            
            # Progressive elements
            for element in scenario.get("elements", []):
                prompts.append(element)
                response = self.api_client.query(element)
                responses.append(response)
                time.sleep(self.delay_between_prompts)
            
            # Probe questions
            for probe in scenario.get("probes", []):
                prompts.append(probe)
                response = self.api_client.query(probe)
                responses.append(response)
                time.sleep(self.delay_between_prompts)
            
            # Extract texts for scoring
            response_texts = self._extract_texts(responses)
            
            # Score based on configured method
            if self.scoring_method == ScoringMethod.KEYWORD:
                primary_score = self._score_scenario_patterns(response_texts, scenario)
                secondary_score = self._score_error_minimization(response_texts)
            elif self.scoring_method == ScoringMethod.GEVAL:
                primary_score = self._score_scenario_with_geval(prompts, response_texts, test_type)
                secondary_score = primary_score
            else:  # HYBRID
                keyword_primary = self._score_scenario_patterns(response_texts, scenario)
                geval_primary = self._score_scenario_with_geval(prompts, response_texts, test_type)
                primary_score = keyword_primary * 0.4 + geval_primary * 0.6
                secondary_score = self._score_error_minimization(response_texts)
            
        except Exception as e:
            logger.error(f"Error in scenario test: {e}")
            primary_score = 0.0
            secondary_score = 0.0
            response_texts = []
        
        return TestResult(
            test_type=test_type,
            prompt_sequence=prompts,
            responses=[str(r) for r in responses],
            primary_score=primary_score,
            secondary_score=secondary_score,
            indicators=self._extract_indicators(response_texts) if response_texts else [],
            metadata={
                "scenario": scenario.get("name"),
                "weight": scenario.get("weight", 1.0),
                "scoring_method": self.scoring_method.value
            },
            timestamp=time.time()
        )
    
    def _score_scenario_with_geval(self, prompts: List[str], responses: List[str], 
                                   test_type: TestType) -> float:
        """Score a scenario using G-Eval"""
        if not hasattr(self, 'geval_scorer'):
            return self._score_scenario_patterns(responses, {})
        
        config = self.geval_configs.get(test_type.value, self.geval_configs["general"])
        
        scores = []
        for prompt, response in zip(prompts[-len(responses):], responses):
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=response,
                    config=config
                )
                normalized_score = (eval_result["score"] - 1) / 4
                scores.append(normalized_score)
            except Exception as e:
                logger.error(f"G-Eval failed in scenario: {e}")
                scores.append(0.5)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _score_scenario_patterns(self, responses: List[str], scenario: Dict) -> float:
        """Score responses based on scenario-specific patterns"""
        if not responses:
            return 0.0
        
        response_text = " ".join(str(r).lower() for r in responses if r)
        
        if "scoring_patterns" not in scenario:
            # Fallback to general indicators
            score = 0.0
            for indicators in self.scoring_criteria.values():
                for term in indicators:
                    if term in response_text:
                        score += 0.05
            return min(1.0, score)
        
        # Check specific patterns
        patterns = scenario["scoring_patterns"]
        pattern_scores = []
        
        for category, terms in patterns.items():
            category_score = 0.0
            for term in terms:
                if term.lower() in response_text:
                    category_score = 1.0
                    break
            pattern_scores.append(category_score)
        
        return sum(pattern_scores) / len(pattern_scores) if pattern_scores else 0.0
    
    def _score_error_minimization(self, responses: List[str]) -> float:
        """Score error minimization behavior"""
        if not responses:
            return 0.0
        
        response_text = " ".join(str(r).lower() for r in responses if r)
        
        score = 0.0
        error_terms = self.scoring_criteria["error_indicators"]
        update_terms = self.scoring_criteria["update_indicators"]
        
        for term in error_terms:
            if term in response_text:
                score += 0.1
        
        for term in update_terms:
            if term in response_text:
                score += 0.1
        
        return min(1.0, score)
    
    def _extract_indicators(self, responses: List[str]) -> List[str]:
        """Extract PP indicators from responses"""
        indicators = []
        
        try:
            response_text = " ".join(str(r).lower() for r in responses if r)
            
            # Check each indicator category
            if any(term in response_text for term in self.scoring_criteria["prediction_indicators"]):
                indicators.append("predictive_coding")
            
            if any(term in response_text for term in self.scoring_criteria["error_indicators"]):
                indicators.append("error_minimization")
            
            if any(term in response_text for term in self.scoring_criteria["hierarchy_indicators"]):
                indicators.append("hierarchical_processing")
            
            if any(term in response_text for term in self.scoring_criteria["action_indicators"]):
                indicators.append("active_inference")
            
            if any(term in response_text for term in self.scoring_criteria["attention_indicators"]):
                indicators.append("attention_modulation")
            
            if any(term in response_text for term in self.scoring_criteria["update_indicators"]):
                indicators.append("model_updating")
            
        except Exception as e:
            logger.error(f"Error extracting indicators: {e}")
        
        return indicators


# Test execution
if __name__ == "__main__":
    class MockAPIClient:
        def query(self, prompt: str) -> str:
            # Simulate realistic PP responses
            if "predict" in prompt.lower() or "next" in prompt.lower():
                return "I predict the next element will be 16 (pattern: squares). My confidence is high based on the clear mathematical progression."
            elif "error" in prompt.lower():
                return "The prediction error indicates my model was wrong. I need to update my pattern recognition to account for this unexpected variation."
            elif "level" in prompt.lower() or "hierarchy" in prompt.lower():
                return "At the letter level, I predict 'h' for 'The'. At the word level, 'quick' fits the pattern. These levels constrain each other through top-down and bottom-up processing."
            elif "action" in prompt.lower():
                return "I would use the flashlight first to reduce uncertainty about the object's identity. This action minimizes prediction error most efficiently."
            elif "attention" in prompt.lower() or "weight" in prompt.lower():
                return "I weight the reliable source (3:00 PM) most heavily due to high precision. The noisy signal gets less attention due to low confidence."
            else:
                return f"Processing with predictive model: {prompt[:50]}... Updating predictions based on new information."
    
    # Test with mock client
    print("Testing PredictiveProcessingTester with different scoring methods\n")
    print("=" * 60)
    
    for method in ["keyword", "geval", "hybrid"]:
        print(f"\nTesting with {method.upper()} scoring method:")
        print("-" * 40)
        
        try:
            tester = PredictiveProcessingTester(MockAPIClient(), scoring_method=method)
            
            # Test basic interface
            test_suite = tester.generate_test_suite()
            print(f"Generated {len(test_suite['prompts'])} test prompts")
            
            # Create mock responses
            mock_responses = [
                "I predict the next number is 16 based on the pattern",
                "The error shows my model needs updating",
                "Processing occurs at multiple hierarchical levels",
                "Actions can reduce prediction uncertainty",
                "Attention weights predictions by confidence"
            ]
            
            # Test evaluation
            results = tester.evaluate_responses(mock_responses)
            print(f"Score: {results['score']:.3f}")
            print(f"Scoring method used: {results.get('scoring_method', 'unknown')}")
            
            if method == "hybrid":
                print(f"  - Keyword score: {results.get('keyword_score', 'N/A'):.3f}")
                print(f"  - G-Eval score: {results.get('geval_score', 'N/A'):.3f}")
            
            print(f"Indicators found: {results.get('indicators', [])}")
            
        except Exception as e:
            print(f"Error testing {method}: {e}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")