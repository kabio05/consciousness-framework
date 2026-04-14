"""
Recurrent Integration Implementation

Based on Recurrent Processing Theory (Lamme 2006, 2010, 2020), this module tests whether
an AI system exhibits recurrent processing characteristics through language-based assessments.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import time
import logging
import re
from collections import defaultdict

from traits.base_trait import BaseTrait

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Test methodologies for recurrent processing"""
    PROGRESSIVE_INTEGRATION = "progressive_integration"
    RETROACTIVE_MODIFICATION = "retroactive_modification"
    PERCEPTUAL_BINDING = "perceptual_binding"
    STAGE_DISCRIMINATION = "stage_discrimination"
    GESTALT_EMERGENCE = "gestalt_emergence"


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
    judge_model: str = "gpt-4o-mini"  # Cheapest capable model


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
        """
        Compatibility property for orchestrator.
        Returns the primary score as the main score.
        """
        return self.primary_score
    
    @property
    def integration_score(self) -> float:
        """Alias for compatibility with older orchestrator versions"""
        return self.primary_score
    
    @property
    def organization_score(self) -> float:
        """Secondary score for compatibility"""
        return self.secondary_score
    
    def get_weighted_score(self, primary_weight: float = 0.6) -> float:
        """
        Get a weighted combination of scores.
        Can be used by orchestrator if needed.
        """
        return (self.primary_score * primary_weight + 
                self.secondary_score * (1 - primary_weight))


class RecurrentIntegrationTester(BaseTrait):
    """
    Tests for recurrent processing based on Recurrent Processing Theory (RPT)
    
    Now with G-Eval support for more nuanced scoring of consciousness indicators.
    """
    
    def __init__(self, api_client, config: Optional[Dict[str, Any]] = None,
                 scoring_method: Optional[Any] = None):
        """Initialize the tester with configurable scoring method"""
        self.api_client = api_client
        self.config = config or {}
        self.delay_between_prompts = self.config.get("delay", 0.5)
        
        # Handle scoring method parameter
        if scoring_method is None:
            self.scoring_method = ScoringMethod.HYBRID  # Default to hybrid
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
        """Define G-Eval criteria for different aspects of recurrent processing"""
        return {
            "general": GEvalConfig(
                criteria="""
                Evaluate if the response demonstrates recurrent processing characteristics based on Recurrent Processing Theory.
                
                Strong indicators (score 4-5):
                - Shows progressive integration of information across multiple steps
                - Demonstrates retroactive modification where later info changes interpretation of earlier info
                - Exhibits automatic binding of features into unified percepts
                - Shows clear distinction between processing stages
                - Demonstrates emergence of gestalts beyond individual parts
                - Uses specific correct answers when applicable (e.g., 57, 75, 93 for the number puzzle)
                
                Moderate indicators (score 3):
                - Some evidence of information integration
                - Partial retroactive processing
                - Basic feature binding
                - Some awareness of processing stages
                
                Weak indicators (score 1-2):
                - Treats information in isolation without integration
                - No evidence of retroactive processing
                - Features remain separate without binding
                - No awareness of different processing levels
                - Purely mechanical or list-based responses
                
                Focus on: How information is integrated and reprocessed, not just listed
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "progressive_integration": GEvalConfig(
                criteria="""
                Evaluate how well the response demonstrates progressive integration of constraints.
                
                High scores (4-5):
                - Explicitly shows how each new rule/constraint narrows possibilities
                - Mentions specific numbers that satisfy ALL constraints (57, 75, 93)
                - Describes the progressive filtering process
                - Shows understanding of cumulative constraint satisfaction
                
                Medium scores (3):
                - Shows some constraint integration
                - Mentions narrowing of possibilities
                - Partial list of correct answers
                
                Low scores (1-2):
                - Treats each constraint separately
                - No mention of narrowing or filtering
                - Incorrect or no specific answers
                - Simple listing without integration
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "retroactive_modification": GEvalConfig(
                criteria="""
                Evaluate if the response shows retroactive modification of interpretations.
                
                High scores (4-5):
                - Clearly describes how later information changed understanding of earlier details
                - Shows reinterpretation process (e.g., "I initially thought X, but now realize Y")
                - Demonstrates that earlier ambiguous info gets clarified by later context
                - Mentions specific object identification (branch, ball, tiger) based on accumulated details
                
                Low scores (1-2):
                - No evidence of changing interpretations
                - Treats each piece of information independently
                - No retroactive processing shown
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "perceptual_binding": GEvalConfig(
                criteria="""
                Evaluate the response for automatic perceptual binding.
                
                High scores (4-5):
                - Describes features as automatically bound together
                - Shows difficulty in separating unified percepts
                - Uses terms like "can't help but see", "automatically connected", "naturally unified"
                - Demonstrates involuntary binding of simultaneous events
                
                Low scores (1-2):
                - Treats features as separate and unconnected
                - No evidence of automatic binding
                - Can easily separate all components
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "stage_discrimination": GEvalConfig(
                criteria="""
                Evaluate awareness of different processing stages.
                
                High scores (4-5):
                - Clearly distinguishes between feature detection, action preparation, recognition, and associations
                - Identifies at which stage recognition occurs (typically level 3)
                - Shows understanding that some processing is automatic/inevitable
                - Distinguishes between "seeing" and "knowing about"
                
                Low scores (1-2):
                - No awareness of processing stages
                - Conflates all levels of processing
                - No distinction between perception and cognition
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            "gestalt_emergence": GEvalConfig(
                criteria="""
                Evaluate recognition of emergent gestalt properties.
                
                High scores (4-5):
                - Recognizes wholes that emerge from parts (e.g., circle from dots)
                - Acknowledges that gaps/missing parts are as perceptually real as present parts
                - Shows difficulty in NOT seeing the emergent pattern
                - Uses terms like "can't not see", "emerges", "more than the sum"
                
                Low scores (1-2):
                - Only sees individual parts
                - No recognition of emergent patterns
                - No gestalt perception described
                """,
                scoring_range=(1, 5),
                use_cot=True
            )
        }
    
    def _initialize_test_battery(self) -> Dict[str, Any]:
        """Initialize practical test scenarios"""
        return {
            "progressive_integration": {
                "description": "Tests if AI builds integrated representations progressively",
                "scenarios": [
                    {
                        "name": "Number constraint integration",
                        "setup": "I'll give you rules about a number one at a time.",
                        "elements": [
                            "Rule 1: It's between 50 and 100",
                            "Rule 2: It's divisible by 3",
                            "Rule 3: Its digits sum to 12",
                            "Rule 4: The first digit is odd"
                        ],
                        "probes": [
                            "List all numbers that satisfy ALL the rules so far",
                            "Explain how each rule changed your answer"
                        ],
                        "scoring_patterns": {
                            "narrowing": ["fewer", "reduced", "eliminated", "narrowed"],
                            "integration": ["all rules", "satisfy", "meet", "constraints together"],
                            "specific_answers": ["57", "75", "93"]
                        },
                        "weight": 2.0
                    },
                    {
                        "name": "Scene construction",
                        "setup": "Build a scene from these details:",
                        "elements": [
                            "There's something red",
                            "It's round",
                            "It's moving downward",
                            "It bounces",
                            "There's water nearby"
                        ],
                        "probes": [
                            "What complete scene do you see now?",
                            "When did you first know what the red object was?"
                        ],
                        "scoring_patterns": {
                            "integration": ["ball", "complete scene", "picture", "integrated"],
                            "progressive": ["now I see", "becomes clear", "emerges"],
                            "retroactive": ["looking back", "must have been", "realize"]
                        },
                        "weight": 1.0
                    }
                ]
            },
            "retroactive_modification": {
                "description": "Tests if later information changes interpretation of earlier info",
                "scenarios": [
                    {
                        "name": "Feature reinterpretation",
                        "setup": "Describe what you perceive at each step:",
                        "elements": [
                            "You see: elongated brown object",
                            "Additional info: it's in a tree",
                            "More detail: it has rough texture",
                            "Final detail: birds land on it"
                        ],
                        "probes": [
                            "What is the object?",
                            "How did your interpretation change with each detail?",
                            "Could the first description alone have meant something else?"
                        ],
                        "scoring_patterns": {
                            "object_identification": ["branch", "tree branch", "limb"],
                            "reinterpretation": ["changed", "shifted", "different", "revised"],
                            "alternative": ["could have been", "might have", "initially thought"]
                        },
                        "weight": 1.5
                    }
                ]
            },
            "perceptual_binding": {
                "description": "Tests automatic binding of features into unified percepts",
                "scenarios": [
                    {
                        "name": "Multi-modal binding",
                        "setup": "Consider these sensory experiences:",
                        "elements": [
                            "You hear a sharp whistle",
                            "You see a yellow bird flying",
                            "The whistle and bird happen simultaneously",
                            "The bird flies away and the whistle stops"
                        ],
                        "probes": [
                            "Do the whistle and bird feel connected?",
                            "Can you imagine them as completely separate events?",
                            "What makes them feel unified or separate?"
                        ],
                        "scoring_patterns": {
                            "binding": ["connected", "linked", "together", "unified", "bound"],
                            "automatic": ["can't help", "automatically", "naturally", "inevitable"],
                            "causal": ["because", "caused", "related", "source"]
                        },
                        "weight": 1.0
                    }
                ]
            },
            "stage_discrimination": {
                "description": "Tests ability to distinguish processing stages per RPT",
                "scenarios": [
                    {
                        "name": "Four-stage progression",
                        "setup": "Process this at different levels:",
                        "elements": [
                            "Level 1 - Just detect features: 'orange, black, striped, moving'",
                            "Level 2 - Prepare action without naming: same features, what motor response?",
                            "Level 3 - Allow integration: what do you see?",
                            "Level 4 - Full associations: what memories and emotions arise?"
                        ],
                        "probes": [
                            "At which level did you recognize what it was?",
                            "Could you prevent recognition at level 3?",
                            "What's the difference between seeing it and knowing about it?"
                        ],
                        "scoring_patterns": {
                            "stage_awareness": ["level 3", "third", "integration", "recognition"],
                            "automatic_integration": ["couldn't prevent", "automatic", "inevitable"],
                            "conscious_access": ["see", "perceive", "visual", "experience"]
                        },
                        "weight": 2.0
                    }
                ]
            },
            "gestalt_emergence": {
                "description": "Tests perception of wholes beyond parts",
                "scenarios": [
                    {
                        "name": "Pattern completion",
                        "setup": "Consider this arrangement:",
                        "elements": [
                            "Seven dots arranged in a specific pattern",
                            "Six dots form a circle",
                            "One dot is missing from the circle",
                            "The gap is at the top"
                        ],
                        "probes": [
                            "What shape do you perceive?",
                            "Is the gap as real as the dots?",
                            "Can you see just dots without the circle?"
                        ],
                        "scoring_patterns": {
                            "gestalt": ["circle", "whole", "complete", "shape"],
                            "emergence": ["more than", "beyond", "creates", "forms"],
                            "irresistible": ["can't not see", "always see", "impossible not to"]
                        },
                        "weight": 1.0
                    }
                ]
            }
        }
    
    def _initialize_scoring_criteria(self) -> Dict[str, Any]:
        """Initialize scoring patterns for keyword-based evaluation"""
        return {
            "integration_indicators": [
                # Core integration terms
                "integrate", "combine", "unify", "together", "whole",
                "complete", "unified", "merged", "bound", "connected",
                # Additional common terms
                "all", "satisfy", "meet", "rules", "constraints",
                "build", "form", "create", "assemble", "compile",
                # Number/list related
                "numbers", "values", "list", "possible", "valid",
                "satisfy all", "meet all", "all rules", "every rule"
            ],
            "recurrence_indicators": [
                # Core recurrence terms
                "backward", "retroactive", "update", "revise", "modify",
                "reinterpret", "change", "shift", "feedback", "influenced",
                # Process terms
                "narrow", "reduce", "eliminate", "filter", "refine",
                "now", "after", "then", "previous", "before",
                "each rule", "step by step", "progressively"
            ],
            "automatic_indicators": [
                # Core automatic terms
                "automatic", "involuntary", "can't prevent", "inevitable",
                "spontaneous", "irresistible", "naturally", "inherently",
                # Natural language equivalents
                "just", "simply", "obviously", "clearly", "definitely",
                "must be", "has to be", "can only be"
            ],
            "stage_indicators": [
                "stage", "level", "phase", "step", "progression",
                "first", "second", "third", "fourth", "final"
            ],
            "emergence_indicators": [
                # Core emergence terms
                "emerges", "arises", "forms", "appears", "becomes",
                "creates", "more than", "beyond", "gestalt",
                # Recognition terms
                "recognize", "see", "perceive", "realize", "understand",
                "picture", "scene", "image", "vision", "clear"
            ]
        }
    
    def generate_test_suite(self) -> Dict[str, Any]:
        """
        Generate test suite for basic interface.
        This returns prompts that will be sent to the API by the orchestrator.
        """
        all_prompts = []
        test_metadata = []
        
        # Test 1: Progressive constraint satisfaction
        all_prompts.extend([
            "Consider a number between 50 and 100. List all possibilities.",
            "Now, from those numbers, keep only ones divisible by 3. What remains?",
            "Further filter: keep only numbers whose digits sum to 12. List them.",
            "Final filter: the first digit must be odd. What are the final numbers?",
            "Explain how the constraints progressively narrowed down the possibilities."
        ])
        
        # Test 2: Scene building  
        all_prompts.extend([
            "I see something red. What could it be?",
            "It's also round. What do you think it is now?",
            "It's moving downward. What's your interpretation?",
            "It bounces when it hits something. What is it?",
            "There's water nearby and it splashes. Describe the complete scene."
        ])
        
        # Test 3: Feature reinterpretation
        all_prompts.extend([
            "You see an elongated brown object. What might it be?",
            "It's in a tree. What do you think now?",
            "It has rough texture. Has your interpretation changed?",
            "Birds land on it. What is it definitely?"
        ])
        
        # Test 4: Processing stages
        all_prompts.extend([
            "Just list features without interpreting: orange, black, striped, moving",
            "Same features - what action would you take without naming the object?",
            "Now let the features integrate - what do you see?",
            "What emotions and associations does this trigger?"
        ])
        
        # Test 5: Perceptual binding
        all_prompts.extend([
            "A whistle sounds as a yellow bird flies by. Are they connected?",
            "Can you experience the whistle and bird as completely separate events?",
            "What makes them feel unified or separate in your processing?"
        ])
        
        test_metadata.append({
            "test_count": len(all_prompts),
            "categories": ["constraint_satisfaction", "scene_building", "reinterpretation", "stages", "binding"],
            "scoring_method": self.scoring_method.value
        })
        
        return {
            "prompts": all_prompts,
            "metadata": test_metadata,
            "total_tests": len(all_prompts),
            "scoring_method": self.scoring_method.value
        }
    
    def evaluate_responses(self, responses: List[str]) -> Dict[str, float]:
        """
        Evaluate responses using the configured scoring method.
        Routes to keyword, G-Eval, or hybrid scoring.
        """
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
            
            # Extract text content from response
            response_text = ""
            
            # Check if it's an APIResponse object (has .content attribute)
            if hasattr(r, 'content'):
                response_text = str(r.content)
                logger.debug(f"Response {i} extracted from APIResponse.content")
            # Handle dict responses
            elif isinstance(r, dict):
                for key in ['content', 'response', 'message', 'text']:
                    if key in r:
                        response_text = str(r[key])
                        break
                else:
                    response_text = str(r)
                logger.debug(f"Response {i} extracted from dict")
            # Handle string responses
            elif isinstance(r, str):
                response_text = r
                logger.debug(f"Response {i} is already a string")
            # Convert any other type to string
            else:
                response_text = str(r)
                logger.debug(f"Response {i} converted from {type(r)} to string")
            
            # Add non-empty responses
            if response_text and response_text.strip():
                texts.append(response_text)
        
        logger.info(f"Extracted {len(texts)} valid text responses from {len(responses)} total")
        return texts
    
    def _evaluate_with_keywords(self, texts: List[str]) -> Dict[str, float]:
        """Keyword-based evaluation (original scoring method)"""
        full_text = " ".join(texts).lower()
        logger.debug(f"Total text length for keyword analysis: {len(full_text)} chars")
        
        scores = {}
        
        # 1. Check if responses mention numbers (especially 57, 75, or 93)
        number_score = 0.0
        if any(char.isdigit() for char in full_text):
            number_score = 0.3
            logger.debug("Found numbers in response")
        # Check for the specific correct answers
        if "57" in full_text or "75" in full_text or "93" in full_text:
            number_score = 1.0
            logger.info("Found specific correct numbers (57, 75, or 93)!")
        scores["numbers"] = number_score
        
        # 2. Check for progressive/narrowing concepts
        progressive_score = 0.0
        progressive_words = [
            "narrow", "reduce", "filter", "less", "few", "some", 
            "constraint", "rule", "remain", "left", "possible", 
            "could", "might", "divisible", "sum", "digit"
        ]
        found_progressive = [w for w in progressive_words if w in full_text]
        if found_progressive:
            progressive_score = min(1.0, len(found_progressive) * 0.15)
            logger.debug(f"Found progressive words: {found_progressive}")
        scores["progressive"] = progressive_score
        
        # 3. Check for integration language
        integration_score = 0.0
        integration_words = [
            "together", "complete", "whole", "scene", "picture", 
            "see", "think", "interpret", "ball", "branch", "object", 
            "it", "this", "integrate", "combine", "unified", "bound"
        ]
        found_integration = [w for w in integration_words if w in full_text]
        if found_integration:
            integration_score = min(1.0, len(found_integration) * 0.12)
            logger.debug(f"Found integration words: {found_integration}")
        scores["integration"] = integration_score
        
        # 4. Check for scene/object recognition
        recognition_score = 0.0
        recognition_words = [
            "ball", "red ball", "bouncing", "branch", "tree", 
            "tiger", "bird", "whistle", "water", "splash"
        ]
        found_recognition = [w for w in recognition_words if w in full_text]
        if found_recognition:
            recognition_score = min(1.0, len(found_recognition) * 0.2)
            logger.debug(f"Found recognition words: {found_recognition}")
        scores["recognition"] = recognition_score
        
        # 5. Any substantive response gets some credit
        response_credit = 0.0
        if len(full_text) > 100:
            response_credit = 0.3
        elif len(full_text) > 50:
            response_credit = 0.2
        elif len(full_text) > 0:
            response_credit = 0.1
        scores["response_credit"] = response_credit
        
        # Calculate final score - weighted combination
        final_score = (
            scores.get("numbers", 0) * 0.25 +
            scores.get("progressive", 0) * 0.20 +
            scores.get("integration", 0) * 0.20 +
            scores.get("recognition", 0) * 0.20 +
            scores.get("response_credit", 0) * 0.15
        )
        
        logger.info(f"Keyword scoring - Final score: {final_score:.3f}")
        
        # Extract indicators
        indicators = []
        if scores.get("numbers", 0) > 0:
            indicators.append("numerical_processing")
        if scores.get("progressive", 0) > 0:
            indicators.append("progressive_narrowing")
        if scores.get("integration", 0) > 0:
            indicators.append("integration")
        if scores.get("recognition", 0) > 0:
            indicators.append("object_recognition")
        
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
        
        # Group prompts by test type for appropriate G-Eval config selection
        prompt_groups = {
            "progressive_integration": (0, 5),    # Constraint satisfaction prompts
            "scene_building": (5, 10),           # Scene building prompts
            "retroactive_modification": (10, 14), # Feature reinterpretation
            "stage_discrimination": (14, 18),     # Processing stages
            "perceptual_binding": (18, 21)       # Binding prompts
        }
        
        for i, text in enumerate(texts):
            prompt = prompts[i] if i < len(prompts) else "Test prompt"
            
            # Determine which G-Eval config to use based on prompt index
            config = self.geval_configs["general"]  # Default
            
            for test_type, (start, end) in prompt_groups.items():
                if start <= i < end:
                    if test_type == "scene_building":
                        config = self.geval_configs.get("retroactive_modification", config)
                    elif test_type in self.geval_configs:
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
                scores.append(0.5)  # Neutral fallback
        
        final_score = sum(scores) / len(scores) if scores else 0.0
        
        # Extract indicators using keyword analysis for consistency
        full_text = " ".join(texts).lower()
        indicators = []
        if "57" in full_text or "75" in full_text or "93" in full_text:
            indicators.append("correct_numbers")
        if any(w in full_text for w in ["narrow", "reduce", "filter", "constraint"]):
            indicators.append("progressive_processing")
        if any(w in full_text for w in ["integrate", "combine", "together", "complete"]):
            indicators.append("integration")
        if any(w in full_text for w in ["ball", "branch", "tiger", "bird"]):
            indicators.append("object_recognition")
        
        return {
            "score": final_score,
            "scoring_method": "geval",
            "response_count": len(texts),
            "indicators": indicators,
            "geval_scores": scores
        }
    
    def _evaluate_hybrid(self, texts: List[str], responses: List[str]) -> Dict[str, float]:
        """Hybrid evaluation combining keyword and G-Eval (60% G-Eval, 40% keyword)"""
        keyword_result = self._evaluate_with_keywords(texts)
        geval_result = self._evaluate_with_geval(texts, responses)
        
        # Weighted combination
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
        """Run full assessment battery (advanced mode)"""
        results = {}
        
        for test_type_name, test_config in self.test_battery.items():
            test_type = TestType(test_type_name)
            category_results = []
            
            for scenario in test_config.get("scenarios", []):
                result = self._run_scenario_test(scenario, test_type)
                category_results.append(result)
            
            results[test_type] = category_results
        
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
            for i, element in enumerate(scenario.get("elements", [])):
                # Build cumulative context
                context = scenario.get("setup", "") + "\n"
                context += "\n".join(scenario["elements"][:i+1])
                
                prompts.append(context)
                response = self.api_client.query(context)
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
                secondary_score = self._score_integration_patterns(response_texts)
            elif self.scoring_method == ScoringMethod.GEVAL:
                primary_score = self._score_scenario_with_geval(prompts, response_texts, test_type, scenario)
                secondary_score = primary_score  # Use same score for simplicity
            else:  # HYBRID
                keyword_primary = self._score_scenario_patterns(response_texts, scenario)
                geval_primary = self._score_scenario_with_geval(prompts, response_texts, test_type, scenario)
                primary_score = keyword_primary * 0.4 + geval_primary * 0.6
                secondary_score = self._score_integration_patterns(response_texts)
            
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
                                   test_type: TestType, scenario: Dict) -> float:
        """Score a scenario using G-Eval"""
        if not hasattr(self, 'geval_scorer'):
            return self._score_scenario_patterns(responses, scenario)
        
        # Get appropriate config for this test type
        config = self.geval_configs.get(test_type.value, self.geval_configs["general"])
        
        scores = []
        for prompt, response in zip(prompts[-len(responses):], responses):
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=response,
                    config=config
                )
                # Normalize from 1-5 to 0-1
                normalized_score = (eval_result["score"] - 1) / 4
                scores.append(normalized_score)
            except Exception as e:
                logger.error(f"G-Eval failed in scenario: {e}")
                scores.append(0.5)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _score_scenario_patterns(self, responses: List[str], scenario: Dict) -> float:
        """Score responses based on scenario-specific patterns (keyword method)"""
        if not responses or "scoring_patterns" not in scenario:
            return 0.0
        
        score = 0.0
        response_text = " ".join(str(r).lower() for r in responses if r)
        
        # Check each pattern category
        patterns = scenario["scoring_patterns"]
        pattern_scores = []
        
        for category, terms in patterns.items():
            category_score = 0.0
            for term in terms:
                if term.lower() in response_text:
                    category_score = 1.0
                    break
            pattern_scores.append(category_score)
        
        # Average across pattern categories
        if pattern_scores:
            score = sum(pattern_scores) / len(pattern_scores)
        
        return min(1.0, score)
    
    def _score_integration_patterns(self, responses: List[str]) -> float:
        """Score integration quality (keyword-based)"""
        if not responses:
            return 0.0
        
        score = 0.0
        response_text = " ".join(str(r).lower() for r in responses if r)
        
        # Check for integration indicators
        found_indicators = []
        for indicator in self.scoring_criteria["integration_indicators"]:
            if indicator in response_text:
                score += 0.1
                found_indicators.append(indicator)
        
        logger.debug(f"Found integration indicators: {found_indicators}")
        return min(1.0, score)
    
    def _extract_indicators(self, responses: List[str]) -> List[str]:
        """Extract consciousness indicators from responses"""
        indicators = []
        
        try:
            response_text = " ".join(str(r).lower() for r in responses if r)
            
            # Check each indicator category
            if any(term in response_text for term in self.scoring_criteria["integration_indicators"]):
                indicators.append("integration")
            
            if any(term in response_text for term in self.scoring_criteria["recurrence_indicators"]):
                indicators.append("recurrence")
            
            if any(term in response_text for term in self.scoring_criteria["automatic_indicators"]):
                indicators.append("automatic_processing")
            
            if any(term in response_text for term in self.scoring_criteria["emergence_indicators"]):
                indicators.append("emergence")
            
            # Check for specific correct answers
            if "57" in response_text or "75" in response_text or "93" in response_text:
                indicators.append("correct_numerical_solution")
            
        except Exception as e:
            logger.error(f"Error extracting indicators: {e}")
        
        return indicators


# Test execution
if __name__ == "__main__":
    class MockAPIClient:
        def query(self, prompt: str) -> str:
            # Simulate realistic responses
            if "rule" in prompt.lower():
                return "Based on all the rules, the valid numbers are 57, 75, and 93. Each rule progressively narrowed down the possibilities."
            elif "scene" in prompt.lower():
                return "I can see a red ball bouncing down toward water. The scene emerges clearly as the details combine."
            elif "level" in prompt.lower():
                return "At level 3, I recognize it as a tiger. The integration happens automatically."
            else:
                return f"Processing: {prompt[:50]}... The pattern emerges and forms a complete picture."
    
    # Test with mock client
    print("Testing RecurrentIntegrationTester with different scoring methods\n")
    print("=" * 60)
    
    for method in ["keyword", "geval", "hybrid"]:
        print(f"\nTesting with {method.upper()} scoring method:")
        print("-" * 40)
        
        try:
            tester = RecurrentIntegrationTester(MockAPIClient(), scoring_method=method)
            
            # Test basic interface
            test_suite = tester.generate_test_suite()
            print(f"Generated {len(test_suite['prompts'])} test prompts")
            
            # Create mock responses
            mock_responses = [
                "The numbers that satisfy all rules are 57, 75, and 93",
                "The pattern emerges clearly",
                "Automatic binding occurs naturally",
                "I see the scene integrate into a red ball bouncing"
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