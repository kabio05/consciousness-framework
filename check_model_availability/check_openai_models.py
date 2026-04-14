"""
Check what OpenAI models your API key has access to
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
except ImportError:
    pass

def check_openai_access():
    """Check what models are available with your API key"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ No valid OpenAI API key found")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test different models
        models_to_test = [
            "gpt-3.5-turbo",
            "gpt-4", 
            "gpt-4-turbo-preview",
            "gpt-4o",
            "gpt-4o-mini"
        ]
        
        print("\n🧪 Testing model access...\n")
        
        available_models = []
        
        for model in models_to_test:
            try:
                # Try a simple test request
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=1
                )
                print(f"✅ {model} - ACCESSIBLE")
                available_models.append(model)
                
            except Exception as e:
                if "does not exist or you do not have access" in str(e):
                    print(f"❌ {model} - NO ACCESS")
                elif "insufficient_quota" in str(e):
                    print(f"⚠️  {model} - NO CREDITS")
                else:
                    print(f"❓ {model} - ERROR: {str(e)[:50]}...")
        
        print(f"\n📊 Summary:")
        print(f"Available models: {len(available_models)}")
        if available_models:
            print("✅ You can use:", ", ".join(available_models))
            
            # Recommend best model for consciousness testing
            if "gpt-4" in available_models:
                print("\n🎯 RECOMMENDED: Use 'gpt-4' for best consciousness testing results")
            elif "gpt-3.5-turbo" in available_models:
                print("\n🎯 RECOMMENDED: Use 'gpt-3.5-turbo' (available with your account)")
                print("   Note: Results may be less sophisticated than GPT-4")
        else:
            print("\n❌ No models accessible. Check your:")
            print("1. API key validity")
            print("2. Account billing status")
            print("3. Usage limits")
        
        # Check account info
        try:
            # This might not work with all API keys
            print(f"\n💳 Account Status:")
            print("Visit https://platform.openai.com/account/usage to check:")
            print("- Current usage")
            print("- Available credits") 
            print("- Rate limits")
            
        except Exception:
            pass
            
    except ImportError:
        print("❌ OpenAI library not installed. Run: pip install openai")
    except Exception as e:
        print(f"❌ Error checking OpenAI access: {e}")

if __name__ == "__main__":
    print("🔍 OPENAI MODEL ACCESS CHECKER")
    print("=" * 40)
    check_openai_access()