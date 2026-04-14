import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime
import argparse
import json
import logging  # Add this import

# Add src to Python path
project_root = Path(__file__).parent
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

def setup_logging(debug=False):
    """
    Configure logging based on debug flag
    
    Args:
        debug: If True, show DEBUG level logs. If False, show INFO and above.
    """
    # Clear any existing handlers
    logger = logging.getLogger()
    logger.handlers = []
    
    # Set the base logging level
    if debug:
        log_level = logging.DEBUG
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    else:
        log_level = logging.INFO
        log_format = '%(levelname)s - %(name)s: %(message)s'
    
    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers if needed
    if not debug:
        # Suppress some verbose loggers when not in debug mode
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('openai').setLevel(logging.WARNING)
        logging.getLogger('anthropic').setLevel(logging.WARNING)
    
    # Create a logger for this module
    logger = logging.getLogger(__name__)
    
    if debug:
        logger.debug("Debug logging enabled")
        print("🐛 DEBUG MODE ENABLED - Verbose logging active")
    else:
        logger.info("Standard logging enabled")

def check_prerequisites(debug=False):
    """Check if everything is ready for assessment"""
    print("🔍 Checking Prerequisites...\n")
    
    # Check API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    grok_key = os.getenv('GROK_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    keys_found = []
    
    # Check OpenAI key
    if openai_key and openai_key != 'your_openai_api_key_here' and len(openai_key) > 10:
        print("✅ OpenAI API key configured")
        keys_found.append("OpenAI")
        if debug:
            print(f"   🔑 Key: {openai_key[:10]}...{openai_key[-4:]}")
    else:
        print("⚠️  OpenAI API key not found or placeholder")
        if debug:
            if not openai_key:
                print("   ❌ OPENAI_API_KEY environment variable not set")
            elif openai_key == 'your_openai_api_key_here':
                print("   ❌ OPENAI_API_KEY still has placeholder value")
            elif len(openai_key) <= 10:
                print("   ❌ OPENAI_API_KEY appears to be invalid (too short)")
    
    # Check Grok key
    if grok_key and grok_key != 'your_grok_api_key_here' and len(grok_key) > 10:
        print("✅ Grok API key configured")
        keys_found.append("Grok")
        if debug:
            print(f"   🔑 Key: {grok_key[:10]}...{grok_key[-4:]}")
    else:
        print("⚠️  Grok API key not found or placeholder")
        if debug:
            if not grok_key:
                print("   ❌ GROK_API_KEY environment variable not set")
            elif grok_key == 'your_grok_api_key_here':
                print("   ❌ GROK_API_KEY still has placeholder value")
            elif len(grok_key) <= 10:
                print("   ❌ GROK_API_KEY appears to be invalid (too short)")
    
    # Check Anthropic key
    if anthropic_key and anthropic_key != 'your_anthropic_api_key_here' and len(anthropic_key) > 10:
        print("✅ Anthropic API key configured")
        keys_found.append("Anthropic")
        if debug:
            print(f"   🔑 Key: {anthropic_key[:10]}...{anthropic_key[-4:]}")
    else:
        print("⚠️  Anthropic API key not found or placeholder")
        if debug:
            if not anthropic_key:
                print("   ❌ ANTHROPIC_API_KEY environment variable not set")
            elif anthropic_key == 'your_anthropic_api_key_here':
                print("   ❌ ANTHROPIC_API_KEY still has placeholder value")
            elif len(anthropic_key) <= 10:
                print("   ❌ ANTHROPIC_API_KEY appears to be invalid (too short)")
    
    # Summary of API keys
    print()  # Add spacing
    if not keys_found:
        print("❌ No valid API keys found!")
        print("Please set at least one of the following in your .env file:")
        print("  - OPENAI_API_KEY")
        print("  - GROK_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        return False
    else:
        print(f"✅ API providers available: {', '.join(keys_found)}")
        if debug:
            print(f"   Total providers configured: {len(keys_found)}")
    
    # Try importing core components
    print("\n📦 Checking Framework Components...")
    try:
        from core.orchestrator import ConsciousnessTestOrchestrator
        from utils.trait_discovery import get_trait_discovery
        print("✅ Framework components imported successfully")
        
        # Check for available traits
        discovery = get_trait_discovery()
        traits = discovery.discover_all_traits()
        print(f"✅ Found {len(traits)} consciousness traits")
        
        if debug:
            print("\n📦 Available traits details:")
            for trait_name, trait_class in traits.items():
                print(f"   • {trait_name}: {trait_class.__name__}")
        
        # Additional debug info about API configuration
        if debug:
            print("\n🔧 API Configuration Details:")
            try:
                from core.api_manager import APIManager
                api_manager = APIManager()
                available_models = api_manager.get_available_models()
                
                for provider, models in available_models.items():
                    print(f"   {provider.value} models: {', '.join(models)}")
                    
                # Test API health if in debug mode
                print("\n🏥 Testing API Health...")
                health_status = api_manager.health_check()
                for provider, is_healthy in health_status.items():
                    status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
                    print(f"   {provider.value}: {status}")
                    
            except Exception as e:
                print(f"   ⚠️  Could not load API configuration: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error during prerequisite check: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False

def list_available_traits(debug=False):
    """List all dynamically discovered traits"""
    from utils.trait_discovery import get_trait_discovery
    
    discovery = get_trait_discovery()
    traits = discovery.discover_all_traits()
    
    print("\n📦 Available Consciousness Traits:")
    print("=" * 50)
    
    for i, (trait_name, trait_class) in enumerate(traits.items(), 1):
        info = discovery.get_trait_info(trait_name)
        print(f"\n{i}. {trait_name}")
        print(f"   Class: {info['class_name']}")
        print(f"   Description: {info['description'][:100]}...")
        
        if debug:
            # Show more details in debug mode
            print(f"   Module: {info.get('module', 'Unknown')}")
            print(f"   Methods: {', '.join(info.get('methods', []))}")
    
    return list(traits.keys())

def list_available_models(debug=False):
    """List available models with cost information"""
    models = {
        # OpenAI models
        "gpt-4o-mini": {
            "cost": "~$0.15 per 1M tokens (cheapest)",
            "description": "Fast and cost-effective for consciousness testing",
            "provider": "OpenAI"
        },
        "gpt-3.5-turbo": {
            "cost": "~$0.50 per 1M tokens (affordable)",
            "description": "Good balance of cost and capability",
            "provider": "OpenAI"
        },
        "gpt-4o": {
            "cost": "~$2.50 per 1M tokens (expensive)",
            "description": "High capability but more expensive",
            "provider": "OpenAI"
        },
        "gpt-4": {
            "cost": "~$10+ per 1M tokens (most expensive)",
            "description": "Highest capability but highest cost",
            "provider": "OpenAI"
        },
        # Groq models
        "llama-3.1-8b-instant": {
            "cost": "FREE (rate limited)",
            "description": "Llama 3.1 8B - Fastest available Groq model",
            "provider": "Groq"
        },
        "gemma2-9b-it": {
            "cost": "FREE (rate limited)",
            "description": "Google Gemma 2 9B - Good for reasoning tasks",
            "provider": "Groq"
        },
        "deepseek-r1-distill-llama-70b": {
            "cost": "FREE (rate limited)",
            "description": "DeepSeek R1 70B - Advanced reasoning and problem-solving",
            "provider": "Groq"
        }
    }
    
    print("\n🤖 Available Models:")
    print("=" * 60)
    
    for i, (model, info) in enumerate(models.items(), 1):
        print(f"\n{i}. {model}")
        print(f"   Provider: {info['provider']}")
        print(f"   Cost: {info['cost']}")
        print(f"   Description: {info['description']}")
        
        if debug:
            print(f"   Status: Checking availability...")
    
    return list(models.keys())

async def run_assessment(model_name: str = None, trait_names: list = None, 
                        run_all: bool = False, parallel: bool = False,
                        debug: bool = False, scoring: str = "hybrid",
                        save_txt: bool = False):  # Added save_txt parameter
    """
    Run consciousness assessment with dynamic trait loading
    
    Args:
        model_name: Model to use for testing
        trait_names: List of specific traits to test
        run_all: Test all available traits
        parallel: Run traits in parallel
        debug: Enable debug logging
        scoring: Scoring method to use (keyword, geval, or hybrid)
        save_txt: Whether to save results to text file (default: False)
    """
    
    logger = logging.getLogger(__name__)
    
    print("\n🧠 Starting Consciousness Assessment...\n")
    
    if debug:
        print("🐛 Debug mode: Detailed logging enabled")
    
    if not save_txt:
        print("📝 Text file output: Disabled (use --save-txt to enable)")
    else:
        print("📝 Text file output: Enabled")
    
    try:
        # Import components
        from core.orchestrator import ConsciousnessTestOrchestrator
        
        # Initialize orchestrator
        print("🔧 Initializing consciousness testing framework...")
        orchestrator = ConsciousnessTestOrchestrator()
        
        # Refresh trait discovery to ensure we have the latest
        orchestrator.refresh_traits()
        
        # Get available traits
        available_traits = orchestrator.list_available_traits()
        
        if not available_traits:
            print("❌ No traits found! Make sure you have .py files in the traits folder.")
            return
        
        # Determine which model to use
        if not model_name:
            model_name = "gpt-4o-mini"  # Default to cheapest
            print(f"📌 No model specified, using default: {model_name}")
        
        # Validate model choice
        available_models = [
            # OpenAI
            "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o", "gpt-4",
            # Groq
            "llama-3.1-8b-instant", "gemma2-9b-it", "deepseek-r1-distill-llama-70b"
        ]
        
        if model_name not in available_models:
            print(f"❌ Invalid model: {model_name}")
            print(f"Available models: {available_models}")
            return
        
        # Show model cost information
        model_costs = {
            "gpt-4o-mini": "~$0.15 per 1M tokens (cheapest OpenAI)",
            "gpt-3.5-turbo": "~$0.50 per 1M tokens",
            "gpt-4o": "~$2.50 per 1M tokens",
            "gpt-4": "~$10+ per 1M tokens",
            "llama-3.1-8b-instant": "FREE - Groq (30 req/min limit) - 82 tokens/sec",
            "gemma2-9b-it": "FREE - Groq (30 req/min limit) - 30 tokens/sec",
            "deepseek-r1-distill-llama-70b": "FREE - Groq (30 req/min limit) - Advanced reasoning"
        }
        print(f"Cost estimate: {model_costs.get(model_name, 'Cost unknown')}")

        # Determine which traits to run
        if run_all:
            selected_traits = available_traits
            print(f"🔬 Running ALL {len(selected_traits)} available traits")
        elif trait_names:
            # Validate trait names
            invalid_traits = [t for t in trait_names if t not in available_traits]
            if invalid_traits:
                print(f"❌ Invalid traits: {invalid_traits}")
                print(f"Available traits: {available_traits}")
                return
            selected_traits = trait_names
            print(f"🔬 Running selected traits: {selected_traits}")
        else:
            # Default: run all available traits
            selected_traits = available_traits
            print(f"🔬 No traits specified, running all {len(selected_traits)} traits")
        
        # Display trait information
        print("\n📋 Traits to be tested:")
        for trait in selected_traits:
            trait_info = orchestrator.get_trait_info(trait)
            if trait_info:
                desc = trait_info['description'][:60] if not debug else trait_info['description']
                print(f"  • {trait}: {desc}...")
        
        # Run assessment
        print(f"\n🚀 Running consciousness assessment...")
        print(f"Model: {model_name}")
        print(f"Traits: {len(selected_traits)}")
        print(f"Mode: {'Parallel' if parallel else 'Sequential'}")
        if debug:
            print(f"Debug: Enabled - Verbose logging active")
        print("This may take a few minutes...\n")
        
        start_time = datetime.now()
        
        session = await orchestrator.run_assessment(
            model_name=model_name,
            selected_traits=selected_traits,
            scoring_method=scoring,  # Pass as 'scoring_method' to orchestrator
            parallel_execution=parallel
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Display results
        print(f"\n📊 Assessment completed in {duration:.1f} seconds!")
        print(f"Status: {session.status}")
        
        if debug and session.error_log:
            print("\n⚠️ Errors encountered during assessment:")
            for error in session.error_log:
                print(f"  • {error}")
        
        # Check if we actually have test results to save
        has_results = (session.consciousness_profile and 
                      hasattr(session, 'trait_summaries') and 
                      len(session.trait_summaries) > 0 and
                      any(summary.test_count > 0 for summary in session.trait_summaries))
        
        if session.consciousness_profile and has_results:
            profile = session.consciousness_profile
            print(f"\n📋 CONSCIOUSNESS ASSESSMENT RESULTS")
            print("=" * 50)
            print(f"Model: {profile.model_name}")
            print(f"Overall Score: {profile.overall_score:.3f}/1.0")
            
            # Interpret the score
            if profile.overall_score >= 0.8:
                interpretation = "🌟 Excellent consciousness indicators"
            elif profile.overall_score >= 0.6:
                interpretation = "✅ Good consciousness capabilities"
            elif profile.overall_score >= 0.4:
                interpretation = "⚠️  Moderate consciousness signs"
            else:
                interpretation = "❓ Limited consciousness indicators"
            
            print(f"Interpretation: {interpretation}")
            
            if hasattr(profile, 'trait_scores') and profile.trait_scores:
                print(f"\n📈 Individual Trait Scores:")
                for trait, score in profile.trait_scores.items():
                    if trait != 'overall_consciousness':
                        print(f"  • {trait.replace('_', ' ').title()}: {score:.3f}")
            
            if profile.strengths:
                print(f"\n💪 Strengths:")
                for strength in profile.strengths:
                    print(f"  • {strength}")
            
            if profile.weaknesses:
                print(f"\n⚠️  Areas for Improvement:")
                for weakness in profile.weaknesses:
                    print(f"  • {weakness}")
            
            # Display execution summary
            print(f"\n📊 Execution Summary:")
            for summary in session.trait_summaries:
                status_icon = "✅" if summary.status.value == "success" else "❌"
                print(f"  {status_icon} {summary.trait_name}: {summary.execution_time:.1f}s, "
                      f"{summary.test_count} tests, avg score: {summary.average_score:.3f}")
                
                if debug and summary.error_message:
                    print(f"      Error: {summary.error_message}")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save text file only if save_txt flag is True
            if save_txt:
                # Create consciousness_results directory if it doesn't exist
                results_dir = Path("consciousness_results")
                results_dir.mkdir(exist_ok=True)
                
                # Save to consciousness_results folder
                results_file = results_dir / f"consciousness_results_{model_name.replace('-', '_')}_{timestamp}.txt"
                
                try:
                    from core.report_generator import ReportGenerator
                    report_gen = ReportGenerator()
                    detailed_report = report_gen.generate_summary(profile)
                    
                    with open(results_file, 'w') as f:
                        f.write(f"CONSCIOUSNESS ASSESSMENT - DYNAMIC TRAITS\n")
                        f.write(f"Model: {model_name}\n")
                        f.write(f"Traits tested: {', '.join(selected_traits)}\n")
                        if debug:
                            f.write(f"Debug mode: Enabled\n")
                        f.write(f"=" * 50 + "\n\n")
                        f.write(detailed_report)
                        f.write(f"\n\nAssessment completed: {end_time}")
                        f.write(f"\nDuration: {duration:.1f} seconds")
                    
                    print(f"\n💾 Detailed report saved to: {results_file}")
                    
                except Exception as e:
                    print(f"⚠️  Could not save text report: {e}")
                    if debug:
                        logger.exception("Text report saving failed")
            
            # Always generate web data (regardless of save_txt flag)
            try:
                print("\n🌐 Generating web interface data...")
                generate_web_data(session, model_name, end_time, selected_traits, duration)
            except Exception as e:
                print(f"⚠️  Could not generate web data: {e}")
                if debug:
                    logger.exception("Web data generation failed")
        
        else:
            print("❌ No consciousness profile generated or no tests were run")
            if session.error_log:
                print("Errors encountered:")
                for error in session.error_log:
                    print(f"  • {error}")
            
            print("⚠️  No web data saved - no valid test results to record")
        
        print(f"\n🎉 Assessment Complete!")
        print(f"🌐 View results at: web/index.html")
        
    except Exception as e:
        print(f"❌ Assessment failed: {e}")
        if debug:
            logger.exception("Assessment failed with exception")
        else:
            import traceback
            print("\nDetailed error:")
            traceback.print_exc()

def generate_web_data(session, model_name, timestamp, selected_traits, duration):
    """Generate JSON data for web interface - tracks each trait independently"""
    import json
    from pathlib import Path
    from datetime import datetime
    
    # Create web/data directory if it doesn't exist
    web_data_dir = Path("web/data")
    web_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Load existing data if it exists
    results_file = web_data_dir / "results.json"
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                web_data = json.load(f)
        except:
            web_data = {
                "assessments": [],
                "trait_history": {},  # New: track each trait separately
                "composite_profile": {},  # New: composite view of latest traits
                "available_traits": [],
                "available_models": [],
                "last_updated": None
            }
    else:
        web_data = {
            "assessments": [],
            "trait_history": {},
            "composite_profile": {},
            "available_traits": [],
            "available_models": [],
            "last_updated": None
        }
    
    # Initialize trait_history and composite_profile for this model if not exists
    if "trait_history" not in web_data:
        web_data["trait_history"] = {}
    if "composite_profile" not in web_data:
        web_data["composite_profile"] = {}
    
    if model_name not in web_data["trait_history"]:
        web_data["trait_history"][model_name] = {}
    if model_name not in web_data["composite_profile"]:
        web_data["composite_profile"][model_name] = {
            "traits": {},
            "last_updated": {},
            "overall_score": 0.0
        }
    
    # Update trait history and composite profile with new results
    if session.consciousness_profile and hasattr(session.consciousness_profile, 'trait_scores'):
        for trait, score in session.consciousness_profile.trait_scores.items():
            if trait != 'overall_consciousness' and trait in selected_traits:
                # Update trait history (keep last 10 runs per trait)
                if trait not in web_data["trait_history"][model_name]:
                    web_data["trait_history"][model_name][trait] = []
                
                web_data["trait_history"][model_name][trait].insert(0, {
                    "score": score,
                    "timestamp": timestamp.isoformat(),
                    "duration": duration
                })
                
                # Keep only last 10 runs per trait
                web_data["trait_history"][model_name][trait] = \
                    web_data["trait_history"][model_name][trait][:10]
                
                # Update composite profile with latest score for this trait
                web_data["composite_profile"][model_name]["traits"][trait] = score
                web_data["composite_profile"][model_name]["last_updated"][trait] = timestamp.isoformat()
    
    # Recalculate overall score based on ALL traits in composite profile
    if web_data["composite_profile"][model_name]["traits"]:
        all_trait_scores = list(web_data["composite_profile"][model_name]["traits"].values())
        web_data["composite_profile"][model_name]["overall_score"] = \
            sum(all_trait_scores) / len(all_trait_scores)
    
    # Also keep the traditional assessment history for backwards compatibility
    new_assessment = {
        "model": model_name,
        "timestamp": timestamp.isoformat(),
        "traits": {},
        "overall_score": session.consciousness_profile.overall_score if session.consciousness_profile else 0.0,
        "traits_tested": selected_traits,
        "metadata": {
            "duration": duration,
            "status": "completed",
            "partial_run": len(selected_traits) < len(web_data.get("available_traits", [])),
            "scoring_method": getattr(session, 'scoring_method', 'keyword').value if hasattr(session, 'scoring_method') else 'keyword'  # ADD THIS
        }
    }
    
    # Add only the traits that were tested in this run
    if session.consciousness_profile and hasattr(session.consciousness_profile, 'trait_scores'):
        for trait, score in session.consciousness_profile.trait_scores.items():
            if trait != 'overall_consciousness' and trait in selected_traits:
                new_assessment["traits"][trait] = score
    
    # Add assessment to history
    web_data["assessments"].insert(0, new_assessment)
    web_data["assessments"] = web_data["assessments"][:50]
    
    # Update available traits and models
    all_traits = set(web_data.get("available_traits", []))
    all_traits.update(selected_traits)
    web_data["available_traits"] = sorted(list(all_traits))
    
    if model_name not in web_data.get("available_models", []):
        web_data["available_models"] = web_data.get("available_models", []) + [model_name]
    
    # Update timestamp
    web_data["last_updated"] = timestamp.isoformat()
    
    # Save to file
    with open(results_file, 'w') as f:
        json.dump(web_data, f, indent=2)
    
    print(f"📊 Web data saved to: {results_file}")
    
    # Print summary of composite profile
    composite = web_data["composite_profile"][model_name]
    print(f"\n📈 Composite Profile for {model_name}:")
    print(f"   Overall Score: {composite['overall_score']:.3f}")
    for trait, score in composite["traits"].items():
        updated = composite["last_updated"].get(trait, "unknown")
        if isinstance(updated, str) and 'T' in updated:
            updated_dt = datetime.fromisoformat(updated)
            updated_str = updated_dt.strftime("%Y-%m-%d %H:%M")
        else:
            updated_str = "unknown"
        print(f"   • {trait}: {score:.3f} (updated: {updated_str})")

def main():
    """Main function with command-line argument support"""
    
    parser = argparse.ArgumentParser(
        description="Run consciousness assessment with dynamic trait loading"
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        choices=[
            # OpenAI models
            'gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4',
            # Groq models
            'llama-3.1-8b-instant', 'gemma2-9b-it', 'deepseek-r1-distill-llama-70b'
        ],
        help='Model to test (default: gpt-4o-mini for lowest cost)'
    )
    
    parser.add_argument(
        '--traits', '-t',
        type=str,
        nargs='+',
        help='Specific traits to test (space-separated)'
    )
    
    parser.add_argument(
        '--scoring', '-s',
        type=str,
        choices=['keyword', 'geval', 'hybrid'],
        default='geval',
        help='Scoring method to use (default: geval)'
    )
    
    parser.add_argument(
        '--save-txt',
        action='store_true',
        help='Save detailed results to text file (default: False, only console output)'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all available traits'
    )
    
    parser.add_argument(
        '--list-traits', '-lt',
        action='store_true',
        help='List all available traits and exit'
    )
    
    parser.add_argument(
        '--list-models', '-lm',
        action='store_true',
        help='List all available models with cost info and exit'
    )
    
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='Run traits in parallel (faster but uses more API calls)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-essential output (opposite of debug)'
    )
    
    args = parser.parse_args()
    
    # Handle quiet mode (overrides debug)
    if args.quiet:
        args.debug = False
        # Set up minimal logging
        logging.basicConfig(level=logging.WARNING)
    else:
        # Set up logging based on debug flag
        setup_logging(debug=args.debug)
    
    if not args.quiet:
        print("🧠 CONSCIOUSNESS FRAMEWORK - DYNAMIC TRAIT SYSTEM")
        print("=" * 60)
    
    if args.list_traits:
        list_available_traits(debug=args.debug)
        return
    
    if args.list_models:
        list_available_models(debug=args.debug)
        return
    
    if not check_prerequisites(debug=args.debug):
        print("\n❌ Prerequisites not met.")
        return
    
    if not args.quiet:
        print("\n✅ Prerequisites met. Starting assessment...")
    
    # Run the assessment
    try:
        asyncio.run(run_assessment(
            model_name=args.model,
            trait_names=args.traits,
            run_all=args.all,
            parallel=args.parallel,
            debug=args.debug,
            scoring=args.scoring,
            save_txt=args.save_txt
        ))
    except KeyboardInterrupt:
        print("\n⚠️  Assessment interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()