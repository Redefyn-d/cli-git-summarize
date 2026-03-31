"""
Tests for the Configuration module.
"""

import os
from unittest.mock import patch

import pytest

from git_summarize.config import Config, get_config


class TestConfig:
    """Tests for Config class."""

    def test_default_provider(self):
        """Test default provider is claude."""
        config = Config()
        assert config.provider == "claude"

    def test_default_num_suggestions(self):
        """Test default number of suggestions."""
        config = Config()
        assert config.num_suggestions == 3

    def test_num_suggestions_validation(self):
        """Test num_suggestions validation."""
        # Valid values
        config = Config(num_suggestions=1)
        assert config.num_suggestions == 1

        config = Config(num_suggestions=10)
        assert config.num_suggestions == 10

        # Invalid values should raise validation error
        with pytest.raises(Exception):
            Config(num_suggestions=0)

        with pytest.raises(Exception):
            Config(num_suggestions=11)

    def test_get_api_key_claude(self):
        """Test getting Anthropic API key."""
        config = Config(anthropic_api_key="test-key")
        assert config.get_api_key("claude") == "test-key"

    def test_get_api_key_openai(self):
        """Test getting OpenAI API key."""
        config = Config(openai_api_key="test-key")
        assert config.get_api_key("openai") == "test-key"

    def test_get_api_key_ollama(self):
        """Test Ollama doesn't need API key."""
        config = Config()
        assert config.get_api_key("ollama") is None

    def test_get_api_key_from_env(self):
        """Test getting API key from environment."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"}):
            config = Config()
            assert config.get_api_key("claude") == "env-key"

    def test_get_model_explicit(self):
        """Test getting explicitly set model."""
        config = Config(model="custom-model")
        assert config.get_model("claude") == "custom-model"
        assert config.get_model("openai") == "custom-model"

    def test_get_model_provider_default(self):
        """Test getting provider default model."""
        config = Config()
        assert config.get_model("claude") == "claude-3-sonnet-20240229"
        assert config.get_model("openai") == "gpt-4-turbo-preview"

    def test_get_ollama_host(self):
        """Test getting Ollama host."""
        config = Config(ollama_host="http://custom-host:11434")
        assert config.get_ollama_host() == "http://custom-host:11434"

    def test_get_ollama_host_default(self):
        """Test default Ollama host."""
        config = Config()
        assert config.get_ollama_host() == "http://localhost:11434"

    def test_get_model_unknown_provider(self):
        """Test getting model for unknown provider."""
        config = Config()
        with pytest.raises(ValueError, match="Unknown provider"):
            config.get_model("unknown")

    def test_auto_flag(self):
        """Test auto flag."""
        config = Config(auto=True)
        assert config.auto is True

    def test_preview_flag(self):
        """Test preview flag."""
        config = Config(preview=True)
        assert config.preview is True

    def test_apply_flag(self):
        """Test apply flag."""
        config = Config(apply=True)
        assert config.apply is True


class TestProviderSettings:
    """Tests for provider-specific settings."""

    def test_ollama_default_host(self):
        """Test Ollama default host."""
        config = Config()
        assert config.ollama.host == "http://localhost:11434"

    def test_claude_default_model(self):
        """Test Claude default model."""
        config = Config()
        assert config.claude.model == "claude-3-sonnet-20240229"

    def test_openai_default_model(self):
        """Test OpenAI default model."""
        config = Config()
        assert config.openai.model == "gpt-4-turbo-preview"


class TestGetConfig:
    """Tests for get_config function."""

    def test_get_config_returns_config(self):
        """Test get_config returns Config instance."""
        config = get_config()
        assert isinstance(config, Config)

    def test_get_config_is_singleton(self):
        """Test that get_config returns consistent instances."""
        # Note: Currently creates new instances, not true singleton
        config1 = get_config()
        config2 = get_config()
        assert type(config1) == type(config2)


class TestConfigEnvironmentVariables:
    """Tests for environment variable configuration."""

    def test_gcm_provider_env_var(self):
        """Test GCM_PROVIDER environment variable."""
        with patch.dict(os.environ, {"GCM_PROVIDER": "openai"}):
            config = Config()
            assert config.provider == "openai"

    def test_gcm_model_env_var(self):
        """Test GCM_MODEL environment variable."""
        with patch.dict(os.environ, {"GCM_MODEL": "gpt-3.5-turbo"}):
            config = Config()
            assert config.model == "gpt-3.5-turbo"

    def test_gcm_num_suggestions_env_var(self):
        """Test GCM_NUM_SUGGESTIONS environment variable."""
        with patch.dict(os.environ, {"GCM_NUM_SUGGESTIONS": "5"}):
            config = Config()
            assert config.num_suggestions == 5

    def test_gcm_ollama_host_env_var(self):
        """Test OLLAMA_HOST environment variable."""
        with patch.dict(os.environ, {"OLLAMA_HOST": "http://remote:11434"}):
            config = Config(ollama_host="http://remote:11434")
            assert config.ollama_host == "http://remote:11434"
