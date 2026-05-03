from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.models.research_models import LLMResponse
from app.providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    def __init__(self, settings):
        self.settings = settings

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        messages = []
        if system is not None:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.settings.GROQ_MODEL,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.settings.LLM_TEMPERATURE,
            "max_tokens": max_tokens if max_tokens is not None else self.settings.LLM_MAX_TOKENS,
        }

        headers = {
            "Authorization": f"Bearer {self.settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.LLM_TIMEOUT_S) as client:
                r = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )
                r.raise_for_status()
                data = r.json()

            text = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens")
            return LLMResponse(
                text=text,
                model=self.settings.GROQ_MODEL,
                tokens_used=tokens_used,
            )

        except httpx.HTTPError as e:
            logger.error(f"Groq API error: {e}")
            return LLMResponse(text="", model=self.settings.GROQ_MODEL)
        except Exception as e:
            logger.error(f"Unexpected error in GroqProvider: {e}")
            return LLMResponse(text="", model=self.settings.GROQ_MODEL)

    async def is_available(self) -> bool:
        headers = {
            "Authorization": f"Bearer {self.settings.GROQ_API_KEY}",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers=headers,
                )
                return r.status_code == 200
        except Exception:
            return False