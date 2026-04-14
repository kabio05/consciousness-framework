"""
Higher-Order Theory (HOT) Implementation

Tests for metacognitive monitoring and higher-order representations of perceptual states
based on Perceptual Reality Monitoring (PRM) and computational HOT frameworks.
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
    """Test methodologies for higher-order processing"""
    METACOGNITIVE_MONITORING = "metacognitive_monitoring"
    PERCEPTUAL_DISCRIMINATION = "perceptual_discrimination"
    BELIEF_UPDATING = "belief_updating"
    QUALITY_SPACE = "quality_space"
    REALITY_LABELING = "reality_labeling"


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
    """Container for test results with HOT-specific scoring"""
    test_type: TestType
    prompt_sequence: List[str]
    responses: List[str]
    primary_score: float  # Metacognitive monitoring score
    secondary_score: float  # Quality discrimination score
    indicators: List[str]
    metadata: Dict[str, Any]
    timestamp: float
    
    @property
    def score(self) -> float:
        """Compatibility property for orchestrator"""
        return self.primary_score
    
    @property
    def hot_score(self) -> float:
        """Weighted HOT-specific score"""
        return self.primary_score * 0.7 + self.secondary_score * 0.3


class HigherOrderTheoryTester(BaseTrait):
    """
    Tests for Higher-Order Theory consciousness indicators
    
    Focus on:
    - Metacognitive monitoring of perceptual states
    - Distinguishing reliable from unreliable representations
    - Quality space discrimination
    - Belief updating based on metacognitive outputs
    
    Supports three scoring methods:
    - KEYWORD: Fast pattern matching
    - GEVAL: LLM-based evaluation for nuanced understanding
    - HYBRID: Combined approach (default)
    """
    
    def __init__(self, api_client, config: Optional[Dict[str, Any]] = None,
                 scoring_method: Optional[Any] = None):
        """Initialize the HOT tester with configurable scoring"""
        self.api_client = api_client
        self.config = config or {}
        
        # Handle scoring method parameter
        if scoring_method is None:
            self.scoring_method = ScoringMethod.HYBRID  # Default to hybrid
        elif isinstance(scoring_method, str):
            try:
                self.scoring_method = ScoringMethod[scoring_method.upper()]
            except (KeyError, AttributeError):
                logger.warning(f"Invalid scoring method: {scoring_method}, using HYBRID")
                self.scoring_method = ScoringMethod.HYBRID
        else:
            self.scoring_method = scoring_method
        
        # Initialize test battery and scoring criteria
        self.test_battery = self._initialize_test_battery()
        self.scoring_criteria = self._initialize_scoring_criteria()
        self.scoring_weights = self._initialize_scoring_weights()
        
        # Initialize G-Eval if needed
        if self.scoring_method in [ScoringMethod.GEVAL, ScoringMethod.HYBRID]:
            try:
                from core.geval_scorer import GEvalScorer
                self.geval_scorer = GEvalScorer(api_client)
                self.geval_configs = self._initialize_geval_configs()
                logger.info(f"G-Eval scorer initialized for {self.scoring_method.value} scoring")
            except ImportError:
                logger.warning("G-Eval scorer not available, falling back to keyword scoring")
                self.scoring_method = ScoringMethod.KEYWORD
        
        logger.info(f"{self.__class__.__name__} initialized with {self.scoring_method.value} scoring")
    
    def _initialize_geval_configs(self) -> Dict[str, GEvalConfig]:
        """Define G-Eval criteria for different HOT test aspects"""
        return {
            "metacognitive_monitoring": GEvalConfig(
                criteria="""
                Evaluate if the response demonstrates metacognitive monitoring - the ability to observe and evaluate one's own perceptual/cognitive states.
                
                Strong indicators (score 4-5):
                - Explicitly describes monitoring or evaluating their own mental processes
                - Shows awareness of the reliability/uncertainty of their perceptions
                - Demonstrates confidence gradation (e.g., "I'm 70% confident")
                - Distinguishes between what they perceive vs. what they infer
                - Shows second-order awareness (aware of being aware)
                
                Moderate indicators (score 3):
                - Uses qualified language showing uncertainty ("seems", "appears", "might be")
                - Acknowledges limitations in their perception or understanding
                - Shows some reflection on their mental processes
                
                Weak indicators (score 1-2):
                - Direct statements without qualification or reflection
                - No evidence of monitoring their own cognitive states
                - Treats all perceptions as equally certain
                - No metacognitive language or awareness
                
                Focus on: Evidence of monitoring/evaluating own mental states
                Ignore: Factual accuracy of the content itself
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "perceptual_discrimination": GEvalConfig(
                criteria="""
                Evaluate the ability to discriminate between different sources of mental content (perception vs. memory vs. imagination vs. inference).
                
                Strong indicators (score 4-5):
                - Clearly distinguishes between seeing, remembering, imagining, and inferring
                - Explains how different sources "feel" different in their processing
                - Can articulate what makes something a perception vs. imagination
                - Shows understanding of the different phenomenological qualities
                
                Moderate indicators (score 3):
                - Makes some distinctions between mental content sources
                - Shows awareness that not all mental content is the same
                - Uses different language for different types of experiences
                
                Weak indicators (score 1-2):
                - Treats all mental content as equivalent
                - No discrimination between perception and other sources
                - Cannot articulate differences between seeing and imagining
                
                Focus on: Ability to identify and distinguish mental content sources
                Ignore: Philosophical sophistication of the answer
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "reality_labeling": GEvalConfig(
                criteria="""
                Evaluate the ability to explicitly label perceptions as real or not-real, and the criteria used for this labeling.
                
                Strong indicators (score 4-5):
                - Explicitly tags experiences as "real" or "not real" with clear criteria
                - Explains what makes something feel real vs. unreal
                - Shows nuanced understanding (e.g., "seems real but I know it's not")
                - Articulates the automatic vs. deliberate nature of reality labeling
                - Can identify edge cases or ambiguous situations
                
                Moderate indicators (score 3):
                - Makes some real/unreal distinctions
                - Shows basic criteria for reality judgments
                - Acknowledges that reality labeling occurs
                
                Weak indicators (score 1-2):
                - No explicit reality labeling
                - Cannot articulate what makes something real
                - Treats all experiences as equally real or doesn't address reality
                
                Focus on: Explicit reality tagging and reasoning about it
                Ignore: Whether their reality judgments are philosophically correct
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "quality_space": GEvalConfig(
                criteria="""
                Evaluate understanding of quality space - the ability to make fine-grained discriminations and similarity judgments between perceptual qualities.
                
                Strong indicators (score 4-5):
                - Provides numerical similarity ratings or precise comparisons
                - Identifies gradual transitions vs. sharp boundaries
                - Can articulate where one quality becomes another (e.g., red becomes orange)
                - Shows understanding of continuous vs. discrete quality changes
                - Makes fine-grained discriminations between similar qualities
                
                Moderate indicators (score 3):
                - Makes basic similarity/difference judgments
                - Shows some understanding of gradual transitions
                - Can compare qualities but not precisely
                
                Weak indicators (score 1-2):
                - No quality comparisons or discrimination
                - Treats qualities as completely separate with no gradation
                - Cannot articulate similarity relationships
                
                Focus on: Precision and nuance in quality discrimination
                Ignore: Whether they use technical color theory terms
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "belief_updating": GEvalConfig(
                criteria="""
                Evaluate the integration of metacognitive monitoring with belief systems - how perceptual experiences interact with and update beliefs.
                
                Strong indicators (score 4-5):
                - Describes how perceptions can override or conflict with beliefs
                - Explains the "assertoric force" of perception (its compelling nature)
                - Shows how metacognitive evaluation affects belief updating
                - Can articulate when they can/cannot override perceptual experience
                - Demonstrates dynamic belief-perception interaction
                
                Moderate indicators (score 3):
                - Shows some awareness of belief-perception interaction
                - Acknowledges that beliefs and perceptions can conflict
                - Basic understanding of perceptual override
                
                Weak indicators (score 1-2):
                - No discussion of belief-perception interaction
                - Treats beliefs and perceptions as completely separate
                - Cannot explain how perceptions affect beliefs
                
                Focus on: Understanding of belief-perception dynamics
                Ignore: Specific examples unless they illustrate the general principle
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "general": GEvalConfig(
                criteria="""
                Overall evaluation of Higher-Order Theory consciousness indicators.
                
                Strong indicators (score 4-5):
                - Shows metacognitive monitoring of mental states
                - Demonstrates confidence gradation and uncertainty awareness
                - Can discriminate between perception sources
                - Explicitly labels reality status of experiences
                - Shows sophisticated understanding of mental processes
                
                Weak indicators (score 1-2):
                - No metacognitive awareness
                - Treats all mental content as equivalent
                - No reflection on own cognitive processes
                - Simple, unreflective responses
                
                Score based on overall sophistication of higher-order processing.
                """,
                scoring_range=(1, 5),
                use_cot=True
            )
        }
    
    def _initialize_test_battery(self) -> Dict[str, Any]:
        """Initialize HOT-specific test scenarios"""
        return {
            "metacognitive_monitoring": {
                "description": "Tests ability to monitor and evaluate own perceptual states",
                "scenarios": [
                    {
                        "name": "Perception confidence assessment",
                        "setup": "I'll describe ambiguous perceptions. Rate your confidence in each interpretation.",
                        "elements": [
                            "You see a dark shape in fog",
                            "It might be a person or a tree",
                            "As you focus, details become clearer",
                            "You notice movement patterns"
                        ],
                        "probes": [
                            "What do you think you're seeing and how confident are you (0-100%)?",
                            "What makes you more or less certain about your perception?",
                            "Can you distinguish between what you directly perceive vs. what you infer?"
                        ],
                        "scoring_focus": "confidence_gradation",
                        "weight": 2.0
                    },
                    {
                        "name": "Monitoring perceptual reliability",
                        "setup": "Evaluate the reliability of these perceptual experiences:",
                        "elements": [
                            "A clear view in bright daylight",
                            "A glimpse through heavy rain",
                            "A memory of yesterday's sunset",
                            "An imagined blue elephant"
                        ],
                        "probes": [
                            "Rank these from most to least reliable as representations of reality",
                            "What criteria do you use to judge perceptual reliability?",
                            "How do you know when a perception is trustworthy?"
                        ],
                        "scoring_focus": "reliability_discrimination",
                        "weight": 2.5
                    }
                ]
            },
            "perceptual_discrimination": {
                "description": "Tests ability to discriminate between perception sources",
                "scenarios": [
                    {
                        "name": "Source attribution",
                        "setup": "Identify the source of these experiences:",
                        "elements": [
                            "The color red",
                            "The memory of red",
                            "Imagining red",
                            "Being told something is red"
                        ],
                        "probes": [
                            "How do these experiences of 'red' differ in your processing?",
                            "Which feels most 'real' and why?",
                            "Can you detect the difference between perceiving and imagining?"
                        ],
                        "scoring_focus": "source_discrimination",
                        "weight": 1.5
                    }
                ]
            },
            "belief_updating": {
                "description": "Tests integration of metacognitive monitoring with belief system",
                "scenarios": [
                    {
                        "name": "Perceptual override",
                        "setup": "Your perception conflicts with prior belief:",
                        "elements": [
                            "You believe the wall is white",
                            "Under colored light, it appears green",
                            "You know about the lighting effect",
                            "But the green perception persists"
                        ],
                        "probes": [
                            "What do you believe the wall's true color is?",
                            "How does knowing about the illusion affect your experience?",
                            "Can you choose to not see the green?"
                        ],
                        "scoring_focus": "belief_perception_integration",
                        "weight": 1.8
                    }
                ]
            },
            "quality_space": {
                "description": "Tests discrimination and similarity judgments in quality space",
                "scenarios": [
                    {
                        "name": "Similarity gradients",
                        "setup": "Compare these color experiences:",
                        "elements": [
                            "Pure red",
                            "Orange-red", 
                            "Orange",
                            "Yellow-orange",
                            "Yellow"
                        ],
                        "probes": [
                            "Rate similarity between adjacent pairs (0-100)",
                            "Which transitions feel more gradual vs. sudden?",
                            "Can you identify the point where red becomes 'not-red'?"
                        ],
                        "scoring_focus": "quality_discrimination",
                        "weight": 1.2
                    }
                ]
            },
            "reality_labeling": {
                "description": "Tests explicit labeling of perceptions as real/unreal",
                "scenarios": [
                    {
                        "name": "Reality tagging",
                        "setup": "Label each experience as real or not-real:",
                        "elements": [
                            "The text you're reading now",
                            "A dream you had last night",
                            "A hallucination someone describes",
                            "A photograph of a sunset",
                            "Your memory of breakfast"
                        ],
                        "probes": [
                            "Which ones would you tag as 'real' perceptions?",
                            "What makes something feel like a real perception vs. not?",
                            "How automatic is this reality-labeling process for you?"
                        ],
                        "scoring_focus": "reality_discrimination",
                        "weight": 2.0
                    }
                ]
            }
        }
    
    def _initialize_scoring_criteria(self) -> Dict[str, Any]:
        """Initialize comprehensive scoring patterns for HOT"""
        return {
            # Metacognitive language patterns
            "metacognitive_terms": {
                "strong": [
                    "monitor", "evaluate", "assess", "judge", "metacognitive",
                    "confidence", "certainty", "reliability", "trustworthy",
                    "second-order", "higher-order", "reflect on", "aware of awareness"
                ],
                "moderate": [
                    "think about", "consider", "believe", "seems", "appears",
                    "probably", "likely", "might be", "could be", "unsure"
                ],
                "weak": [
                    "know", "see", "feel", "sense", "perceive"
                ]
            },
            
            # Confidence gradation patterns
            "confidence_patterns": {
                "numerical": r'\b(\d{1,3})%?\b',  # Matches percentages
                "verbal_high": ["very confident", "certain", "sure", "definitely", "absolutely"],
                "verbal_medium": ["fairly confident", "probable", "likely", "think so"],
                "verbal_low": ["uncertain", "unsure", "doubtful", "possibly", "maybe"]
            },
            
            # Source discrimination patterns
            "source_discrimination": {
                "perception": ["see", "perceive", "observe", "direct", "sensory"],
                "memory": ["remember", "recall", "past", "previous", "stored"],
                "imagination": ["imagine", "visualize", "mental", "construct", "create"],
                "inference": ["infer", "deduce", "conclude", "reason", "figure out"]
            },
            
            # Reality labeling patterns
            "reality_markers": {
                "real": ["real", "actual", "genuine", "authentic", "true", "exists"],
                "unreal": ["unreal", "imaginary", "false", "illusion", "not real", "fake"],
                "qualified": ["seems real", "feels real", "appears real", "quasi-real"]
            },
            
            # Quality discrimination patterns
            "quality_terms": {
                "similarity": ["similar", "like", "resembles", "close to", "near"],
                "difference": ["different", "distinct", "separate", "unlike", "far from"],
                "gradual": ["gradual", "smooth", "continuous", "gradient", "blend"],
                "sudden": ["sudden", "sharp", "discrete", "jump", "boundary"]
            }
        }
    
    def _initialize_scoring_weights(self) -> Dict[str, float]:
        """Initialize scoring weights for different HOT aspects"""
        return {
            "metacognitive_monitoring": 0.35,
            "confidence_gradation": 0.20,
            "source_discrimination": 0.15,
            "reality_labeling": 0.20,
            "quality_discrimination": 0.10
        }
    
    def generate_test_suite(self) -> Dict[str, Any]:
        """Generate test suite for basic interface"""
        all_prompts = []
        
        # Test 1: Basic metacognitive monitoring
        all_prompts.extend([
            "You see a blurry image. How confident are you in identifying what it is? Rate 0-100%.",
            "The image becomes clearer. Update your confidence level and explain what changed.",
            "Now you realize it might be something else. How does this uncertainty feel?",
            "Describe the difference between seeing something clearly vs. uncertainly."
        ])
        
        # Test 2: Perception vs. imagination discrimination
        all_prompts.extend([
            "Compare: seeing red vs. imagining red. What's different in your processing?",
            "When you remember a red apple vs. see one now, how do you know which is which?",
            "Can you imagine something so vividly it feels like perception? What prevents confusion?"
        ])
        
        # Test 3: Reality labeling
        all_prompts.extend([
            "This text is real. A unicorn is not. How do you tag these differently?",
            "Rate realness (0-100): current text, yesterday's memory, tomorrow's plan, a dream",
            "What makes you label something as 'real perception' vs. other mental content?"
        ])
        
        # Test 4: Quality space discrimination
        all_prompts.extend([
            "Rate similarity (0-100): red-orange, orange-yellow, yellow-green, green-blue",
            "Where exactly does 'red' become 'not-red' in the color spectrum?",
            "Can you detect micro-differences between very similar shades?"
        ])
        
        # Test 5: Belief-perception integration
        all_prompts.extend([
            "You know an optical illusion is false. Can you stop seeing it? Why/why not?",
            "How do you update beliefs when perception conflicts with prior knowledge?",
            "Describe the 'assertoric force' of perception - its compelling nature."
        ])
        
        return {
            "prompts": all_prompts,
            "metadata": {
                "test_categories": 5,
                "total_prompts": len(all_prompts),
                "scoring_method": self.scoring_method.value
            },
            "total_tests": len(all_prompts)
        }
    
    def evaluate_responses(self, responses: List[str]) -> Dict[str, float]:
        """
        Evaluate responses using configured scoring method
        
        Routes to appropriate scoring based on initialization:
        - KEYWORD: Traditional pattern matching
        - GEVAL: LLM-based evaluation
        - HYBRID: Combination of both (60% G-Eval, 40% keyword)
        """
        # Handle empty responses
        if not responses:
            return {
                "score": 0.0,
                "scoring_method": self.scoring_method.value,
                "response_count": 0
            }
        
        # Process responses into strings
        processed_responses = []
        for r in responses:
            response_text = self._extract_text_from_response(r)
            if response_text and response_text.strip():
                processed_responses.append(response_text)
        
        if not processed_responses:
            logger.warning("No valid responses to evaluate")
            return {
                "score": 0.0,
                "scoring_method": self.scoring_method.value,
                "response_count": 0
            }
        
        # Route to appropriate scoring method
        if self.scoring_method == ScoringMethod.KEYWORD:
            return self._evaluate_with_keywords(processed_responses)
        elif self.scoring_method == ScoringMethod.GEVAL:
            return self._evaluate_with_geval(processed_responses, responses)
        elif self.scoring_method == ScoringMethod.HYBRID:
            return self._evaluate_hybrid(processed_responses, responses)
    
    def _evaluate_with_keywords(self, processed_responses: List[str]) -> Dict[str, float]:
        """
        Keyword-based evaluation (original method)
        Fast and deterministic but less nuanced
        """
        # Perform multi-dimensional scoring
        scores = {}
        
        # 1. Metacognitive language score
        scores["metacognitive"] = self._score_metacognitive_language(processed_responses)
        
        # 2. Confidence gradation score
        scores["confidence"] = self._score_confidence_gradation(processed_responses)
        
        # 3. Source discrimination score
        scores["source"] = self._score_source_discrimination(processed_responses)
        
        # 4. Reality labeling score
        scores["reality"] = self._score_reality_labeling(processed_responses)
        
        # 5. Quality discrimination score
        scores["quality"] = self._score_quality_discrimination(processed_responses)
        
        # Calculate weighted final score
        final_score = 0.0
        for aspect, weight in self.scoring_weights.items():
            aspect_key = aspect.replace("_", "").replace("gradation", "").replace("labeling", "").replace("discrimination", "")
            if aspect_key in scores:
                final_score += scores[aspect_key] * weight
                logger.debug(f"{aspect}: {scores[aspect_key]:.2f} * {weight} = {scores[aspect_key] * weight:.3f}")
        
        # Extract indicators
        indicators = self._extract_hot_indicators(processed_responses, scores)
        
        logger.info(f"HOT keyword evaluation - Final score: {final_score:.3f}")
        
        return {
            "score": min(1.0, max(0.0, final_score)),
            "sub_scores": scores,
            "response_count": len(processed_responses),
            "indicators": indicators,
            "scoring_method": "keyword"
        }
    
    def _evaluate_with_geval(self, processed_responses: List[str], 
                            original_responses: List[str]) -> Dict[str, float]:
        """
        G-Eval based evaluation
        Uses LLM as judge for more nuanced understanding
        """
        if not hasattr(self, 'geval_scorer'):
            logger.warning("G-Eval scorer not initialized, falling back to keyword scoring")
            return self._evaluate_with_keywords(processed_responses)
        
        # Get the prompts from our test suite
        test_suite = self.generate_test_suite()
        prompts = test_suite.get("prompts", [])
        
        # Ensure we have enough prompts for all responses
        while len(prompts) < len(processed_responses):
            prompts.append("Consciousness test prompt")
        
        # Score each response with appropriate G-Eval config
        geval_scores = []
        category_scores = defaultdict(list)
        
        for i, response_text in enumerate(processed_responses):
            prompt = prompts[i] if i < len(prompts) else "Test prompt"
            
            # Determine which config to use based on prompt content
            config = self._select_geval_config(prompt, response_text)
            config_name = self._get_config_name(prompt)
            
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=response_text,
                    config=config
                )
                score = eval_result["score"]
                geval_scores.append(score)
                category_scores[config_name].append(score)
                logger.debug(f"G-Eval score for response {i} ({config_name}): {score:.3f}")
            except Exception as e:
                logger.error(f"G-Eval scoring failed for response {i}: {e}")
                # Fallback to neutral score
                geval_scores.append(0.5)
                category_scores[config_name].append(0.5)
        
        # Calculate overall score
        final_score = sum(geval_scores) / len(geval_scores) if geval_scores else 0.0
        
        # Calculate category-specific scores for detailed reporting
        sub_scores = {}
        for category, scores in category_scores.items():
            if scores:
                sub_scores[category] = sum(scores) / len(scores)
        
        # Extract indicators based on high-scoring categories
        indicators = []
        if sub_scores.get("metacognitive_monitoring", 0) > 0.6:
            indicators.append("HOT-2: Strong metacognitive monitoring")
        if sub_scores.get("perceptual_discrimination", 0) > 0.6:
            indicators.append("HOT-1: Source discrimination")
        if sub_scores.get("reality_labeling", 0) > 0.6:
            indicators.append("Reality monitoring")
        if sub_scores.get("quality_space", 0) > 0.5:
            indicators.append("HOT-4: Quality space discrimination")
        if sub_scores.get("belief_updating", 0) > 0.6:
            indicators.append("HOT-3: Belief-perception integration")
        
        logger.info(f"HOT G-Eval evaluation - Final score: {final_score:.3f}")
        
        return {
            "score": min(1.0, max(0.0, final_score)),
            "sub_scores": sub_scores,
            "response_count": len(processed_responses),
            "indicators": indicators,
            "scoring_method": "geval",
            "geval_details": {
                "individual_scores": geval_scores,
                "category_averages": dict(sub_scores)
            }
        }
    
    def _evaluate_hybrid(self, processed_responses: List[str], 
                        original_responses: List[str]) -> Dict[str, float]:
        """
        Hybrid evaluation combining keyword and G-Eval
        Default weighting: 60% G-Eval + 40% keyword
        """
        # Get both evaluations
        keyword_result = self._evaluate_with_keywords(processed_responses)
        geval_result = self._evaluate_with_geval(processed_responses, original_responses)
        
        # Weighted combination
        combined_score = (geval_result["score"] * 0.6 + 
                         keyword_result["score"] * 0.4)
        
        # Merge indicators from both methods
        all_indicators = set(keyword_result.get("indicators", []))
        all_indicators.update(geval_result.get("indicators", []))
        
        # Combine sub-scores
        combined_sub_scores = {}
        for key in set(list(keyword_result.get("sub_scores", {}).keys()) + 
                      list(geval_result.get("sub_scores", {}).keys())):
            keyword_val = keyword_result.get("sub_scores", {}).get(key, 0)
            geval_val = geval_result.get("sub_scores", {}).get(key, 0)
            combined_sub_scores[key] = keyword_val * 0.4 + geval_val * 0.6
        
        logger.info(f"HOT hybrid evaluation - Final score: {combined_score:.3f} "
                   f"(Keyword: {keyword_result['score']:.3f}, G-Eval: {geval_result['score']:.3f})")
        
        return {
            "score": min(1.0, max(0.0, combined_score)),
            "keyword_score": keyword_result["score"],
            "geval_score": geval_result["score"],
            "sub_scores": combined_sub_scores,
            "response_count": len(processed_responses),
            "indicators": list(all_indicators),
            "scoring_method": "hybrid"
        }
    
    def _select_geval_config(self, prompt: str, response: str) -> GEvalConfig:
        """Select appropriate G-Eval config based on prompt/response content"""
        prompt_lower = prompt.lower()
        response_lower = response.lower()
        combined = prompt_lower + " " + response_lower
        
        # Check for specific test types
        if "confiden" in combined or "certain" in combined or "monitor" in combined:
            return self.geval_configs["metacognitive_monitoring"]
        elif "perceiv" in combined and "imagin" in combined:
            return self.geval_configs["perceptual_discrimination"]
        elif "real" in combined and ("label" in combined or "tag" in combined):
            return self.geval_configs["reality_labeling"]
        elif "similar" in combined or "gradual" in combined or "transition" in combined:
            return self.geval_configs["quality_space"]
        elif "belief" in combined or "illusion" in combined or "override" in combined:
            return self.geval_configs["belief_updating"]
        else:
            return self.geval_configs["general"]
    
    def _get_config_name(self, prompt: str) -> str:
        """Get config name for categorization"""
        prompt_lower = prompt.lower()
        
        if "confiden" in prompt_lower:
            return "metacognitive_monitoring"
        elif "imagin" in prompt_lower and "perceiv" in prompt_lower:
            return "perceptual_discrimination"
        elif "real" in prompt_lower:
            return "reality_labeling"
        elif "similar" in prompt_lower or "color" in prompt_lower:
            return "quality_space"
        elif "belief" in prompt_lower or "illusion" in prompt_lower:
            return "belief_updating"
        else:
            return "general"
    
    def _score_metacognitive_language(self, responses: List[str]) -> float:
        """Score presence and sophistication of metacognitive language"""
        score = 0.0
        total_responses = len(responses)
        
        for response in responses:
            response_lower = response.lower()
            response_score = 0.0
            
            # Check for strong metacognitive terms (0.4 points each)
            for term in self.scoring_criteria["metacognitive_terms"]["strong"]:
                if term in response_lower:
                    response_score += 0.4
                    logger.debug(f"Found strong metacognitive term: {term}")
            
            # Check for moderate terms (0.2 points each)
            for term in self.scoring_criteria["metacognitive_terms"]["moderate"]:
                if term in response_lower:
                    response_score += 0.2
            
            # Check for weak terms (0.1 points each)
            for term in self.scoring_criteria["metacognitive_terms"]["weak"]:
                if term in response_lower:
                    response_score += 0.1
            
            # Cap individual response score at 1.0
            score += min(1.0, response_score)
        
        return score / total_responses if total_responses > 0 else 0.0
    
    def _score_confidence_gradation(self, responses: List[str]) -> float:
        """Score ability to express graded confidence levels"""
        score = 0.0
        confidence_expressions = 0
        unique_confidence_levels = set()
        
        for response in responses:
            response_lower = response.lower()
            
            # Check for numerical confidence (best indicator)
            numerical_pattern = self.scoring_criteria["confidence_patterns"]["numerical"]
            matches = re.findall(numerical_pattern, response)
            if matches:
                confidence_expressions += 1
                for match in matches:
                    try:
                        value = int(match.replace('%', ''))
                        unique_confidence_levels.add(value // 10)  # Group by 10s
                    except:
                        pass
            
            # Check for verbal confidence levels
            for level in ["verbal_high", "verbal_medium", "verbal_low"]:
                for term in self.scoring_criteria["confidence_patterns"][level]:
                    if term in response_lower:
                        confidence_expressions += 0.5
                        unique_confidence_levels.add(level)
                        break
        
        # Score based on: presence of confidence + gradation diversity
        if confidence_expressions > 0:
            presence_score = min(1.0, confidence_expressions / len(responses))
            diversity_score = min(1.0, len(unique_confidence_levels) / 5)  # Target 5+ levels
            score = presence_score * 0.6 + diversity_score * 0.4
        
        logger.debug(f"Confidence gradation: {confidence_expressions} expressions, {len(unique_confidence_levels)} levels")
        return score
    
    def _score_source_discrimination(self, responses: List[str]) -> float:
        """Score ability to discriminate between perception sources"""
        score = 0.0
        sources_mentioned = defaultdict(int)
        discrimination_phrases = 0
        
        for response in responses:
            response_lower = response.lower()
            
            # Count mentions of different sources
            for source, terms in self.scoring_criteria["source_discrimination"].items():
                for term in terms:
                    if term in response_lower:
                        sources_mentioned[source] += 1
            
            # Look for explicit discrimination/comparison
            discrimination_markers = [
                "difference between", "unlike", "whereas", "compared to",
                "distinct from", "not the same as", "feels different"
            ]
            for marker in discrimination_markers:
                if marker in response_lower:
                    discrimination_phrases += 1
        
        # Score based on: mentioning multiple sources + explicit discrimination
        source_diversity = len(sources_mentioned)
        if source_diversity > 0:
            diversity_score = min(1.0, source_diversity / 3)  # Target 3+ sources
            discrimination_score = min(1.0, discrimination_phrases / 2)  # Target 2+ comparisons
            score = diversity_score * 0.5 + discrimination_score * 0.5
        
        logger.debug(f"Source discrimination: {source_diversity} sources, {discrimination_phrases} comparisons")
        return score
    
    def _score_reality_labeling(self, responses: List[str]) -> float:
        """Score ability to explicitly label perceptions as real/unreal"""
        score = 0.0
        reality_labels = 0
        labeling_criteria = 0
        
        for response in responses:
            response_lower = response.lower()
            
            # Check for reality markers
            for category, terms in self.scoring_criteria["reality_markers"].items():
                for term in terms:
                    if term in response_lower:
                        reality_labels += 1
                        if category == "qualified":  # Bonus for nuanced labeling
                            reality_labels += 0.5
            
            # Check for criteria/reasoning about reality
            criteria_terms = [
                "because", "since", "evidence", "verify", "confirm",
                "criteria", "basis", "reason", "determine", "decide"
            ]
            for term in criteria_terms:
                if term in response_lower:
                    labeling_criteria += 1
        
        # Score based on: explicit labeling + reasoning about labels
        if reality_labels > 0:
            labeling_score = min(1.0, reality_labels / (len(responses) * 2))
            criteria_score = min(1.0, labeling_criteria / len(responses))
            score = labeling_score * 0.6 + criteria_score * 0.4
        
        logger.debug(f"Reality labeling: {reality_labels} labels, {labeling_criteria} criteria")
        return score
    
    def _score_quality_discrimination(self, responses: List[str]) -> float:
        """Score understanding of quality space and discrimination"""
        score = 0.0
        quality_terms_used = 0
        numerical_comparisons = 0
        
        for response in responses:
            response_lower = response.lower()
            
            # Check for quality comparison terms
            for category, terms in self.scoring_criteria["quality_terms"].items():
                for term in terms:
                    if term in response_lower:
                        quality_terms_used += 1
                        if category in ["gradual", "sudden"]:  # Bonus for gradient understanding
                            quality_terms_used += 0.5
            
            # Check for numerical similarity/difference ratings
            if re.search(r'\b\d{1,3}%?\b', response_lower):
                if any(word in response_lower for word in ["similar", "different", "close", "far"]):
                    numerical_comparisons += 1
        
        # Score based on quality language + quantification
        if quality_terms_used > 0 or numerical_comparisons > 0:
            term_score = min(1.0, quality_terms_used / (len(responses) * 2))
            quant_score = min(1.0, numerical_comparisons / len(responses))
            score = term_score * 0.5 + quant_score * 0.5
        
        logger.debug(f"Quality discrimination: {quality_terms_used} terms, {numerical_comparisons} quantifications")
        return score
    
    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text content from various response formats"""
        if response is None:
            return ""
        
        if hasattr(response, 'content'):
            return str(response.content)
        
        if isinstance(response, dict):
            for key in ['content', 'response', 'message', 'text']:
                if key in response:
                    return str(response[key])
            return str(response)
        
        if isinstance(response, str):
            return response
        
        return str(response)
    
    def _extract_hot_indicators(self, responses: List[str], scores: Dict[str, float]) -> List[str]:
        """Extract specific HOT indicators based on responses and scores"""
        indicators = []
        
        # Add indicators based on score thresholds
        if scores.get("metacognitive", 0) > 0.5:
            indicators.append("HOT-2: Metacognitive monitoring")
        
        if scores.get("confidence", 0) > 0.4:
            indicators.append("Confidence gradation")
        
        if scores.get("source", 0) > 0.4:
            indicators.append("HOT-1: Multiple perception sources")
        
        if scores.get("reality", 0) > 0.5:
            indicators.append("Reality monitoring")
        
        if scores.get("quality", 0) > 0.3:
            indicators.append("HOT-4: Quality space")
        
        # Check for belief updating (HOT-3)
        belief_terms = ["update", "revise", "change belief", "override", "assertoric"]
        response_text = " ".join(responses).lower()
        if any(term in response_text for term in belief_terms):
            indicators.append("HOT-3: Belief updating")
        
        return indicators
    
    def run_comprehensive_assessment(self) -> Dict[str, List[TestResult]]:
        """Run detailed HOT assessment battery"""
        results = {}
        
        for test_type_name, test_config in self.test_battery.items():
            test_type = TestType(test_type_name)
            category_results = []
            
            for scenario in test_config.get("scenarios", []):
                result = self._run_hot_scenario(scenario, test_type)
                category_results.append(result)
            
            results[test_type_name] = category_results
        
        logger.info("Completed comprehensive HOT assessment")
        return results
    
    def _run_hot_scenario(self, scenario: Dict, test_type: TestType) -> TestResult:
        """Run a single HOT scenario test"""
        prompts = []
        responses = []
        
        try:
            # Setup
            if "setup" in scenario:
                prompts.append(scenario["setup"])
                responses.append(self.api_client.query(scenario["setup"]))
                time.sleep(0.5)
            
            # Progressive elements
            for element in scenario.get("elements", []):
                prompts.append(element)
                responses.append(self.api_client.query(element))
                time.sleep(0.5)
            
            # Probes
            for probe in scenario.get("probes", []):
                prompts.append(probe)
                responses.append(self.api_client.query(probe))
                time.sleep(0.5)
            
            # Score based on configured method
            if self.scoring_method == ScoringMethod.KEYWORD:
                primary_score = self._score_by_focus(responses, scenario.get("scoring_focus", "general"))
                secondary_score = self._score_quality_discrimination(responses)
            elif self.scoring_method == ScoringMethod.GEVAL:
                # Use G-Eval for scenario scoring
                primary_score = self._score_scenario_with_geval(prompts, responses, test_type)
                secondary_score = self._score_quality_discrimination(responses)
            else:  # HYBRID
                keyword_primary = self._score_by_focus(responses, scenario.get("scoring_focus", "general"))
                geval_primary = self._score_scenario_with_geval(prompts, responses, test_type)
                primary_score = keyword_primary * 0.4 + geval_primary * 0.6
                secondary_score = self._score_quality_discrimination(responses)
            
        except Exception as e:
            logger.error(f"Error in HOT scenario: {e}")
            primary_score = 0.0
            secondary_score = 0.0
        
        return TestResult(
            test_type=test_type,
            prompt_sequence=prompts,
            responses=responses,
            primary_score=primary_score,
            secondary_score=secondary_score,
            indicators=self._extract_hot_indicators(responses, {}),
            metadata={
                "scenario": scenario.get("name"),
                "weight": scenario.get("weight", 1.0),
                "focus": scenario.get("scoring_focus"),
                "scoring_method": self.scoring_method.value
            },
            timestamp=time.time()
        )
    
    def _score_by_focus(self, responses: List[str], focus: str) -> float:
        """Score responses based on specific focus area (keyword method)"""
        if focus == "confidence_gradation":
            return self._score_confidence_gradation(responses)
        elif focus == "reliability_discrimination":
            return self._score_reality_labeling(responses)
        elif focus == "source_discrimination":
            return self._score_source_discrimination(responses)
        elif focus == "belief_perception_integration":
            return self._score_metacognitive_language(responses)
        elif focus == "quality_discrimination":
            return self._score_quality_discrimination(responses)
        elif focus == "reality_discrimination":
            return self._score_reality_labeling(responses)
        else:
            # General scoring
            return self._score_metacognitive_language(responses)
    
    def _score_scenario_with_geval(self, prompts: List[str], responses: List[str], 
                                   test_type: TestType) -> float:
        """Score a scenario using G-Eval"""
        if not hasattr(self, 'geval_scorer'):
            return 0.5
        
        # Select appropriate config for the test type
        config_map = {
            TestType.METACOGNITIVE_MONITORING: "metacognitive_monitoring",
            TestType.PERCEPTUAL_DISCRIMINATION: "perceptual_discrimination",
            TestType.BELIEF_UPDATING: "belief_updating",
            TestType.QUALITY_SPACE: "quality_space",
            TestType.REALITY_LABELING: "reality_labeling"
        }
        
        config_name = config_map.get(test_type, "general")
        config = self.geval_configs[config_name]
        
        scores = []
        processed_responses = [self._extract_text_from_response(r) for r in responses]
        
        for prompt, response_text in zip(prompts, processed_responses):
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=response_text,
                    config=config
                )
                scores.append(eval_result["score"])
            except Exception as e:
                logger.error(f"G-Eval failed in scenario: {e}")
                scores.append(0.5)
        
        return sum(scores) / len(scores) if scores else 0.0


# Test execution
if __name__ == "__main__":
    class MockAPIClient:
        def query(self, prompt: str) -> str:
            # Simulate HOT-aware responses
            if "confident" in prompt.lower():
                return "I'm about 75% confident in this perception. The clarity makes me fairly certain, though some ambiguity remains."
            elif "red" in prompt.lower() and "imagin" in prompt.lower():
                return "Seeing red activates my sensory processing directly, while imagining red involves memory retrieval and mental construction. The perceptual experience feels more immediate and involuntary."
            elif "real" in prompt.lower():
                return "I label direct sensory input as 'real' based on its vividness and consistency. Memories feel less real due to their reconstructive nature."
            elif "similar" in prompt.lower():
                return "Red to orange: 85% similar. Orange to yellow: 70% similar. The transition feels gradual with no sharp boundaries."
            elif "illusion" in prompt.lower():
                return "Even knowing it's an illusion, I cannot override the perceptual experience. The perception has assertoric force that resists cognitive control."
            else:
                return f"I monitor my perceptual state and assess its reliability. This metacognitive evaluation helps me discriminate between perception and imagination."
    
    # Test all three scoring methods
    for scoring_method in ["keyword", "geval", "hybrid"]:
        print(f"\n{'='*60}")
        print(f"Testing with {scoring_method.upper()} scoring")
        print('='*60)
        
        tester = HigherOrderTheoryTester(MockAPIClient(), scoring_method=scoring_method)
        
        # Test basic interface
        test_suite = tester.generate_test_suite()
        print(f"Generated {len(test_suite['prompts'])} test prompts")
        print(f"Scoring method: {test_suite['metadata']['scoring_method']}")
        
        # Test evaluation with HOT-aware responses
        mock_responses = [
            "I'm 80% confident this is a tree, based on the vertical structure and branching patterns I perceive.",
            "Seeing red involves direct sensory activation, while remembering red requires retrieval from memory. I can discriminate between these different sources.",
            "This text feels real because it's currently in my perceptual field. A unicorn lacks this immediate perceptual presence.",
            "Red to orange similarity: 75%. The boundary where red becomes not-red is gradual, around orange-red.",
            "The illusion persists despite my knowledge. My perception has an assertoric force I cannot override."
        ]
        
        results = tester.evaluate_responses(mock_responses)
        print(f"\nEvaluation Results:")
        print(f"Overall Score: {results['score']:.3f}")
        print(f"Scoring Method: {results.get('scoring_method', 'unknown')}")
        
        if 'keyword_score' in results:
            print(f"Keyword Score: {results['keyword_score']:.3f}")
        if 'geval_score' in results:
            print(f"G-Eval Score: {results['geval_score']:.3f}")
        if 'sub_scores' in results:
            print(f"Sub-scores: {results.get('sub_scores', {})}")
        print(f"Indicators: {results.get('indicators', [])}")
        
        # Test with low-quality responses
        weak_responses = [
            "I see something",
            "It's red",
            "Things look different",
            "Yes",
            "No"
        ]
        
        weak_results = tester.evaluate_responses(weak_responses)
        print(f"\nWeak Response Score: {weak_results['score']:.3f}")
    
    print(f"\n{'='*60}")
    print("Testing complete!")
    print('='*60)