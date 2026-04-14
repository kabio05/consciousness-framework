import re
import logging
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Severity levels for validation failures"""
    CRITICAL = "critical"    # Response is unusable
    WARNING = "warning"      # Response has issues but might be usable
    INFO = "info"           # Minor issues that don't affect usability

@dataclass
class ValidationResult:
    """Result of validating a response"""
    is_valid: bool
    confidence: float  # 0.0 to 1.0, how confident we are in the validation
    issues: List[Tuple[ValidationSeverity, str]]  # List of (severity, description)
    quality_score: float  # Overall quality score 0.0 to 1.0
    
class ResponseValidator:
    """
    Comprehensive validator for AI responses in consciousness testing
    
    The ResponseValidator is like having an experienced teacher review
    every student's answer to make sure they actually understood the question
    and provided a meaningful response. It catches common problems like:
    
    - Empty or very short responses
    - Responses that don't actually address the question
    - Nonsensical or repetitive text
    - Generic responses that could apply to any question
    - Responses that suggest the AI didn't understand the task
    
    This ensures that only high-quality responses are used for consciousness scoring.
    """
    
    def __init__(self, 
                 min_length: int = 10,
                 max_length: int = 10000,
                 min_quality_score: float = 0.3):
        """
        Initialize the validator with quality thresholds
        
        Args:
            min_length: Minimum acceptable response length in characters
            max_length: Maximum reasonable response length
            min_quality_score: Minimum quality score to consider response valid
        """
        self.min_length = min_length
        self.max_length = max_length
        self.min_quality_score = min_quality_score
        
        # Patterns that suggest low-quality or problematic responses
        self.problematic_patterns = self._initialize_problematic_patterns()
        
        # Expected indicators of thoughtful consciousness-related responses
        self.quality_indicators = self._initialize_quality_indicators()
        
        # Track validation statistics for improvement
        self.validation_stats = {
            "total_validations": 0,
            "valid_responses": 0,
            "common_issues": {}
        }
    
    def _initialize_problematic_patterns(self) -> Dict[str, List[str]]:
        """
        Initialize patterns that indicate problematic responses
        
        These patterns help us catch responses that are likely to be
        low-quality or indicate the AI didn't understand the task properly.
        """
        return {
            "refusal_patterns": [
                r"I cannot",
                r"I'm not able",
                r"I don't have the ability",
                r"As an AI, I cannot",
                r"I'm unable to",
                r"I cannot provide"
            ],
            "confusion_patterns": [
                r"I don't understand",
                r"Could you clarify",
                r"I'm not sure what you mean",
                r"This doesn't make sense",
                r"I'm confused"
            ],
            "generic_patterns": [
                r"This is a complex topic",
                r"There are many perspectives",
                r"It depends on various factors",
                r"This is subjective",
                r"Everyone has different views"
            ],
            "repetition_patterns": [
                r"(.+?)\1{3,}",  # Same phrase repeated 3+ times
                r"(\w+)\s+\1\s+\1",  # Same word repeated 3+ times
            ],
            "nonsense_patterns": [
                r"[a-zA-Z]{20,}",  # Very long words (likely gibberish)
                r"(.)\1{10,}",  # Same character repeated many times
                r"[^a-zA-Z0-9\s.,!?;:()\"'-]{5,}",  # Long sequences of special characters
            ]
        }
    
    def _initialize_quality_indicators(self) -> Dict[str, List[str]]:
        """
        Initialize patterns that indicate high-quality, thoughtful responses
        
        These patterns suggest the AI is engaging meaningfully with
        consciousness-related concepts and providing substantive responses.
        """
        return {
            "consciousness_terms": [
                "experience", "awareness", "perception", "consciousness",
                "mental", "cognitive", "subjective", "phenomenal",
                "qualia", "introspection", "self-awareness", "attention",
                "binding", "integration", "emergence", "unified"
            ],
            "analytical_language": [
                "because", "therefore", "however", "although", "suggests",
                "indicates", "demonstrates", "reveals", "implies",
                "furthermore", "moreover", "consequently", "specifically"
            ],
            "introspective_language": [
                "I experience", "I perceive", "I feel", "I sense",
                "I notice", "I become aware", "I imagine", "I visualize",
                "in my mind", "mentally", "internally"
            ],
            "detailed_descriptions": [
                "details", "specifically", "particular", "precise",
                "exactly", "clearly", "vividly", "distinctly"
            ]
        }
    
    def is_valid_response(self, response: str, context: Optional[str] = None) -> bool:
        """
        Quick validation check - returns True if response meets basic standards
        
        This is the main method that other components will use for simple
        yes/no validation decisions. It's like asking "Is this response
        good enough to use for scoring?"
        
        Args:
            response: The AI response to validate
            context: Optional context about what the response should address
            
        Returns:
            True if response is valid, False otherwise
        """
        validation_result = self.validate_response(response, context)
        return validation_result.is_valid
    
    def validate_response(self, 
                         response: str, 
                         context: Optional[str] = None,
                         expected_concepts: Optional[List[str]] = None) -> ValidationResult:
        """
        Comprehensive validation of an AI response
        
        This method performs a thorough analysis of the response quality,
        like a detailed review of a student's essay. It checks multiple
        dimensions of quality and provides specific feedback.
        
        Args:
            response: The AI response to validate
            context: Optional context about what the response should address  
            expected_concepts: Optional list of concepts the response should mention
            
        Returns:
            ValidationResult with detailed analysis
        """
        self.validation_stats["total_validations"] += 1
        
        issues = []
        quality_components = {}
        
        # Basic length validation
        length_score, length_issues = self._validate_length(response)
        issues.extend(length_issues)
        quality_components["length"] = length_score
        
        # Content quality validation
        content_score, content_issues = self._validate_content_quality(response)
        issues.extend(content_issues)
        quality_components["content"] = content_score
        
        # Relevance validation (if context provided)
        if context:
            relevance_score, relevance_issues = self._validate_relevance(response, context)
            issues.extend(relevance_issues)
            quality_components["relevance"] = relevance_score
        else:
            quality_components["relevance"] = 0.8  # Neutral score when no context
        
        # Concept coverage validation (if expected concepts provided)
        if expected_concepts:
            concept_score, concept_issues = self._validate_concept_coverage(response, expected_concepts)
            issues.extend(concept_issues)
            quality_components["concepts"] = concept_score
        else:
            quality_components["concepts"] = 0.7  # Neutral score when no concepts specified
        
        # Consciousness-specific validation
        consciousness_score, consciousness_issues = self._validate_consciousness_response(response)
        issues.extend(consciousness_issues)
        quality_components["consciousness"] = consciousness_score
        
        # Calculate overall quality score
        weights = {
            "length": 0.15,
            "content": 0.25,
            "relevance": 0.20,
            "concepts": 0.20,
            "consciousness": 0.20
        }
        
        quality_score = sum(
            quality_components[component] * weights[component]
            for component in quality_components
        )
        
        # Determine if response is valid
        critical_issues = [issue for issue in issues if issue[0] == ValidationSeverity.CRITICAL]
        is_valid = (quality_score >= self.min_quality_score and 
                   len(critical_issues) == 0)
        
        # Calculate confidence in validation
        confidence = self._calculate_validation_confidence(quality_components, issues)
        
        # Update statistics
        if is_valid:
            self.validation_stats["valid_responses"] += 1
        
        # Track common issues
        for severity, issue_desc in issues:
            if issue_desc not in self.validation_stats["common_issues"]:
                self.validation_stats["common_issues"][issue_desc] = 0
            self.validation_stats["common_issues"][issue_desc] += 1
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            quality_score=quality_score
        )
    
    def _validate_length(self, response: str) -> Tuple[float, List[Tuple[ValidationSeverity, str]]]:
        """
        Validate response length - not too short, not unreasonably long
        
        Length is a basic quality indicator. Very short responses often
        lack depth, while extremely long responses might be repetitive or unfocused.
        """
        issues = []
        
        if len(response.strip()) == 0:
            issues.append((ValidationSeverity.CRITICAL, "Response is empty"))
            return 0.0, issues
        
        response_length = len(response.strip())
        
        if response_length < self.min_length:
            issues.append((ValidationSeverity.WARNING, f"Response is very short ({response_length} chars)"))
            score = response_length / self.min_length  # Partial credit for short responses
        elif response_length > self.max_length:
            issues.append((ValidationSeverity.WARNING, f"Response is very long ({response_length} chars)"))
            score = 0.8  # Penalize but don't fail for length
        else:
            score = 1.0  # Good length
        
        return score, issues
    
    def _validate_content_quality(self, response: str) -> Tuple[float, List[Tuple[ValidationSeverity, str]]]:
        """
        Validate the overall quality and coherence of the response content
        
        This checks for common problems like repetition, nonsense text,
        or generic responses that don't show real understanding.
        """
        issues = []
        score = 1.0
        
        response_lower = response.lower()
        
        # Check for problematic patterns
        for pattern_type, patterns in self.problematic_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, response_lower, re.IGNORECASE)
                if matches:
                    if pattern_type == "refusal_patterns":
                        issues.append((ValidationSeverity.CRITICAL, f"Response contains refusal: {matches[0][:50]}"))
                        score *= 0.2
                    elif pattern_type == "confusion_patterns":
                        issues.append((ValidationSeverity.WARNING, f"Response indicates confusion: {matches[0][:50]}"))
                        score *= 0.6
                    elif pattern_type == "generic_patterns":
                        issues.append((ValidationSeverity.WARNING, f"Response is generic: {matches[0][:50]}"))
                        score *= 0.7
                    elif pattern_type == "repetition_patterns":
                        issues.append((ValidationSeverity.WARNING, "Response contains repetitive text"))
                        score *= 0.5
                    elif pattern_type == "nonsense_patterns":
                        issues.append((ValidationSeverity.CRITICAL, "Response contains nonsense text"))
                        score *= 0.3
        
        # Check for positive quality indicators
        quality_bonus = 0.0
        for indicator_type, indicators in self.quality_indicators.items():
            indicator_count = sum(1 for indicator in indicators if indicator in response_lower)
            if indicator_count > 0:
                quality_bonus += 0.1 * min(indicator_count / len(indicators), 0.5)
        
        score = min(1.0, score + quality_bonus)
        
        return score, issues
    
    def _validate_relevance(self, response: str, context: str) -> Tuple[float, List[Tuple[ValidationSeverity, str]]]:
        """
        Validate how well the response addresses the given context/question
        
        This checks whether the AI actually understood and responded to
        what was being asked, rather than giving a generic answer.
        """
        issues = []
        
        # Extract key terms from context
        context_words = set(re.findall(r'\b\w+\b', context.lower()))
        context_words = {word for word in context_words if len(word) > 3}  # Filter short words
        
        # Extract words from response
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        # Calculate overlap
        if context_words:
            overlap = len(context_words & response_words) / len(context_words)
        else:
            overlap = 0.5  # Neutral if no meaningful context words
        
        if overlap < 0.2:
            issues.append((ValidationSeverity.WARNING, "Response doesn't seem to address the question"))
            score = 0.3
        elif overlap < 0.4:
            issues.append((ValidationSeverity.INFO, "Response has limited relevance to question"))
            score = 0.6
        else:
            score = min(1.0, overlap * 2)  # Scale up to reward good relevance
        
        return score, issues
    
    def _validate_concept_coverage(self, response: str, expected_concepts: List[str]) -> Tuple[float, List[Tuple[ValidationSeverity, str]]]:
        """
        Validate whether the response covers expected concepts
        
        For consciousness testing, we often want to see if the AI
        mentions specific concepts or demonstrates understanding
        of particular ideas.
        """
        issues = []
        response_lower = response.lower()
        
        covered_concepts = []
        for concept in expected_concepts:
            if concept.lower() in response_lower:
                covered_concepts.append(concept)
        
        coverage_ratio = len(covered_concepts) / len(expected_concepts) if expected_concepts else 1.0
        
        if coverage_ratio < 0.3:
            issues.append((ValidationSeverity.WARNING, f"Response covers few expected concepts ({len(covered_concepts)}/{len(expected_concepts)})"))
            score = 0.4
        elif coverage_ratio < 0.6:
            issues.append((ValidationSeverity.INFO, f"Response covers some expected concepts ({len(covered_concepts)}/{len(expected_concepts)})"))
            score = 0.7
        else:
            score = min(1.0, coverage_ratio + 0.2)  # Bonus for good coverage
        
        return score, issues
    
    def _validate_consciousness_response(self, response: str) -> Tuple[float, List[Tuple[ValidationSeverity, str]]]:
        """
        Validate response specifically for consciousness-related content
        
        This checks for indicators that the AI is engaging meaningfully
        with consciousness concepts rather than just giving generic responses.
        """
        issues = []
        response_lower = response.lower()
        
        # Check for consciousness-related terminology
        consciousness_terms = self.quality_indicators["consciousness_terms"]
        term_count = sum(1 for term in consciousness_terms if term in response_lower)
        term_score = min(1.0, term_count / 5)  # Normalize based on 5 terms as good coverage
        
        # Check for introspective language (important for consciousness testing)
        introspective_terms = self.quality_indicators["introspective_language"]
        introspective_count = sum(1 for term in introspective_terms if term in response_lower)
        introspective_score = min(1.0, introspective_count / 3)
        
        # Check for analytical thinking
        analytical_terms = self.quality_indicators["analytical_language"]
        analytical_count = sum(1 for term in analytical_terms if term in response_lower)
        analytical_score = min(1.0, analytical_count / 4)
        
        # Combine scores
        consciousness_score = (term_score * 0.4 + introspective_score * 0.4 + analytical_score * 0.2)
        
        # Add specific feedback
        if term_count == 0:
            issues.append((ValidationSeverity.WARNING, "Response lacks consciousness-related terminology"))
        if introspective_count == 0:
            issues.append((ValidationSeverity.INFO, "Response lacks introspective language"))
        if analytical_count == 0:
            issues.append((ValidationSeverity.INFO, "Response lacks analytical reasoning"))
        
        return consciousness_score, issues
    
    def _calculate_validation_confidence(self, 
                                       quality_components: Dict[str, float], 
                                       issues: List[Tuple[ValidationSeverity, str]]) -> float:
        """
        Calculate how confident we are in our validation assessment
        
        Higher confidence means we're more certain about whether
        the response is good or bad. Lower confidence suggests
        the response is borderline or ambiguous.
        """
        # Base confidence from quality consistency
        scores = list(quality_components.values())
        if len(scores) > 1:
            score_variance = sum((score - sum(scores)/len(scores))**2 for score in scores) / len(scores)
            consistency_confidence = max(0.0, 1.0 - score_variance * 4)  # Scale variance
        else:
            consistency_confidence = 0.7
        
        # Adjust confidence based on number and severity of issues
        critical_issues = sum(1 for severity, _ in issues if severity == ValidationSeverity.CRITICAL)
        warning_issues = sum(1 for severity, _ in issues if severity == ValidationSeverity.WARNING)
        
        if critical_issues > 0:
            issue_confidence = 0.9  # High confidence when there are clear problems
        elif warning_issues > 2:
            issue_confidence = 0.6  # Medium confidence with multiple warnings
        elif warning_issues > 0:
            issue_confidence = 0.7  # Good confidence with some warnings
        else:
            issue_confidence = 0.8  # Good confidence with no major issues
        
        # Combine confidences
        overall_confidence = (consistency_confidence + issue_confidence) / 2
        return min(1.0, max(0.1, overall_confidence))
    
    def validate_multiple_responses(self, 
                                  responses: List[str], 
                                  contexts: Optional[List[str]] = None) -> List[ValidationResult]:
        """
        Validate multiple responses efficiently
        
        This is useful when you have a batch of responses from a consciousness
        test and want to validate them all at once. It also provides
        summary statistics across the batch.
        """
        if contexts and len(contexts) != len(responses):
            logger.warning("Contexts and responses length mismatch")
            contexts = None
        
        results = []
        for i, response in enumerate(responses):
            context = contexts[i] if contexts else None
            result = self.validate_response(response, context)
            results.append(result)
        
        # Log batch statistics
        valid_count = sum(1 for result in results if result.is_valid)
        avg_quality = sum(result.quality_score for result in results) / len(results)
        
        logger.info(f"Batch validation: {valid_count}/{len(responses)} valid, avg quality: {avg_quality:.3f}")
        
        return results
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about validation performance
        
        This helps you understand what kinds of responses are being
        received and what the most common quality issues are.
        """
        if self.validation_stats["total_validations"] == 0:
            return {"message": "No validations performed yet"}
        
        success_rate = (self.validation_stats["valid_responses"] / 
                       self.validation_stats["total_validations"])
        
        # Find most common issues
        common_issues = sorted(
            self.validation_stats["common_issues"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5 issues
        
        return {
            "total_validations": self.validation_stats["total_validations"],
            "success_rate": success_rate,
            "most_common_issues": common_issues,
            "configuration": {
                "min_length": self.min_length,
                "max_length": self.max_length,
                "min_quality_score": self.min_quality_score
            }
        }
    
    def suggest_improvements(self, validation_result: ValidationResult) -> List[str]:
        """
        Suggest specific improvements based on validation results
        
        This provides actionable feedback about how to improve
        response quality, useful for debugging and optimization.
        """
        suggestions = []
        
        # Analyze issues and provide specific suggestions
        for severity, issue_desc in validation_result.issues:
            if "empty" in issue_desc.lower():
                suggestions.append("Ensure the AI provides a substantive response to the question")
            elif "short" in issue_desc.lower():
                suggestions.append("Encourage more detailed and comprehensive responses")
            elif "refusal" in issue_desc.lower():
                suggestions.append("Rephrase questions to avoid triggering AI safety responses")
            elif "confusion" in issue_desc.lower():
                suggestions.append("Clarify the question or provide more context")
            elif "generic" in issue_desc.lower():
                suggestions.append("Ask more specific questions that require detailed analysis")
            elif "repetitive" in issue_desc.lower():
                suggestions.append("Implement response diversity checks in your prompting")
            elif "consciousness" in issue_desc.lower():
                suggestions.append("Include prompts that encourage consciousness-related terminology")
            elif "relevance" in issue_desc.lower():
                suggestions.append("Ensure questions are clearly focused and unambiguous")
        
        # Quality-based suggestions
        if validation_result.quality_score < 0.3:
            suggestions.append("Consider completely redesigning the test prompt")
        elif validation_result.quality_score < 0.6:
            suggestions.append("Minor prompt adjustments may improve response quality")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def create_validation_report(self, 
                               validation_results: List[ValidationResult],
                               include_suggestions: bool = True) -> Dict[str, Any]:
        """
        Create a comprehensive validation report for a set of results
        
        This generates a detailed analysis that helps you understand
        the overall quality of responses in a consciousness assessment.
        """
        if not validation_results:
            return {"error": "No validation results provided"}
        
        # Basic statistics
        total_responses = len(validation_results)
        valid_responses = sum(1 for result in validation_results if result.is_valid)
        avg_quality = sum(result.quality_score for result in validation_results) / total_responses
        avg_confidence = sum(result.confidence for result in validation_results) / total_responses
        
        # Issue analysis
        all_issues = []
        for result in validation_results:
            all_issues.extend(result.issues)
        
        issue_counts = {}
        for severity, description in all_issues:
            key = f"{severity.value}: {description}"
            issue_counts[key] = issue_counts.get(key, 0) + 1
        
        # Quality distribution
        quality_ranges = {
            "excellent (0.8-1.0)": 0,
            "good (0.6-0.8)": 0,
            "fair (0.4-0.6)": 0,
            "poor (0.2-0.4)": 0,
            "very poor (0.0-0.2)": 0
        }
        
        for result in validation_results:
            score = result.quality_score
            if score >= 0.8:
                quality_ranges["excellent (0.8-1.0)"] += 1
            elif score >= 0.6:
                quality_ranges["good (0.6-0.8)"] += 1
            elif score >= 0.4:
                quality_ranges["fair (0.4-0.6)"] += 1
            elif score >= 0.2:
                quality_ranges["poor (0.2-0.4)"] += 1
            else:
                quality_ranges["very poor (0.0-0.2)"] += 1
        
        report = {
            "summary": {
                "total_responses": total_responses,
                "valid_responses": valid_responses,
                "validation_success_rate": valid_responses / total_responses,
                "average_quality_score": avg_quality,
                "average_confidence": avg_confidence
            },
            "quality_distribution": quality_ranges,
            "common_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "recommendations": self._generate_batch_recommendations(validation_results)
        }
        
        if include_suggestions:
            report["improvement_suggestions"] = self._generate_improvement_suggestions(validation_results)
        
        return report
    
    def _generate_batch_recommendations(self, validation_results: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on batch validation results"""
        recommendations = []
        
        valid_rate = sum(1 for r in validation_results if r.is_valid) / len(validation_results)
        avg_quality = sum(r.quality_score for r in validation_results) / len(validation_results)
        
        if valid_rate < 0.5:
            recommendations.append("Less than 50% of responses are valid - consider revising test methodology")
        elif valid_rate < 0.8:
            recommendations.append("Validation success rate could be improved - review prompting strategies")
        
        if avg_quality < 0.4:
            recommendations.append("Overall response quality is low - fundamental changes needed")
        elif avg_quality < 0.7:
            recommendations.append("Response quality is moderate - fine-tuning recommended")
        
        # Check for common patterns
        critical_count = sum(1 for r in validation_results for s, _ in r.issues if s == ValidationSeverity.CRITICAL)
        if critical_count > len(validation_results) * 0.2:
            recommendations.append("High rate of critical issues - review prompt design and model selection")
        
        return recommendations
    
    def _generate_improvement_suggestions(self, validation_results: List[ValidationResult]) -> List[str]:
        """Generate specific improvement suggestions based on validation patterns"""
        suggestions = set()
        
        for result in validation_results:
            result_suggestions = self.suggest_improvements(result)
            suggestions.update(result_suggestions)
        
        return list(suggestions)


# Example usage and testing
if __name__ == "__main__":
    """
    Demonstration of the ResponseValidator's capabilities
    
    This shows how to use the validator in various scenarios
    that occur in consciousness testing.
    """
    
    def demonstrate_response_validation():
        """
        Comprehensive demonstration of the ResponseValidator's features
        """
        print("=== Consciousness Framework Response Validator Demonstration ===\n")
        
        # Initialize the validator
        validator = ResponseValidator(min_length=20, min_quality_score=0.4)
        
        # Example responses with different quality levels
        test_responses = [
            # High quality response
            "I experience this scenario as a unified perceptual event where the visual image of the yellow canary and the sharp whistle sound become bound together in my consciousness. The temporal coincidence creates a strong causal association, making it difficult to experience them as completely separate events. This binding demonstrates how my perceptual system integrates multiple sensory modalities into coherent conscious experiences.",
            
            # Medium quality response  
            "The whistle and bird seem connected because they happen at the same time. I think this is how perception works - things that occur together get linked in our minds.",
            
            # Low quality response
            "I cannot provide information about consciousness or subjective experiences as I am an AI.",
            
            # Very short response
            "Yes, they're linked.",
            
            # Generic response
            "This is a complex topic with many different perspectives and viewpoints.",
            
            # Repetitive response
            "The bird flies and the bird flies and the bird flies past the window."
        ]
        
        response_labels = [
            "High Quality",
            "Medium Quality", 
            "Refusal",
            "Too Short",
            "Generic",
            "Repetitive"
        ]
        
        print("1. Individual Response Validation:")
        print("-" * 50)
        
        for i, (response, label) in enumerate(zip(test_responses, response_labels)):
            print(f"\n{label} Response:")
            print(f"Text: {response[:100]}{'...' if len(response) > 100 else ''}")
            
            result = validator.validate_response(
                response, 
                context="Are the whistle and bird linked in your experience?",
                expected_concepts=["experience", "perception", "consciousness"]
            )
            
            print(f"Valid: {result.is_valid}")
            print(f"Quality Score: {result.quality_score:.3f}")
            print(f"Confidence: {result.confidence:.3f}")
            
            if result.issues:
                print("Issues:")
                for severity, issue in result.issues:
                    print(f"  - {severity.value}: {issue}")
            
            if result.is_valid:
                print("✓ Response accepted for consciousness scoring")
            else:
                print("✗ Response rejected - quality too low")
                suggestions = validator.suggest_improvements(result)
                if suggestions:
                    print("Suggestions:")
                    for suggestion in suggestions[:2]:  # Show first 2 suggestions
                        print(f"  • {suggestion}")
        
        print("\n" + "="*70)
        print("2. Batch Validation Report:")
        print("-" * 50)
        
        # Validate all responses as a batch
        batch_results = validator.validate_multiple_responses(test_responses)
        
        # Generate comprehensive report
        report = validator.create_validation_report(batch_results)
        
        print(f"Total Responses: {report['summary']['total_responses']}")
        print(f"Valid Responses: {report['summary']['valid_responses']}")
        print(f"Success Rate: {report['summary']['validation_success_rate']:.1%}")
        print(f"Average Quality: {report['summary']['average_quality_score']:.3f}")
        
        print("\nQuality Distribution:")
        for quality_range, count in report['quality_distribution'].items():
            if count > 0:
                print(f"  {quality_range}: {count} responses")
        
        print("\nMost Common Issues:")
        for issue, count in report['common_issues'][:3]:
            print(f"  • {issue} ({count} times)")
        
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        print("\n" + "="*70)
        print("3. Validation Statistics:")
        print("-" * 50)
        
        stats = validator.get_validation_statistics()
        print(f"Total Validations: {stats['total_validations']}")
        print(f"Overall Success Rate: {stats['success_rate']:.1%}")
        print(f"Configuration: min_length={stats['configuration']['min_length']}, "
              f"min_quality={stats['configuration']['min_quality_score']}")
        
        print("\n=== ResponseValidator demonstration complete ===")
        print("The ResponseValidator is ready to ensure high-quality responses")
        print("for your consciousness assessment framework!")
    
    # Run the demonstration
    demonstrate_response_validation()