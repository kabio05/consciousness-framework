"""
Check Groq API key validity and available models
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

def check_groq_access():
    """Check what models are available with your Groq API key"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_api_key_here':
        print("❌ No valid Groq API key found in environment")
        print("   Please set GROQ_API_KEY in your .env file")
        print("\n📝 How to get a Groq API key:")
        print("1. Go to https://console.groq.com")
        print("2. Sign up for a free account")
        print("3. Navigate to API Keys section")
        print("4. Create a new API key")
        print("5. Copy the key and add to .env: GROQ_API_KEY=your_key_here")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    
    base_url = "https://api.groq.com/openai/v1"
    
    # Available Groq models
    models_to_test = [
        "mixtral-8x7b-32768",         # Mixtral 8x7B
        "llama-3.1-70b-versatile",    # Llama 3.1 70B  
        "llama-3.1-8b-instant",       # Llama 3.1 8B (fastest)
        "llama-3.2-11b-text-preview", # Llama 3.2 11B
        "llama-3.2-90b-text-preview", # Llama 3.2 90B
        "gemma2-9b-it",               # Google Gemma 2
    ]
    
    print("\n🧪 Testing Groq API access...\n")
    
    # Test API key validity
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    test_data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": "Hi"}],
        "temperature": 0.0,
        "max_tokens": 5
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API key is valid and working!")
            
            # Show token usage and cost info
            data = response.json()
            if 'usage' in data:
                usage = data['usage']
                print(f"   Tokens used: {usage.get('total_tokens', 'N/A')}")
                
        elif response.status_code == 401:
            print("❌ AUTHENTICATION FAILED")
            print("   Your API key is invalid or expired")
            print("   Please check your Groq API key")
            return
        elif response.status_code == 429:
            print("⚠️  RATE LIMIT EXCEEDED")
            print("   Your key is valid but you've hit rate limits")
            print("   Groq free tier limits:")
            print("   - 30 requests/minute")
            print("   - 14,400 requests/day")
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
    print("\n📋 Testing model availability:\n")
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
                print(f"✅ {model:<30} - AVAILABLE")
                available_models.append(model)
                
                # Parse response time if available
                data = response.json()
                if 'usage' in data:
                    usage = data['usage']
                    print(f"   Speed: ~{usage.get('total_tokens', 0) * 2} tokens/sec (estimated)")
                    
            elif response.status_code == 404:
                print(f"❌ {model:<30} - NOT FOUND")
            elif response.status_code == 429:
                print(f"⚠️  {model:<30} - RATE LIMITED (but available)")
                available_models.append(model)
            else:
                print(f"❓ {model:<30} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {model:<30} - Error: {str(e)[:30]}")
    
    # Summary and recommendations
    print(f"\n📊 Summary:")
    print(f"Available models: {len(available_models)}")
    
    if available_models:
        print("\n✅ You can use these models:")
        for model in available_models:
            print(f"  - {model}")
        
        print("\n🎯 RECOMMENDATIONS:")
        print("For consciousness testing with Groq:")
        print("  1. llama-3.1-8b-instant    - Fastest, good for quick tests")
        print("  2. mixtral-8x7b-32768      - Best balance of speed and quality")
        print("  3. llama-3.1-70b-versatile - Highest quality, slower")
        
        print("\n💡 Cost Information:")
        print("Groq offers FREE tier with:")
        print("  - No cost per token")
        print("  - Rate limit: 30 requests/minute")
        print("  - Daily limit: 14,400 requests")
        print("  - Perfect for consciousness testing!")
    else:
        print("\n❌ No models accessible. Check your API key.")
    
    # Test response quality
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
        except Exception as e:
            print(f"⚠️  Quality test failed: {e}")

if __name__ == "__main__":
    print("🤖 GROQ API ACCESS CHECKER")
    print("=" * 50)
    
    check_groq_access()
    
    print("\n" + "=" * 50)
    print("Check complete!")
    print("\nNext steps:")
    print("1. Get your Groq API key from https://console.groq.com")
    print("2. Add to .env: GROQ_API_KEY=your_key_here")
    print("3. Run: python run_assessment.py --model mixtral-8x7b-32768 --all")