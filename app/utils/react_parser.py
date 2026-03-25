import json
import re
import logging

logger = logging.getLogger(__name__)


def _clean_action_input(text: str) -> str:
    """Remove hallucinated conversation from action input."""
    # Cut at first newline
    text = text.split('\n')[0].strip()
    # Cut at conversation markers if LLM hallucinated future steps
    for marker in ['Observation', 'Thought:', 'Action:', '\n\n']:
        idx = text.find(marker)
        if idx > 0:
            text = text[:idx].strip()
    # Limit length
    if len(text) > 200:
        text = text[:200]
    return text


def parse_react_response(text: str) -> dict:
    thought = ""
    action = ""
    action_input_raw = ""

    thought_match = re.search(r"Thought:(.*?)(?=Action:|$)", text, re.DOTALL)
    action_match = re.search(r"Action:(.*?)(?=Action Input:|$)", text, re.DOTALL)
    action_input_match = re.search(r"Action Input:(.*)", text, re.DOTALL)

    if not any([thought_match, action_match, action_input_match]):
        return {"thought": text, "action": "", "action_input": {}, "raw": text}

    if thought_match:
        thought = thought_match.group(1).strip()
    if action_match:
        action = action_match.group(1).strip().lower().split()[0] if action_match.group(1).strip() else ""
    if action_input_match:
        action_input_raw = _clean_action_input(action_input_match.group(1).strip())

    try:
        action_input_parsed = json.loads(action_input_raw)
    except (json.JSONDecodeError, ValueError):
        logger.debug("Action Input was not valid JSON, wrapping as query: %s", action_input_raw[:100])
        # Truncate and strip any hallucinated conversation from the fallback value
        query_val = action_input_raw[:200]
        for marker in ['Observation', 'Thought']:
            idx = query_val.find(marker)
            if idx > 0:
                query_val = query_val[:idx].strip()
        action_input_parsed = {"query": query_val}

    return {
        "thought": thought,
        "action": action,
        "action_input": action_input_parsed,
        "raw": text,
    }


def format_observation(tool_name: str, result: str) -> str:
    return f"Observation [{tool_name}]: {result}\n"
