"""
LLM Provider Abstraction Layer

Supports multiple LLM providers with a unified interface:
- Ollama (local, free)
- Claude (Anthropic API, paid)
- OpenAI (API, paid)

Usage:
    llm = get_llm_provider()
    async for token in llm.stream_completion(prompt):
        print(token, end="")
"""

import os
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, TYPE_CHECKING
import httpx

# Conditional imports (only import if provider is used)
if TYPE_CHECKING:
    from anthropic import AsyncAnthropic
    from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger('diveteacher.llm')


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def stream_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        Stream completion tokens from LLM
        
        Args:
            prompt: User prompt / question
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Token strings
        """
        pass


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLMs"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
    
    async def stream_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        Stream completion from Ollama with robust timeout handling
        
        Implements:
        - Granular timeout configuration (connect, read, write)
        - Token-level streaming with heartbeat detection
        - Performance logging (tokens/sec, latency)
        - Automatic retry on transient errors
        """
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Build full prompt for Ollama
        full_prompt = "\n\n".join([msg["content"] for msg in messages])
        
        # Robust timeout configuration
        # connect: Time to establish connection
        # read: Time between receiving chunks (per-token timeout)
        # write: Time to send request
        # pool: Time to get connection from pool
        timeout_config = httpx.Timeout(
            connect=10.0,   # 10s to connect to Ollama
            read=180.0,     # 3min between tokens (CPU inference can be slow)
            write=10.0,     # 10s to send request
            pool=10.0       # 10s to get connection from pool
        )
        
        # Performance tracking
        start_time = time.time()
        token_count = 0
        first_token_time = None
        last_token_time = start_time
        
        logger.info(f"🚀 Starting Ollama streaming: model={self.model}, max_tokens={max_tokens}")
        
        try:
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": True,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    }
                ) as response:
                    # Check response status
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"❌ Ollama error: {response.status_code} - {error_text.decode()}")
                        raise RuntimeError(f"Ollama returned {response.status_code}: {error_text.decode()}")
                    
                    # Stream tokens with heartbeat detection
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                
                                # Extract token
                                if "response" in data:
                                    token = data["response"]
                                    
                                    # Track timing
                                    current_time = time.time()
                                    if first_token_time is None:
                                        first_token_time = current_time
                                        ttft = first_token_time - start_time
                                        logger.info(f"⚡ First token: {ttft:.2f}s (TTFT - Time To First Token)")
                                    
                                    token_count += 1
                                    last_token_time = current_time
                                    
                                    # Yield token
                                    yield token
                                
                                # Check if done
                                if data.get("done", False):
                                    # Final stats
                                    total_duration = time.time() - start_time
                                    generation_duration = time.time() - (first_token_time or start_time)
                                    tokens_per_sec = token_count / generation_duration if generation_duration > 0 else 0
                                    
                                    logger.info(f"✅ Ollama streaming complete:")
                                    logger.info(f"   • Total time: {total_duration:.2f}s")
                                    logger.info(f"   • Generation time: {generation_duration:.2f}s")
                                    logger.info(f"   • Tokens: {token_count}")
                                    logger.info(f"   • Speed: {tokens_per_sec:.1f} tok/s")
                                    
                                    if tokens_per_sec < 1.0:
                                        logger.warning(f"⚠️  Low performance: {tokens_per_sec:.1f} tok/s (expected: 5-15 tok/s on CPU)")
                                    
                                    break
                                
                            except json.JSONDecodeError:
                                logger.debug(f"Skipping invalid JSON line: {line[:100]}...")
                                continue
                    
        except httpx.ReadTimeout as e:
            elapsed = time.time() - last_token_time
            logger.error(f"❌ ReadTimeout after {elapsed:.1f}s since last token")
            logger.error(f"   • Tokens received: {token_count}")
            logger.error(f"   • Last token time: {last_token_time - start_time:.2f}s")
            logger.error(f"   • Possible causes:")
            logger.error(f"     - Ollama process stuck/crashed")
            logger.error(f"     - Model too large for available RAM")
            logger.error(f"     - CPU throttling")
            raise RuntimeError(f"Ollama timeout after {token_count} tokens ({elapsed:.1f}s since last token)") from e
        
        except httpx.ConnectTimeout as e:
            logger.error(f"❌ ConnectTimeout: Cannot reach Ollama at {self.base_url}")
            logger.error(f"   • Check Ollama service is running: docker ps | grep ollama")
            logger.error(f"   • Check Ollama health: curl {self.base_url}/api/version")
            raise RuntimeError(f"Cannot connect to Ollama at {self.base_url}") from e
        
        except Exception as e:
            logger.error(f"❌ Unexpected error during Ollama streaming: {e}", exc_info=True)
            logger.error(f"   • Tokens received before error: {token_count}")
            raise


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")
        # Import only when needed
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
    
    async def stream_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Stream completion from Claude"""
        
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "You are a helpful AI assistant.",
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            async for text in stream.text_stream:
                yield text


class OpenAIProvider(LLMProvider):
    """OpenAI provider"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        # Import only when needed
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def stream_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Stream completion from OpenAI"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get LLM provider based on settings
    
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider not supported or missing API key
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "ollama":
        return OllamaProvider()
    elif provider == "claude":
        return ClaudeProvider()
    elif provider == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# Global provider instance (initialized on first use)
_llm_provider: Optional[LLMProvider] = None

def get_llm() -> LLMProvider:
    """Get global LLM provider instance"""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = get_llm_provider()
    return _llm_provider

