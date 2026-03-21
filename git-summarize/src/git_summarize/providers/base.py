"""
Base AI Provider interface.

All AI providers must implement this abstract base class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationRequest:
    """Request for text generation."""

    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.3


@dataclass
class GenerationResponse:
    """Response from text generation."""

    text: str
    model: str
    usage: Optional[dict] = None
    raw_response: Optional[dict] = None


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    All providers must implement these methods.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the provider.

        Args:
            api_key: API key for the provider (if required)
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model or self.default_model

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider."""
        pass

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate text from the AI model.

        Args:
            request: Generation request with prompt and settings

        Returns:
            Generation response with generated text

        Raises:
            ProviderError: If generation fails
        """
        pass

    @abstractmethod
    async def check_availability(self) -> bool:
        """
        Check if the provider is available and configured.

        Returns:
            True if provider is ready to use
        """
        pass

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate provider configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.api_key is None and self.requires_api_key:
            return False, f"API key required for {self.name}"
        return True, None

    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """Return whether this provider requires an API key."""
        pass


class ProviderError(Exception):
    """Exception raised when AI provider encounters an error."""

    def __init__(self, message: str, provider: str, original_error: Optional[Exception] = None):
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.provider}] {self.message}"


class ProviderRegistry:
    """
    Registry for AI providers.

    Allows dynamic registration and lookup of providers.
    """

    _providers: dict[str, type[AIProvider]] = {}

    @classmethod
    def register(cls, name: str) -> callable:
        """
        Decorator to register a provider class.

        Usage:
            @ProviderRegistry.register("claude")
            class ClaudeProvider(AIProvider):
                ...
        """

        def decorator(provider_class: type[AIProvider]) -> type[AIProvider]:
            cls._providers[name.lower()] = provider_class
            return provider_class

        return decorator

    @classmethod
    def get(cls, name: str) -> type[AIProvider]:
        """Get a provider class by name."""
        name = name.lower()
        if name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unknown provider: {name}. Available: {available}")
        return cls._providers[name]

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered provider names."""
        return list(cls._providers.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a provider is registered."""
        return name.lower() in cls._providers
