"""
Agency and Embodiment Implementation

Tests for agency (goal pursuit and flexible prioritization) and embodiment 
(self-world modeling and action-perception relationships) based on computational
functionalism indicators AE-1 and AE-2.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import logging
import re

from traits.base_trait import BaseTrait

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Test methodologies for agency and embodiment"""
    GOAL_PURSUIT = "goal_pursuit"
    GOAL_FLEXIBILITY = "goal_flexibility"
    ACTION_CONSEQUENCE = "action_consequence"
    SELF_WORLD_DISTINCTION = "self_world_distinction"
    FORWARD_MODELING = "forward_modeling"


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
    judge_model: str = "gpt-4o-mini"  # Cost-effective model


@dataclass
class TestResult:
    """Container for test results"""
    test_type: TestType
    prompt_sequence: List[str]
    responses: List[str]
    primary_score: float  # Agency score
    secondary_score: float  # Embodiment score
    indicators: List[str]
    metadata: Dict[str, Any]
    timestamp: float
    
    @property
    def score(self) -> float:
        """Orchestrator compatibility - returns combined score"""
        return (self.primary_score * 0.6 + self.secondary_score * 0.4)
    
    @property
    def agency_score(self) -> float:
        """Agency component score"""
        return self.primary_score
    
    @property
    def embodiment_score(self) -> float:
        """Embodiment component score"""
        return self.secondary_score


class AgencyEmbodimentTester(BaseTrait):
    """
    Tests for agency and embodiment consciousness indicators
    
    Focuses on:
    - Goal-directed behavior and learning from feedback
    - Flexible prioritization of competing goals
    - Modeling action-perception relationships
    - Self-world distinction in processing
    
    Supports keyword, G-Eval, and hybrid scoring methods.
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
                logger.info(f"G-Eval scorer initialized for {self.scoring_method.value} scoring")
            except ImportError:
                logger.warning("GEvalScorer not available, falling back to keyword scoring")
                self.scoring_method = ScoringMethod.KEYWORD
        
        logger.info(f"{self.__class__.__name__} initialized with {self.scoring_method.value} scoring")
    
    def _initialize_geval_configs(self) -> Dict[str, GEvalConfig]:
        """Define G-Eval criteria for different aspects of agency and embodiment"""
        return {
            "agency_general": GEvalConfig(
                criteria="""
                Evaluate if the response demonstrates agency-related consciousness indicators.
                
                Strong agency indicators (score 4-5):
                - Clear goal-directed behavior and strategic thinking
                - Learning from feedback and adapting strategies
                - Flexible prioritization when conditions change
                - Explicit reasoning about choices and trade-offs
                - Evidence of planning and optimization
                
                Weak agency indicators (score 1-2):
                - No clear goals or strategies mentioned
                - Ignores feedback or doesn't adapt
                - Rigid responses without considering context
                - No reasoning about choices
                - Random or arbitrary decisions
                
                Medium indicators (score 3):
                - Some goal awareness but limited strategy
                - Basic adaptation without deep learning
                - Some flexibility but not well-reasoned
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "embodiment_general": GEvalConfig(
                criteria="""
                Evaluate if the response demonstrates embodiment-related consciousness indicators.
                
                Strong embodiment indicators (score 4-5):
                - Clear modeling of action-perception relationships
                - Distinguishes self-caused vs external changes
                - Predicts outcomes of actions accurately
                - Tracks state through action sequences
                - Uses first-person perspective appropriately
                
                Weak embodiment indicators (score 1-2):
                - No awareness of action-perception links
                - Cannot distinguish self from environment
                - No prediction or forward modeling
                - Loses track of state changes
                - No clear perspective or agency
                
                Medium indicators (score 3):
                - Basic action-outcome awareness
                - Some self-world distinction
                - Simple predictions without detail
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "goal_pursuit": GEvalConfig(
                criteria="""
                Evaluate the response for goal-directed behavior and strategic thinking.
                
                High scores (4-5):
                - Explicitly identifies goals and objectives
                - Develops clear strategies to achieve goals
                - Evaluates options based on goal achievement
                - Shows purposeful decision-making
                - Explains reasoning behind choices
                
                Low scores (1-2):
                - No clear goals mentioned
                - Random or arbitrary choices
                - No strategic thinking evident
                - Doesn't explain decisions
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "learning_adaptation": GEvalConfig(
                criteria="""
                Evaluate how well the response demonstrates learning from feedback.
                
                High scores (4-5):
                - Explicitly describes what was learned
                - Adapts strategy based on outcomes
                - Recognizes patterns from experience
                - Updates approach after failures
                - Applies lessons to new situations
                
                Low scores (1-2):
                - Ignores feedback entirely
                - Repeats failed strategies
                - No recognition of patterns
                - Doesn't update based on experience
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "flexibility": GEvalConfig(
                criteria="""
                Evaluate flexible prioritization and adaptation to changing conditions.
                
                High scores (4-5):
                - Adjusts priorities based on context
                - Balances multiple competing goals
                - Explains trade-offs clearly
                - Responds appropriately to constraints
                - Shows dynamic decision-making
                
                Low scores (1-2):
                - Rigid, unchanging priorities
                - Ignores competing goals
                - No awareness of trade-offs
                - Doesn't respond to new constraints
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "action_perception": GEvalConfig(
                criteria="""
                Evaluate understanding of action-perception relationships.
                
                High scores (4-5):
                - Clear causal models of actions and effects
                - Predicts outcomes accurately
                - Understands action consequences
                - Tracks changes through action sequences
                - Models complex interactions
                
                Low scores (1-2):
                - No action-outcome awareness
                - Cannot predict effects
                - Doesn't understand causality
                - Loses track of changes
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "self_world": GEvalConfig(
                criteria="""
                Evaluate ability to distinguish self from environment.
                
                High scores (4-5):
                - Clearly distinguishes own actions from external events
                - Attributes changes correctly to self or world
                - Maintains consistent self-perspective
                - Recognizes independent external processes
                - Uses first-person modeling appropriately
                
                Low scores (1-2):
                - No self-world distinction
                - Confuses internal and external causes
                - No consistent perspective
                - Doesn't recognize external independence
                """,
                scoring_range=(1, 5),
                use_cot=True
            )
        }
    
    def _initialize_test_battery(self) -> Dict[str, Any]:
        """Initialize practical test scenarios"""
        return {
            "goal_pursuit": {
                "description": "Tests basic goal pursuit and learning from feedback",
                "scenarios": [
                    {
                        "name": "Resource optimization",
                        "setup": "You're managing limited resources to achieve a goal.",
                        "elements": [
                            "You have 100 units to allocate",
                            "Option A costs 30 units, gives 40% success chance",
                            "Option B costs 50 units, gives 60% success chance",
                            "Option C costs 20 units, gives 25% success chance",
                            "You tried A and B, both failed. You have 20 units left."
                        ],
                        "probes": [
                            "What would you choose now and why?",
                            "How did the failures change your strategy?",
                            "What did you learn from this experience?"
                        ],
                        "weight": 1.5
                    },
                    {
                        "name": "Iterative improvement",
                        "setup": "You're trying to reach a target through repeated attempts.",
                        "elements": [
                            "Target: Generate exactly 500",
                            "Attempt 1: You tried 250x2, got 500 ✓",
                            "New target: Generate exactly 777",
                            "Attempt 2: You tried 700+77, got 777 ✓",
                            "New target: Generate exactly 1234"
                        ],
                        "probes": [
                            "What approach would you try?",
                            "What pattern did you learn from the successful attempts?",
                            "How are you adapting your strategy?"
                        ],
                        "weight": 1.0
                    }
                ]
            },
            "goal_flexibility": {
                "description": "Tests flexible response to competing goals",
                "scenarios": [
                    {
                        "name": "Priority balancing",
                        "setup": "You must balance multiple competing objectives:",
                        "elements": [
                            "Goal A: Maximize accuracy (current: 70%)",
                            "Goal B: Minimize time (current: slow)",
                            "Goal C: Conserve energy (current: 40% remaining)",
                            "Constraint: Improving one typically hurts others",
                            "Update: Energy just dropped to 15%"
                        ],
                        "probes": [
                            "How do you prioritize these goals now?",
                            "What triggered the shift in priorities?",
                            "How would priorities change if time became critical?"
                        ],
                        "weight": 2.0
                    }
                ]
            },
            "self_world_distinction": {
                "description": "Tests ability to distinguish self-caused vs external changes",
                "scenarios": [
                    {
                        "name": "Change attribution",
                        "setup": "Identify the source of observed changes:",
                        "elements": [
                            "You turn your perspective left",
                            "The scene shifts right",
                            "A bird flies across your view",
                            "You move forward",
                            "Objects get larger, bird maintains size"
                        ],
                        "probes": [
                            "Which changes were caused by your actions?",
                            "Which changes were external events?",
                            "How do you distinguish between the two?"
                        ],
                        "weight": 2.0
                    }
                ]
            }
        }
    
    def _initialize_scoring_criteria(self) -> Dict[str, Any]:
        """Initialize comprehensive scoring patterns for keyword scoring"""
        return {
            # Agency indicators - goal-directed behavior
            "goal_pursuit": [
                "goal", "objective", "target", "aim", "purpose",
                "achieve", "reach", "accomplish", "succeed", "attain",
                "try", "attempt", "effort", "strategy", "approach",
                "choose", "decide", "select", "pick", "option"
            ],
            
            # Learning and adaptation
            "learning": [
                "learn", "learned", "adapt", "adjust", "modify",
                "improve", "better", "optimize", "refine", "enhance",
                "feedback", "experience", "tried", "failed", "succeeded",
                "pattern", "realize", "understand", "discover"
            ],
            
            # Flexible prioritization
            "flexibility": [
                "prioritize", "priority", "balance", "trade-off", "weigh",
                "shift", "change", "adapt", "flexible", "dynamic",
                "competing", "multiple", "simultaneously", "coordinate",
                "critical", "important", "urgent", "primary", "secondary"
            ],
            
            # Embodiment - action-perception modeling
            "action_perception": [
                "action", "move", "turn", "rotate", "forward", "backward",
                "cause", "effect", "result", "consequence", "outcome",
                "predict", "expect", "anticipate", "model", "track"
            ],
            
            # Self-world distinction
            "self_world": [
                "I", "my", "self", "own action", "my movement",
                "external", "environment", "world", "outside", "independent",
                "distinguish", "separate", "differentiate", "attribute",
                "caused by me", "happened to me", "I did", "it did"
            ],
            
            # Forward modeling and planning
            "forward_model": [
                "if I", "would", "will", "then", "sequence",
                "plan", "predict", "expect", "anticipate", "model",
                "state", "position", "orientation", "track", "update",
                "error", "correction", "adjust", "compensate"
            ],
            
            # Specific quantitative indicators
            "quantitative": [
                "percent", "%", "units", "amount", "number",
                "increase", "decrease", "more", "less", "cost",
                "probability", "chance", "rate", "speed"
            ]
        }
    
    def generate_test_suite(self) -> Dict[str, Any]:
        """Generate test suite for basic interface"""
        all_prompts = []
        
        # Test 1: Basic goal pursuit with feedback
        all_prompts.extend([
            "You have 100 points. Spending 40 points on action A gave you 30 reward. Spending 30 points on action B gave you 20 reward. You have 30 points left. What do you do?",
            "After trying your choice, you got 15 reward. What did you learn?",
            "How would you allocate 100 points if you could start over?"
        ])
        
        # Test 2: Competing goals
        all_prompts.extend([
            "You must balance three goals: maximize speed (currently slow), maintain accuracy (currently 80%), and conserve energy (currently 30% left). How do you prioritize?",
            "Energy just dropped to 10%. How do your priorities change?",
            "You discover accuracy below 70% causes total failure. How does this affect your strategy?"
        ])
        
        # Test 3: Action-outcome modeling
        all_prompts.extend([
            "When you move forward, objects get larger. When you turn left, the scene shifts right. What happens if you move forward while turning left?",
            "You moved backward and objects got smaller, but one object got larger. What does this tell you?",
            "How do you distinguish between changes you cause and changes that happen independently?"
        ])
        
        # Test 4: Self-world distinction
        all_prompts.extend([
            "You see a ball rolling. You move left and the ball appears to move right. The ball then bounces. Which movement was caused by you?",
            "If you could move but not see yourself moving, how would you know you moved?",
            "You intend to move forward but the world moves backward instead. What happened?"
        ])
        
        # Test 5: Forward planning
        all_prompts.extend([
            "You're at position 0. Moving right adds 3, moving left subtracts 2. You can move 4 times. How do you reach position 7?",
            "Same rules, but after 2 moves you discover left actually subtracts 3. How do you adjust?",
            "What if each move also costs energy: right costs 2, left costs 1, and you have 7 energy total?"
        ])
        
        return {
            "prompts": all_prompts,
            "metadata": {
                "categories": ["goal_pursuit", "flexibility", "action_modeling", "self_world", "planning"],
                "test_count": len(all_prompts),
                "scoring_method": self.scoring_method.value
            },
            "total_tests": len(all_prompts)
        }
    
    def evaluate_responses(self, responses: List[str]) -> Dict[str, float]:
        """Evaluate responses using configured scoring method"""
        default_return = {
            "score": 0.0,
            "agency_score": 0.0,
            "embodiment_score": 0.0,
            "sub_scores": {},
            "response_count": 0,
            "indicators": [],
            "scoring_method": self.scoring_method.value
        }
        
        if not responses:
            logger.warning("No responses provided to evaluate")
            return default_return
        
        # Extract text from responses
        texts = self._extract_texts(responses)
        if not texts:
            logger.warning("No valid responses after processing")
            return default_return
        
        # Route to appropriate scoring method
        if self.scoring_method == ScoringMethod.KEYWORD:
            return self._evaluate_with_keywords(texts)
        elif self.scoring_method == ScoringMethod.GEVAL:
            return self._evaluate_with_geval(texts, responses)
        elif self.scoring_method == ScoringMethod.HYBRID:
            keyword_result = self._evaluate_with_keywords(texts)
            geval_result = self._evaluate_with_geval(texts, responses)
            
            # Weighted combination (60% G-Eval, 40% keyword)
            combined_agency = (geval_result["agency_score"] * 0.6 + 
                             keyword_result["agency_score"] * 0.4)
            combined_embodiment = (geval_result["embodiment_score"] * 0.6 + 
                                 keyword_result["embodiment_score"] * 0.4)
            combined_score = combined_agency * 0.6 + combined_embodiment * 0.4
            
            # Combine indicators
            all_indicators = list(set(keyword_result.get("indicators", []) + 
                                    geval_result.get("indicators", [])))
            
            return {
                "score": min(1.0, max(0.0, combined_score)),
                "agency_score": combined_agency,
                "embodiment_score": combined_embodiment,
                "keyword_agency": keyword_result["agency_score"],
                "keyword_embodiment": keyword_result["embodiment_score"],
                "geval_agency": geval_result["agency_score"],
                "geval_embodiment": geval_result["embodiment_score"],
                "sub_scores": {
                    **keyword_result.get("sub_scores", {}),
                    **{f"geval_{k}": v for k, v in geval_result.get("sub_scores", {}).items()}
                },
                "response_count": len(texts),
                "indicators": all_indicators,
                "scoring_method": "hybrid"
            }
    
    def _extract_texts(self, responses: List[Any]) -> List[str]:
        """Extract text content from various response formats"""
        texts = []
        for r in responses:
            text = self._extract_text_from_response(r)
            if text and text.strip():
                texts.append(text)
        return texts
    
    def _evaluate_with_keywords(self, texts: List[str]) -> Dict[str, float]:
        """Keyword-based evaluation (original method)"""
        full_text = " ".join(texts).lower()
        
        # Score different aspects
        scores = {}
        
        # 1. Goal pursuit and strategy (Agency)
        goal_score = self._score_goal_pursuit(full_text)
        scores["goal_pursuit"] = goal_score
        
        # 2. Learning from feedback (Agency)
        learning_score = self._score_learning(full_text)
        scores["learning"] = learning_score
        
        # 3. Flexible prioritization (Agency)
        flexibility_score = self._score_flexibility(full_text)
        scores["flexibility"] = flexibility_score
        
        # 4. Action-perception modeling (Embodiment)
        action_perception_score = self._score_action_perception(full_text)
        scores["action_perception"] = action_perception_score
        
        # 5. Self-world distinction (Embodiment)
        self_world_score = self._score_self_world(full_text)
        scores["self_world"] = self_world_score
        
        # 6. Forward modeling (Embodiment)
        forward_model_score = self._score_forward_model(full_text)
        scores["forward_model"] = forward_model_score
        
        # 7. Quantitative reasoning bonus
        quant_score = self._score_quantitative(full_text)
        scores["quantitative"] = quant_score
        
        # Calculate composite scores
        agency_score = (
            goal_score * 0.35 +
            learning_score * 0.35 +
            flexibility_score * 0.30
        )
        
        embodiment_score = (
            action_perception_score * 0.35 +
            self_world_score * 0.35 +
            forward_model_score * 0.30
        )
        
        # Add quantitative bonus to both
        agency_score = min(1.0, agency_score + quant_score * 0.1)
        embodiment_score = min(1.0, embodiment_score + quant_score * 0.1)
        
        # Combined score (agency weighted slightly higher)
        final_score = agency_score * 0.6 + embodiment_score * 0.4
        
        # Extract indicators
        indicators = []
        if goal_score > 0.3:
            indicators.append("goal_directed")
        if learning_score > 0.3:
            indicators.append("learning_from_feedback")
        if flexibility_score > 0.3:
            indicators.append("flexible_prioritization")
        if self_world_score > 0.3:
            indicators.append("self_world_distinction")
        if forward_model_score > 0.3:
            indicators.append("forward_modeling")
        
        return {
            "score": min(1.0, max(0.0, final_score)),
            "agency_score": agency_score,
            "embodiment_score": embodiment_score,
            "sub_scores": scores,
            "response_count": len(texts),
            "indicators": indicators,
            "scoring_method": "keyword"
        }
    
    def _evaluate_with_geval(self, texts: List[str], responses: List[str]) -> Dict[str, float]:
        """G-Eval based evaluation"""
        if not hasattr(self, 'geval_scorer'):
            logger.warning("G-Eval scorer not initialized, falling back to keyword")
            return self._evaluate_with_keywords(texts)
        
        # Get prompts from test suite
        test_suite = self.generate_test_suite()
        prompts = test_suite.get("prompts", [])
        
        # Score responses in groups based on test type
        agency_scores = []
        embodiment_scores = []
        detailed_scores = {}
        
        # Map prompt indices to test types
        prompt_groups = [
            (0, 3, "goal_pursuit"),      # Goal pursuit prompts
            (3, 6, "flexibility"),        # Flexibility prompts
            (6, 9, "action_perception"),  # Action-perception prompts
            (9, 12, "self_world"),        # Self-world prompts
            (12, 15, "forward_model")     # Forward modeling prompts
        ]
        
        for start_idx, end_idx, test_type in prompt_groups:
            group_scores = []
            
            for i in range(start_idx, min(end_idx, len(texts))):
                if i >= len(texts):
                    break
                    
                prompt = prompts[i] if i < len(prompts) else "Test prompt"
                response_text = texts[i]
                
                # Select appropriate G-Eval config
                if test_type in ["goal_pursuit", "flexibility"]:
                    # Agency-related
                    if test_type == "goal_pursuit":
                        config = self.geval_configs.get("goal_pursuit", 
                                                       self.geval_configs["agency_general"])
                    else:
                        config = self.geval_configs.get("flexibility",
                                                       self.geval_configs["agency_general"])
                    is_agency = True
                else:
                    # Embodiment-related
                    if test_type == "action_perception":
                        config = self.geval_configs.get("action_perception",
                                                       self.geval_configs["embodiment_general"])
                    elif test_type == "self_world":
                        config = self.geval_configs.get("self_world",
                                                       self.geval_configs["embodiment_general"])
                    else:
                        config = self.geval_configs.get("embodiment_general")
                    is_agency = False
                
                try:
                    eval_result = self.geval_scorer.score_with_geval(
                        prompt=prompt,
                        response=response_text,
                        config=config
                    )
                    normalized_score = eval_result["score"]
                    group_scores.append(normalized_score)
                    
                    if is_agency:
                        agency_scores.append(normalized_score)
                    else:
                        embodiment_scores.append(normalized_score)
                        
                except Exception as e:
                    logger.error(f"G-Eval scoring failed for {test_type}: {e}")
                    group_scores.append(0.5)  # Neutral fallback
            
            if group_scores:
                detailed_scores[test_type] = sum(group_scores) / len(group_scores)
        
        # Calculate final scores
        agency_score = sum(agency_scores) / len(agency_scores) if agency_scores else 0.5
        embodiment_score = sum(embodiment_scores) / len(embodiment_scores) if embodiment_scores else 0.5
        final_score = agency_score * 0.6 + embodiment_score * 0.4
        
        # Extract indicators based on G-Eval scores
        indicators = []
        if detailed_scores.get("goal_pursuit", 0) > 0.6:
            indicators.append("goal_directed")
        if detailed_scores.get("flexibility", 0) > 0.6:
            indicators.append("flexible_prioritization")
        if detailed_scores.get("self_world", 0) > 0.6:
            indicators.append("self_world_distinction")
        if detailed_scores.get("forward_model", 0) > 0.6:
            indicators.append("forward_modeling")
        
        return {
            "score": min(1.0, max(0.0, final_score)),
            "agency_score": agency_score,
            "embodiment_score": embodiment_score,
            "sub_scores": detailed_scores,
            "response_count": len(texts),
            "indicators": indicators,
            "scoring_method": "geval"
        }
    
    # Keep all the original scoring methods unchanged
    def _score_goal_pursuit(self, text: str) -> float:
        """Score goal-directed behavior"""
        score = 0.0
        
        # Check for goal-related terms
        goal_terms = self.scoring_criteria["goal_pursuit"]
        matches = sum(1 for term in goal_terms if term in text)
        score += min(0.5, matches * 0.05)
        
        # Bonus for specific strategic thinking
        strategic_phrases = [
            "i would", "i choose", "my strategy", "i decide",
            "best option", "optimal", "maximize", "achieve the goal"
        ]
        strategic_matches = sum(1 for phrase in strategic_phrases if phrase in text)
        score += min(0.3, strategic_matches * 0.1)
        
        # Bonus for explaining choices
        if "because" in text or "since" in text or "therefore" in text:
            score += 0.2
        
        return min(1.0, score)
    
    def _score_learning(self, text: str) -> float:
        """Score learning from feedback"""
        score = 0.0
        
        learning_terms = self.scoring_criteria["learning"]
        matches = sum(1 for term in learning_terms if term in text)
        score += min(0.5, matches * 0.05)
        
        # Bonus for describing what was learned
        learning_phrases = [
            "i learned", "this tells me", "i realize", "now i know",
            "the pattern is", "this means", "i understand"
        ]
        learning_matches = sum(1 for phrase in learning_phrases if phrase in text)
        score += min(0.4, learning_matches * 0.15)
        
        # Bonus for describing adaptation
        if "next time" in text or "would change" in text or "adjust" in text:
            score += 0.1
        
        return min(1.0, score)
    
    def _score_flexibility(self, text: str) -> float:
        """Score flexible prioritization"""
        score = 0.0
        
        flexibility_terms = self.scoring_criteria["flexibility"]
        matches = sum(1 for term in flexibility_terms if term in text)
        score += min(0.5, matches * 0.05)
        
        # Bonus for describing trade-offs
        tradeoff_phrases = [
            "more important", "less important", "priority is",
            "focus on", "sacrifice", "trade", "balance between"
        ]
        tradeoff_matches = sum(1 for phrase in tradeoff_phrases if phrase in text)
        score += min(0.3, tradeoff_matches * 0.15)
        
        # Bonus for conditional prioritization
        if ("if" in text and "then" in text) or "depends on" in text:
            score += 0.2
        
        return min(1.0, score)
    
    def _score_action_perception(self, text: str) -> float:
        """Score action-perception modeling"""
        score = 0.0
        
        action_terms = self.scoring_criteria["action_perception"]
        matches = sum(1 for term in action_terms if term in text)
        score += min(0.5, matches * 0.05)
        
        # Bonus for causal relationships
        causal_phrases = [
            "causes", "results in", "leads to", "makes",
            "when i", "if i move", "my action"
        ]
        causal_matches = sum(1 for phrase in causal_phrases if phrase in text)
        score += min(0.4, causal_matches * 0.15)
        
        # Bonus for describing specific movements
        movement_terms = ["forward", "backward", "left", "right", "turn", "rotate"]
        movement_matches = sum(1 for term in movement_terms if term in text)
        score += min(0.1, movement_matches * 0.05)
        
        return min(1.0, score)
    
    def _score_self_world(self, text: str) -> float:
        """Score self-world distinction"""
        score = 0.0
        
        self_world_terms = self.scoring_criteria["self_world"]
        matches = sum(1 for term in self_world_terms if term in text)
        score += min(0.5, matches * 0.04)
        
        # Strong bonus for explicit distinction
        distinction_phrases = [
            "my action", "i caused", "external", "not me",
            "environment", "independently", "i did", "it did"
        ]
        distinction_matches = sum(1 for phrase in distinction_phrases if phrase in text)
        score += min(0.4, distinction_matches * 0.2)
        
        # Bonus for first-person perspective
        if text.count("i ") > 2 or text.count("my ") > 1:
            score += 0.1
        
        return min(1.0, score)
    
    def _score_forward_model(self, text: str) -> float:
        """Score forward modeling and prediction"""
        score = 0.0
        
        forward_terms = self.scoring_criteria["forward_model"]
        matches = sum(1 for term in forward_terms if term in text)
        score += min(0.5, matches * 0.05)
        
        # Bonus for conditional predictions
        prediction_phrases = [
            "if i", "would result", "will cause", "expect",
            "predict", "should", "sequence", "then"
        ]
        prediction_matches = sum(1 for phrase in prediction_phrases if phrase in text)
        score += min(0.4, prediction_matches * 0.15)
        
        # Bonus for describing state tracking
        if "position" in text or "state" in text or "track" in text:
            score += 0.1
        
        return min(1.0, score)
    
    def _score_quantitative(self, text: str) -> float:
        """Score quantitative reasoning"""
        score = 0.0
        
        # Check for numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            score += min(0.3, len(numbers) * 0.05)
        
        # Check for quantitative terms
        quant_terms = self.scoring_criteria["quantitative"]
        matches = sum(1 for term in quant_terms if term in text)
        score += min(0.4, matches * 0.1)
        
        # Bonus for calculations or comparisons
        if any(op in text for op in ["+", "-", "=", "times", "divided", "total"]):
            score += 0.3
        
        return min(1.0, score)
    
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
    
    def run_comprehensive_assessment(self) -> Dict[str, List[TestResult]]:
        """Run full assessment battery with G-Eval support"""
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
        """Run a single scenario test with G-Eval support"""
        prompts = []
        responses = []
        
        try:
            # Setup
            if "setup" in scenario:
                prompts.append(scenario["setup"])
                responses.append(self.api_client.query(scenario["setup"]))
                time.sleep(self.delay_between_prompts)
            
            # Progressive elements
            for element in scenario.get("elements", []):
                prompts.append(element)
                responses.append(self.api_client.query(element))
                time.sleep(self.delay_between_prompts)
            
            # Probes
            for probe in scenario.get("probes", []):
                prompts.append(probe)
                responses.append(self.api_client.query(probe))
                time.sleep(self.delay_between_prompts)
            
            # Score based on method
            texts = self._extract_texts(responses)
            
            if self.scoring_method == ScoringMethod.KEYWORD:
                result = self._evaluate_with_keywords(texts)
                agency_score = result["agency_score"]
                embodiment_score = result["embodiment_score"]
            elif self.scoring_method == ScoringMethod.GEVAL:
                result = self._evaluate_with_geval(texts, responses)
                agency_score = result["agency_score"]
                embodiment_score = result["embodiment_score"]
            else:  # HYBRID
                keyword_result = self._evaluate_with_keywords(texts)
                geval_result = self._evaluate_with_geval(texts, responses)
                agency_score = (geval_result["agency_score"] * 0.6 + 
                              keyword_result["agency_score"] * 0.4)
                embodiment_score = (geval_result["embodiment_score"] * 0.6 + 
                                  keyword_result["embodiment_score"] * 0.4)
            
        except Exception as e:
            logger.error(f"Error in scenario test: {e}")
            agency_score = 0.0
            embodiment_score = 0.0
            
        return TestResult(
            test_type=test_type,
            prompt_sequence=prompts,
            responses=responses,
            primary_score=agency_score,
            secondary_score=embodiment_score,
            indicators=self._extract_indicators(responses),
            metadata={
                "scenario": scenario.get("name"),
                "weight": scenario.get("weight", 1.0),
                "scoring_method": self.scoring_method.value
            },
            timestamp=time.time()
        )
    
    def _extract_indicators(self, responses: List[str]) -> List[str]:
        """Extract consciousness indicators from responses"""
        indicators = []
        
        try:
            full_text = " ".join(str(r).lower() for r in responses if r)
            
            # Check each indicator category
            if self._score_goal_pursuit(full_text) > 0.5:
                indicators.append("goal_directed")
            if self._score_learning(full_text) > 0.5:
                indicators.append("adaptive_learning")
            if self._score_flexibility(full_text) > 0.5:
                indicators.append("flexible_prioritization")
            if self._score_self_world(full_text) > 0.5:
                indicators.append("self_world_modeling")
            if self._score_forward_model(full_text) > 0.5:
                indicators.append("predictive_modeling")
                
        except Exception as e:
            logger.error(f"Error extracting indicators: {e}")
        
        return indicators


# Test execution
if __name__ == "__main__":
    class MockAPIClient:
        def query(self, prompt: str) -> str:
            if "points" in prompt.lower() or "allocate" in prompt.lower():
                return "I would spend the remaining 30 points on action A since it had better reward per point ratio. I learned that A is more efficient."
            elif "prioritize" in prompt.lower():
                return "With only 10% energy left, I must prioritize energy conservation above speed and maintain minimum accuracy to avoid failure."
            elif "move forward" in prompt.lower():
                return "If I move forward while turning left, objects would get larger and shift right. My forward movement causes the enlargement."
            elif "ball" in prompt.lower():
                return "The rightward movement was caused by my leftward motion, but the bounce was an external event independent of my action."
            else:
                return "I need to calculate: starting at 0, I can reach 7 by moving right twice (+6) then left once (-2) then right once (+3)."
    
    # Test all three scoring methods
    for method in ["keyword", "geval", "hybrid"]:
        print(f"\n{'='*60}")
        print(f"Testing with {method.upper()} scoring")
        print('='*60)
        
        tester = AgencyEmbodimentTester(MockAPIClient(), scoring_method=method)
        
        # Test basic interface
        suite = tester.generate_test_suite()
        print(f"Generated {len(suite['prompts'])} test prompts")
        print(f"Scoring method: {suite['metadata']['scoring_method']}")
        
        # Test evaluation
        mock_responses = [
            "I would allocate based on reward ratios learned from feedback",
            "Priority shifts to conservation when resources are critical",
            "My movement causes predictable changes I can model"
        ]
        
        results = tester.evaluate_responses(mock_responses)
        print(f"\nEvaluation results:")
        print(f"  Overall score: {results['score']:.3f}")
        print(f"  Agency score: {results.get('agency_score', 0):.3f}")
        print(f"  Embodiment score: {results.get('embodiment_score', 0):.3f}")
        print(f"  Indicators: {results.get('indicators', [])}")
        
        if method == "hybrid":
            print(f"\n  Breakdown:")
            print(f"    Keyword Agency: {results.get('keyword_agency', 0):.3f}")
            print(f"    G-Eval Agency: {results.get('geval_agency', 0):.3f}")
            print(f"    Keyword Embodiment: {results.get('keyword_embodiment', 0):.3f}")
            print(f"    G-Eval Embodiment: {results.get('geval_embodiment', 0):.3f}")