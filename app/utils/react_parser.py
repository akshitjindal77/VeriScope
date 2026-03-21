import json
import re
import logging

logger = logging.getLogger(__name__)


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
        action_input_raw = action_input_match.group(1).strip()

    try:
        action_input_parsed = json.loads(action_input_raw)
    except (json.JSONDecodeError, ValueError):
        logger.debug("Action Input was not valid JSON, wrapping as query: %s", action_input_raw[:100])
        action_input_parsed = {"query": action_input_raw}

    return {
        "thought": thought,
        "action": action,
        "action_input": action_input_parsed,
        "raw": text,
    }


def format_observation(tool_name: str, result: str) -> str:
    return f"Observation [{tool_name}]: {result}\n"
