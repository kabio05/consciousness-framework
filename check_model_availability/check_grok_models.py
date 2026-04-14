"""
Check Grok API key validity and available models
"""

import os
import sys
import requests
import json
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

def check_grok_access():
    """Check what models are available with your Grok API key"""
    
    api_key = os.getenv('GROK_API_KEY')
    if not api_key or api_key == 'your_grok_api_key_here':
        print("❌ No Grok API key found in environment")
        print("   Please set GROK_API_KEY in your .env file")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Key format: Starts with '{api_key[:4]}' (length: {len(api_key)})")
    
    # Check key format
    if api_key.startswith('xai-'):
        print("✅ Key format looks correct (starts with 'xai-')")
    elif api_key.startswith('gsk_'):
        print("⚠️  Key starts with 'gsk_' - this might be incorrect")
        print("   Grok keys typically start with 'xai-'")
    else:
        print("⚠️  Unusual key format - verify this is correct")
    
    base_url = "https://api.x.ai/v1"
    
    # Test different Grok models
    models_to_test = [
        "grok-beta",
        "grok-2-1212", 
        "grok-2-mini-beta",
        "grok-2",
        "grok-2-mini"
    ]
    
    print("\n🧪 Testing Grok API access...\n")
    
    # First, try a simple API call to check if key is valid
    print("Testing API key validity...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    test_data = {
        "model": "grok-beta",
        "messages": [{"role": "user", "content": "Hi"}],
        "temperature": 0.0,
        "max_tokens": 1
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API key is valid and working!\n")
        elif response.status_code == 400:
            error_data = response.json()
            if "Incorrect API key" in str(error_data):
                print("❌ INVALID API KEY")
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                print("\n🔧 How to fix:")
                print("1. Go to https://console.x.ai")
                print("2. Sign in to your account")
                print("3. Navigate to API Keys section")
                print("4. Generate a new API key")
                print("5. Copy the ENTIRE key (should start with 'xai-')")
                print("6. Update your .env file: GROK_API_KEY=xai-your-key-here")
                return
            else:
                print(f"⚠️  Bad request: {error_data}")
        elif response.status_code == 401:
            print("❌ AUTHENTICATION FAILED")
            print("   Your API key is not being accepted")
            print("   Make sure you copied the complete key")
        elif response.status_code == 429:
            print("⚠️  RATE LIMIT EXCEEDED")
            print("   Your key is valid but you've hit rate limits")
        else:
            print(f"❓ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out - API might be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - check your internet connection")
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return
    
    # Test each model
    print("\nTesting model availability:\n")
    available_models = []
    
    for model in models_to_test:
        try:
            test_data["model"] = model
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {model} - ACCESSIBLE")
                available_models.append(model)
                
                # Get token usage info if available
                try:
                    data = response.json()
                    if 'usage' in data:
                        usage = data['usage']
                        print(f"   Tokens used: {usage.get('total_tokens', 'N/A')}")
                except:
                    pass
                    
            elif response.status_code == 404:
                print(f"❌ {model} - MODEL NOT FOUND")
            elif response.status_code == 429:
                print(f"⚠️  {model} - RATE LIMITED")
                available_models.append(model)  # Model exists but rate limited
            elif response.status_code == 402:
                print(f"💳 {model} - PAYMENT REQUIRED")
            else:
                print(f"❓ {model} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {model} - Error: {str(e)[:50]}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"Available models: {len(available_models)}")
    
    if available_models:
        print("✅ You can use:", ", ".join(available_models))
        
        # Recommend best model for consciousness testing
        if "grok-2-mini-beta" in available_models:
            print("\n🎯 RECOMMENDED: Use 'grok-2-mini-beta' for cost-effective testing")
            print("   Cost: ~$1 per 1M input / $2 per 1M output tokens")
        elif "grok-beta" in available_models:
            print("\n🎯 Available: 'grok-beta'")
            print("   Cost: ~$5 per 1M input / $15 per 1M output tokens")
            
        print("\n💡 Tip: grok-2-mini-beta is the cheapest Grok option")
    else:
        print("\n❌ No models accessible. Possible issues:")
        print("1. Invalid API key")
        print("2. Account not activated")
        print("3. No credits/billing issues")
        print("4. API service down")
    
    # Additional info
    print(f"\n📚 Documentation:")
    print("- Get API keys: https://console.x.ai")
    print("- API docs: https://docs.x.ai/api")
    print("- Pricing: https://x.ai/api#pricing")
    
    # Test response quality with a real question
    if available_models:
        print("\n🔬 Testing response quality...")
        try:
            test_model = available_models[0]
            quality_test = {
                "model": test_model,
                "messages": [{"role": "user", "content": "What is 2+2?"}],
                "temperature": 0.0,
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=quality_test,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['choices'][0]['message']['content']
                print(f"✅ Model {test_model} responds correctly: '{answer}'")
            else:
                print(f"⚠️  Could not test response quality")
                
        except Exception as e:
            print(f"⚠️  Quality test failed: {e}")

def diagnose_key_issues():
    """Provide detailed diagnostics for common Grok API key issues"""
    print("\n🔍 Diagnosing API Key Issues:\n")
    
    api_key = os.getenv('GROK_API_KEY')
    
    if not api_key:
        print("❌ No GROK_API_KEY environment variable found")
        print("   Solution: Add to your .env file:")
        print("   GROK_API_KEY=xai-your-key-here")
        return
    
    # Check common issues
    issues = []
    
    if len(api_key) < 20:
        issues.append("Key seems too short (might be truncated)")
    
    if ' ' in api_key:
        issues.append("Key contains spaces (copy/paste error?)")
    
    if api_key.startswith('"') or api_key.endswith('"'):
        issues.append("Key has quotes (remove them)")
    
    if api_key.startswith('sk-'):
        issues.append("This looks like an OpenAI key, not a Grok key")
    
    if api_key.startswith('gsk_'):
        issues.append("Key format 'gsk_' might be outdated - new keys start with 'xai-'")
    
    if issues:
        print("⚠️  Potential issues found:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ Key format appears correct")
    
    print("\n📋 Checklist for fixing API key issues:")
    print("1. [ ] Key starts with 'xai-' (new format)")
    print("2. [ ] No extra spaces or quotes")
    print("3. [ ] Complete key copied (usually 50+ characters)")
    print("4. [ ] Key is from https://console.x.ai (not OpenAI/Anthropic)")
    print("5. [ ] Account is activated and has credits")

if __name__ == "__main__":
    print("🤖 GROK API ACCESS CHECKER")
    print("=" * 50)
    
    check_grok_access()
    diagnose_key_issues()
    
    print("\n" + "=" * 50)
    print("Check complete!")