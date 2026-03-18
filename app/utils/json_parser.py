import json
import logging

logger = logging.getLogger(__name__)


def parse_llm_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1:
            text = text[first_brace:last_brace + 1]

    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace == -1 or last_brace == -1:
        logger.warning("No JSON object found in LLM response: %s", text[:200])
        return {}

    text = text[first_brace:last_brace + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON from LLM response: %s", text[:200])
        return {}
