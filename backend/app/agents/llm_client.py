from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import settings


class LLMClient(ABC):
    """Abstract LLM client so the provider can be swapped without touching business logic."""

    @abstractmethod
    def chat(self, system: str, user: str, response_format_json: bool = True) -> str:
        ...


class OpenAICompatibleClient(LLMClient):
    """Client for any OpenAI-compatible API (GLM, DeepSeek, etc.)."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or settings.AI_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL
        self.timeout = timeout

    def chat(self, system: str, user: str, response_format_json: bool = True) -> str:
        if not self.api_key:
            raise RuntimeError("AI_API_KEY is not configured")
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if response_format_json:
            payload["response_format"] = {"type": "json_object"}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


class MockLLMClient(LLMClient):
    """Deterministic mock used in tests and when AI_API_KEY is empty."""

    def chat(self, system: str, user: str, response_format_json: bool = True) -> str:
        import json

        s = system.lower()
        if "analyze" in s and "material" in s:
            return json.dumps(
                {
                    "materials": [
                        {
                            "type": "unknown",
                            "category": "OTHER",
                            "condition": "UNKNOWN",
                            "estimated_reuse": None,
                            "risk_level": "SAFE",
                            "confidence": 0.3,
                        }
                    ]
                }
            )
        if "interpret" in s and "need" in s:
            return json.dumps(
                {
                    "material_category": "OTHER",
                    "material_name": None,
                    "quantity": None,
                    "unit": None,
                    "confidence": 0.3,
                    "missing_info": ["quantity", "unit"],
                }
            )
        if "explain" in s and "match" in s:
            return json.dumps({"score": 80, "reasons": ["Material compatible"], "confidence": 0.8})
        if "contingency" in s:
            return json.dumps({"collector_id": None, "reason": "No candidates", "confidence": 0.0})
        return json.dumps({"response": "mock", "confidence": 0.0})


def get_llm_client() -> LLMClient:
    if settings.AI_API_KEY:
        return OpenAICompatibleClient()
    return MockLLMClient()
