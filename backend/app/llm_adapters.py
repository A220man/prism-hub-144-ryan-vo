# LLM Provider Adapters
"""Adapters for multiple LLM providers with unified interface.

Supports: OpenAI-compatible, Anthropic, Gemini, Ollama.
All adapters work with httpx for async HTTP calls.
"""

import os
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, AsyncIterator
import httpx


@dataclass
class LLMMessage:
    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Optional[dict] = None
    raw: Optional[dict] = None


class LLMAdapter(ABC):
    """Base class for LLM adapters."""

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @abstractmethod
    async def complete(self, messages: list[LLMMessage], **kwargs) -> LLMResponse:
        pass

    async def stream(self, messages: list[LLMMessage], **kwargs) -> AsyncIterator[str]:
        """Stream completion (default: fake stream from complete)."""
        response = await self.complete(messages, **kwargs)
        yield response.content


class OpenAICompatibleAdapter(LLMAdapter):
    """Adapter for OpenAI-compatible APIs (OpenAI, LiteLLM, OpenRouter, Ollama)."""

    @property
    def provider_name(self) -> str:
        return "openai-compatible"

    def _get_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _get_url(self) -> str:
        base = self.base_url or "https://api.openai.com/v1"
        return f"{base.rstrip('/')}/chat/completions"

    async def complete(self, messages: list[LLMMessage], **kwargs) -> LLMResponse:
        client = self._get_client()
        url = self._get_url()

        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": False,
        }

        try:
            resp = await client.post(url, headers=self._get_headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()

            choice = data["choices"][0]
            content = choice["message"]["content"]
            usage = data.get("usage")

            return LLMResponse(
                content=content,
                model=data.get("model", self.model),
                usage=usage,
                raw=data,
            )
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            raise RuntimeError(f"{self.provider_name} API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            raise RuntimeError(f"{self.provider_name} request failed: {e}")


class AnthropicAdapter(LLMAdapter):
    """Adapter for Anthropic Messages API."""

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
        }

    def _get_url(self) -> str:
        base = self.base_url or "https://api.anthropic.com/v1"
        return f"{base.rstrip('/')}/messages"

    async def complete(self, messages: list[LLMMessage], **kwargs) -> LLMResponse:
        client = self._get_client()
        url = self._get_url()

        # Convert messages - Anthropic uses system param separately
        system_msg = None
        anthropic_messages = []
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                anthropic_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.7),
        }
        if system_msg:
            payload["system"] = system_msg

        try:
            resp = await client.post(url, headers=self._get_headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()

            content = "".join(block["text"] for block in data["content"] if block["type"] == "text")
            usage = {"input_tokens": data.get("usage", {}).get("input_tokens"),
                     "output_tokens": data.get("usage", {}).get("output_tokens")}

            return LLMResponse(
                content=content,
                model=data.get("model", self.model),
                usage=usage,
                raw=data,
            )
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            raise RuntimeError(f"{self.provider_name} API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            raise RuntimeError(f"{self.provider_name} request failed: {e}")


class GeminiAdapter(LLMAdapter):
    """Adapter for Google Gemini API."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _get_url(self) -> str:
        base = self.base_url or "https://generativelanguage.googleapis.com/v1beta"
        return f"{base.rstrip('/')}/models/{self.model}:generateContent"

    def _get_params(self) -> dict:
        params = {}
        if self.api_key:
            params["key"] = self.api_key
        return params

    async def complete(self, messages: list[LLMMessage], **kwargs) -> LLMResponse:
        client = self._get_client()
        url = self._get_url()

        # Convert to Gemini format
        contents = []
        for m in messages:
            role = "user" if m.role in ("user", "system") else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 2048),
            },
        }

        try:
            resp = await client.post(url, params=self._get_params(), json=payload)
            resp.raise_for_status()
            data = resp.json()

            candidate = data["candidates"][0]
            content = candidate["content"]["parts"][0]["text"]
            usage = data.get("usageMetadata")

            return LLMResponse(
                content=content,
                model=self.model,
                usage=usage,
                raw=data,
            )
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            raise RuntimeError(f"{self.provider_name} API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            raise RuntimeError(f"{self.provider_name} request failed: {e}")


class OllamaAdapter(OpenAICompatibleAdapter):
    """Adapter for Ollama (uses OpenAI-compatible API)."""

    @property
    def provider_name(self) -> str:
        return "ollama"

    def _get_url(self) -> str:
        base = self.base_url or "http://localhost:11434/v1"
        return f"{base.rstrip('/')}/chat/completions"

    def _get_headers(self) -> dict:
        # Ollama doesn't require auth by default
        return {"Content-Type": "application/json"}


def create_adapter(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: float = 60.0,
) -> LLMAdapter:
    """Factory function to create LLM adapter."""
    provider = provider.lower()

    if provider in ("openai", "openai-compatible", "litellm", "openrouter"):
        return OpenAICompatibleAdapter(model, api_key, base_url, timeout)
    elif provider in ("anthropic", "claude"):
        return AnthropicAdapter(model, api_key, base_url, timeout)
    elif provider in ("gemini", "google"):
        return GeminiAdapter(model, api_key, base_url, timeout)
    elif provider in ("ollama",):
        return OllamaAdapter(model, api_key, base_url, timeout)
    else:
        raise ValueError(f"Unknown provider: {provider}. Supported: openai-compatible, anthropic, gemini, ollama")


async def test_adapter(adapter: LLMAdapter) -> bool:
    """Test adapter with a simple request."""
    try:
        response = await adapter.complete([
            LLMMessage(role="user", content="Say 'OK' if you receive this.")
        ], max_tokens=10)
        return "OK" in response.content.upper()
    except Exception:
        return False