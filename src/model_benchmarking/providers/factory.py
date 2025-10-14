"""Provider factory for model adapters."""
from __future__ import annotations

from typing import Any


def make_provider(
    provider: str,
    *,
    model: str,
    host: str = "http://localhost:11434",
    temperature: float = 0.1,
    top_p: float = 0.9,
    max_tokens: int = 256,
    use_strands: bool = False,
) -> Any:
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

    raise ValueError(f"Unknown provider: {provider}")
