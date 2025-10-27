"""
Custom LLM Client pour gpt-5-nano avec max_completion_tokens

Ce client hérite de OpenAIClient de Graphiti et adapte les appels API
pour utiliser max_completion_tokens au lieu de max_tokens, nécessaire
pour certains modèles OpenAI comme gpt-5-nano.
"""
import logging
from typing import Type, Optional, Any
from pydantic import BaseModel
from openai import AsyncOpenAI

from graphiti_core.llm_client import OpenAIClient, LLMConfig

logger = logging.getLogger('diveteacher.custom_llm')


class Gpt5NanoClient(OpenAIClient):
    """
    Custom OpenAI Client pour gpt-5-nano
    
    Différences avec OpenAIClient standard:
    - Utilise max_completion_tokens au lieu de max_tokens
    - Compatible avec l'API gpt-5-nano (Responses/Assistants API)
    
    Note:
        gpt-5-nano nécessite max_completion_tokens selon la doc OpenAI:
        https://platform.openai.com/docs/assistants/deep-dive/max-completion-and-max-prompt-tokens
    """
    
    def __init__(self, config: LLMConfig, client: AsyncOpenAI):
        """
        Initialize custom client
        
        Args:
            config: LLM configuration with model settings
            client: AsyncOpenAI client instance
        """
        super().__init__(config=config, client=client)
        logger.info(f"🔧 Initialized Gpt5NanoClient for model: {config.model}")
        logger.info(f"   Using max_completion_tokens instead of max_tokens")
    
    async def _generate_response(
        self,
        messages: list[dict[str, str]],
        response_model: Optional[Type[BaseModel]] = None,
        max_tokens: Optional[int] = None,
        model_size: str = 'large'
    ) -> Any:
        """
        Generate response with max_completion_tokens override
        
        Cette méthode override celle du parent pour remplacer max_tokens
        par max_completion_tokens avant l'appel OpenAI.
        
        Args:
            messages: Chat messages
            response_model: Optional Pydantic model for structured output
            max_tokens: Maximum tokens to generate (will be converted to max_completion_tokens)
            model_size: Model size hint ('large' or 'small')
            
        Returns:
            Generated response (structured if response_model provided)
        """
        # ════════════════════════════════════════════════════════
        # CONVERSION max_tokens → max_completion_tokens
        # ════════════════════════════════════════════════════════
        
        # Utiliser max_tokens fourni ou celui du config
        tokens_limit = max_tokens or getattr(self.config, 'max_tokens', None)
        
        # Choisir le bon modèle selon model_size
        model = self.config.model if model_size == 'large' else self.config.small_model
        
        # Préparer les paramètres pour l'appel API
        api_params = {
            'model': model,
            'messages': messages
        }
        
        # ✅ Utiliser max_completion_tokens au lieu de max_tokens
        if tokens_limit:
            api_params['max_completion_tokens'] = tokens_limit
            logger.debug(f"Using max_completion_tokens={tokens_limit} for {model}")
        
        # Appel API avec structured output si response_model fourni
        if response_model:
            logger.debug(f"Calling OpenAI beta.chat.completions.parse with response_model")
            response = await self.client.beta.chat.completions.parse(
                response_format=response_model,
                **api_params
            )
            parsed_obj = response.choices[0].message.parsed
            
            # ✅ Graphiti attend un dict, pas un objet Pydantic!
            # Convertir l'objet Pydantic en dict
            if hasattr(parsed_obj, 'model_dump'):
                return parsed_obj.model_dump()
            elif hasattr(parsed_obj, 'dict'):
                return parsed_obj.dict()
            else:
                return parsed_obj
        else:
            logger.debug(f"Calling OpenAI chat.completions.create")
            response = await self.client.chat.completions.create(**api_params)
            return response.choices[0].message.content

