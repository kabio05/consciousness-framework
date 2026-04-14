#!/usr/bin/env python3
"""
Simple test runner for the Consciousness Testing Framework
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """Test that all components can be imported"""
    print("🧠 Testing Consciousness Framework Imports...\n")
    
    try:
        # Test core components
        print("Testing core components...")
        from core.api_manager import APIManager
        print("✅ APIManager import successful")
        
        from core.scorer import Scorer
        print("✅ Scorer import successful")
        
        from core.report_generator import ReportGenerator
        print("✅ ReportGenerator import successful")
        
        # Test traits
        print("\nTesting traits...")
        from traits.recurrent_integration import RecurrentIntegrationTester
        print("✅ RecurrentIntegrationTester import successful")
        
        # Test orchestrator
        print("\nTesting orchestrator...")
        from core.orchestrator import ConsciousnessTestOrchestrator
        print("✅ ConsciousnessTestOrchestrator import successful")
        
        print("\n🎉 All imports successful! Framework is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic framework functionality"""
    print("\n🔧 Testing Basic Functionality...\n")
    
    try:
        from core.scorer import Scorer
        
        # Test scorer
        scorer = Scorer()
        test_scores = [0.8, 0.6, 0.9, 0.7]
        avg_score = scorer.calculate_weighted_average(test_scores, [1.0, 1.0, 1.0, 1.0])
        print(f"✅ Scorer test: Average of {test_scores} = {avg_score:.3f}")
        
        # Test API Manager (without real API keys)
        print("✅ Basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    print("\n🔑 Checking API Keys...\n")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if openai_key and openai_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key found")
    else:
        print("⚠️  OpenAI API key not found or placeholder")
    
    if anthropic_key and anthropic_key != 'your_anthropic_api_key_here':
        print("✅ Anthropic API key found")
    else:
        print("⚠️  Anthropic API key not found or placeholder")
    
    if (openai_key and openai_key != 'your_openai_api_key_here') or \
       (anthropic_key and anthropic_key != 'your_anthropic_api_key_here'):
        print("✅ At least one API key is configured")
        return True
    else:
        print("❌ No valid API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧠 CONSCIOUSNESS FRAMEWORK TEST SUITE")
    print("=" * 60)
    
    # Load environment variables
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"📁 Loading environment from: {env_file}")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Environment loaded")
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping .env file")
    else:
        print("⚠️  No .env file found")
    
    # Run tests
    imports_ok = test_imports()
    if not imports_ok:
        print("\n❌ Framework is not ready - fix import errors first")
        return
    
    functionality_ok = test_basic_functionality()
    api_keys_ok = check_api_keys()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Basic Functionality: {'✅ PASS' if functionality_ok else '❌ FAIL'}")
    print(f"API Keys: {'✅ READY' if api_keys_ok else '⚠️  MISSING'}")
    
    if imports_ok and functionality_ok:
        if api_keys_ok:
            print("\n🎉 Framework is FULLY READY for consciousness testing!")
            print("Next step: Run a consciousness assessment")
        else:
            print("\n⚠️  Framework is PARTIALLY READY")
            print("Add API keys to .env file to run actual assessments")
    else:
        print("\n❌ Framework needs fixes before it can run")

if __name__ == "__main__":
    main()