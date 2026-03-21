"""
OpenAI provider for git-summarize.
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


@ProviderRegistry.register("openai")
class OpenAIProvider(AIProvider):
    """
    OpenAI GPT provider.

    Supports GPT-3.5, GPT-4, and newer models.
    """

    @property
    def name(self) -> str:
        return "OpenAI"

    @property
    def default_model(self) -> str:
        return "gpt-4-turbo-preview"

    @property
    def requires_api_key(self) -> bool:
        return True

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using OpenAI."""
        try:
            client = self._get_client()

            messages = []

            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})

            messages.append({"role": "user", "content": request.prompt})

            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )

            return GenerationResponse(
                text=response.choices[0].message.content,
                model=self.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                raw_response=response.model_dump(),
            )

        except Exception as e:
            raise ProviderError(
                f"Failed to generate with OpenAI: {str(e)}",
                provider="openai",
                original_error=e,
            )

    async def check_availability(self) -> bool:
        """Check if OpenAI API is available."""
        if not self.api_key:
            return False

        try:
            client = self._get_client()
            # Try a minimal request to check connectivity
            await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "."}],
            )
            return True
        except Exception:
            return False

    def _get_client(self):
        """Get OpenAI client instance."""
        import openai

        return openai.OpenAI(api_key=self.api_key)
