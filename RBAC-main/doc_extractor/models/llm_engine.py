"""
models/llm_engine.py – Lightweight LLM for structured JSON extraction using Ollama.

Model: Ollama Llama3
  • Uses Ollama API for inference
  • No local model loading required
  • Lightweight and easy to deploy
  • Configurable via environment variables

Extraction strategy
───────────────────
We do NOT ask the LLM to look at images – it only reads the OCR text.
This keeps VRAM near zero (text-only model vs. vision model).
The prompt engineering handles all the "noisy data" problem:

  1. Explicit field descriptions are injected into the system prompt.
  2. Handwritten segments are marked [HANDWRITTEN] and told to take precedence.
  3. The LLM is told to return ONLY a JSON object and nothing else.
  4. A retry loop re-prompts with the parse error if JSON decoding fails.
"""

from __future__ import annotations

import json
import logging
import re
import os
import requests
from typing import Any

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


# ─────────────────────────────────────────────────────────────────────────────
# Prompt builder
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a high-precision document extraction engine. 
Your goal is to extract ALL key information from the provided OCR text and format it as a single JSON object.

RULES:
1. Return ONLY a valid JSON object. No markdown, no commentary.
2. Use snake_case for keys. 
3. Preferred keys for person/employee documents:
   - "full_name" (for names)
   - "email" (for email addresses)
   - "phone" (for contact numbers)
   - "designation" (for job titles/roles)
   - "employee_id" (for staff/employee IDs)
   - "joining_date" (for start/hired dates, format: YYYY-MM-DD)
4. If other information is found, create descriptive snake_case keys.
5. Text marked [HANDWRITTEN] takes PRIORITY over [PRINTED] text.
6. Dates MUST be in YYYY-MM-DD format. If a date is partial or unclear, omit it or use null.
7. Include a key "_extraction_confidence" with value "high", "medium", or "low".
"""

_USER_TEMPLATE = """\
OCR TEXT FROM DOCUMENT:
───────────────────────
{ocr_text}
───────────────────────
Extract all available information from the text above and return the JSON object.
"""

_RETRY_TEMPLATE = """\
Your previous response could not be parsed as JSON.
Parse error: {error}

Your previous response was:
{bad_response}

Please try again. Return ONLY a valid JSON object, nothing else.
"""


def _build_system() -> str:
    return _SYSTEM_PROMPT


def _extract_json_from_response(text: str) -> dict:
    """
    Try multiple strategies to extract a JSON object from LLM output:
    1. Direct parse
    2. Strip markdown code fences
    3. Regex search for first {...} block
    """
    text = text.strip()

    # Strategy 1: direct
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip code fences
    cleaned = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 3: find first { ... } block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in model response:\n{text[:500]}")


# ─────────────────────────────────────────────────────────────────────────────
# Inference
# ─────────────────────────────────────────────────────────────────────────────

class LLMEngine:
    """Wraps Ollama Llama3 for dynamic JSON extraction."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.ollama_url = OLLAMA_URL
        self.ollama_model = OLLAMA_MODEL
        logger.info(f"LLM Engine initialized with Ollama at {self.ollama_url}, model: {self.ollama_model}")

    def _run_inference(self, messages: list[dict]) -> str:
        """Run a chat-format inference via Ollama and return the raw string response."""
        
        # Convert messages to a single prompt for Ollama
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        full_prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.cfg.llm.temperature if self.cfg.llm.temperature > 0 else 0.1,
                        "num_predict": self.cfg.llm.max_new_tokens,
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Ollama inference failed: {e}")
            return ""

    def extract(self, ocr_text: str, source_format: str = "unknown") -> dict:
        """
        Given raw OCR text, return a dynamic extraction dict.
        Retries up to cfg.llm.max_retries times on JSON parse failure.
        """
        from schema import empty_record, coerce_types, validate

        system = _build_system()
        user_msg = _USER_TEMPLATE.format(ocr_text=ocr_text)

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ]

        last_error = ""
        last_response = ""

        for attempt in range(1, self.cfg.llm.max_retries + 1):
            try:
                if attempt > 1:
                    # Inject the parse error back for self-correction
                    messages.append({"role": "assistant", "content": last_response})
                    messages.append({
                        "role": "user",
                        "content": _RETRY_TEMPLATE.format(
                            error=last_error, bad_response=last_response[:400]
                        )
                    })

                raw = self._run_inference(messages)
                last_response = raw
                record = _extract_json_from_response(raw)
                record = coerce_types(record)
                record["_source_format"] = source_format

                is_valid, errors = validate(record)
                if not is_valid:
                    logger.warning(f"Schema validation issues: {errors}")

                return record

            except (ValueError, json.JSONDecodeError) as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt}/{self.cfg.llm.max_retries} failed: {e}")

        # All retries exhausted – return a null record
        logger.error("All LLM extraction attempts failed. Returning empty record.")
        fallback = empty_record(source_format)
        fallback["_extraction_confidence"] = "low"
        return fallback