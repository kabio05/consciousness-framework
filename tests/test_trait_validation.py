#!/usr/bin/env python3
"""
Rigorous Trait Implementation Validator

This test ensures that all traits follow the required structure and
implement the interface correctly. It catches common implementation errors
before they cause runtime failures.
"""

import sys
import inspect
import traceback
from pathlib import Path
from typing import Dict, List, Any, Type
from dataclasses import dataclass
from enum import Enum

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from traits.base_trait import BaseTrait
from utils.trait_discovery import get_trait_discovery


class ValidationSeverity(Enum):
    ERROR = "error"      # Must fix - trait won't work
    WARNING = "warning"  # Should fix - might cause issues
    INFO = "info"        # Nice to have - best practices


@dataclass
class ValidationIssue:
    severity: ValidationSeverity
    trait_name: str
    issue_type: str
    message: str
    suggestion: str


class TraitImplementationValidator:
    """
    Comprehensive validator for consciousness trait implementations
    
    This ensures that traits not only inherit from BaseTrait but also
    properly implement all required methods with correct signatures
    and return types.
    """
    
    def __init__(self):
        self.discovery = get_trait_discovery()
        self.issues: List[ValidationIssue] = []
    
    def validate_all_traits(self) -> Dict[str, List[ValidationIssue]]:
        """Validate all discovered traits"""
        print("🔍 Validating Consciousness Trait Implementations\n")
        
        traits = self.discovery.discover_all_traits()
        validation_results = {}
        
        for trait_name, trait_class in traits.items():
            print(f"Validating {trait_name}...")
            issues = self.validate_trait(trait_name, trait_class)
            validation_results[trait_name] = issues
            
            if not issues:
                print(f"  ✅ {trait_name} - All checks passed!")
            else:
                for issue in issues:
                    icon = "❌" if issue.severity == ValidationSeverity.ERROR else "⚠️"
                    print(f"  {icon} {issue.severity.value}: {issue.message}")
        
        return validation_results
    
    def validate_trait(self, trait_name: str, trait_class: Type) -> List[ValidationIssue]:
        """Validate a single trait implementation"""
        issues = []
        
        # 1. Check inheritance
        if not issubclass(trait_class, BaseTrait):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                trait_name=trait_name,
                issue_type="inheritance",
                message=f"{trait_class.__name__} does not inherit from BaseTrait",
                suggestion="Make sure your class inherits from BaseTrait: class YourTrait(BaseTrait):"
            ))
            return issues  # Can't continue without proper inheritance
        
        # 2. Check required methods implementation
        issues.extend(self._check_required_methods(trait_name, trait_class))
        
        # 3. Check constructor signature
        issues.extend(self._check_constructor(trait_name, trait_class))
        
        # 4. Test instantiation
        issues.extend(self._check_instantiation(trait_name, trait_class))
        
        # 5. Check method signatures and return types
        issues.extend(self._check_method_signatures(trait_name, trait_class))
        
        # 6. Test method execution
        issues.extend(self._test_method_execution(trait_name, trait_class))
        
        # 7. Check best practices
        issues.extend(self._check_best_practices(trait_name, trait_class))
        
        return issues
    
    def _check_required_methods(self, trait_name: str, trait_class: Type) -> List[ValidationIssue]:
        """Check if required abstract methods are implemented"""
        issues = []
        
        # Get abstract methods from BaseTrait
        abstract_methods = {
            name for name, method in inspect.getmembers(BaseTrait)
            if inspect.isfunction(method) and hasattr(method, '__isabstractmethod__')
        }
        
        # Check each is implemented
        for method_name in abstract_methods:
            if not hasattr(trait_class, method_name):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    trait_name=trait_name,
                    issue_type="missing_method",
                    message=f"Required method '{method_name}' is not implemented",
                    suggestion=f"Add the {method_name} method to your trait class"
                ))
            else:
                method = getattr(trait_class, method_name)
                # Check it's not still abstract
                if hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        trait_name=trait_name,
                        issue_type="abstract_method",
                        message=f"Method '{method_name}' is still abstract",
                        suggestion=f"Provide a concrete implementation of {method_name}"
                    ))
        
        return issues
    
    def _check_constructor(self, trait_name: str, trait_class: Type) -> List[ValidationIssue]:
        """Check constructor accepts api_client parameter"""
        issues = []
        
        try:
            sig = inspect.signature(trait_class.__init__)
            params = list(sig.parameters.keys())
            
            # Should have self and api_client at minimum
            if 'api_client' not in params:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    trait_name=trait_name,
                    issue_type="constructor",
                    message="Constructor must accept 'api_client' parameter",
                    suggestion="Add api_client parameter: def __init__(self, api_client, ...):"
                ))
            
            # Check if api_client is the first parameter after self
            if len(params) > 1 and params[1] != 'api_client':
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    trait_name=trait_name,
                    issue_type="constructor",
                    message="api_client should be the first parameter after self",
                    suggestion="Reorder parameters: def __init__(self, api_client, ...):"
                ))
        
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                trait_name=trait_name,
                issue_type="constructor",
                message=f"Cannot inspect constructor: {e}",
                suggestion="Ensure the trait has a proper __init__ method"
            ))
        
        return issues
    
    def _check_instantiation(self, trait_name: str, trait_class: Type) -> List[ValidationIssue]:
        """Try to instantiate the trait with a mock client"""
        issues = []
        
        class MockAPIClient:
            def query(self, prompt: str) -> str:
                return "Mock response"
        
        try:
            instance = trait_class(MockAPIClient())
            
            # Check instance has required attributes
            if not hasattr(instance, 'api_client'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    trait_name=trait_name,
                    issue_type="instantiation",
                    message="Instance doesn't store api_client",
                    suggestion="Store api_client in __init__: self.api_client = api_client"
                ))
        
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                trait_name=trait_name,
                issue_type="instantiation",
                message=f"Failed to instantiate: {e}",
                suggestion="Check __init__ method for errors"
            ))
        
        return issues
    
    def _check_method_signatures(self, trait_name: str, trait_class: Type) -> List[ValidationIssue]:
        """Check method signatures match expected interface"""
        issues = []
        
        # Check generate_test_suite
        if hasattr(trait_class, 'generate_test_suite'):
            try:
                sig = inspect.signature(trait_class.generate_test_suite)
                params = list(sig.parameters.keys())
                
                # Should only have 'self'
                if len(params) > 1:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        trait_name=trait_name,
                        issue_type="signature",
                        message="generate_test_suite should not take additional parameters",
                        suggestion="Use only 'self' parameter: def generate_test_suite(self) -> Dict[str, Any]:"
                    ))
                
                # Check return type annotation
                if sig.return_annotation == inspect.Signature.empty:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        trait_name=trait_name,
                        issue_type="type_hint",
                        message="generate_test_suite missing return type hint",
                        suggestion="Add type hint: def generate_test_suite(self) -> Dict[str, Any]:"
                    ))
            except:
                pass
        
        # Check evaluate_responses
        if hasattr(trait_class, 'evaluate_responses'):
            try:
                sig = inspect.signature(trait_class.evaluate_responses)
                params = list(sig.parameters.keys())
                
                if 'responses' not in params:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        trait_name=trait_name,
                        issue_type="signature",
                        message="evaluate_responses must accept 'responses' parameter",
                        suggestion="Add responses parameter: def evaluate_responses(self, responses: List[str]) -> Dict[str, float]:"
                    ))
            except:
                pass
        
        return issues
    
    def _test_method_execution(self, trait_name: str, trait_class: Type) -> List[ValidationIssue]:
        """Test that methods execute without errors"""
        issues = []
        
        class MockAPIClient:
            def query(self, prompt: str) -> str:
                return "Mock response for testing"
        
        try:
            instance = trait_class(MockAPIClient())
            
            # Test generate_test_suite
            try:
                test_suite = instance.generate_test_suite()
                
                # Validate return value
                if not isinstance(test_suite, dict):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        trait_name=trait_name,
                        issue_type="return_type",
                        message=f"generate_test_suite returned {type(test_suite).__name__} instead of dict",
                        suggestion="Return a dictionary with test configuration"
                    ))
                elif 'prompts' not in test_suite:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        trait_name=trait_name,
                        issue_type="return_value",
                        message="generate_test_suite dict missing 'prompts' key",
                        suggestion="Include 'prompts' key with list of test prompts"
                    ))
                    
            except Exception as e:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    trait_name=trait_name,
                    issue_type="execution",
                    message=f"generate_test_suite raised exception: {str(e)}",
                    suggestion="Fix the error in generate_test_suite method"
                ))
            
            # Test evaluate_responses
            try:
                test_responses = ["Test response 1", "Test response 2"]
                evaluation = instance.evaluate_responses(test_responses)
                
                # Validate return value
                if not isinstance(evaluation, dict):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        trait_name=trait_name,
                        issue_type="return_type",
                        message=f"evaluate_responses returned {type(evaluation).__name__} instead of dict",
                        suggestion="Return a dictionary with score information"
                    ))
                elif 'score' not in evaluation:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        trait_name=trait_name,
                        issue_type="return_value",
                        message="evaluate_responses dict missing 'score' key",
                        suggestion="Include 'score' key with float value between 0 and 1"
                    ))
                elif not isinstance(evaluation.get('score'), (int, float)):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        trait_name=trait_name,
                        issue_type="return_value",
                        message=f"'score' must be numeric, got {type(evaluation.get('score')).__name__}",
                        suggestion="Ensure score is a float between 0.0 and 1.0"
                    ))
                elif not 0 <= evaluation.get('score', 0) <= 1:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        trait_name=trait_name,
                        issue_type="return_value",
                        message=f"Score {evaluation.get('score')} is outside [0, 1] range",
                        suggestion="Normalize scores to be between 0.0 and 1.0"
                    ))
                    
            except Exception as e:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    trait_name=trait_name,
                    issue_type="execution",
                    message=f"evaluate_responses raised exception: {str(e)}",
                    suggestion="Fix the error in evaluate_responses method"
                ))
        
        except:
            pass  # Already handled in instantiation check
        
        return issues
    
    def _check_best_practices(self, trait_name: str, trait_class: Type) -> List[ValidationIssue]:
        """Check for best practices and common patterns"""
        issues = []
        
        # Check for docstrings
        if not trait_class.__doc__ or len(trait_class.__doc__.strip()) < 20:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                trait_name=trait_name,
                issue_type="documentation",
                message="Trait class lacks comprehensive docstring",
                suggestion="Add a docstring explaining what consciousness aspect this trait tests"
            ))
        
        try:
            # Check for test battery initialization
            if hasattr(trait_class, '__init__'):
                try:
                    init_source = inspect.getsource(trait_class.__init__)
                    if 'test_battery' not in init_source and '_initialize_test_battery' not in init_source:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.INFO,
                            trait_name=trait_name,
                            issue_type="pattern",
                            message="Consider initializing test configurations in __init__",
                            suggestion="Store test configurations for better organization"
                        ))
                except (TypeError, OSError):
                    # Can't get source for dynamically imported classes sometimes
                    pass
            
            # Check for logging
            try:
                source = inspect.getsource(trait_class)
                if 'logger' not in source and 'logging' not in source:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        trait_name=trait_name,
                        issue_type="logging",
                        message="No logging detected",
                        suggestion="Add logging for debugging: logger = logging.getLogger(__name__)"
                    ))
            except (TypeError, OSError):
                # Can't get source, skip this check
                pass
                
        except Exception as e:
            # Log but don't fail on best practices checks
            print(f"  ℹ️  Note: Could not check some best practices due to dynamic loading")
        
        # Check for optional run_comprehensive_assessment
        if hasattr(trait_class, 'run_comprehensive_assessment'):
            try:
                sig = inspect.signature(trait_class.run_comprehensive_assessment)
                if sig.return_annotation == inspect.Signature.empty:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        trait_name=trait_name,
                        issue_type="type_hint",
                        message="run_comprehensive_assessment missing return type hint",
                        suggestion="Add type hint for better code clarity"
                    ))
            except:
                pass
        
        return issues
    
    def generate_report(self, validation_results: Dict[str, List[ValidationIssue]]) -> str:
        """Generate a summary report of all validation issues"""
        report = []
        report.append("=" * 60)
        report.append("TRAIT VALIDATION REPORT")
        report.append("=" * 60)
        
        total_traits = len(validation_results)
        perfect_traits = sum(1 for issues in validation_results.values() if not issues)
        total_errors = sum(1 for issues in validation_results.values() 
                          for issue in issues if issue.severity == ValidationSeverity.ERROR)
        total_warnings = sum(1 for issues in validation_results.values() 
                            for issue in issues if issue.severity == ValidationSeverity.WARNING)
        
        report.append(f"\nSummary:")
        report.append(f"  Total traits validated: {total_traits}")
        report.append(f"  Perfect implementations: {perfect_traits}")
        report.append(f"  Total errors: {total_errors}")
        report.append(f"  Total warnings: {total_warnings}")
        
        if total_errors > 0:
            report.append("\n❌ CRITICAL ERRORS (must fix):")
            for trait_name, issues in validation_results.items():
                errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
                if errors:
                    report.append(f"\n  {trait_name}:")
                    for error in errors:
                        report.append(f"    - {error.message}")
                        report.append(f"      Fix: {error.suggestion}")
        
        if total_warnings > 0:
            report.append("\n⚠️  WARNINGS (should fix):")
            for trait_name, issues in validation_results.items():
                warnings = [i for i in issues if i.severity == ValidationSeverity.WARNING]
                if warnings:
                    report.append(f"\n  {trait_name}:")
                    for warning in warnings:
                        report.append(f"    - {warning.message}")
        
        if perfect_traits > 0:
            report.append("\n✅ PERFECT IMPLEMENTATIONS:")
            for trait_name, issues in validation_results.items():
                if not issues:
                    report.append(f"  - {trait_name}")
        
        return "\n".join(report)


def main():
    """Run the trait validation test"""
    validator = TraitImplementationValidator()
    
    # Validate all traits
    results = validator.validate_all_traits()
    
    # Generate and print report
    print("\n" + validator.generate_report(results))
    
    # Exit with error code if there are errors
    total_errors = sum(1 for issues in results.values() 
                      for issue in issues if issue.severity == ValidationSeverity.ERROR)
    
    if total_errors > 0:
        print(f"\n❌ Validation failed with {total_errors} errors!")
        sys.exit(1)
    else:
        print("\n✅ All traits passed validation!")
        sys.exit(0)


if __name__ == "__main__":
    main()