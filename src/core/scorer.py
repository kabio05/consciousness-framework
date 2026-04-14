from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
from statistics import mean, median, stdev
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoringMethod(Enum):
    """Different methods for calculating composite scores"""
    WEIGHTED_AVERAGE = "weighted_average"
    GEOMETRIC_MEAN = "geometric_mean"
    HARMONIC_MEAN = "harmonic_mean"
    ROOT_MEAN_SQUARE = "root_mean_square"

class NormalizationMethod(Enum):
    """Different methods for normalizing scores"""
    MIN_MAX = "min_max"           # Scale to [0, 1] range
    Z_SCORE = "z_score"           # Standardize to mean=0, std=1
    ROBUST = "robust"             # Use median and IQR for outlier resistance
    SIGMOID = "sigmoid"           # Apply sigmoid transformation

@dataclass
class ScoreStatistics:
    """Statistical summary of scores"""
    mean: float
    median: float
    std_dev: float
    min_score: float
    max_score: float
    confidence_interval: Tuple[float, float]
    outlier_count: int

class Scorer:
    """
    Advanced scoring system for consciousness assessments
    
    The Scorer acts like a sophisticated teacher who not only grades tests
    but also understands how to weight different types of questions,
    handle outliers, and provide statistical confidence in the results.
    
    Think of it as the statistical brain of your consciousness framework
    that ensures fair, reliable, and meaningful scoring across all tests.
    """
    
    def __init__(self, 
                 default_normalization: NormalizationMethod = NormalizationMethod.MIN_MAX,
                 default_scoring: ScoringMethod = ScoringMethod.WEIGHTED_AVERAGE,
                 outlier_threshold: float = 2.0):
        """
        Initialize the Scorer with default methods and parameters
        
        Args:
            default_normalization: Default method for normalizing scores
            default_scoring: Default method for combining multiple scores
            outlier_threshold: Standard deviations beyond which scores are considered outliers
        """
        self.default_normalization = default_normalization
        self.default_scoring = default_scoring
        self.outlier_threshold = outlier_threshold
        
        # Track scoring history for adaptive improvements
        self.scoring_history = []
        
    def normalize_score(self, 
                       raw_score: float, 
                       min_val: float = 0.0, 
                       max_val: float = 1.0,
                       method: Optional[NormalizationMethod] = None) -> float:
        """
        Normalize a single score to a standard range
        
        This is like converting different grading scales (A-F, 0-100, 0-10) 
        into a common scale so we can compare them fairly.
        
        Args:
            raw_score: The original score to normalize
            min_val: Minimum possible value for the score
            max_val: Maximum possible value for the score
            method: Normalization method to use
            
        Returns:
            Normalized score in [0, 1] range
        """
        method = method or self.default_normalization
        
        try:
            if method == NormalizationMethod.MIN_MAX:
                # Simple linear scaling to [0, 1]
                if max_val == min_val:
                    return 0.5  # Handle edge case where min equals max
                normalized = (raw_score - min_val) / (max_val - min_val)
                return max(0.0, min(1.0, normalized))  # Clamp to [0, 1]
                
            elif method == NormalizationMethod.SIGMOID:
                # Apply sigmoid transformation for smooth scaling
                # This naturally maps any real number to [0, 1] range
                return 1 / (1 + math.exp(-raw_score))
                
            else:
                # For other methods, we need a collection of scores
                # Fall back to min-max for single score normalization
                logger.warning(f"Method {method} requires multiple scores, using min-max")
                return self.normalize_score(raw_score, min_val, max_val, NormalizationMethod.MIN_MAX)
                
        except Exception as e:
            logger.error(f"Error normalizing score {raw_score}: {e}")
            return 0.5  # Safe fallback
    
    def normalize_scores(self, 
                        scores: List[float],
                        method: Optional[NormalizationMethod] = None) -> List[float]:
        """
        Normalize a collection of scores using statistical methods
        
        This is like grading on a curve - we look at how all students performed
        and adjust scores relative to the group performance.
        
        Args:
            scores: List of raw scores to normalize
            method: Normalization method to use
            
        Returns:
            List of normalized scores
        """
        if not scores:
            return []
            
        method = method or self.default_normalization
        
        try:
            if method == NormalizationMethod.MIN_MAX:
                min_score = min(scores)
                max_score = max(scores)
                if max_score == min_score:
                    return [0.5] * len(scores)  # All scores are the same
                return [(score - min_score) / (max_score - min_score) for score in scores]
                
            elif method == NormalizationMethod.Z_SCORE:
                # Standardize to mean=0, std=1, then map to [0, 1]
                score_mean = mean(scores)
                score_std = stdev(scores) if len(scores) > 1 else 1.0
                
                if score_std == 0:
                    return [0.5] * len(scores)
                    
                z_scores = [(score - score_mean) / score_std for score in scores]
                # Map z-scores to [0, 1] using sigmoid
                return [1 / (1 + math.exp(-z)) for z in z_scores]
                
            elif method == NormalizationMethod.ROBUST:
                # Use median and IQR for outlier-resistant normalization
                sorted_scores = sorted(scores)
                n = len(sorted_scores)
                
                # Calculate median and quartiles
                median_score = median(scores)
                q1 = sorted_scores[n // 4]
                q3 = sorted_scores[3 * n // 4]
                iqr = q3 - q1
                
                if iqr == 0:
                    return [0.5] * len(scores)
                    
                # Normalize using robust statistics
                robust_scores = [(score - median_score) / iqr for score in scores]
                # Map to [0, 1] using sigmoid
                return [1 / (1 + math.exp(-score)) for score in robust_scores]
                
            elif method == NormalizationMethod.SIGMOID:
                # Apply sigmoid to each score individually
                return [1 / (1 + math.exp(-score)) for score in scores]
                
        except Exception as e:
            logger.error(f"Error normalizing scores: {e}")
            return [0.5] * len(scores)  # Safe fallback
    
    def calculate_weighted_average(self, 
                                  scores: List[float], 
                                  weights: List[float]) -> float:
        """
        Calculate weighted average of scores
        
        This is like calculating a course grade where homework is worth 20%,
        midterm 30%, and final exam 50%. Different components have different importance.
        
        Args:
            scores: List of scores to combine
            weights: List of weights (importance) for each score
            
        Returns:
            Weighted average score
        """
        if not scores or not weights:
            return 0.0
            
        if len(scores) != len(weights):
            logger.warning("Scores and weights length mismatch, truncating to shorter")
            min_len = min(len(scores), len(weights))
            scores = scores[:min_len]
            weights = weights[:min_len]
        
        try:
            # Handle case where all weights are zero
            total_weight = sum(weights)
            if total_weight == 0:
                logger.warning("All weights are zero, using equal weighting")
                weights = [1.0] * len(weights)
                total_weight = len(weights)
            
            # Calculate weighted sum
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            return weighted_sum / total_weight
            
        except Exception as e:
            logger.error(f"Error calculating weighted average: {e}")
            return mean(scores) if scores else 0.0
    
    def calculate_composite_score(self, 
                                 scores: List[float],
                                 weights: Optional[List[float]] = None,
                                 method: Optional[ScoringMethod] = None) -> float:
        """
        Calculate composite score using various mathematical methods
        
        Different methods emphasize different aspects:
        - Weighted average: Most common, linear combination
        - Geometric mean: Penalizes low scores more heavily
        - Harmonic mean: Emphasizes balance across all scores
        - Root mean square: Emphasizes higher scores
        
        Args:
            scores: List of scores to combine
            weights: Optional weights for each score
            method: Method to use for combination
            
        Returns:
            Composite score
        """
        if not scores:
            return 0.0
            
        method = method or self.default_scoring
        weights = weights or [1.0] * len(scores)
        
        try:
            if method == ScoringMethod.WEIGHTED_AVERAGE:
                return self.calculate_weighted_average(scores, weights)
                
            elif method == ScoringMethod.GEOMETRIC_MEAN:
                # Geometric mean: (x1 * x2 * ... * xn)^(1/n)
                # Add small epsilon to prevent log(0) issues
                epsilon = 1e-10
                safe_scores = [max(score, epsilon) for score in scores]
                
                if weights:
                    # Weighted geometric mean
                    total_weight = sum(weights)
                    weighted_product = 1.0
                    for score, weight in zip(safe_scores, weights):
                        weighted_product *= score ** (weight / total_weight)
                    return weighted_product
                else:
                    # Simple geometric mean
                    product = 1.0
                    for score in safe_scores:
                        product *= score
                    return product ** (1.0 / len(scores))
                    
            elif method == ScoringMethod.HARMONIC_MEAN:
                # Harmonic mean: n / (1/x1 + 1/x2 + ... + 1/xn)
                epsilon = 1e-10
                safe_scores = [max(score, epsilon) for score in scores]
                
                if weights:
                    # Weighted harmonic mean
                    total_weight = sum(weights)
                    weighted_reciprocal_sum = sum(weight / score for score, weight in zip(safe_scores, weights))
                    return total_weight / weighted_reciprocal_sum
                else:
                    # Simple harmonic mean
                    reciprocal_sum = sum(1.0 / score for score in safe_scores)
                    return len(scores) / reciprocal_sum
                    
            elif method == ScoringMethod.ROOT_MEAN_SQUARE:
                # Root mean square: sqrt((x1^2 + x2^2 + ... + xn^2) / n)
                if weights:
                    # Weighted RMS
                    total_weight = sum(weights)
                    weighted_sum_squares = sum(weight * score * score for score, weight in zip(scores, weights))
                    return math.sqrt(weighted_sum_squares / total_weight)
                else:
                    # Simple RMS
                    sum_squares = sum(score * score for score in scores)
                    return math.sqrt(sum_squares / len(scores))
                    
        except Exception as e:
            logger.error(f"Error calculating composite score with method {method}: {e}")
            return mean(scores)  # Fallback to simple average
    
    def detect_outliers(self, scores: List[float]) -> List[int]:
        """
        Detect outlier scores using statistical methods
        
        Outliers are scores that are unusually high or low compared to the rest.
        They might indicate errors in testing or genuinely exceptional performance.
        
        Args:
            scores: List of scores to analyze
            
        Returns:
            List of indices where outliers were detected
        """
        if len(scores) < 3:
            return []  # Need at least 3 scores for meaningful outlier detection
            
        try:
            score_mean = mean(scores)
            score_std = stdev(scores)
            
            outlier_indices = []
            
            for i, score in enumerate(scores):
                # Calculate z-score (how many standard deviations from mean)
                z_score = abs(score - score_mean) / score_std if score_std > 0 else 0
                
                # Mark as outlier if beyond threshold
                if z_score > self.outlier_threshold:
                    outlier_indices.append(i)
            
            return outlier_indices
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            return []
    
    def calculate_score_statistics(self, scores: List[float]) -> ScoreStatistics:
        """
        Calculate comprehensive statistics for a set of scores
        
        This gives us a complete picture of how the AI performed across all tests,
        including measures of central tendency, variability, and confidence.
        Think of it as generating a detailed report card with context.
        
        Args:
            scores: List of scores to analyze
            
        Returns:
            ScoreStatistics object with comprehensive metrics
        """
        if not scores:
            return ScoreStatistics(0, 0, 0, 0, 0, (0, 0), 0)
        
        try:
            # Basic descriptive statistics
            score_mean = mean(scores)
            score_median = median(scores)
            score_std = stdev(scores) if len(scores) > 1 else 0.0
            score_min = min(scores)
            score_max = max(scores)
            
            # Calculate confidence interval (95% by default)
            confidence_level = 0.95
            alpha = 1 - confidence_level
            n = len(scores)
            
            if n > 1 and score_std > 0:
                # Use t-distribution for small samples, normal for large samples
                if n < 30:
                    # For small samples, we'd need scipy.stats for exact t-values
                    # Using approximation: t ≈ 2.0 for 95% confidence with small n
                    t_value = 2.0
                else:
                    # For large samples, use normal distribution (z ≈ 1.96 for 95%)
                    t_value = 1.96
                
                margin_of_error = t_value * (score_std / math.sqrt(n))
                confidence_interval = (
                    max(0.0, score_mean - margin_of_error),
                    min(1.0, score_mean + margin_of_error)
                )
            else:
                # Can't calculate meaningful confidence interval
                confidence_interval = (score_mean, score_mean)
            
            # Count outliers
            outlier_indices = self.detect_outliers(scores)
            outlier_count = len(outlier_indices)
            
            return ScoreStatistics(
                mean=score_mean,
                median=score_median,
                std_dev=score_std,
                min_score=score_min,
                max_score=score_max,
                confidence_interval=confidence_interval,
                outlier_count=outlier_count
            )
            
        except Exception as e:
            logger.error(f"Error calculating score statistics: {e}")
            return ScoreStatistics(0, 0, 0, 0, 0, (0, 0), 0)
    
    def score_consciousness_trait(self, 
                                 trait_results: List[Any],
                                 integration_weight: float = 0.6,
                                 organization_weight: float = 0.4) -> Dict[str, float]:
        """
        Calculate comprehensive scores for a consciousness trait
        
        This method takes raw trait test results and produces a complete
        scoring analysis. It's like having an expert psychologist review
        all the test results and provide a detailed assessment.
        
        Args:
            trait_results: List of test results from a consciousness trait
            integration_weight: How much to weight integration scores
            organization_weight: How much to weight organization scores
            
        Returns:
            Dictionary with various score metrics
        """
        if not trait_results:
            return {
                'trait_score': 0.0,
                'integration_score': 0.0,
                'organization_score': 0.0,
                'consistency_score': 0.0,
                'confidence_score': 0.0
            }
        
        try:
            # Extract individual scores from results
            integration_scores = []
            organization_scores = []
            
            for result in trait_results:
                if hasattr(result, 'integration_score') and hasattr(result, 'organization_score'):
                    integration_scores.append(result.integration_score)
                    organization_scores.append(result.organization_score)
            
            if not integration_scores or not organization_scores:
                logger.warning("No valid scores found in trait results")
                return {
                    'trait_score': 0.0,
                    'integration_score': 0.0,
                    'organization_score': 0.0,
                    'consistency_score': 0.0,
                    'confidence_score': 0.0
                }
            
            # Calculate average scores for each component
            avg_integration = mean(integration_scores)
            avg_organization = mean(organization_scores)
            
            # Calculate overall trait score using weighted combination
            trait_score = self.calculate_weighted_average(
                [avg_integration, avg_organization],
                [integration_weight, organization_weight]
            )
            
            # Calculate consistency score (inverse of variability)
            # More consistent performance across tests indicates more reliable consciousness
            all_scores = integration_scores + organization_scores
            consistency_score = self._calculate_consistency_score(all_scores)
            
            # Calculate confidence score based on statistical reliability
            confidence_score = self._calculate_confidence_score(all_scores)
            
            return {
                'trait_score': trait_score,
                'integration_score': avg_integration,
                'organization_score': avg_organization,
                'consistency_score': consistency_score,
                'confidence_score': confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error scoring consciousness trait: {e}")
            return {
                'trait_score': 0.0,
                'integration_score': 0.0,
                'organization_score': 0.0,
                'consistency_score': 0.0,
                'confidence_score': 0.0
            }
    
    def _calculate_consistency_score(self, scores: List[float]) -> float:
        """
        Calculate how consistent the scores are (low variability = high consistency)
        
        Consistency is important because a truly conscious system should perform
        similarly across different tests of the same trait. High variability
        might indicate randomness rather than genuine understanding.
        """
        if len(scores) < 2:
            return 1.0  # Perfect consistency if only one score
        
        try:
            score_std = stdev(scores)
            score_mean = mean(scores)
            
            # Calculate coefficient of variation (relative variability)
            if score_mean > 0:
                cv = score_std / score_mean
                # Convert to consistency score (lower CV = higher consistency)
                consistency = 1.0 / (1.0 + cv)
            else:
                consistency = 1.0 if score_std == 0 else 0.0
            
            return consistency
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {e}")
            return 0.5  # Neutral consistency
    
    def _calculate_confidence_score(self, scores: List[float]) -> float:
        """
        Calculate statistical confidence in the results
        
        This tells us how reliable our assessment is. More tests and
        tighter confidence intervals lead to higher confidence scores.
        """
        if not scores:
            return 0.0
        
        try:
            n = len(scores)
            
            # More samples generally mean higher confidence
            sample_confidence = min(1.0, n / 20.0)  # Asymptotic approach to 1.0
            
            # Tighter confidence intervals mean higher confidence
            stats = self.calculate_score_statistics(scores)
            ci_width = stats.confidence_interval[1] - stats.confidence_interval[0]
            interval_confidence = max(0.0, 1.0 - ci_width)
            
            # Combine sample size and interval width for overall confidence
            overall_confidence = (sample_confidence + interval_confidence) / 2.0
            
            return overall_confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5  # Neutral confidence


# Example usage and testing functions
if __name__ == "__main__":
    """
    Demonstration of the Scorer's capabilities
    
    This section shows how to use the Scorer in various scenarios
    that might occur in your consciousness testing framework.
    """
    
    def demonstrate_scorer_capabilities():
        """
        Comprehensive demonstration of the Scorer's features
        """
        print("=== Consciousness Framework Scorer Demonstration ===\n")
        
        # Initialize the scorer
        scorer = Scorer()
        
        # Example 1: Basic score normalization
        print("1. Score Normalization Examples:")
        raw_scores = [0.2, 0.7, 0.9, 0.1, 0.8, 0.6]
        normalized = scorer.normalize_scores(raw_scores, NormalizationMethod.MIN_MAX)
        print(f"Raw scores: {[f'{s:.2f}' for s in raw_scores]}")
        print(f"Normalized: {[f'{s:.2f}' for s in normalized]}")
        
        # Example 2: Weighted averaging for consciousness traits
        print("\n2. Weighted Consciousness Scoring:")
        integration_scores = [0.8, 0.7, 0.9]
        organization_scores = [0.6, 0.8, 0.7]
        
        trait_score = scorer.calculate_weighted_average(
            [mean(integration_scores), mean(organization_scores)],
            [0.6, 0.4]  # 60% integration, 40% organization
        )
        print(f"Integration scores: {integration_scores} (avg: {mean(integration_scores):.3f})")
        print(f"Organization scores: {organization_scores} (avg: {mean(organization_scores):.3f})")
        print(f"Weighted trait score: {trait_score:.3f}")
        
        # Example 3: Statistical analysis
        print("\n3. Statistical Analysis:")
        test_scores = [0.75, 0.82, 0.68, 0.91, 0.77, 0.85, 0.73, 0.89]
        stats = scorer.calculate_score_statistics(test_scores)
        print(f"Test scores: {[f'{s:.2f}' for s in test_scores]}")
        print(f"Mean: {stats.mean:.3f}, Median: {stats.median:.3f}")
        print(f"Std Dev: {stats.std_dev:.3f}")
        print(f"95% Confidence Interval: ({stats.confidence_interval[0]:.3f}, {stats.confidence_interval[1]:.3f})")
        print(f"Outliers detected: {stats.outlier_count}")
        
        # Example 4: Different scoring methods
        print("\n4. Comparison of Scoring Methods:")
        component_scores = [0.8, 0.6, 0.9, 0.7]
        weights = [1.0, 1.2, 0.8, 1.0]
        
        methods = [
            ScoringMethod.WEIGHTED_AVERAGE,
            ScoringMethod.GEOMETRIC_MEAN,
            ScoringMethod.HARMONIC_MEAN,
            ScoringMethod.ROOT_MEAN_SQUARE
        ]
        
        print(f"Component scores: {component_scores}")
        print(f"Weights: {weights}")
        for method in methods:
            score = scorer.calculate_composite_score(component_scores, weights, method)
            print(f"{method.value}: {score:.3f}")
        
        print("\n=== Scorer demonstration complete ===")
        print("The Scorer is ready to provide sophisticated statistical analysis")
        print("for your consciousness assessment framework!")
    
    # Run the demonstration
    demonstrate_scorer_capabilities()