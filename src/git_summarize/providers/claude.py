"""
Anthropic Claude provider for git-summarize.
"""

import asyncio
from typing import Optional

from git_summarize.providers.base import (
    AIProvider,
    GenerationRequest,
    GenerationResponse,
    ProviderError,
    ProviderRegistry,
)


@ProviderRegistry.register("claude")
class ClaudeProvider(AIProvider):
    """
    Anthropic Claude AI provider.

    Supports Claude 3 models (Haiku, Sonnet, Opus).
    """

    @property
    def name(self) -> str:
        return "Claude"

    @property
    def default_model(self) -> str:
        return "claude-3-sonnet-20240229"

    @property
    def requires_api_key(self) -> bool:
        return True

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using Claude."""
        try:
            anthropic = self._get_client()

            message_params = {
                "model": self.model,
                "max_tokens": request.max_tokens,
                "messages": [{"role": "user", "content": request.prompt}],
            }

            if request.system_prompt:
                message_params["system"] = request.system_prompt

            if request.temperature:
                message_params["temperature"] = request.temperature

            response = await asyncio.to_thread(
                anthropic.messages.create,
                **message_params,
            )

            return GenerationResponse(
                text=response.content[0].text,
                model=self.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                raw_response=response.model_dump(),
            )

        except Exception as e:
            raise ProviderError(
                f"Failed to generate with Claude: {str(e)}",
                provider="claude",
                original_error=e,
            )

    async def check_availability(self) -> bool:
        """Check if Claude API is available."""
        if not self.api_key:
            return False

        try:
            anthropic = self._get_client()
            # Try a minimal request to check connectivity
            await asyncio.to_thread(
                anthropic.messages.create,
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "."}],
            )
            return True
        except Exception:
            return False

    def _get_client(self):
        """Get Anthropic client instance."""
        import anthropic

        return anthropic.Anthropic(api_key=self.api_key)
