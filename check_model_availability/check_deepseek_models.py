"""
Check DeepSeek API models available through Groq
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

def check_deepseek_access():
    """Check what DeepSeek models are available through your Groq API key"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_api_key_here':
        print("❌ No valid Groq API key found in environment")
        print("   DeepSeek models are accessed through Groq's infrastructure")
        return
    
    print(f"🔑 Groq API Key: {api_key[:10]}...{api_key[-4:]}")
    print("   Using Groq infrastructure to access DeepSeek models")
    
    base_url = "https://api.groq.com/openai/v1"
    
    # DeepSeek models that might be available through Groq
    deepseek_models = [
        "deepseek-r1-distill-llama-70b",  # DeepSeek R1 Distilled version
        "deepseek-r1-distill-qwen-32b",   # DeepSeek R1 Qwen distilled
        "deepseek-coder-33b-instruct",    # DeepSeek Coder model
        "deepseek-llm-67b-chat",          # DeepSeek LLM Chat
        "deepseek-math-7b-instruct",      # DeepSeek Math specialized
    ]
    
    print("\n🧪 Testing DeepSeek model availability through Groq...\n")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    available_models = []
    
    for model in deepseek_models:
        try:
            test_data = {
                "model": model,
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": 0.0,
                "max_tokens": 5
            }
            
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {model:<35} - AVAILABLE")
                available_models.append(model)
                
                # Show token usage
                data = response.json()
                if 'usage' in data:
                    usage = data['usage']
                    print(f"   Tokens used: {usage.get('total_tokens', 'N/A')}")
                    
            elif response.status_code == 404:
                print(f"❌ {model:<35} - NOT AVAILABLE")
            elif response.status_code == 429:
                print(f"⚠️  {model:<35} - RATE LIMITED (but exists)")
                available_models.append(model)
            else:
                print(f"❓ {model:<35} - Status: {response.status_code}")
                # Try to parse error message
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        print(f"   Error: {error_data['error'].get('message', 'Unknown')}")
                except:
                    pass
                
        except Exception as e:
            print(f"❌ {model:<35} - Error: {str(e)[:50]}")
    
    # Also check if there are any DeepSeek models in the general model list
    print("\n📋 Checking Groq's model list for any DeepSeek models...\n")
    
    try:
        # Some providers expose a models endpoint
        response = requests.get(
            f"{base_url}/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models_data = response.json()
            if 'data' in models_data:
                deepseek_found = []
                for model_info in models_data['data']:
                    model_id = model_info.get('id', '')
                    if 'deepseek' in model_id.lower():
                        deepseek_found.append(model_id)
                        if model_id not in available_models:
                            print(f"🔍 Found additional DeepSeek model: {model_id}")
                            available_models.append(model_id)
        else:
            print("ℹ️  Could not retrieve full model list")
    except Exception as e:
        print(f"ℹ️  Model list endpoint not accessible: {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"DeepSeek models available: {len(available_models)}")
    
    if available_models:
        print("\n✅ You can use these DeepSeek models:")
        for model in available_models:
            print(f"  - {model}")
        
        print("\n🎯 RECOMMENDATIONS:")
        print("For consciousness testing with DeepSeek models:")
        if "deepseek-r1-distill-llama-70b" in available_models:
            print("  1. deepseek-r1-distill-llama-70b - Latest R1 reasoning model")
        if "deepseek-coder-33b-instruct" in available_models:
            print("  2. deepseek-coder-33b-instruct - For code-related consciousness tests")
        if "deepseek-llm-67b-chat" in available_models:
            print("  3. deepseek-llm-67b-chat - General purpose chat model")
            
        print("\n💡 About DeepSeek Models:")
        print("  - DeepSeek R1 models excel at reasoning tasks")
        print("  - Very cost-effective through Groq's infrastructure")
        print("  - Particularly good at mathematical and logical reasoning")
        print("  - The R1 models use chain-of-thought reasoning internally")
    else:
        print("\n❌ No DeepSeek models currently accessible through your Groq API key")
        print("\n💡 Note: DeepSeek model availability through Groq may vary")
        print("   Check Groq's documentation for current model offerings")
    
    # Test response quality if any models are available
    if available_models:
        print("\n🔬 Testing DeepSeek model response quality...")
        try:
            test_model = available_models[0]
            quality_test = {
                "model": test_model,
                "messages": [{"role": "user", "content": "What is consciousness in one sentence?"}],
                "temperature": 0.0,
                "max_tokens": 100
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
                print(f"✅ Model {test_model} responds:")
                print(f"   '{answer[:200]}{'...' if len(answer) > 200 else ''}'")
        except Exception as e:
            print(f"⚠️  Quality test failed: {e}")

if __name__ == "__main__":
    print("🤖 DEEPSEEK MODEL ACCESS CHECKER (via Groq)")
    print("=" * 50)
    
    check_deepseek_access()
    
    print("\n" + "=" * 50)
    print("Check complete!")
    print("\nNote: DeepSeek models are accessed through Groq's API")
    print("Your existing GROQ_API_KEY is used for authentication")