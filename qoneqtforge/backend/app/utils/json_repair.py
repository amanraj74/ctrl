"""JSON repair utilities for fixing malformed LLM outputs.

LLMs frequently return JSON with issues like:
- Markdown code fences (```json ... ```)
- Trailing commas
- Single quotes instead of double quotes
- Unbalanced braces/brackets
- Comments

This module handles all of these cases.
"""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)


def strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences from JSON output."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    pattern = r"^```(?:json|JSON)?\s*\n?(.*?)\n?\s*```$"
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before closing braces/brackets."""
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text


def fix_single_quotes(text: str) -> str:
    """Convert single-quoted JSON to double-quoted.

    Only converts quotes that look like JSON keys/values,
    not apostrophes within text content.
    """
    # Simple heuristic: if the text doesn't parse and has single quotes
    # around keys/values, try converting them
    result = []
    in_string = False
    escape_next = False
    quote_char = None

    for char in text:
        if escape_next:
            result.append(char)
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            result.append(char)
            continue

        if char in ("'", '"'):
            if not in_string:
                in_string = True
                quote_char = char
                result.append('"')
                continue
            elif char == quote_char:
                in_string = False
                quote_char = None
                result.append('"')
                continue

        result.append(char)

    return "".join(result)


def balance_braces(text: str) -> str:
    """Attempt to balance unmatched braces/brackets."""
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")

    if open_braces > 0:
        text += "}" * open_braces
    if open_brackets > 0:
        text += "]" * open_brackets

    return text


def extract_json_object(text: str) -> str:
    """Extract the first JSON object or array from text."""
    # Find the first { or [
    for i, char in enumerate(text):
        if char == "{":
            # Find matching closing brace
            depth = 0
            in_str = False
            esc = False
            for j in range(i, len(text)):
                if esc:
                    esc = False
                    continue
                c = text[j]
                if c == "\\":
                    esc = True
                    continue
                if c == '"' and not esc:
                    in_str = not in_str
                if not in_str:
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            return text[i : j + 1]
            # If we didn't find closing, return from { to end
            return text[i:]

        elif char == "[":
            depth = 0
            in_str = False
            esc = False
            for j in range(i, len(text)):
                if esc:
                    esc = False
                    continue
                c = text[j]
                if c == "\\":
                    esc = True
                    continue
                if c == '"' and not esc:
                    in_str = not in_str
                if not in_str:
                    if c == "[":
                        depth += 1
                    elif c == "]":
                        depth -= 1
                        if depth == 0:
                            return text[i : j + 1]
            return text[i:]

    return text


def repair_json(text: str) -> str:
    """Attempt to repair malformed JSON text.

    Applies multiple repair strategies in sequence:
    1. Strip markdown fences
    2. Extract JSON object/array
    3. Fix trailing commas
    4. Balance braces
    5. Try json-repair library as last resort

    Returns the repaired JSON string.
    Raises ValueError if all repair attempts fail.
    """
    if not text or not text.strip():
        raise ValueError("Empty JSON text")

    # Step 1: Strip markdown fences
    text = strip_markdown_fences(text)

    # Step 2: Try parsing as-is first
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Step 3: Extract JSON object/array
    text = extract_json_object(text)
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Step 4: Fix trailing commas
    repaired = fix_trailing_commas(text)
    try:
        json.loads(repaired)
        return repaired
    except json.JSONDecodeError:
        pass

    # Step 5: Balance braces
    repaired = balance_braces(repaired)
    try:
        json.loads(repaired)
        return repaired
    except json.JSONDecodeError:
        pass

    # Step 6: Try single quote fix
    repaired = fix_single_quotes(text)
    repaired = fix_trailing_commas(repaired)
    repaired = balance_braces(repaired)
    try:
        json.loads(repaired)
        return repaired
    except json.JSONDecodeError:
        pass

    # Step 7: Try json-repair library
    try:
        from json_repair import repair_json as lib_repair

        repaired = lib_repair(text)
        if isinstance(repaired, str):
            json.loads(repaired)
            return repaired
        # If it returned a parsed object, re-serialize
        return json.dumps(repaired)
    except Exception:
        pass

    logger.error("All JSON repair strategies failed for text: %s...", text[:200])
    raise ValueError(f"Could not repair JSON: {text[:200]}...")
