from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from .config import LLMConfig


class LLMError(RuntimeError):
    pass


class DeepSeekClient:
    def __init__(self, config: LLMConfig):
        if not config.api_key:
            raise LLMError("DEEPSEEK_API_KEY is required for non-mock LLM execution.")
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=model or self.config.default_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            response_format={"type": "json_object"},
            extra_body={"thinking": {"type": "disabled"}},
        )
        content = response.choices[0].message.content or ""
        return _parse_json(content)

    def complete_text(
        self,
        *,
        system: str,
        user: str,
        model: str | None = None,
    ) -> str:
        response = self.client.chat.completions.create(
            model=model or self.config.report_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            extra_body={"thinking": {"type": "disabled"}},
        )
        return (response.choices[0].message.content or "").strip()


def _parse_json(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, flags=re.S)
        if not match:
            raise LLMError("LLM did not return valid JSON")
        parsed = json.loads(match.group(1))
    if not isinstance(parsed, dict):
        raise LLMError("LLM JSON output must be an object")
    return parsed

