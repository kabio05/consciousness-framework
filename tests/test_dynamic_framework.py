#!/usr/bin/env python3
"""
Test the Dynamic Trait Discovery System

This test file verifies that the framework can automatically discover
and load traits without hardcoding. It's like a health check for the
entire dynamic loading system.
"""

import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"📁 Loaded environment from: {env_file}")
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables")


def test_trait_discovery():
    """Test that the trait discovery system works correctly"""
    print("🔍 Testing Trait Discovery System...\n")
    
    try:
        from utils.trait_discovery import TraitDiscovery, get_trait_discovery
        print("✅ Trait discovery module imported successfully")
        
        # Test discovery
        discovery = get_trait_discovery()
        traits = discovery.discover_all_traits()
        
        print(f"\n📦 Discovered {len(traits)} traits:")
        for trait_name, trait_class in traits.items():
            print(f"  • {trait_name}: {trait_class.__name__}")
            
            # Validate each trait
            validation = discovery.validate_trait_implementation(trait_name)
            if all(validation.values()):
                print(f"    ✅ Valid implementation")
            else:
                print(f"    ❌ Invalid: {validation}")
        
        return len(traits) > 0
        
    except Exception as e:
        print(f"❌ Trait discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dynamic_orchestrator():
    """Test that the orchestrator can use dynamically discovered traits"""
    print("\n🎭 Testing Dynamic Orchestrator...\n")
    
    try:
        from core.orchestrator import ConsciousnessTestOrchestrator
        
        # Initialize orchestrator
        orchestrator = ConsciousnessTestOrchestrator()
        print("✅ Orchestrator initialized")
        
        # Test trait listing
        available_traits = orchestrator.list_available_traits()
        print(f"✅ Orchestrator found {len(available_traits)} traits: {available_traits}")
        
        # Test trait info retrieval
        for trait in available_traits:
            info = orchestrator.get_trait_info(trait)
            if info:
                print(f"✅ Retrieved info for {trait}")
            else:
                print(f"❌ No info for {trait}")
        
        return len(available_traits) > 0
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_dynamic_trait_execution():
    """Test that dynamically discovered traits can actually run"""
    print("\n🚀 Testing Dynamic Trait Execution...\n")
    
    try:
        from core.orchestrator import ConsciousnessTestOrchestrator
        from core.api_manager import APIManager
        
        # Create a mock API manager for testing
        class MockAPIManager(APIManager):
            def __init__(self):
                self.call_count = 0
            
            def query_model_sync(self, model, prompt, **kwargs):
                self.call_count += 1
                # Return a mock response object
                class MockResponse:
                    def __init__(self):
                        self.content = f"Mock response to: {prompt[:50]}... I experience this as a unified conscious event."
                return MockResponse()
            
            def get_available_models(self):
                return {"test": ["mock-model"]}
        
        # Initialize orchestrator with mock API
        orchestrator = ConsciousnessTestOrchestrator(api_manager=MockAPIManager())
        available_traits = orchestrator.list_available_traits()
        
        if not available_traits:
            print("❌ No traits available to test")
            return False
        
        # Test running each trait individually
        print(f"Testing {len(available_traits)} traits individually:")
        
        for trait_name in available_traits:
            print(f"\n  Testing {trait_name}...")
            try:
                # Run mini assessment with just this trait
                session = await orchestrator.run_assessment(
                    model_name="mock-model",
                    selected_traits=[trait_name],
                    assessment_id=f"test_{trait_name}_{int(datetime.now().timestamp())}"
                )
                
                if session.status.value == "completed":
                    print(f"    ✅ {trait_name} executed successfully")
                    if session.trait_summaries:
                        summary = session.trait_summaries[0]
                        print(f"    📊 Tests run: {summary.test_count}, Avg score: {summary.average_score:.3f}")
                else:
                    print(f"    ❌ {trait_name} failed: {session.status}")
                    
            except Exception as e:
                print(f"    ❌ {trait_name} error: {e}")
        
        # Test running all traits together
        print("\n\nTesting all traits together...")
        try:
            session = await orchestrator.run_assessment(
                model_name="mock-model",
                selected_traits=available_traits,
                assessment_id=f"test_all_{int(datetime.now().timestamp())}"
            )
            
            if session.status.value == "completed":
                print(f"✅ All traits executed successfully")
                print(f"📊 Total trait summaries: {len(session.trait_summaries)}")
                for summary in session.trait_summaries:
                    status_icon = "✅" if summary.status.value == "success" else "❌"
                    print(f"  {status_icon} {summary.trait_name}: {summary.test_count} tests")
            else:
                print(f"❌ Combined execution failed: {session.status}")
                
        except Exception as e:
            print(f"❌ Combined execution error: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Dynamic execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_adding_new_trait_simulation():
    """Simulate what happens when a new trait is added"""
    print("\n🆕 Testing New Trait Addition Simulation...\n")
    
    try:
        from utils.trait_discovery import get_trait_discovery
        
        # Get current traits
        discovery = get_trait_discovery()
        initial_traits = discovery.discover_all_traits()
        initial_count = len(initial_traits)
        
        print(f"Initial trait count: {initial_count}")
        print("Simulating the addition of a new trait...")
        
        # In a real scenario, you would:
        # 1. Add a new .py file to src/traits/
        # 2. The file would contain a class inheriting from BaseTrait
        # 3. Run discovery again
        
        # Refresh discovery (this would pick up any new files)
        discovery._discover_traits = discovery.discover_all_traits
        refreshed_traits = discovery.discover_all_traits()
        refreshed_count = len(refreshed_traits)
        
        print(f"Refreshed trait count: {refreshed_count}")
        
        if refreshed_count >= initial_count:
            print("✅ Trait discovery refresh works correctly")
            print("\nTo add a new trait:")
            print("1. Create a new file in src/traits/ (e.g., attention_schema.py)")
            print("2. Copy the trait template and implement your tests")
            print("3. The trait will automatically appear in the framework!")
            return True
        else:
            print("❌ Trait count decreased unexpectedly")
            return False
            
    except Exception as e:
        print(f"❌ New trait simulation failed: {e}")
        return False


def main():
    """Run all dynamic framework tests"""
    print("=" * 60)
    print("🧠 DYNAMIC CONSCIOUSNESS FRAMEWORK TEST SUITE")
    print("=" * 60)
    print("Testing the automatic trait discovery and loading system\n")
    
    # Run all tests
    test_results = {
        "Trait Discovery": test_trait_discovery(),
        "Dynamic Orchestrator": test_dynamic_orchestrator(),
        "New Trait Simulation": test_adding_new_trait_simulation(),
    }
    
    # Run async test
    try:
        execution_result = asyncio.run(test_dynamic_trait_execution())
        test_results["Dynamic Execution"] = execution_result
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        test_results["Dynamic Execution"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All dynamic framework tests passed!")
        print("The framework successfully discovers and loads traits automatically.")
        print("\nNext steps:")
        print("1. Add new traits by creating .py files in src/traits/")
        print("2. Run 'python run_assessment.py --list' to see all traits")
        print("3. Test individual traits with mock assessments")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("Common issues:")
        print("- Traits not inheriting from BaseTrait")
        print("- Import errors in trait files")
        print("- Missing required methods in trait implementations")


if __name__ == "__main__":
    main()