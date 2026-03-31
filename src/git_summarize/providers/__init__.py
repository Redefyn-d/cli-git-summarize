"""
AI Provider Layer for git-summarize.

Provides swappable backends for different AI models:
- Claude (Anthropic)
- OpenAI (GPT models)
- Ollama (Local models)
- Gemini (Google)
"""

from git_summarize.providers.base import (
    AIProvider,
    GenerationRequest,
    GenerationResponse,
    ProviderError,
    ProviderRegistry,
)
from git_summarize.providers.claude import ClaudeProvider
from git_summarize.providers.openai import OpenAIProvider
from git_summarize.providers.ollama import OllamaProvider
from git_summarize.providers.gemini import GeminiProvider

__all__ = [
    "AIProvider",
    "ProviderRegistry",
    "ProviderError",
    "GenerationRequest",
    "GenerationResponse",
    "ClaudeProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "GeminiProvider",
]
