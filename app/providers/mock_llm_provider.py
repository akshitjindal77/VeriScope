from typing import Optional

from app.models.research_models import LLMResponse
from app.providers.llm_provider import LLMProvider


class MockLLMProvider(LLMProvider):
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        return LLMResponse(
            text=f"Mock synthesis for prompt: {prompt[:100]}",
            model="mock",
            tokens_used=0,
        )

    def is_available(self) -> bool:
        return True
