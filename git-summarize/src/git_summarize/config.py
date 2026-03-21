"""
Configuration management for git-summarize.

Handles environment variables, config files, and default settings.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSettings(BaseSettings):
    """Settings for a specific AI provider."""

    host: Optional[str] = None
    model: Optional[str] = None


class OllamaSettings(ProviderSettings):
    """Ollama-specific settings."""

    host: str = "http://localhost:11434"
    model: str = "llama2"


class ClaudeSettings(ProviderSettings):
    """Claude-specific settings."""

    model: str = "claude-3-sonnet-20240229"


class OpenAISettings(ProviderSettings):
    """OpenAI-specific settings."""

    model: str = "gpt-4-turbo-preview"


class Config(BaseSettings):
    """
    Main configuration for git-summarize.

    Loads from environment variables and config file.
    Priority: Environment variables > Config file > Defaults
    """

    model_config = SettingsConfigDict(
        env_prefix="GCM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # AI Provider settings
    provider: str = Field(
        default="claude",
        description="Default AI provider (claude, openai, ollama)",
    )
    model: Optional[str] = Field(
        default=None,
        description="Model name (overrides provider default)",
    )
    num_suggestions: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of commit message suggestions to generate",
    )

    # API Keys
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude",
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key",
    )

    # Ollama settings
    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Ollama server host",
    )
    ollama_model: str = Field(
        default="llama2",
        description="Ollama model name",
    )

    # Behavior settings
    auto: bool = Field(
        default=False,
        description="Auto-select first suggestion without interaction",
    )
    preview: bool = Field(
        default=False,
        description="Preview suggestions without committing",
    )
    apply: bool = Field(
        default=False,
        description="Apply first suggestion directly",
    )

    # Provider-specific configurations
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    claude: ClaudeSettings = Field(default_factory=ClaudeSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for specified provider."""
        if provider == "claude":
            return self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        elif provider == "openai":
            return self.openai_api_key or os.getenv("OPENAI_API_KEY")
        return None  # Ollama doesn't need a key

    def get_model(self, provider: str) -> str:
        """Get model name for specified provider."""
        if self.model:
            return self.model

        if provider == "claude":
            return self.claude.model
        elif provider == "openai":
            return self.openai.model
        elif provider == "ollama":
            return self.ollama_model

        raise ValueError(f"Unknown provider: {provider}")

    def get_ollama_host(self) -> str:
        """Get Ollama host URL."""
        return self.ollama_host or self.ollama.host or "http://localhost:11434"

    @classmethod
    def load(cls) -> "Config":
        """
        Load configuration from environment and config file.

        Config file location: ~/.git-summarize/config.toml
        """
        config_file = Path.home() / ".git-summarize" / "config.toml"

        if config_file.exists():
            return cls(_env_file=".env", _env_file_encoding="utf-8")

        return cls(_env_file=".env", _env_file_encoding="utf-8")


def get_config() -> Config:
    """Get the global configuration instance."""
    return Config.load()
