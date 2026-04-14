import asyncio
import time
import os
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
from abc import ABC, abstractmethod
import json

# Third-party imports (would need to be added to requirements.txt)
try:
    import openai
    from anthropic import Anthropic
    import aiohttp
    import requests
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install: pip install openai anthropic aiohttp requests")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIProvider(Enum):
    """Supported AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROK = "grok"
    GROQ = "groq"
    # Future providers can be added here

@dataclass
class APIResponse:
    """Standardized response format from any AI provider"""
    content: str
    provider: APIProvider
    model: str
    usage_tokens: Optional[int] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    requests_per_hour: int = 3000
    tokens_per_minute: int = 150000
    
class APIError(Exception):
    """Custom exception for API-related errors"""
    def __init__(self, message: str, provider: APIProvider, status_code: Optional[int] = None):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(self.message)

class BaseAPIClient(ABC):
    """Abstract base class for all AI provider clients"""
    
    def __init__(self, api_key: str, rate_limit_config: RateLimitConfig):
        self.api_key = api_key
        self.rate_limit_config = rate_limit_config
        self.request_history = []  # Track requests for rate limiting
        
    @abstractmethod
    async def query_async(self, prompt: str, model: str, **kwargs) -> APIResponse:
        """Async method to query the AI service"""
        pass
    
    @abstractmethod
    def query_sync(self, prompt: str, model: str, **kwargs) -> APIResponse:
        """Synchronous method to query the AI service"""
        pass
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        
        # Remove old requests (older than 1 hour)
        self.request_history = [
            req_time for req_time in self.request_history 
            if current_time - req_time < 3600
        ]
        
        # Check requests per minute
        recent_requests = [
            req_time for req_time in self.request_history 
            if current_time - req_time < 60
        ]
        
        if len(recent_requests) >= self.rate_limit_config.requests_per_minute:
            return False
            
        # Check requests per hour
        if len(self.request_history) >= self.rate_limit_config.requests_per_hour:
            return False
            
        return True
    
    def _wait_for_rate_limit(self):
        """Wait until we can make another request"""
        while not self._check_rate_limit():
            logger.info(f"Rate limit reached for {self.__class__.__name__}, waiting...")
            time.sleep(1)
    
    def _record_request(self):
        """Record that we made a request"""
        self.request_history.append(time.time())

class OpenAIClient(BaseAPIClient):
    """Client for OpenAI API"""
    
    def __init__(self, api_key: str, rate_limit_config: RateLimitConfig):
        super().__init__(api_key, rate_limit_config)
        self.client = openai.OpenAI(api_key=api_key)
        
    async def query_async(self, prompt: str, model: str = "gpt-4", **kwargs) -> APIResponse:
        """Async query to OpenAI"""
        self._wait_for_rate_limit()
        start_time = time.time()
        
        try:
            # Convert sync client to work with async context
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._make_openai_request, prompt, model, kwargs
            )
            
            response_time = time.time() - start_time
            self._record_request()
            
            return APIResponse(
                content=response.choices[0].message.content,
                provider=APIProvider.OPENAI,
                model=model,
                usage_tokens=response.usage.total_tokens if response.usage else None,
                response_time=response_time,
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIError(f"OpenAI request failed: {e}", APIProvider.OPENAI)
    
    def query_sync(self, prompt: str, model: str = "gpt-4", **kwargs) -> APIResponse:
        """Synchronous query to OpenAI"""
        self._wait_for_rate_limit()
        start_time = time.time()
        
        try:
            response = self._make_openai_request(prompt, model, kwargs)
            response_time = time.time() - start_time
            self._record_request()
            
            return APIResponse(
                content=response.choices[0].message.content,
                provider=APIProvider.OPENAI,
                model=model,
                usage_tokens=response.usage.total_tokens if response.usage else None,
                response_time=response_time,
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIError(f"OpenAI request failed: {e}", APIProvider.OPENAI)
    
    def _make_openai_request(self, prompt: str, model: str, kwargs: Dict):
        """Make the actual OpenAI API request"""
        return self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
            **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
        )

class AnthropicClient(BaseAPIClient):
    """Client for Anthropic Claude API"""
    
    def __init__(self, api_key: str, rate_limit_config: RateLimitConfig):
        super().__init__(api_key, rate_limit_config)
        self.client = Anthropic(api_key=api_key)
        
    async def query_async(self, prompt: str, model: str = "claude-3-opus-20240229", **kwargs) -> APIResponse:
        """Async query to Anthropic"""
        self._wait_for_rate_limit()
        start_time = time.time()
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._make_anthropic_request, prompt, model, kwargs
            )
            
            response_time = time.time() - start_time
            self._record_request()
            
            return APIResponse(
                content=response.content[0].text,
                provider=APIProvider.ANTHROPIC,
                model=model,
                usage_tokens=response.usage.output_tokens + response.usage.input_tokens,
                response_time=response_time,
                metadata={"stop_reason": response.stop_reason}
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise APIError(f"Anthropic request failed: {e}", APIProvider.ANTHROPIC)
    
    def query_sync(self, prompt: str, model: str = "claude-3-opus-20240229", **kwargs) -> APIResponse:
        """Synchronous query to Anthropic"""
        self._wait_for_rate_limit()
        start_time = time.time()
        
        try:
            response = self._make_anthropic_request(prompt, model, kwargs)
            response_time = time.time() - start_time
            self._record_request()
            
            return APIResponse(
                content=response.content[0].text,
                provider=APIProvider.ANTHROPIC,
                model=model,
                usage_tokens=response.usage.output_tokens + response.usage.input_tokens,
                response_time=response_time,
                metadata={"stop_reason": response.stop_reason}
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise APIError(f"Anthropic request failed: {e}", APIProvider.ANTHROPIC)
    
    def _make_anthropic_request(self, prompt: str, model: str, kwargs: Dict):
        """Make the actual Anthropic API request"""
        return self.client.messages.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.7),
            messages=[{"role": "user", "content": prompt}]
        )

class GrokClient(BaseAPIClient):
    """Client for Grok API (xAI)"""
    
    def __init__(self, api_key: str, rate_limit_config: RateLimitConfig):
        super().__init__(api_key, rate_limit_config)
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1"
        
    async def query_async(self, prompt: str, model: str = "grok-beta", **kwargs) -> APIResponse:
        """Async query to Grok"""
        self._wait_for_rate_limit()
        start_time = time.time()
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._make_grok_request, prompt, model, kwargs
            )
            
            response_time = time.time() - start_time
            self._record_request()
            
            return APIResponse(
                content=response['choices'][0]['message']['content'],
                provider=APIProvider.GROK,
                model=model,
                usage_tokens=response.get('usage', {}).get('total_tokens'),
                response_time=response_time,
                metadata={"finish_reason": response['choices'][0].get('finish_reason')}
            )
            
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            raise APIError(f"Grok request failed: {e}", APIProvider.GROK)
    
    def query_sync(self, prompt: str, model: str = "grok-beta", **kwargs) -> APIResponse:
        """Synchronous query to Grok"""
        self._wait_for_rate_limit()
        start_time = time.time()
        
        try:
            response = self._make_grok_request(prompt, model, kwargs)
            response_time = time.time() - start_time
            self._record_request()
            
            return APIResponse(
                content=response['choices'][0]['message']['content'],
                provider=APIProvider.GROK,
                model=model,
                usage_tokens=response.get('usage', {}).get('total_tokens'),
                response_time=response_time,
                metadata={"finish_reason": response['choices'][0].get('finish_reason')}
            )
            
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            raise APIError(f"Grok request failed: {e}", APIProvider.GROK)
    
    def _make_grok_request(self, prompt: str, model: str, kwargs: Dict):
        """Make the actual Grok API request"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise APIError(
                f"Grok API returned status {response.status_code}: {response.text}",
                APIProvider.GROK,
                response.status_code
            )
        
        return response.json()

class GroqClient(BaseAPIClient):
    """Client for Groq API"""
    
    def __init__(self, api_key: str, rate_limit_config: RateLimitConfig):
        super().__init__(api_key, rate_limit_config)
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"  # Groq uses OpenAI-compatible endpoint
        
    async def query_async(self, prompt: str, model: str = "mixtral-8x7b-32768", **kwargs) -> APIResponse:
        """Async query to Groq"""
        self._wait_for_rate_limit()
        start_time = time.time()
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._make_groq_request, prompt, model, kwargs
            )
            
            response_time = time.time() - start_time
            self._record_request()
            
            return APIResponse(
                content=response['choices'][0]['message']['content'],
                provider=APIProvider.GROQ,
                model=model,
                usage_tokens=response.get('usage', {}).get('total_tokens'),
                response_time=response_time,
                metadata={"finish_reason": response['choices'][0].get('finish_reason')}
            )
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise APIError(f"Groq request failed: {e}", APIProvider.GROQ)
    
    def query_sync(self, prompt: str, model: str = "mixtral-8x7b-32768", **kwargs) -> APIResponse:
        """Synchronous query to Groq"""
        self._wait_for_rate_limit()
        start_time = time.time()
        
        try:
            response = self._make_groq_request(prompt, model, kwargs)
            response_time = time.time() - start_time
            self._record_request()
            
            return APIResponse(
                content=response['choices'][0]['message']['content'],
                provider=APIProvider.GROQ,
                model=model,
                usage_tokens=response.get('usage', {}).get('total_tokens'),
                response_time=response_time,
                metadata={"finish_reason": response['choices'][0].get('finish_reason')}
            )
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise APIError(f"Groq request failed: {e}", APIProvider.GROQ)
    
    def _make_groq_request(self, prompt: str, model: str, kwargs: Dict):
        """Make the actual Groq API request"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise APIError(
                f"Groq API returned status {response.status_code}: {response.text}",
                APIProvider.GROQ,
                response.status_code
            )
        
        return response.json()

class APIManager:
    """
    Central manager for all AI API interactions
    
    This class acts as the unified interface for your consciousness testing framework
    to communicate with different AI providers. It handles:
    - Multiple provider support (OpenAI, Anthropic, etc.)
    - Automatic retry logic with exponential backoff
    - Rate limiting across all providers
    - Error handling and graceful degradation
    - Configuration management
    """
    
    def __init__(self, config_path: str = "config/api_config.yaml"):
        """
        Initialize the API Manager
        
        Args:
            config_path: Path to the API configuration file
        """
        # Try to load config from file, but don't fail if it doesn't exist
        try:
            self.config = self._load_config(config_path)
        except:
            self.config = {}
            logger.info("No config file found, using environment variables only")
        
        self.clients: Dict[APIProvider, BaseAPIClient] = {}
        self._initialize_clients()  # This will check environment variables
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                
            # Replace environment variables
            def replace_env_vars(obj):
                if isinstance(obj, dict):
                    return {k: replace_env_vars(v) for k, v in obj.items()}
                elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
                    env_var = obj[2:-1]  # Remove ${ and }
                    return os.getenv(env_var, obj)
                else:
                    return obj
                    
            return replace_env_vars(config)
            
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}")
            return {}
    
    def _initialize_clients(self):
        """Initialize API clients for each configured provider"""
        
        # First try to initialize from config file
        if 'openai' in self.config:
            openai_config = self.config['openai']
            if openai_config.get('api_key'):
                rate_limit = RateLimitConfig(
                    requests_per_minute=openai_config.get('rate_limit', 60)
                )
                self.clients[APIProvider.OPENAI] = OpenAIClient(
                    openai_config['api_key'], 
                    rate_limit
                )
                logger.info("OpenAI client initialized from config")
        
        if 'anthropic' in self.config:
            anthropic_config = self.config['anthropic']
            if anthropic_config.get('api_key'):
                rate_limit = RateLimitConfig(
                    requests_per_minute=anthropic_config.get('rate_limit', 60)
                )
                self.clients[APIProvider.ANTHROPIC] = AnthropicClient(
                    anthropic_config['api_key'], 
                    rate_limit
                )
                logger.info("Anthropic client initialized from config")

        if 'grok' in self.config:
            grok_config = self.config['grok']
            if grok_config.get('api_key'):
                rate_limit = RateLimitConfig(
                    requests_per_minute=grok_config.get('rate_limit', 60)
                )
                self.clients[APIProvider.GROK] = GrokClient(
                    grok_config['api_key'], 
                    rate_limit
                )
                logger.info("Grok client initialized from config")
        
        if 'groq' in self.config:
            groq_config = self.config['groq']
            if groq_config.get('api_key'):
                rate_limit = RateLimitConfig(
                    requests_per_minute=groq_config.get('rate_limit', 30)
                )
                self.clients[APIProvider.GROQ] = GroqClient(
                    groq_config['api_key'], 
                    rate_limit
                )
                logger.info("Groq client initialized from config")
        
        # Now also check environment variables (these override config file)
        # Check for OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here' and len(openai_key) > 10:
            if APIProvider.OPENAI not in self.clients:  # Only if not already initialized
                rate_limit = RateLimitConfig(requests_per_minute=60)
                self.clients[APIProvider.OPENAI] = OpenAIClient(openai_key, rate_limit)
                logger.info("OpenAI client initialized from environment")
        
        # Check for Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key and anthropic_key != 'your_anthropic_api_key_here' and len(anthropic_key) > 10:
            if APIProvider.ANTHROPIC not in self.clients:
                rate_limit = RateLimitConfig(requests_per_minute=60)
                self.clients[APIProvider.ANTHROPIC] = AnthropicClient(anthropic_key, rate_limit)
                logger.info("Anthropic client initialized from environment")
        
        # Check for Grok
        grok_key = os.getenv('GROK_API_KEY')
        if grok_key and grok_key != 'your_grok_api_key_here' and len(grok_key) > 10:
            if APIProvider.GROK not in self.clients:
                rate_limit = RateLimitConfig(requests_per_minute=60)
                self.clients[APIProvider.GROK] = GrokClient(grok_key, rate_limit)
                logger.info("Grok client initialized from environment")
        
        # CHECK FOR GROQ - THIS IS THE KEY PART!
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key and groq_key != 'your_groq_api_key_here' and len(groq_key) > 10:
            if APIProvider.GROQ not in self.clients:
                rate_limit = RateLimitConfig(requests_per_minute=30)  # Groq has lower rate limits
                self.clients[APIProvider.GROQ] = GroqClient(groq_key, rate_limit)
                logger.info("Groq client initialized from environment")
                logger.info(f"Groq API key detected: {groq_key[:10]}...{groq_key[-4:]}")
        else:
            logger.debug(f"Groq client NOT initialized. Key found: {bool(groq_key)}, Key value: {groq_key[:20] if groq_key else 'None'}...")

    async def query_model_async(self, model_name: str, prompt: str, **kwargs) -> APIResponse:
        """
        Query a specific model asynchronously with retry logic
        
        Args:
            model_name: Name of the model (e.g., 'gpt-4', 'claude-3-opus')
            prompt: The prompt to send to the model
            **kwargs: Additional parameters for the API call
            
        Returns:
            APIResponse object with the model's response
        """
        provider, model = self._parse_model_name(model_name)
        client = self._get_client(provider)
        
        # Implement retry logic with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                response = await client.query_async(prompt, model, **kwargs)
                logger.info(f"Successfully queried {model_name} (attempt {attempt + 1})")
                return response
                
            except APIError as e:
                if attempt == self.max_retries:
                    logger.error(f"All retry attempts failed for {model_name}: {e}")
                    raise
                    
                # Calculate delay with exponential backoff
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed for {model_name}, retrying in {delay}s")
                await asyncio.sleep(delay)
    
    def query_model_sync(self, model_name: str, prompt: str, **kwargs) -> APIResponse:
        """
        Query a specific model synchronously with retry logic
        
        This is the main method your consciousness tests will use.
        """
        provider, model = self._parse_model_name(model_name)
        client = self._get_client(provider)
        
        # Implement retry logic with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                response = client.query_sync(prompt, model, **kwargs)
                logger.info(f"Successfully queried {model_name} (attempt {attempt + 1})")
                return response
                
            except APIError as e:
                if attempt == self.max_retries:
                    logger.error(f"All retry attempts failed for {model_name}: {e}")
                    raise
                    
                # Calculate delay with exponential backoff
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed for {model_name}, retrying in {delay}s")
                time.sleep(delay)
    
    def _parse_model_name(self, model_name: str) -> tuple[APIProvider, str]:
        """Parse model name to determine provider and model"""
        model_name_lower = model_name.lower()
        
        if any(name in model_name_lower for name in ['llama', 'mixtral', 'gemma', 'deepseek']):
            return APIProvider.GROQ, model_name
        elif any(name in model_name_lower for name in ['gpt', 'davinci', 'curie', 'babbage']):
            return APIProvider.OPENAI, model_name
        elif 'claude' in model_name_lower:
            if 'claude-3-opus' in model_name_lower:
                return APIProvider.ANTHROPIC, 'claude-3-opus-20240229'
            elif 'claude-3-sonnet' in model_name_lower:
                return APIProvider.ANTHROPIC, 'claude-3-sonnet-20240229'
            else:
                return APIProvider.ANTHROPIC, model_name
        elif 'grok' in model_name_lower:
            return APIProvider.GROK, model_name
        else:
            # Default fallback - try to determine by checking available clients
            if APIProvider.GROQ in self.clients:
                # Check if it might be a Groq model
                return APIProvider.GROQ, model_name
            raise ValueError(f"Unknown model: {model_name}")
    
    def _get_client(self, provider: APIProvider) -> BaseAPIClient:
        """Get the appropriate client for a provider"""
        if provider not in self.clients:
            raise ValueError(f"No client configured for provider: {provider}")
        return self.clients[provider]
    
    def get_available_models(self) -> Dict[APIProvider, List[str]]:
        """Get list of available models for each provider"""
        available_models = {}
        
        for provider, client in self.clients.items():
            if provider == APIProvider.OPENAI:
                available_models[provider] = ['gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4']
            elif provider == APIProvider.ANTHROPIC:
                available_models[provider] = ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
            elif provider == APIProvider.GROQ:
                available_models[provider] = [
                    'llama-3.1-8b-instant',
                    'gemma2-9b-it',
                    'mixtral-8x7b-32768',
                    'llama-3.1-70b-versatile',
                    'deepseek-r1-distill-llama-70b'
                ]
            elif provider == APIProvider.GROK:
                available_models[provider] = ['grok-beta', 'grok-2-mini-beta']
        
        logger.info(f"Available models by provider: {available_models}")
        return available_models

    def health_check(self) -> Dict[APIProvider, bool]:
        """Check if all configured APIs are healthy"""
        health_status = {}
        
        for provider, client in self.clients.items():
            try:
                test_prompt = "Hello, please respond with 'API is working'"
                if provider == APIProvider.OPENAI:
                    response = client.query_sync(test_prompt, "gpt-3.5-turbo")
                elif provider == APIProvider.ANTHROPIC:
                    response = client.query_sync(test_prompt, "claude-3-sonnet-20240229")
                elif provider == APIProvider.GROQ:
                    response = client.query_sync(test_prompt, "llama-3.1-8b-instant")
                elif provider == APIProvider.GROK:
                    response = client.query_sync(test_prompt, "grok-beta")
                
                health_status[provider] = True
                logger.info(f"{provider.value} API is healthy")
                
            except Exception as e:
                health_status[provider] = False
                logger.error(f"{provider.value} API health check failed: {e}")
        
        return health_status

# Example usage and testing
if __name__ == "__main__":
    # This would be used for testing the API Manager
    async def test_api_manager():
        """Test function to verify API Manager functionality"""
        
        # Initialize API Manager
        try:
            api_manager = APIManager("config/api_config.yaml")
            
            # Check health
            health = api_manager.health_check()
            print(f"API Health Status: {health}")
            
            # Test a simple query
            test_prompt = "What is consciousness? Please provide a brief definition."
            
            # Test synchronous query
            response = api_manager.query_model_sync("gpt-4", test_prompt)
            print(f"Response from GPT-4: {response.content[:100]}...")
            
            # Test asynchronous query
            response = await api_manager.query_model_async("claude-3-opus", test_prompt)
            print(f"Response from Claude: {response.content[:100]}...")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run the test
    # asyncio.run(test_api_manager())
    print("API Manager implementation complete. Run test_api_manager() to verify functionality.")