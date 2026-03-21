"""
Tests for AI Provider modules.
"""

import pytest

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


class TestGenerationRequest:
    """Tests for GenerationRequest dataclass."""

    def test_create_request(self):
        """Test creating a generation request."""
        request = GenerationRequest(
            prompt="Generate a commit message",
            max_tokens=512,
            temperature=0.3,
        )

        assert request.prompt == "Generate a commit message"
        assert request.max_tokens == 512
        assert request.temperature == 0.3

    def test_request_default_values(self):
        """Test default values in request."""
        request = GenerationRequest(prompt="test")

        assert request.max_tokens == 1024
        assert request.temperature == 0.3
        assert request.system_prompt is None


class TestGenerationResponse:
    """Tests for GenerationResponse dataclass."""

    def test_create_response(self):
        """Test creating a generation response."""
        response = GenerationResponse(
            text="feat: add feature",
            model="claude-3-sonnet-20240229",
        )

        assert response.text == "feat: add feature"
        assert response.model == "claude-3-sonnet-20240229"

    def test_response_with_usage(self):
        """Test response with usage information."""
        response = GenerationResponse(
            text="fix: bug fix",
            model="gpt-4",
            usage={"prompt_tokens": 100, "completion_tokens": 50},
        )

        assert response.usage is not None
        assert response.usage["prompt_tokens"] == 100


class TestProviderError:
    """Tests for ProviderError exception."""

    def test_error_message(self):
        """Test error message format."""
        error = ProviderError("API key invalid", "claude")
        assert "[claude]" in str(error)
        assert "API key invalid" in str(error)

    def test_error_with_original(self):
        """Test error with original exception."""
        original = ValueError("original error")
        error = ProviderError("Wrapped error", "openai", original)

        assert error.original_error is original
        assert error.provider == "openai"


class TestProviderRegistry:
    """Tests for ProviderRegistry class."""

    def test_list_providers(self):
        """Test listing registered providers."""
        providers = ProviderRegistry.list_providers()

        assert "claude" in providers
        assert "openai" in providers
        assert "ollama" in providers

    def test_get_provider_claude(self):
        """Test getting Claude provider class."""
        provider_class = ProviderRegistry.get("claude")
        assert provider_class == ClaudeProvider

    def test_get_provider_openai(self):
        """Test getting OpenAI provider class."""
        provider_class = ProviderRegistry.get("openai")
        assert provider_class == OpenAIProvider

    def test_get_provider_ollama(self):
        """Test getting Ollama provider class."""
        provider_class = ProviderRegistry.get("ollama")
        assert provider_class == OllamaProvider

    def test_get_provider_unknown(self):
        """Test getting unknown provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            ProviderRegistry.get("unknown")

    def test_get_provider_case_insensitive(self):
        """Test provider lookup is case insensitive."""
        assert ProviderRegistry.get("CLAUDE") == ClaudeProvider
        assert ProviderRegistry.get("OpenAI") == OpenAIProvider

    def test_is_registered(self):
        """Test checking if provider is registered."""
        assert ProviderRegistry.is_registered("claude") is True
        assert ProviderRegistry.is_registered("unknown") is False


class TestClaudeProvider:
    """Tests for ClaudeProvider class."""

    def test_provider_name(self):
        """Test provider name property."""
        provider = ClaudeProvider(api_key="test-key")
        assert provider.name == "Claude"

    def test_default_model(self):
        """Test default model."""
        provider = ClaudeProvider(api_key="test-key")
        assert provider.default_model == "claude-3-sonnet-20240229"

    def test_custom_model(self):
        """Test custom model."""
        provider = ClaudeProvider(api_key="test-key", model="claude-3-opus-20240229")
        assert provider.model == "claude-3-opus-20240229"

    def test_requires_api_key(self):
        """Test API key requirement."""
        provider = ClaudeProvider(api_key="test-key")
        assert provider.requires_api_key is True

    def test_validate_with_key(self):
        """Test validation with API key."""
        provider = ClaudeProvider(api_key="test-key")
        is_valid, error = provider.validate()
        assert is_valid is True
        assert error is None

    def test_validate_without_key(self):
        """Test validation without API key."""
        provider = ClaudeProvider(api_key=None)
        is_valid, error = provider.validate()
        assert is_valid is False
        assert error is not None


class TestOpenAIProvider:
    """Tests for OpenAIProvider class."""

    def test_provider_name(self):
        """Test provider name property."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.name == "OpenAI"

    def test_default_model(self):
        """Test default model."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.default_model == "gpt-4-turbo-preview"

    def test_custom_model(self):
        """Test custom model."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-3.5-turbo")
        assert provider.model == "gpt-3.5-turbo"

    def test_requires_api_key(self):
        """Test API key requirement."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.requires_api_key is True

    def test_validate_with_key(self):
        """Test validation with API key."""
        provider = OpenAIProvider(api_key="test-key")
        is_valid, error = provider.validate()
        assert is_valid is True
        assert error is None

    def test_validate_without_key(self):
        """Test validation without API key."""
        provider = OpenAIProvider(api_key=None)
        is_valid, error = provider.validate()
        assert is_valid is False
        assert error is not None


class TestOllamaProvider:
    """Tests for OllamaProvider class."""

    def test_provider_name(self):
        """Test provider name property."""
        provider = OllamaProvider()
        assert provider.name == "Ollama"

    def test_default_model(self):
        """Test default model."""
        provider = OllamaProvider()
        assert provider.default_model == "llama2"

    def test_custom_model(self):
        """Test custom model."""
        provider = OllamaProvider(model="mistral")
        assert provider.model == "mistral"

    def test_custom_host(self):
        """Test custom host."""
        provider = OllamaProvider(host="http://remote:11434")
        assert provider.host == "http://remote:11434"

    def test_requires_api_key(self):
        """Test Ollama doesn't require API key."""
        provider = OllamaProvider()
        assert provider.requires_api_key is False

    def test_validate_no_key_needed(self):
        """Test validation without API key."""
        provider = OllamaProvider()
        is_valid, error = provider.validate()
        assert is_valid is True
        assert error is None

    def test_default_host(self):
        """Test default host."""
        provider = OllamaProvider()
        assert provider.host == "http://localhost:11434"


class TestAIProviderAbstract:
    """Tests for AIProvider abstract base class."""

    def test_cannot_instantiate_abstract(self):
        """Test that AIProvider cannot be instantiated."""
        with pytest.raises(TypeError):
            AIProvider()

    def test_concrete_implementation(self):
        """Test creating a concrete implementation."""

        class TestProvider(AIProvider):
            @property
            def name(self) -> str:
                return "Test"

            @property
            def default_model(self) -> str:
                return "test-model"

            @property
            def requires_api_key(self) -> bool:
                return False

            async def generate(self, request):
                return GenerationResponse(text="test", model="test")

            async def check_availability(self) -> bool:
                return True

        provider = TestProvider()
        assert provider.name == "Test"
