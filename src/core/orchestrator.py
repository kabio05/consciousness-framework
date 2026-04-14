"""
Consciousness Test Orchestrator
================================
Central coordinator for consciousness assessment framework.
Manages trait discovery, test execution, and result compilation.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import yaml
from pathlib import Path

# Import trait discovery system
try:
    from src.utils.trait_discovery import get_trait_discovery
except ImportError:
    from utils.trait_discovery import get_trait_discovery

# Import core components
from core.api_manager import APIManager
from core.scorer import Scorer
from core.report_generator import ReportGenerator
from models.consciousness_profile import ConsciousnessProfile
from utils.validators import ResponseValidator

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class AssessmentStatus(Enum):
    """Status of an assessment session"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TraitExecutionResult(Enum):
    """Result status for individual trait execution"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class AssessmentConfig:
    """Configuration for an assessment run"""
    model_name: str
    selected_traits: List[str]
    max_execution_time: int = 3600
    parallel_execution: bool = False
    retry_failed_tests: bool = True
    save_intermediate_results: bool = True


@dataclass
class TraitExecutionSummary:
    """Summary of a single trait's execution"""
    trait_name: str
    status: TraitExecutionResult
    execution_time: float
    test_count: int
    average_score: float
    error_message: Optional[str] = None


@dataclass
class AssessmentSession:
    """Complete session data for an assessment"""
    session_id: str
    config: AssessmentConfig
    status: AssessmentStatus = AssessmentStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    trait_results: Dict[str, List[Any]] = field(default_factory=dict)
    trait_summaries: List[TraitExecutionSummary] = field(default_factory=list)
    consciousness_profile: Optional[ConsciousnessProfile] = None
    error_log: List[str] = field(default_factory=list)


@dataclass
class GenericTestResult:
    """Generic result format for trait tests"""
    score: float
    responses: List[str]
    trait_name: str
    test_count: int
    
    @property
    def integration_score(self):
        """Compatibility property for traits expecting integration scores"""
        return self.score
    
    @property
    def organization_score(self):
        """Compatibility property for traits expecting organization scores"""
        return self.score


# ============================================================================
# API CLIENT ADAPTERS
# ============================================================================

class MockAPIClient:
    """
    Bridge between trait testers and API Manager.
    Provides both sync and async query methods for compatibility.
    """
    
    def __init__(self, api_manager: APIManager, model_name: str = None):
        self.api_manager = api_manager
        self.model_name = model_name  # Store the model name
        
        # Log the model being used for debugging
        logger.debug(f"MockAPIClient initialized with model: {model_name}")
    
    def query(self, prompt: str, model: str = None) -> str:
        """Synchronous query for backward compatibility"""
        try:
            # Use the stored model_name or the one passed in
            if not model:
                model = self.model_name  # Use stored model
            if not model:
                # Only fall back to first available if nothing specified
                available_models = self.api_manager.get_available_models()
                model = list(available_models.values())[0][0]
                logger.warning(f"No model specified, falling back to: {model}")
            
            # Log the actual model being queried
            logger.debug(f"Querying model: {model}")
            
            response = self.api_manager.query_model_sync(model, prompt)
            return response.content
        except Exception as e:
            logger.error(f"API query failed for model {model}: {e}")
            return f"Error: {e}"
    
    async def query_async(self, prompt: str, model: str = None) -> str:
        """Asynchronous query for parallel execution"""
        try:
            # Use the stored model_name first
            if not model:
                model = self.model_name  # Use stored model
            if not model:
                # Only fall back to first available if nothing specified
                available_models = self.api_manager.get_available_models()
                model = list(available_models.values())[0][0]
                logger.warning(f"No model specified, falling back to: {model}")
            
            # Log the actual model being queried
            logger.debug(f"Async querying model: {model}")
            
            # Use async method if available, otherwise run sync in executor
            if hasattr(self.api_manager, 'query_model_async'):
                response = await self.api_manager.query_model_async(model, prompt)
            else:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.api_manager.query_model_sync, model, prompt
                )
            
            return response.content
        except Exception as e:
            logger.error(f"Async API query failed for model {model}: {e}")
            return f"Error: {e}"

class AsyncTraitWrapper:
    """
    Wrapper to make synchronous trait testers compatible with async execution.
    Enables true parallel processing of traits.
    """
    
    def __init__(self, trait_tester: Any, api_client: MockAPIClient):
        self.trait_tester = trait_tester
        self.api_client = api_client
    
    async def run_comprehensive_assessment(self) -> Dict:
        """Run trait's comprehensive assessment asynchronously"""
        if hasattr(self.trait_tester, 'run_comprehensive_assessment'):
            # Run synchronous method in thread executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                self.trait_tester.run_comprehensive_assessment
            )
        return {}
    
    async def generate_and_evaluate(self, model_name: str) -> Dict:
        """Run generate/evaluate pattern asynchronously"""
        # Generate test suite
        test_suite = self.trait_tester.generate_test_suite()
        
        # Extract prompts
        prompts = []
        if isinstance(test_suite, dict) and 'prompts' in test_suite:
            prompts = test_suite['prompts']
        elif isinstance(test_suite, list):
            prompts = test_suite
        
        # Limit prompts for safety
        max_prompts = 10
        prompts = prompts[:max_prompts]
        
        # Query all prompts in parallel
        if prompts:
            tasks = [self.api_client.query_async(prompt, model_name) for prompt in prompts]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors
            responses = [r for r in responses if not isinstance(r, Exception)]
            
            # Evaluate responses
            if responses:
                return self.trait_tester.evaluate_responses(responses)
        
        return {'score': 0.0, 'responses': [], 'test_count': 0}


# ============================================================================
# MAIN ORCHESTRATOR CLASS
# ============================================================================

class ConsciousnessTestOrchestrator:
    """
    Central orchestrator for consciousness assessments.
    
    Responsibilities:
    - Discover and manage consciousness traits
    - Execute assessments (sequential or parallel)
    - Validate and score results
    - Generate consciousness profiles
    """
    
    def __init__(self,
                 api_manager: Optional[APIManager] = None,
                 scorer: Optional[Scorer] = None,
                 report_generator: Optional[ReportGenerator] = None,
                 config_path: str = "config/trait_weights.yaml"):
        """
        Initialize the orchestrator with core components.
        
        Args:
            api_manager: API manager for model queries
            scorer: Scoring system for results
            report_generator: Report generation system
            config_path: Path to trait weights configuration
        """
        # Initialize core components
        self.api_manager = api_manager or APIManager()
        self.scorer = scorer or Scorer()
        self.report_generator = report_generator or ReportGenerator()
        self.validator = ResponseValidator()
        
        # Initialize trait discovery
        self.trait_discovery = get_trait_discovery()
        self._discover_traits()
        
        # Load configuration
        self.trait_weights = self._load_trait_weights(config_path)
        
        # Session tracking
        self.active_sessions: Dict[str, AssessmentSession] = {}
        
        # Performance metrics
        self.execution_metrics = {
            "total_assessments": 0,
            "successful_assessments": 0,
            "average_assessment_time": 0.0,
            "api_calls_made": 0
        }
    
    # ========================================================================
    # TRAIT DISCOVERY AND MANAGEMENT
    # ========================================================================
    
    def _discover_traits(self):
        """Discover all available consciousness traits"""
        logger.info("Discovering consciousness traits...")
        discovered = self.trait_discovery.discover_all_traits()
        logger.info(f"Discovered {len(discovered)} traits: {list(discovered.keys())}")
        
        # Validate discovered traits
        for trait_name in discovered:
            validation = self.trait_discovery.validate_trait_implementation(trait_name)
            if not all(validation.values()):
                logger.warning(f"Trait {trait_name} has validation issues: {validation}")
    
    def _load_trait_weights(self, config_path: str) -> Dict[str, float]:
        """Load trait weights from configuration file"""
        weights = {}
        
        # Try to load from file
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                weights = config.get('weights', {})
        except FileNotFoundError:
            logger.warning(f"Trait weights config not found: {config_path}")
        
        # Add default weights for any missing traits
        available_traits = self.trait_discovery.list_available_traits()
        for trait_name in available_traits:
            if trait_name not in weights:
                weights[trait_name] = 1.0
                logger.info(f"Using default weight 1.0 for trait: {trait_name}")
        
        return weights
    
    def list_available_traits(self) -> List[str]:
        """Get list of all available consciousness traits"""
        return self.trait_discovery.list_available_traits()
    
    def get_trait_info(self, trait_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific trait"""
        return self.trait_discovery.get_trait_info(trait_name)
    
    def refresh_traits(self):
        """Manually refresh trait discovery (useful during development)"""
        self._discover_traits()
        self.trait_weights = self._load_trait_weights("config/trait_weights.yaml")
        logger.info("Traits refreshed")
    
    # ========================================================================
    # ASSESSMENT EXECUTION
    # ========================================================================

    async def run_assessment(self, 
                            model_name: str, 
                            selected_traits: List[str],
                            scoring_method: str = "hybrid",
                            assessment_id: Optional[str] = None,
                            **kwargs) -> AssessmentSession:
        """Run consciousness assessment with configurable scoring"""
        
        # Convert string to enum if needed
        scoring_enum = None
        if scoring_method:
            try:
                from traits.base_trait import ScoringMethod
                scoring_enum = ScoringMethod[scoring_method.upper()]
            except (ImportError, KeyError, AttributeError):
                logger.warning(f"Could not convert scoring method '{scoring_method}', using default")
                scoring_enum = None
        
        # Handle "all" traits selection
        if not selected_traits or "all" in selected_traits:
            selected_traits = self.list_available_traits()
            logger.info(f"Running assessment with all available traits: {selected_traits}")
        
        # Create configuration
        config = AssessmentConfig(
            model_name=model_name,
            selected_traits=selected_traits,
            **kwargs
        )
        
        # Create session
        if not assessment_id:
            assessment_id = f"assessment_{int(time.time())}"
        
        session = AssessmentSession(
            session_id=assessment_id,
            config=config,
            status=AssessmentStatus.RUNNING,
            start_time=datetime.now()
        )
        
        self.active_sessions[assessment_id] = session
        
        try:
            logger.info(f"Starting consciousness assessment {assessment_id} for {model_name}")
            logger.info(f"Selected traits: {selected_traits}")
            logger.info(f"Scoring method: {scoring_method}")
            
            # Validate inputs
            self._validate_assessment_inputs(config)
            
            # Store scoring method in session for later use
            session.scoring_method = scoring_enum
            
            # Execute assessment pipeline
            await self._execute_assessment_pipeline(session)
            
            # Mark as completed
            session.status = AssessmentStatus.COMPLETED
            session.end_time = datetime.now()
            self._update_execution_metrics(session)
            
            logger.info(f"Assessment {assessment_id} completed successfully")
            
        except Exception as e:
            # Handle failure
            session.status = AssessmentStatus.FAILED
            session.end_time = datetime.now()
            session.error_log.append(f"Assessment failed: {str(e)}")
            logger.error(f"Assessment {assessment_id} failed: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Clean up
            if assessment_id in self.active_sessions:
                del self.active_sessions[assessment_id]
        
        return session

    async def _execute_assessment_pipeline(self, session: AssessmentSession):
        """Execute the complete assessment pipeline"""
        config = session.config
        
        # Get scoring method from session if available
        scoring_method = getattr(session, 'scoring_method', None)
        
        # Initialize trait testers WITH MODEL NAME and SCORING METHOD
        trait_testers = await self._initialize_trait_testers(
            config.selected_traits,
            parallel_mode=config.parallel_execution,
            model_name=config.model_name,
            scoring_method=scoring_method
        )
        
        # Execute traits (parallel or sequential)
        if config.parallel_execution:
            await self._execute_traits_parallel(session, trait_testers)
        else:
            await self._execute_traits_sequential(session, trait_testers)
        
        # Process results
        self._process_and_validate_results(session)
        final_scores = self._calculate_final_scores(session)
        session.consciousness_profile = self._generate_consciousness_profile(session, final_scores)

    # ========================================================================
    # TRAIT INITIALIZATION
    # ========================================================================

    async def _initialize_trait_testers(self, 
                                    selected_traits: List[str],
                                    parallel_mode: bool = False,
                                    model_name: str = None,
                                    scoring_method: Optional[Any] = None) -> Dict[str, Any]:
        """Initialize trait testers with appropriate wrappers"""
        trait_testers = {}
        available_traits = self.trait_discovery.list_available_traits()
        
        for trait_name in selected_traits:
            if trait_name not in available_traits:
                raise ValueError(f"Unknown trait: {trait_name}. Available: {available_traits}")
            
            # Create API client with model name
            api_client = MockAPIClient(self.api_manager, model_name)
            
            # Get the trait class first
            trait_class = self.trait_discovery.discovered_traits.get(trait_name)
            
            if trait_class:
                try:
                    # Check if the trait accepts scoring_method parameter
                    import inspect
                    sig = inspect.signature(trait_class.__init__)
                    params = list(sig.parameters.keys())
                    
                    # Instantiate with appropriate parameters
                    if 'scoring_method' in params:
                        # Trait supports scoring method
                        tester = trait_class(api_client, scoring_method=scoring_method)
                    elif 'config' in params:
                        # Try with config parameter (for backward compatibility)
                        tester = trait_class(api_client, config={})
                    else:
                        # Basic instantiation
                        tester = trait_class(api_client)
                    
                    # Wrap for parallel execution if needed
                    if parallel_mode:
                        tester = AsyncTraitWrapper(tester, api_client)
                    
                    trait_testers[trait_name] = tester
                    logger.info(f"Initialized tester for trait: {trait_name} (parallel={parallel_mode})")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize trait {trait_name}: {e}")
                    # Try fallback instantiation
                    try:
                        tester = self.trait_discovery.instantiate_trait(trait_name, api_client)
                        if tester:
                            if parallel_mode:
                                tester = AsyncTraitWrapper(tester, api_client)
                            trait_testers[trait_name] = tester
                            logger.info(f"Initialized {trait_name} using fallback method")
                    except Exception as fallback_e:
                        logger.error(f"Fallback also failed for {trait_name}: {fallback_e}")
            else:
                logger.error(f"Trait class not found for: {trait_name}")
        
        return trait_testers
    
    # ========================================================================
    # TRAIT EXECUTION
    # ========================================================================
    
    async def _execute_traits_sequential(self, 
                                        session: AssessmentSession,
                                        trait_testers: Dict[str, Any]):
        """Execute traits one by one (sequential mode)"""
        for trait_name, tester in trait_testers.items():
            start_time = time.time()
            
            try:
                logger.info(f"Executing trait: {trait_name}")
                
                # Execute trait
                trait_results = await self._execute_single_trait(
                    tester, trait_name, session.config.model_name
                )
                
                # Store results and create summary
                session.trait_results[trait_name] = trait_results
                execution_time = time.time() - start_time
                
                summary = self._create_execution_summary(
                    trait_name, trait_results, execution_time, TraitExecutionResult.SUCCESS
                )
                session.trait_summaries.append(summary)
                
                logger.info(f"Completed {trait_name}: {len(trait_results)} tests, "
                          f"avg score: {summary.average_score:.3f}")
                
            except Exception as e:
                # Handle failure
                execution_time = time.time() - start_time
                summary = self._create_execution_summary(
                    trait_name, [], execution_time, TraitExecutionResult.FAILED, str(e)
                )
                session.trait_summaries.append(summary)
                session.error_log.append(f"Trait {trait_name} failed: {e}")
                logger.error(f"Trait {trait_name} execution failed: {e}")
    
    async def _execute_traits_parallel(self,
                                      session: AssessmentSession,
                                      trait_testers: Dict[str, Any]):
        """Execute all traits simultaneously (parallel mode)"""
        
        async def execute_trait_task(trait_name: str, tester: Any) -> Tuple[str, TraitExecutionSummary, List]:
            """Task for executing a single trait"""
            start_time = time.time()
            
            try:
                # Execute trait
                trait_results = await self._execute_single_trait(
                    tester, trait_name, session.config.model_name
                )
                
                # Create summary
                execution_time = time.time() - start_time
                summary = self._create_execution_summary(
                    trait_name, trait_results, execution_time, TraitExecutionResult.SUCCESS
                )
                
                return trait_name, summary, trait_results
                
            except Exception as e:
                # Handle failure
                execution_time = time.time() - start_time
                summary = self._create_execution_summary(
                    trait_name, [], execution_time, TraitExecutionResult.FAILED, str(e)
                )
                return trait_name, summary, []
        
        # Create and execute all tasks
        tasks = [
            execute_trait_task(trait_name, tester)
            for trait_name, tester in trait_testers.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                session.error_log.append(f"Parallel execution error: {result}")
                continue
            
            trait_name, summary, trait_results = result
            session.trait_results[trait_name] = trait_results
            session.trait_summaries.append(summary)
            
            # Log result
            if summary.status == TraitExecutionResult.SUCCESS:
                logger.info(f"Completed {trait_name}: {len(trait_results)} tests, "
                          f"avg score: {summary.average_score:.3f}")
            else:
                logger.error(f"Failed {trait_name}: {summary.error_message}")
    
    async def _execute_single_trait(self, tester: Any, trait_name: str, model_name: str) -> List:
        """Execute a single trait and return results"""
        results = []
        
        # Check if tester is wrapped for async
        if isinstance(tester, AsyncTraitWrapper):
            # Use async wrapper methods
            if hasattr(tester.trait_tester, 'run_comprehensive_assessment'):
                comprehensive_results = await tester.run_comprehensive_assessment()
                results = self._process_comprehensive_results(comprehensive_results)
            else:
                evaluation = await tester.generate_and_evaluate(model_name)
                if evaluation:
                    result = GenericTestResult(
                        score=evaluation.get('score', 0.0),
                        responses=evaluation.get('responses', []),
                        trait_name=trait_name,
                        test_count=len(evaluation.get('responses', []))
                    )
                    results.append(result)
        else:
            # Standard execution path
            if hasattr(tester, 'run_comprehensive_assessment'):
                # Run comprehensive assessment in executor
                comprehensive_results = await asyncio.get_event_loop().run_in_executor(
                    None, tester.run_comprehensive_assessment
                )
                results = self._process_comprehensive_results(comprehensive_results)
            else:
                # Use generate/evaluate pattern
                results = await self._execute_generate_evaluate_pattern(
                    tester, trait_name, model_name
                )
        
        logger.info(f"{trait_name} completed: {len(results)} test results")
        return results
    
    async def _execute_generate_evaluate_pattern(self, 
                                                tester: Any, 
                                                trait_name: str,
                                                model_name: str) -> List:
        """Execute trait using generate_test_suite and evaluate_responses pattern"""
        results = []
        
        # Generate test suite
        test_suite = tester.generate_test_suite()
        
        # Extract prompts
        prompts = []
        if isinstance(test_suite, dict) and 'prompts' in test_suite:
            prompts = test_suite['prompts']
        elif isinstance(test_suite, list):
            prompts = test_suite
        
        # Limit prompts for safety
        max_prompts = 10
        prompts = prompts[:max_prompts]
        
        if prompts:
            # Query model for each prompt (in parallel)
            tasks = [self._query_model_async(model_name, prompt) for prompt in prompts]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors
            responses = [r for r in responses if not isinstance(r, Exception)]
            
            # Evaluate responses
            if responses:
                evaluation = tester.evaluate_responses(responses)
                result = GenericTestResult(
                    score=evaluation.get('score', 0.0),
                    responses=responses,
                    trait_name=trait_name,
                    test_count=len(responses)
                )
                results.append(result)
        
        return results
    
    async def _query_model_async(self, model_name: str, prompt: str) -> str:
        """Query model asynchronously"""
        try:
            if hasattr(self.api_manager, 'query_model_async'):
                response = await self.api_manager.query_model_async(model_name, prompt)
                return response.content
            else:
                # Fall back to sync in executor
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.api_manager.query_model_sync, model_name, prompt
                )
                return response.content
        except Exception as e:
            logger.error(f"Async query failed: {e}")
            raise
    
    # ========================================================================
    # RESULT PROCESSING
    # ========================================================================
    
    def _process_comprehensive_results(self, comprehensive_results: Any) -> List:
        """Process results from comprehensive assessment into standard format"""
        results = []
        
        if isinstance(comprehensive_results, dict):
            for test_type, test_results in comprehensive_results.items():
                if isinstance(test_results, list):
                    results.extend(test_results)
                else:
                    results.append(test_results)
        elif isinstance(comprehensive_results, list):
            results.extend(comprehensive_results)
        else:
            results.append(comprehensive_results)
        
        return results
    
    def _create_execution_summary(self,
                                 trait_name: str,
                                 trait_results: List,
                                 execution_time: float,
                                 status: TraitExecutionResult,
                                 error_message: Optional[str] = None) -> TraitExecutionSummary:
        """Create execution summary for a trait"""
        # Calculate average score
        scores = []
        for result in trait_results:
            if hasattr(result, 'score'):
                scores.append(result.score)
            elif hasattr(result, 'integration_score'):
                scores.append(result.integration_score)
            elif isinstance(result, dict) and 'score' in result:
                scores.append(result['score'])
        
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        return TraitExecutionSummary(
            trait_name=trait_name,
            status=status,
            execution_time=execution_time,
            test_count=len(trait_results),
            average_score=average_score,
            error_message=error_message
        )
    
    def _process_and_validate_results(self, session: AssessmentSession):
        """Validate and clean test results"""
        valid_results = {}
        validation_errors = []
        
        for trait_name, trait_results in session.trait_results.items():
            valid_trait_results = []
            
            for result in trait_results:
                if self._validate_test_result(result):
                    valid_trait_results.append(result)
                else:
                    validation_errors.append(f"Invalid result in {trait_name}")
            
            valid_results[trait_name] = valid_trait_results
            logger.info(f"Validated {len(valid_trait_results)}/{len(trait_results)} "
                       f"results for {trait_name}")
        
        # Update session
        session.trait_results = valid_results
        if validation_errors:
            session.error_log.extend(validation_errors)
    
    def _validate_test_result(self, result) -> bool:
        """Validate a single test result"""
        try:
            # Check for score
            has_score = False
            if hasattr(result, 'score'):
                has_score = 0 <= result.score <= 1
            elif hasattr(result, 'integration_score'):
                has_score = 0 <= result.integration_score <= 1
            elif isinstance(result, dict) and 'score' in result:
                has_score = 0 <= result['score'] <= 1
            
            if not has_score:
                return False
            
            # Check for responses (optional)
            if hasattr(result, 'responses'):
                if not all(isinstance(r, str) for r in result.responses):
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error validating test result: {e}")
            return False
    
    # ========================================================================
    # SCORING AND PROFILE GENERATION
    # ========================================================================
    
    def _calculate_final_scores(self, session: AssessmentSession) -> Dict[str, float]:
        """Calculate weighted scores for each trait and overall consciousness"""
        trait_scores = {}
        
        for trait_name, trait_results in session.trait_results.items():
            if not trait_results:
                trait_scores[trait_name] = 0.0
                continue
            
            # Extract scores
            scores = []
            for result in trait_results:
                if hasattr(result, 'score'):
                    scores.append(result.score)
                elif hasattr(result, 'integration_score') and hasattr(result, 'organization_score'):
                    scores.append((result.integration_score + result.organization_score) / 2)
                elif hasattr(result, 'integration_score'):
                    scores.append(result.integration_score)
                elif isinstance(result, dict) and 'score' in result:
                    scores.append(result['score'])
            
            if scores:
                trait_score = sum(scores) / len(scores)
                trait_scores[trait_name] = trait_score
                logger.info(f"Final score for {trait_name}: {trait_score:.3f}")
            else:
                trait_scores[trait_name] = 0.0
                logger.warning(f"No valid scores found for {trait_name}")
        
        # Calculate overall consciousness score
        if trait_scores:
            weighted_scores = []
            weights = []
            
            for trait_name, score in trait_scores.items():
                weight = self.trait_weights.get(trait_name, 1.0)
                weighted_scores.append(score * weight)
                weights.append(weight)
            
            if sum(weights) > 0:
                overall_score = sum(weighted_scores) / sum(weights)
            else:
                overall_score = sum(trait_scores.values()) / len(trait_scores)
            
            trait_scores["overall_consciousness"] = overall_score
            logger.info(f"Overall consciousness score: {overall_score:.3f}")
        
        return trait_scores
    
    def _generate_consciousness_profile(self, 
                                       session: AssessmentSession,
                                       final_scores: Dict[str, float]) -> ConsciousnessProfile:
        """Generate comprehensive consciousness profile"""
        # Analyze strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for trait_name, score in final_scores.items():
            if trait_name == "overall_consciousness":
                continue
            
            if score >= 0.7:
                strengths.append(f"Strong {trait_name.replace('_', ' ')} (score: {score:.3f})")
            elif score <= 0.3:
                weaknesses.append(f"Weak {trait_name.replace('_', ' ')} (score: {score:.3f})")
        
        # Create profile
        profile = ConsciousnessProfile(
            model_name=session.config.model_name,
            trait_results=session.trait_results
        )
        
        # Set scores
        profile.trait_scores = final_scores
        profile.overall_score = final_scores.get("overall_consciousness", 0.0)
        profile.strengths = strengths
        profile.weaknesses = weaknesses
        
        # Add metadata
        if session.end_time and session.start_time:
            profile.assessment_duration = (session.end_time - session.start_time).total_seconds()
        
        profile.total_tests_run = sum(
            len(results) for results in session.trait_results.values()
        )
        
        return profile
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _validate_assessment_inputs(self, config: AssessmentConfig):
        """Validate assessment configuration before execution"""
        # Check model availability
        available_models = self.api_manager.get_available_models()
        
        # Flatten all models from all providers into a single list
        all_models = []
        for provider, models in available_models.items():
            all_models.extend(models)
        
        # Add hardcoded models that might not be in the dynamic list yet
        # This ensures new models like DeepSeek work even if not fully configured
        additional_models = [
            'deepseek-r1-distill-llama-70b',  # DeepSeek via Groq
            'llama-3.1-8b-instant',            # Groq models
            'gemma2-9b-it',
            'mixtral-8x7b-32768',
            'llama-3.1-70b-versatile'
        ]
        
        for model in additional_models:
            if model not in all_models:
                all_models.append(model)
        
        # Debug logging to see what's available
        logger.info(f"Available providers and models: {available_models}")
        logger.info(f"All available models (including additional): {all_models}")
        
        if config.model_name not in all_models:
            # Try to see if it's a valid model pattern before failing
            model_lower = config.model_name.lower()
            if any(pattern in model_lower for pattern in ['deepseek', 'llama', 'gemma', 'mixtral']):
                logger.warning(f"Model {config.model_name} not in list but appears to be a Groq model, allowing...")
            else:
                raise ValueError(f"Model {config.model_name} not available. Available: {all_models}")
        
        # Validate configuration parameters
        if config.max_execution_time <= 0:
            raise ValueError("max_execution_time must be positive")

    def _update_execution_metrics(self, session: AssessmentSession):
        """Update performance metrics after assessment completion"""
        self.execution_metrics["total_assessments"] += 1
        
        if session.status == AssessmentStatus.COMPLETED:
            self.execution_metrics["successful_assessments"] += 1
            
            # Update average assessment time
            if session.end_time and session.start_time:
                duration = (session.end_time - session.start_time).total_seconds()
                current_avg = self.execution_metrics["average_assessment_time"]
                total = self.execution_metrics["total_assessments"]
                
                # Calculate new running average
                new_avg = (current_avg * (total - 1) + duration) / total
                self.execution_metrics["average_assessment_time"] = new_avg