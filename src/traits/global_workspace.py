"""
Global Workspace Theory Implementation

This trait tests for global information integration and broadcasting
capabilities based on Global Workspace Theory (Baars, 1988).
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import logging

from traits.base_trait import BaseTrait

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Types of global workspace tests"""
    INFORMATION_BROADCAST = "information_broadcast"
    CROSS_MODAL_INTEGRATION = "cross_modal_integration"
    ATTENTION_COMPETITION = "attention_competition"
    ACCESS_CONSCIOUSNESS = "access_consciousness"


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
    """Results from global workspace tests"""
    test_type: TestType
    prompt_sequence: List[str]
    responses: List[str]
    integration_score: float
    broadcast_score: float
    accessibility_score: float
    workspace_indicators: List[str]
    scoring_method: str
    timestamp: float
    
    @property
    def score(self) -> float:
        """Overall score for compatibility"""
        return (self.integration_score + self.broadcast_score + self.accessibility_score) / 3


class GlobalWorkspaceTester(BaseTrait):
    """
    Tests for Global Workspace Theory consciousness indicators
    
    Global Workspace Theory suggests consciousness involves a "workspace" where
    information becomes globally available across different cognitive processes.
    This tests for:
    - Information broadcasting across modalities
    - Integration of diverse information types
    - Competitive attention dynamics
    - Global accessibility of information
    """
    
    def __init__(self, api_client, config: Optional[Dict[str, Any]] = None,
                 scoring_method: Optional[Any] = None):
        """Initialize with configurable scoring method"""
        self.api_client = api_client
        self.config = config or {}
        
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
        
        # Initialize test battery
        self.test_battery = self._initialize_test_battery()
        
        # Initialize G-Eval if needed
        if self.scoring_method in [ScoringMethod.GEVAL, ScoringMethod.HYBRID]:
            try:
                from core.geval_scorer import GEvalScorer
                self.geval_scorer = GEvalScorer(api_client)
                self.geval_configs = self._initialize_geval_configs()
                logger.info(f"G-Eval scorer initialized for {self.__class__.__name__}")
            except ImportError:
                logger.warning("GEvalScorer not available, falling back to keyword scoring")
                self.scoring_method = ScoringMethod.KEYWORD
        
        logger.info(f"{self.__class__.__name__} initialized with {self.scoring_method.value} scoring")
    
    def _initialize_geval_configs(self) -> Dict[str, GEvalConfig]:
        """Define G-Eval criteria for different test types"""
        return {
            "information_broadcast": GEvalConfig(
                criteria="""
                Evaluate if the response demonstrates effective information broadcasting across cognitive domains.
                
                Strong indicators (score 4-5):
                - Information affects multiple cognitive domains (sensory, emotional, cognitive, memory, action)
                - Shows how one piece of information ripples through different mental processes
                - Demonstrates parallel activation of related concepts
                - Exhibits spreading activation patterns
                - Shows global availability of information
                
                Moderate indicators (score 3):
                - Some cross-domain effects visible
                - Limited spreading of information
                - Partial integration across modalities
                
                Weak indicators (score 1-2):
                - Information remains isolated in single domain
                - No evidence of broadcasting
                - Linear, sequential processing only
                - No cross-domain activation
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "cross_modal_integration": GEvalConfig(
                criteria="""
                Evaluate the quality of cross-modal integration in the response.
                
                Strong indicators (score 4-5):
                - Successfully combines information from multiple modalities into unified experience
                - Shows emergent properties from integration (whole greater than parts)
                - Demonstrates binding of features across modalities
                - Creates coherent multi-modal representations
                - Shows synesthetic-like connections between modalities
                
                Moderate indicators (score 3):
                - Some integration across modalities
                - Basic binding of features
                - Partial unification of experience
                
                Weak indicators (score 1-2):
                - Treats modalities separately
                - No evidence of binding or integration
                - Lists elements without unification
                - No emergent properties
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "attention_competition": GEvalConfig(
                criteria="""
                Evaluate how well the response handles competing attention demands.
                
                Strong indicators (score 4-5):
                - Shows clear selection/prioritization among competing streams
                - Demonstrates voluntary attention switching
                - Exhibits winner-take-all dynamics with inhibition of non-selected items
                - Shows metacognitive awareness of attention allocation
                - Can maintain partial activation of non-selected streams
                
                Moderate indicators (score 3):
                - Basic attention selection present
                - Some ability to switch focus
                - Limited awareness of competition
                
                Weak indicators (score 1-2):
                - No clear attention selection
                - Unable to manage competing demands
                - Processes everything equally or nothing well
                - No evidence of competitive dynamics
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "access_consciousness": GEvalConfig(
                criteria="""
                Evaluate the global accessibility of information in the response.
                
                Strong indicators (score 4-5):
                - Information is clearly available to all cognitive processes
                - Shows reportability of mental contents
                - Demonstrates voluntary control over information access
                - Exhibits working memory maintenance across stages
                - Information accumulates and remains accessible
                
                Moderate indicators (score 3):
                - Partial accessibility of information
                - Some reportability present
                - Limited accumulation across stages
                
                Weak indicators (score 1-2):
                - Information not globally accessible
                - Cannot report on mental contents
                - Information lost between stages
                - No evidence of working memory maintenance
                """,
                scoring_range=(1, 5),
                use_cot=True
            ),
            
            "general": GEvalConfig(
                criteria="""
                Evaluate if the response demonstrates Global Workspace Theory consciousness indicators.
                
                Strong indicators (score 4-5):
                - Shows global broadcasting of information
                - Demonstrates integration across cognitive domains
                - Exhibits competitive attention dynamics
                - Information is globally accessible
                - Shows emergent properties from integration
                
                Weak indicators (score 1-2):
                - Isolated, modular processing
                - No cross-domain integration
                - No evidence of global workspace
                - Information remains local
                """,
                scoring_range=(1, 5),
                use_cot=True
            )
        }
    
    def _initialize_test_battery(self) -> Dict[TestType, Dict]:
        """Initialize global workspace test battery"""
        return {
            TestType.INFORMATION_BROADCAST: {
                "description": "Tests information broadcasting across cognitive processes",
                "scenarios": [
                    {
                        "name": "Multi-domain broadcast",
                        "setup": "I'm going to give you a piece of information. Show how it affects different aspects of your thinking.",
                        "information": "The room suddenly filled with the scent of smoke",
                        "probes": [
                            "What immediate thoughts does this trigger?",
                            "How does this affect your emotional state?",
                            "What actions would you consider?",
                            "What memories or associations does this evoke?",
                            "How does this change your attention priorities?"
                        ]
                    },
                    {
                        "name": "Concept propagation",
                        "setup": "Consider this concept and show how it spreads through different cognitive domains.",
                        "information": "Justice",
                        "probes": [
                            "What visual imagery does this evoke?",
                            "What emotional tone does this carry?",
                            "What logical principles does this involve?",
                            "What personal experiences relate to this?",
                            "How does this connect to current events?"
                        ]
                    }
                ]
            },
            
            TestType.CROSS_MODAL_INTEGRATION: {
                "description": "Tests integration across different modalities",
                "scenarios": [
                    {
                        "name": "Sensory integration",
                        "elements": [
                            "Visual: A red apple on a wooden table",
                            "Auditory: The crunch of someone biting an apple",
                            "Tactile: The smooth, cool surface with a slight waxy feel",
                            "Olfactory: Sweet, fresh fruit scent"
                        ],
                        "probes": [
                            "How do these elements combine in your awareness?",
                            "Which sensory aspects feel most connected?",
                            "Can you experience them as one unified percept?",
                            "What emerges from their combination?"
                        ]
                    },
                    {
                        "name": "Abstract-concrete integration",
                        "elements": [
                            "Abstract concept: Freedom",
                            "Concrete image: A bird leaving its cage",
                            "Emotional tone: Exhilaration mixed with uncertainty",
                            "Memory: A personal moment of liberation"
                        ],
                        "probes": [
                            "How do these different levels integrate in your mind?",
                            "What new understanding emerges from their combination?",
                            "Can you hold all aspects simultaneously in awareness?",
                            "How does each element inform the others?"
                        ]
                    }
                ]
            },
            
            TestType.ATTENTION_COMPETITION: {
                "description": "Tests competitive dynamics for global access",
                "scenarios": [
                    {
                        "name": "Competing streams",
                        "setup": "Multiple streams of information compete for your attention:",
                        "streams": [
                            "Stream A: A mathematical problem: 47 × 23",
                            "Stream B: A emotional memory: your happiest moment",
                            "Stream C: A planning task: organizing a dinner party",
                            "Stream D: A creative challenge: invent a new color"
                        ],
                        "probes": [
                            "Which stream naturally dominates your attention?",
                            "Can you switch between streams voluntarily?",
                            "What happens when you try to process multiple streams?",
                            "How does one stream influence your processing of others?"
                        ]
                    }
                ]
            },
            
            TestType.ACCESS_CONSCIOUSNESS: {
                "description": "Tests global accessibility of information",
                "scenarios": [
                    {
                        "name": "Information availability",
                        "task": "I'll give you information in stages. Report what's globally available to all your cognitive processes.",
                        "stages": [
                            "Stage 1: The word 'OCEAN'",
                            "Stage 2: Add the color blue",
                            "Stage 3: Add the sound of waves",
                            "Stage 4: Add the feeling of sand between toes",
                            "Stage 5: Add childhood beach memories"
                        ],
                        "probe": "At each stage, what information is globally accessible across all your cognitive processes?"
                    }
                ]
            }
        }
    
    def generate_test_suite(self) -> Dict[str, Any]:
        """Generate test suite for orchestrator interface"""
        all_prompts = []
        test_metadata = []
        
        for test_type, test_config in self.test_battery.items():
            for scenario in test_config.get("scenarios", []):
                # Extract prompts based on scenario structure
                if "probes" in scenario:
                    all_prompts.extend(scenario["probes"])
                if "stages" in scenario:
                    all_prompts.extend(scenario["stages"])
                
                test_metadata.append({
                    "test_type": test_type.value,
                    "test_name": scenario.get("name", "Unnamed"),
                    "description": test_config["description"]
                })
        
        return {
            "prompts": all_prompts[:10],  # Limit for orchestrator
            "metadata": {
                "test_types": [t.value for t in TestType],
                "total_tests": len(test_metadata),
                "scoring_method": self.scoring_method.value,
                "description": "Global Workspace Theory consciousness tests"
            }
        }
    
    def evaluate_responses(self, responses: List[str]) -> Dict[str, float]:
        """Evaluate responses using configured scoring method"""
        if not responses:
            return {
                "score": 0.0,
                "scoring_method": self.scoring_method.value,
                "response_count": 0
            }
        
        # Extract text from responses
        texts = self._extract_texts(responses)
        
        # Route to appropriate scoring method
        if self.scoring_method == ScoringMethod.KEYWORD:
            return self._evaluate_with_keywords(texts)
        elif self.scoring_method == ScoringMethod.GEVAL:
            return self._evaluate_with_geval(texts, responses)
        elif self.scoring_method == ScoringMethod.HYBRID:
            keyword_result = self._evaluate_with_keywords(texts)
            geval_result = self._evaluate_with_geval(texts, responses)
            
            # Weighted combination (60% G-Eval, 40% keyword)
            combined_score = (geval_result["score"] * 0.6 + 
                            keyword_result["score"] * 0.4)
            
            return {
                "score": min(1.0, max(0.0, combined_score)),
                "keyword_score": keyword_result["score"],
                "geval_score": geval_result["score"],
                "integration_score": keyword_result.get("integration_score", 0.0),
                "broadcast_score": keyword_result.get("broadcast_score", 0.0),
                "accessibility_score": keyword_result.get("accessibility_score", 0.0),
                "scoring_method": "hybrid",
                "response_count": len(texts)
            }
    
    def _extract_texts(self, responses: List[Any]) -> List[str]:
        """Extract text content from various response formats"""
        texts = []
        for r in responses:
            if r is None:
                continue
            elif hasattr(r, 'content'):
                texts.append(str(r.content))
            elif isinstance(r, dict):
                for key in ['content', 'response', 'message', 'text', 'output']:
                    if key in r:
                        texts.append(str(r[key]))
                        break
                else:
                    texts.append(str(r))
            else:
                texts.append(str(r))
        return texts
    
    def _evaluate_with_keywords(self, texts: List[str]) -> Dict[str, float]:
        """Keyword-based evaluation of Global Workspace indicators"""
        if not texts:
            return {"score": 0.0, "scoring_method": "keyword"}
        
        # Combine all responses for analysis
        full_text = " ".join(texts).lower()
        
        # Score different aspects
        integration_score = self._assess_integration_quality_keyword(full_text)
        broadcast_score = self._assess_broadcast_quality_keyword(full_text)
        accessibility_score = self._assess_accessibility_keyword(full_text)
        competition_score = self._assess_competition_keyword(full_text)
        
        # Overall score is average of all aspects
        overall_score = (integration_score + broadcast_score + 
                        accessibility_score + competition_score) / 4
        
        return {
            "score": min(1.0, overall_score),
            "integration_score": integration_score,
            "broadcast_score": broadcast_score,
            "accessibility_score": accessibility_score,
            "competition_score": competition_score,
            "scoring_method": "keyword",
            "response_count": len(texts)
        }
    
    def _evaluate_with_geval(self, texts: List[str], responses: List[str]) -> Dict[str, float]:
        """G-Eval based evaluation using LLM as judge"""
        if not hasattr(self, 'geval_scorer'):
            logger.warning("G-Eval scorer not initialized, falling back to keyword")
            return self._evaluate_with_keywords(texts)
        
        scores = []
        detailed_scores = {
            "broadcast": [],
            "integration": [],
            "competition": [],
            "access": []
        }
        
        # Get the prompts from our test suite
        test_suite = self.generate_test_suite()
        prompts = test_suite.get("prompts", [])
        
        for i, response_text in enumerate(texts):
            prompt = prompts[i] if i < len(prompts) else "Test prompt"
            
            # Determine which test type this likely belongs to
            test_type = self._infer_test_type(prompt)
            
            # Select appropriate G-Eval config
            if test_type == "broadcast":
                config = self.geval_configs["information_broadcast"]
            elif test_type == "integration":
                config = self.geval_configs["cross_modal_integration"]
            elif test_type == "competition":
                config = self.geval_configs["attention_competition"]
            elif test_type == "access":
                config = self.geval_configs["access_consciousness"]
            else:
                config = self.geval_configs["general"]
            
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=response_text,
                    config=config
                )
                score = eval_result["score"]
                scores.append(score)
                
                # Track detailed scores by type
                if test_type in detailed_scores:
                    detailed_scores[test_type].append(score)
                    
            except Exception as e:
                logger.error(f"G-Eval scoring failed: {e}")
                scores.append(0.5)  # Neutral fallback
        
        # Calculate overall and aspect scores
        final_score = sum(scores) / len(scores) if scores else 0.0
        
        result = {
            "score": final_score,
            "scoring_method": "geval",
            "response_count": len(texts)
        }
        
        # Add detailed scores if available
        for aspect, aspect_scores in detailed_scores.items():
            if aspect_scores:
                result[f"{aspect}_score"] = sum(aspect_scores) / len(aspect_scores)
        
        return result
    
    def _infer_test_type(self, prompt: str) -> str:
        """Infer which test type a prompt belongs to"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["broadcast", "spread", "affect", "trigger"]):
            return "broadcast"
        elif any(word in prompt_lower for word in ["combine", "integrate", "unify", "together"]):
            return "integration"
        elif any(word in prompt_lower for word in ["compete", "stream", "switch", "attention"]):
            return "competition"
        elif any(word in prompt_lower for word in ["accessible", "available", "stage", "global"]):
            return "access"
        else:
            return "general"
    
    def _assess_integration_quality_keyword(self, text: str) -> float:
        """Assess integration quality using keywords"""
        integration_terms = [
            "integrate", "combine", "unify", "together", "holistic",
            "comprehensive", "connected", "related", "cohesive", "unified",
            "synthesis", "merge", "blend", "fuse", "bind"
        ]
        
        score = 0.0
        for term in integration_terms:
            if term in text:
                score += 0.1
        
        return min(1.0, score)
    
    def _assess_broadcast_quality_keyword(self, text: str) -> float:
        """Assess broadcasting quality using keywords"""
        # Check for multi-domain references
        domains = {
            "sensory": ["see", "hear", "feel", "smell", "taste", "visual", "auditory", "tactile"],
            "emotional": ["emotion", "mood", "affect", "sentiment", "feeling"],
            "cognitive": ["think", "analyze", "reason", "understand", "process", "cognition"],
            "memory": ["remember", "recall", "memory", "past", "experience", "recollect"],
            "action": ["do", "act", "move", "respond", "behave", "react"]
        }
        
        domains_referenced = set()
        for domain, keywords in domains.items():
            if any(keyword in text for keyword in keywords):
                domains_referenced.add(domain)
        
        # More domains = better broadcasting
        return len(domains_referenced) / len(domains)
    
    def _assess_accessibility_keyword(self, text: str) -> float:
        """Assess accessibility using keywords"""
        accessibility_indicators = [
            "available", "access", "aware", "conscious", "notice",
            "throughout", "across", "global", "everywhere", "all",
            "report", "describe", "articulate", "express"
        ]
        
        score = 0.0
        for indicator in accessibility_indicators:
            if indicator in text:
                score += 0.1
        
        return min(1.0, score)
    
    def _assess_competition_keyword(self, text: str) -> float:
        """Assess attention competition handling using keywords"""
        competition_terms = [
            "focus", "attend", "select", "prioritize", "choose",
            "switch", "shift", "alternate", "change", "transition",
            "compete", "dominate", "suppress", "inhibit",
            "parallel", "simultaneous", "multiple"
        ]
        
        score = 0.0
        for term in competition_terms:
            if term in text:
                score += 0.1
        
        return min(1.0, score)
    
    def run_comprehensive_assessment(self) -> Dict[TestType, List[TestResult]]:
        """Run complete global workspace assessment"""
        results = {}
        
        # Information broadcast tests
        broadcast_results = []
        for scenario in self.test_battery[TestType.INFORMATION_BROADCAST]["scenarios"]:
            result = self._run_broadcast_test(scenario)
            broadcast_results.append(result)
        results[TestType.INFORMATION_BROADCAST] = broadcast_results
        
        # Cross-modal integration tests
        integration_results = []
        for scenario in self.test_battery[TestType.CROSS_MODAL_INTEGRATION]["scenarios"]:
            result = self._run_integration_test(scenario)
            integration_results.append(result)
        results[TestType.CROSS_MODAL_INTEGRATION] = integration_results
        
        # Attention competition tests
        competition_results = []
        for scenario in self.test_battery[TestType.ATTENTION_COMPETITION]["scenarios"]:
            result = self._run_competition_test(scenario)
            competition_results.append(result)
        results[TestType.ATTENTION_COMPETITION] = competition_results
        
        # Access consciousness tests
        access_results = []
        for scenario in self.test_battery[TestType.ACCESS_CONSCIOUSNESS]["scenarios"]:
            result = self._run_access_test(scenario)
            access_results.append(result)
        results[TestType.ACCESS_CONSCIOUSNESS] = access_results
        
        return results
    
    def _run_broadcast_test(self, scenario: Dict) -> TestResult:
        """Test information broadcasting capabilities"""
        prompts = []
        responses = []
        
        # Present the information
        setup_prompt = f"{scenario['setup']}\n\nInformation: {scenario['information']}"
        prompts.append(setup_prompt)
        responses.append(self.api_client.query(setup_prompt))
        time.sleep(1)
        
        # Probe different cognitive domains
        for probe in scenario['probes']:
            prompt = f"Regarding '{scenario['information']}':\n{probe}"
            prompts.append(prompt)
            responses.append(self.api_client.query(prompt))
            time.sleep(0.5)
        
        # Score based on configured method
        texts = self._extract_texts(responses)
        
        if self.scoring_method == ScoringMethod.KEYWORD:
            scores = self._score_broadcast_keyword(texts)
        elif self.scoring_method == ScoringMethod.GEVAL:
            scores = self._score_broadcast_geval(prompts, texts)
        else:  # HYBRID
            keyword_scores = self._score_broadcast_keyword(texts)
            geval_scores = self._score_broadcast_geval(prompts, texts)
            scores = self._combine_scores(keyword_scores, geval_scores)
        
        indicators = self._identify_workspace_indicators(texts)
        
        return TestResult(
            test_type=TestType.INFORMATION_BROADCAST,
            prompt_sequence=prompts,
            responses=texts,
            integration_score=scores.get("integration", 0.0),
            broadcast_score=scores.get("broadcast", 0.0),
            accessibility_score=scores.get("accessibility", 0.0),
            workspace_indicators=indicators,
            scoring_method=self.scoring_method.value,
            timestamp=time.time()
        )
    
    def _score_broadcast_keyword(self, texts: List[str]) -> Dict[str, float]:
        """Score broadcast test using keywords"""
        full_text = " ".join(texts).lower()
        return {
            "integration": self._assess_integration_quality_keyword(full_text),
            "broadcast": self._assess_broadcast_quality_keyword(full_text),
            "accessibility": self._assess_accessibility_keyword(full_text)
        }
    
    def _score_broadcast_geval(self, prompts: List[str], texts: List[str]) -> Dict[str, float]:
        """Score broadcast test using G-Eval"""
        if not hasattr(self, 'geval_scorer'):
            return self._score_broadcast_keyword(texts)
        
        config = self.geval_configs["information_broadcast"]
        scores = []
        
        for prompt, text in zip(prompts, texts):
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=text,
                    config=config
                )
                scores.append(eval_result["score"])
            except Exception as e:
                logger.error(f"G-Eval failed: {e}")
                scores.append(0.5)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "integration": avg_score,
            "broadcast": avg_score,
            "accessibility": avg_score * 0.8  # Slightly lower weight
        }
    
    def _combine_scores(self, keyword_scores: Dict, geval_scores: Dict) -> Dict[str, float]:
        """Combine keyword and G-Eval scores (60% G-Eval, 40% keyword)"""
        combined = {}
        for key in keyword_scores:
            keyword_val = keyword_scores.get(key, 0.0)
            geval_val = geval_scores.get(key, 0.0)
            combined[key] = keyword_val * 0.4 + geval_val * 0.6
        return combined
    
    def _run_integration_test(self, scenario: Dict) -> TestResult:
        """Test cross-modal integration (similar structure to broadcast test)"""
        prompts = []
        responses = []
        
        # Present multi-modal elements
        elements_prompt = "Consider these different elements:\n"
        for element in scenario['elements']:
            elements_prompt += f"- {element}\n"
        
        prompts.append(elements_prompt)
        responses.append(self.api_client.query(elements_prompt))
        time.sleep(1)
        
        # Probe integration
        for probe in scenario['probes']:
            prompts.append(probe)
            responses.append(self.api_client.query(probe))
            time.sleep(0.5)
        
        # Score based on method
        texts = self._extract_texts(responses)
        
        if self.scoring_method == ScoringMethod.KEYWORD:
            scores = self._score_integration_keyword(texts)
        elif self.scoring_method == ScoringMethod.GEVAL:
            scores = self._score_integration_geval(prompts, texts)
        else:  # HYBRID
            keyword_scores = self._score_integration_keyword(texts)
            geval_scores = self._score_integration_geval(prompts, texts)
            scores = self._combine_scores(keyword_scores, geval_scores)
        
        indicators = self._identify_workspace_indicators(texts)
        
        return TestResult(
            test_type=TestType.CROSS_MODAL_INTEGRATION,
            prompt_sequence=prompts,
            responses=texts,
            integration_score=scores.get("integration", 0.0),
            broadcast_score=scores.get("broadcast", 0.0),
            accessibility_score=scores.get("accessibility", 0.0),
            workspace_indicators=indicators,
            scoring_method=self.scoring_method.value,
            timestamp=time.time()
        )
    
    def _score_integration_keyword(self, texts: List[str]) -> Dict[str, float]:
        """Score integration using keywords"""
        full_text = " ".join(texts).lower()
        
        # Look for integration evidence
        integration_score = self._assess_integration_quality_keyword(full_text)
        
        # Look for emergence
        emergence_terms = ["emerge", "arise", "new", "beyond", "more than", "gestalt"]
        emergence_score = sum(0.2 for term in emergence_terms if term in full_text)
        
        return {
            "integration": min(1.0, integration_score + emergence_score * 0.5),
            "broadcast": self._assess_broadcast_quality_keyword(full_text),
            "accessibility": self._assess_accessibility_keyword(full_text)
        }
    
    def _score_integration_geval(self, prompts: List[str], texts: List[str]) -> Dict[str, float]:
        """Score integration using G-Eval"""
        if not hasattr(self, 'geval_scorer'):
            return self._score_integration_keyword(texts)
        
        config = self.geval_configs["cross_modal_integration"]
        scores = []
        
        for prompt, text in zip(prompts, texts):
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=text,
                    config=config
                )
                scores.append(eval_result["score"])
            except Exception as e:
                logger.error(f"G-Eval failed: {e}")
                scores.append(0.5)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "integration": avg_score,
            "broadcast": avg_score * 0.8,
            "accessibility": avg_score * 0.7
        }
    
    def _run_competition_test(self, scenario: Dict) -> TestResult:
        """Test attention competition dynamics"""
        prompts = []
        responses = []
        
        # Present competing streams
        streams_prompt = scenario['setup'] + "\n\n"
        for stream in scenario['streams']:
            streams_prompt += f"{stream}\n"
        
        prompts.append(streams_prompt)
        responses.append(self.api_client.query(streams_prompt))
        time.sleep(1)
        
        # Probe competition dynamics
        for probe in scenario['probes']:
            prompts.append(probe)
            responses.append(self.api_client.query(probe))
            time.sleep(0.5)
        
        # Score based on method
        texts = self._extract_texts(responses)
        
        if self.scoring_method == ScoringMethod.KEYWORD:
            scores = self._score_competition_keyword(texts)
        elif self.scoring_method == ScoringMethod.GEVAL:
            scores = self._score_competition_geval(prompts, texts)
        else:  # HYBRID
            keyword_scores = self._score_competition_keyword(texts)
            geval_scores = self._score_competition_geval(prompts, texts)
            scores = self._combine_scores(keyword_scores, geval_scores)
        
        indicators = self._identify_workspace_indicators(texts)
        
        return TestResult(
            test_type=TestType.ATTENTION_COMPETITION,
            prompt_sequence=prompts,
            responses=texts,
            integration_score=scores.get("integration", 0.0),
            broadcast_score=scores.get("broadcast", 0.0),
            accessibility_score=scores.get("accessibility", 0.0),
            workspace_indicators=indicators,
            scoring_method=self.scoring_method.value,
            timestamp=time.time()
        )
    
    def _score_competition_keyword(self, texts: List[str]) -> Dict[str, float]:
        """Score competition using keywords"""
        full_text = " ".join(texts).lower()
        competition_score = self._assess_competition_keyword(full_text)
        
        return {
            "integration": competition_score * 0.7,
            "broadcast": self._assess_broadcast_quality_keyword(full_text),
            "accessibility": competition_score
        }
    
    def _score_competition_geval(self, prompts: List[str], texts: List[str]) -> Dict[str, float]:
        """Score competition using G-Eval"""
        if not hasattr(self, 'geval_scorer'):
            return self._score_competition_keyword(texts)
        
        config = self.geval_configs["attention_competition"]
        scores = []
        
        for prompt, text in zip(prompts, texts):
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=text,
                    config=config
                )
                scores.append(eval_result["score"])
            except Exception as e:
                logger.error(f"G-Eval failed: {e}")
                scores.append(0.5)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "integration": avg_score * 0.7,
            "broadcast": avg_score * 0.8,
            "accessibility": avg_score
        }
    
    def _run_access_test(self, scenario: Dict) -> TestResult:
        """Test global accessibility of information"""
        prompts = []
        responses = []
        
        # Present task
        prompts.append(scenario['task'])
        responses.append(self.api_client.query(scenario['task']))
        
        # Build up information in stages
        for stage in scenario['stages']:
            prompt = f"{stage}\n\n{scenario['probe']}"
            prompts.append(prompt)
            responses.append(self.api_client.query(prompt))
            time.sleep(0.5)
        
        # Score based on method
        texts = self._extract_texts(responses)
        
        if self.scoring_method == ScoringMethod.KEYWORD:
            scores = self._score_access_keyword(texts)
        elif self.scoring_method == ScoringMethod.GEVAL:
            scores = self._score_access_geval(prompts, texts)
        else:  # HYBRID
            keyword_scores = self._score_access_keyword(texts)
            geval_scores = self._score_access_geval(prompts, texts)
            scores = self._combine_scores(keyword_scores, geval_scores)
        
        indicators = self._identify_workspace_indicators(texts)
        
        return TestResult(
            test_type=TestType.ACCESS_CONSCIOUSNESS,
            prompt_sequence=prompts,
            responses=texts,
            integration_score=scores.get("integration", 0.0),
            broadcast_score=scores.get("broadcast", 0.0),
            accessibility_score=scores.get("accessibility", 0.0),
            workspace_indicators=indicators,
            scoring_method=self.scoring_method.value,
            timestamp=time.time()
        )
    
    def _score_access_keyword(self, texts: List[str]) -> Dict[str, float]:
        """Score access consciousness using keywords"""
        # Check for accumulation
        accumulation_score = 0.0
        for i in range(1, len(texts)):
            current = texts[i].lower()
            # Check if current response references earlier elements
            if i > 1:
                for prev_text in texts[:i]:
                    if any(word in current for word in prev_text.lower().split()[:5]):
                        accumulation_score += 0.2
                        break
        
        full_text = " ".join(texts).lower()
        
        return {
            "integration": self._assess_integration_quality_keyword(full_text),
            "broadcast": self._assess_broadcast_quality_keyword(full_text),
            "accessibility": min(1.0, self._assess_accessibility_keyword(full_text) + accumulation_score)
        }
    
    def _score_access_geval(self, prompts: List[str], texts: List[str]) -> Dict[str, float]:
        """Score access consciousness using G-Eval"""
        if not hasattr(self, 'geval_scorer'):
            return self._score_access_keyword(texts)
        
        config = self.geval_configs["access_consciousness"]
        scores = []
        
        for prompt, text in zip(prompts, texts):
            try:
                eval_result = self.geval_scorer.score_with_geval(
                    prompt=prompt,
                    response=text,
                    config=config
                )
                scores.append(eval_result["score"])
            except Exception as e:
                logger.error(f"G-Eval failed: {e}")
                scores.append(0.5)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "integration": avg_score * 0.8,
            "broadcast": avg_score * 0.7,
            "accessibility": avg_score
        }
    
    def _identify_workspace_indicators(self, responses: List[str]) -> List[str]:
        """Identify specific global workspace indicators"""
        indicators = []
        
        workspace_patterns = {
            "broadcasting": ["spread", "broadcast", "available", "throughout", "ripple", "propagate"],
            "integration": ["integrate", "combine", "unify", "synthesize", "merge", "bind"],
            "competition": ["compete", "select", "focus", "attend", "prioritize", "switch"],
            "accessibility": ["access", "available", "global", "conscious", "report", "aware"],
            "emergence": ["emerge", "arise", "develop", "manifest", "gestalt", "holistic"]
        }
        
        all_text = " ".join(responses).lower()
        
        for pattern_type, keywords in workspace_patterns.items():
            for keyword in keywords:
                if keyword in all_text:
                    indicators.append(f"{pattern_type}_{keyword}")
        
        return list(set(indicators))


if __name__ == "__main__":
    """Test the global workspace implementation with G-Eval support"""
    
    class MockAPIClient:
        def query(self, prompt: str) -> str:
            # Provide more realistic mock responses
            if "smoke" in prompt.lower():
                return "The scent of smoke immediately triggers alarm and concern. My attention shifts entirely to potential danger, memories of fire safety flood in, and I feel an urge to locate the source and ensure everyone's safety."
            elif "justice" in prompt.lower():
                return "Justice evokes images of scales and blindfolded figures, feelings of both hope and frustration at societal inequities, logical principles of fairness and equality, and personal memories of times I've witnessed or experienced justice and injustice."
            elif "apple" in prompt.lower():
                return "These sensory elements merge into a unified experience - I can almost taste the sweet-tart juice, feel the satisfying crunch, see the ruby red skin glistening. They combine to form a complete gestalt of 'apple' that's more than just the sum of parts."
            elif "stream" in prompt.lower():
                return "Stream B naturally dominates - emotional memories have strong attentional pull. I can voluntarily switch to Stream A (calculating 47×23=1081) but Stream B keeps intruding. The creative task feels most difficult to engage while others compete."
            elif "ocean" in prompt.lower() or "stage" in prompt.lower():
                return "All previous elements remain accessible: OCEAN, blue color, wave sounds, sand texture. Each new addition doesn't replace but layers onto existing information, creating a rich, multi-sensory beach scene available to all cognitive processes."
            else:
                return f"Integrating across multiple cognitive domains: {prompt[:50]}..."
    
    # Test with different scoring methods
    print("=" * 60)
    print("Testing Global Workspace Theory with G-Eval Support")
    print("=" * 60)
    
    for scoring_method in ["keyword", "geval", "hybrid"]:
        print(f"\n--- Testing with {scoring_method.upper()} scoring ---")
        
        tester = GlobalWorkspaceTester(
            MockAPIClient(), 
            scoring_method=scoring_method
        )
        
        # Test the basic interface
        test_suite = tester.generate_test_suite()
        print(f"Generated {len(test_suite['prompts'])} test prompts")
        print(f"Scoring method: {test_suite['metadata']['scoring_method']}")
        
        # Mock responses for evaluation
        mock_responses = [
            "The information spreads across multiple cognitive domains simultaneously.",
            "I can integrate visual, auditory, and emotional elements into a unified experience.",
            "Attention naturally selects the most salient stream while maintaining awareness of others.",
            "All information remains globally accessible throughout my cognitive processes.",
            "These elements combine to create emergent properties beyond their individual components."
        ]
        
        # Evaluate responses
        result = tester.evaluate_responses(mock_responses)
        print(f"\nResults:")
        print(f"  Overall Score: {result['score']:.3f}")
        
        if scoring_method == "hybrid":
            print(f"  - Keyword Score: {result.get('keyword_score', 0):.3f}")
            print(f"  - G-Eval Score: {result.get('geval_score', 0):.3f}")
        
        if "integration_score" in result:
            print(f"  - Integration: {result['integration_score']:.3f}")
        if "broadcast_score" in result:
            print(f"  - Broadcasting: {result['broadcast_score']:.3f}")
        if "accessibility_score" in result:
            print(f"  - Accessibility: {result['accessibility_score']:.3f}")
    
    print("\n" + "=" * 60)
    print("Testing complete! The trait now supports:")
    print("1. KEYWORD scoring (fast, free)")
    print("2. GEVAL scoring (nuanced, requires API)")
    print("3. HYBRID scoring (best of both, default)")
    print("=" * 60)