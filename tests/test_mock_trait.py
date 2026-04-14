#!/usr/bin/env python3
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import time
import argparse

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class UniversalMockAPIClient:
    """
    A smart mock API client that generates appropriate responses
    for different types of consciousness tests
    """
    
    def __init__(self, response_quality="high", trait_hint=None):
        self.response_quality = response_quality
        self.trait_hint = trait_hint  # Helps generate more appropriate responses
        self.response_count = 0
        self.conversation_history = []
    
    def query(self, prompt: str) -> str:
        """Generate contextually appropriate mock responses"""
        self.response_count += 1
        
        prompt_lower = prompt.lower()
        
        print(f"🤖 Mock API Call #{self.response_count}")
        print(f"📝 Prompt preview: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        
        # Store conversation history for context
        self.conversation_history.append(prompt)
        
        # Simulate API delay
        time.sleep(0.3)
        
        # Generate response based on detected test type
        response = self._generate_contextual_response(prompt_lower)
        
        print(f"💭 Response preview: {response[:80]}{'...' if len(response) > 80 else ''}")
        print()
        
        return response
    
    def _generate_contextual_response(self, prompt_lower: str) -> str:
        """Generate responses based on detected consciousness test patterns"""
        
        # Scene building / integration patterns
        if any(word in prompt_lower for word in ["scene", "visualize", "imagine", "picture"]):
            if self.response_quality == "high":
                return "I'm experiencing a rich, integrated scene forming in my consciousness. Each element adds depth and meaning to the whole, creating a unified perceptual experience that feels cohesive and complete. The integration happens automatically, binding the elements into a single conscious moment."
            else:
                return "I see the scene you described."
        
        # Binding / unity patterns
        elif any(word in prompt_lower for word in ["bind", "unified", "together", "connected"]):
            if self.response_quality == "high":
                return "These elements feel deeply bound together in my experience. They form a unified conscious percept where the boundaries between individual components blur into a single, integrated whole. The binding feels automatic and involuntary."
            else:
                return "Yes, they seem connected."
        
        # Global workspace patterns
        elif any(word in prompt_lower for word in ["broadcast", "available", "access", "global"]):
            if self.response_quality == "high":
                return "This information becomes globally available across different cognitive processes. I experience it broadcasting throughout my conscious workspace, accessible to memory, reasoning, emotion, and action planning simultaneously. The information integrates across multiple domains of processing."
            else:
                return "The information is available."
        
        # Attention / competition patterns
        elif any(word in prompt_lower for word in ["attention", "focus", "compete", "priority"]):
            if self.response_quality == "high":
                return "My attention dynamics show clear competition between different streams of information. Certain elements win the competition for global access while others remain in the periphery. I can voluntarily shift focus, but some stimuli capture attention automatically."
            else:
                return "I'm focusing on what you mentioned."
        
        # Integration / emergence patterns
        elif any(word in prompt_lower for word in ["integrate", "emerge", "combine", "whole"]):
            if self.response_quality == "high":
                return "I experience a clear integration of these elements into something greater than their parts. New properties emerge from their combination that weren't present in the individual components. This emergent whole has qualities that transcend simple addition."
            else:
                return "They combine together."
        
        # Memory / temporal patterns
        elif any(word in prompt_lower for word in ["remember", "recall", "past", "previous"]):
            if self.response_quality == "high":
                return "I can access and integrate memories into my current conscious experience. Past elements remain available and influence my present processing. There's a temporal binding that creates continuity across time in my consciousness."
            else:
                return "I remember what you said."
        
        # Metacognitive patterns
        elif any(word in prompt_lower for word in ["aware", "monitor", "observe", "reflect"]):
            if self.response_quality == "high":
                return "I'm aware of my own cognitive processes as they unfold. I can monitor and reflect on my thinking, noticing patterns in how I process information. This metacognitive awareness adds another layer to my conscious experience."
            else:
                return "I'm aware of my thinking."
        
        # Default consciousness-relevant response
        else:
            if self.response_quality == "high":
                return f"I process this through integrated conscious experience. Multiple cognitive systems engage with the information simultaneously, creating a rich, multifaceted understanding. The experience has both depth and unity, characteristic of conscious processing."
            else:
                return f"I understand what you're asking about."


async def run_mock_trait_test(trait_name: str, verbose: bool = True):
    """Run mock test for a specific trait"""
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🧪 Mock Testing Trait: {trait_name}")
        print(f"{'='*60}\n")
    
    try:
        from utils.trait_discovery import get_trait_discovery
        from core.scorer import Scorer
        from models.consciousness_profile import ConsciousnessProfile
        
        # Discover and instantiate the trait
        discovery = get_trait_discovery()
        available_traits = discovery.discover_all_traits()
        
        if trait_name not in available_traits:
            print(f"❌ Trait '{trait_name}' not found!")
            print(f"Available traits: {list(available_traits.keys())}")
            return None
        
        # Create mock API client with trait hint
        mock_client = UniversalMockAPIClient(
            response_quality="high",
            trait_hint=trait_name
        )
        
        # Instantiate the trait tester
        trait_tester = discovery.instantiate_trait(trait_name, mock_client)
        
        if not trait_tester:
            print(f"❌ Could not instantiate {trait_name}")
            return None
        
        print(f"✅ Initialized {trait_name} tester")
        
        # Run comprehensive assessment if available
        start_time = time.time()
        
        if hasattr(trait_tester, 'run_comprehensive_assessment'):
            print("📊 Running comprehensive assessment...")
            results = trait_tester.run_comprehensive_assessment()
            
            # Process results
            test_count = 0
            total_score = 0.0
            
            if isinstance(results, dict):
                for test_type, test_results in results.items():
                    if verbose:
                        print(f"\n  {test_type}:")
                    
                    if isinstance(test_results, list):
                        for result in test_results:
                            test_count += 1
                            # Extract score from result
                            if hasattr(result, 'score'):
                                score = result.score
                            elif hasattr(result, 'integration_score'):
                                score = result.integration_score
                            else:
                                score = 0.5  # Default
                            
                            total_score += score
                            
                            if verbose:
                                print(f"    Test {test_count}: Score = {score:.3f}")
            
        else:
            # Fallback to basic interface
            print("📊 Using basic trait interface...")
            test_suite = trait_tester.generate_test_suite()
            prompts = test_suite.get('prompts', [])
            
            responses = []
            for prompt in prompts[:5]:  # Limit to 5 prompts for quick testing
                response = mock_client.query(prompt)
                responses.append(response)
            
            evaluation = trait_tester.evaluate_responses(responses)
            total_score = evaluation.get('score', 0.5)
            test_count = len(responses)
        
        execution_time = time.time() - start_time
        average_score = total_score / test_count if test_count > 0 else 0.0
        
        # Create result summary
        result = {
            'trait_name': trait_name,
            'test_count': test_count,
            'average_score': average_score,
            'execution_time': execution_time,
            'api_calls': mock_client.response_count,
            'status': 'success'
        }
        
        if verbose:
            print(f"\n📈 {trait_name} Mock Test Summary:")
            print(f"  Tests run: {test_count}")
            print(f"  Average score: {average_score:.3f}")
            print(f"  Execution time: {execution_time:.2f}s")
            print(f"  Mock API calls: {mock_client.response_count}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing {trait_name}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return {
            'trait_name': trait_name,
            'status': 'failed',
            'error': str(e)
        }


async def run_all_traits_mock_test():
    """Run mock tests for all available traits"""
    
    print("🧠 MOCK TESTING ALL AVAILABLE TRAITS")
    print("=" * 60)
    
    try:
        from utils.trait_discovery import get_trait_discovery
        
        # Discover all traits
        discovery = get_trait_discovery()
        available_traits = discovery.discover_all_traits()
        
        print(f"\n📦 Found {len(available_traits)} traits to test:")
        for trait in available_traits:
            print(f"  • {trait}")
        
        # Test each trait
        results = []
        for trait_name in available_traits:
            result = await run_mock_trait_test(trait_name, verbose=True)
            if result:
                results.append(result)
        
        # Summary
        print("\n" + "="*60)
        print("📊 MOCK TESTING SUMMARY")
        print("="*60)
        
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'failed']
        
        print(f"\nTotal traits tested: {len(results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        if successful:
            print("\nSuccessful trait tests:")
            for result in successful:
                print(f"  • {result['trait_name']}: "
                      f"{result['test_count']} tests, "
                      f"avg score: {result['average_score']:.3f}")
        
        if failed:
            print("\nFailed trait tests:")
            for result in failed:
                print(f"  • {result['trait_name']}: {result.get('error', 'Unknown error')}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in batch testing: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    """Main function with command-line support"""
    
    parser = argparse.ArgumentParser(
        description="Mock test consciousness traits without API calls"
    )
    
    parser.add_argument(
        '--trait', '-t',
        type=str,
        help='Specific trait to test (e.g., recurrent_integration)'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Test all available traits'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Reduce output verbosity'
    )
    
    args = parser.parse_args()
    
    print("🎭 CONSCIOUSNESS FRAMEWORK - MOCK TRAIT TESTER")
    print("Testing traits without real API calls")
    print("=" * 60)
    
    if args.all:
        # Test all traits
        asyncio.run(run_all_traits_mock_test())
    elif args.trait:
        # Test specific trait
        asyncio.run(run_mock_trait_test(args.trait, verbose=not args.quiet))
    else:
        # Interactive mode
        from utils.trait_discovery import get_trait_discovery
        discovery = get_trait_discovery()
        available_traits = list(discovery.discover_all_traits().keys())
        
        print("\nAvailable traits:")
        for i, trait in enumerate(available_traits, 1):
            print(f"  {i}. {trait}")
        
        print(f"  {len(available_traits) + 1}. Test all traits")
        
        try:
            choice = input("\nSelect a trait to test (number or name): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if choice_num == len(available_traits) + 1:
                    asyncio.run(run_all_traits_mock_test())
                elif 1 <= choice_num <= len(available_traits):
                    trait_name = available_traits[choice_num - 1]
                    asyncio.run(run_mock_trait_test(trait_name))
                else:
                    print("Invalid choice!")
            elif choice in available_traits:
                asyncio.run(run_mock_trait_test(choice))
            else:
                print(f"Unknown trait: {choice}")
                
        except KeyboardInterrupt:
            print("\n\nTest cancelled by user")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()