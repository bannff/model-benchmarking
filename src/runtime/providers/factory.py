"""Provider factory for model adapters."""
from __future__ import annotations

from typing import Any
from .base import BaseProvider
from ..constants import (
    DEFAULT_OLLAMA_HOST,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_TOKENS,
)


def make_provider(
    provider: str,
    *,
    model: str,
    host: str = DEFAULT_OLLAMA_HOST,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    use_strands: bool = False,
) -> BaseProvider:
    provider = (provider or "").lower()

    if provider in ("strands-ollama",) or (use_strands and provider in ("ollama", "")):
        from .strands_ollama import StrandsOllamaProvider

        return StrandsOllamaProvider(
            model=model,
            host=host,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

    if provider in ("ollama", ""):
        from .ollama_http import OllamaHttpProvider

        return OllamaHttpProvider(
            model=model,
            base_url=host,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

    if provider == "mock":
        from .mock import MockProvider

        return MockProvider()

    raise ValueError(f"Unknown provider: {provider}")
