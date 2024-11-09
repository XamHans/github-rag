# ai_provider.py
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import ollama
import openai
from openai import OpenAI


@dataclass
class ChatMessage:
    role: str
    content: str

@dataclass
class ChatResponse:
    content: str
    raw_response: Any  # Store the original response from the provider

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for given texts"""
        pass
    
    @abstractmethod
    async def chat_completion(self, 
                            messages: List[ChatMessage], 
                            max_tokens: int = 1000,
                            temperature: float = 0.1) -> ChatResponse:
        """Generate chat completion"""
        pass

class OpenAIProvider(AIProvider):
    """OpenAI implementation"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, headers: Optional[Dict] = None):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=headers
        )
        logging.info("Initialized OpenAI provider")

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            response = self.client.embeddings.create(
                input=texts,
                model="text-embedding-ada-002"
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logging.error(f"Error generating OpenAI embeddings: {str(e)}")
            raise

    async def chat_completion(self, 
                            messages: List[ChatMessage],
                            max_tokens: int = 1000,
                            temperature: float = 0.1) -> ChatResponse:
        try:
            formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                n=1
            )
            return ChatResponse(
                content=response.choices[0].message.content.strip(),
                raw_response=response
            )
        except Exception as e:
            logging.error(f"Error in OpenAI chat completion: {str(e)}")
            raise

class OllamaProvider(AIProvider):
    """Ollama implementation"""
    
    def __init__(self, embedding_model: str = "nomic-embed-text", chat_model: str = "llama3"):
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        logging.info(f"Initialized Ollama provider with embedding model {embedding_model} and chat model {chat_model}")

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = []
            for text in texts:
                response = ollama.embeddings(
                    model=self.embedding_model,
                    prompt=text
                )
                embeddings.append(response['embedding'])
            return embeddings
        except Exception as e:
            logging.error(f"Error generating Ollama embeddings: {str(e)}")
            raise

    async def chat_completion(self, 
                            messages: List[ChatMessage],
                            max_tokens: int = 1000,
                            temperature: float = 0.1) -> ChatResponse:
        try:
            # Convert messages to Ollama format
            formatted_messages = []
            for msg in messages:
                if msg.role == "system":
                    formatted_messages.append({"role": "system", "content": msg.content})
                else:
                    formatted_messages.append({"role": "user" if msg.role == "user" else "assistant", 
                                            "content": msg.content})
            
            response = ollama.chat(
                model=self.chat_model,
                messages=formatted_messages,
                stream=False
            )
            logging.info(f"Ollama chat response: {response}")
            
            return ChatResponse(
                content=response['message']['content'].strip(),
                raw_response=response
            )
        except Exception as e:
            logging.error(f"Error in Ollama chat completion: {str(e)}")
            raise

# Factory for creating AI providers
def create_ai_provider(provider_type: str, **kwargs) -> AIProvider:
    
    """
    Factory function to create AI provider instances
    
    Args:
        provider_type: 'openai' or 'ollama'
        **kwargs: Provider-specific configuration
    """
    if provider_type.lower() == 'openai':
        required_keys = ['api_key']
        if not all(key in kwargs for key in required_keys):
            raise ValueError(f"OpenAI provider requires these parameters: {required_keys}")
        return OpenAIProvider(**kwargs)
    
    elif provider_type.lower() == 'ollama':
        return OllamaProvider(**kwargs)
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
    

# Initialize AI provider based on environment variable
def initialize_ai_provider() -> AIProvider:
    provider_type = os.getenv("AI_PROVIDER", "ollama").lower()
    
    if provider_type == "openai":
        return create_ai_provider(
            "openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    elif provider_type == "ollama":
        return create_ai_provider(
            "ollama",
            embedding_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            chat_model=os.getenv("OLLAMA_CHAT_MODEL", "llama3")
        )
    else:
        raise ValueError(f"Unsupported AI provider: {provider_type}")