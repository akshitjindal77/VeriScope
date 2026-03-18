from abc import ABC, abstractmethod
from typing import Optional

from app.models.research_models import LLMResponse


class LLMProvider(ABC):
    """Abstract base class for LLM backends.

    All concrete providers (e.g. Mistral, OpenAI, Ollama) must implement
    this interface so the rest of the application can treat them uniformly.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Send a prompt to the LLM and return a standardized response.

        Args:
            prompt: The user-facing message to send to the model.
            system: Optional system prompt that sets the model's role or
                    behaviour before the user turn.
            temperature: Controls output randomness. 0.0 is fully
                         deterministic; 1.0 is highly creative. Pass None
                         to fall back to the value in application settings.
            max_tokens: Maximum number of tokens the model may generate.
                        Pass None to fall back to the value in application
                        settings.

        Returns:
            An LLMResponse containing the generated text, the model name,
            and (if reported by the backend) the total tokens consumed.
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Health-check that indicates whether the backend is reachable.

        Returns:
            True if the provider can accept requests; False otherwise.
        """
        raise NotImplementedError
