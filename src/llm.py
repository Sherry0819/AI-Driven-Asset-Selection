from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional

import requests


def _strip_code_fences(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```json\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^```\s*", "", s)
    s = re.sub(r"```\s*$", "", s)
    return s.strip()


def safe_load_json_array(s: str) -> List[Dict]:
    """Parse a JSON array robustly (handles code fences and extra whitespace)."""
    s = _strip_code_fences(s)
    # If model returns leading text, try to extract the first [...] block.
    m = re.search(r"\[[\s\S]*\]", s)
    if m:
        s = m.group(0)
    obj = json.loads(s)
    if not isinstance(obj, list):
        raise ValueError("Expected a JSON array (list of objects).")
    return obj


@dataclass
class LLMConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 800


class LLMClient:
    def select_portfolio(self, headlines_bullets: str, universe_hint: str, n: int = 20) -> List[Dict]:
        raise NotImplementedError


class OllamaClient(LLMClient):
    """Local Ollama chat client (no keys)."""

    def __init__(self, model: str = "gemma2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def select_portfolio(self, headlines_bullets: str, universe_hint: str, n: int = 20) -> List[Dict]:
        system = "You are a financial analyst. Return ONLY valid JSON."
        user = f"""Read the headlines below. Propose a market-neutral long/short portfolio with {n} positions.
Universe hint: {universe_hint}

Return a JSON array of objects with:
- stock: a stock identifier (ticker is fine)
- weight: a real number; long positive, short negative; absolute weights should sum to 1

Headlines:
{headlines_bullets}
"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": 0.0},
        }
        r = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
        r.raise_for_status()
        js = r.json()
        content = js["message"]["content"]
        arr = safe_load_json_array(content)
        return arr


class OpenAIClient(LLMClient):
    """Optional: OpenAI API adapter (requires OPENAI_API_KEY)."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def select_portfolio(self, headlines_bullets: str, universe_hint: str, n: int = 20) -> List[Dict]:
        # Minimal REST call to OpenAI responses endpoint is intentionally omitted here
        # to keep this repo lightweight and avoid hard-coding API schema.
        # Implement with your preferred OpenAI SDK or REST wrapper.
        raise NotImplementedError(
            "OpenAIClient is a stub. Use OllamaClient for local runs, "
            "or plug in your OpenAI SDK call here."
        )
