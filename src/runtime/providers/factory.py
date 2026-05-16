"""Provider factory for model adapters using a dynamic registry."""
from __future__ import annotations

from typing import Any, Type
from .base import BaseProvider
from ..utils.registry import Registry
from ..constants import (
    DEFAULT_OLLAMA_HOST,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_TOKENS,
)

provider_registry = Registry[BaseProvider]("providers")

@provider_registry.register("ollama")
def create_ollama(model: str, host: str, **kwargs) -> BaseProvider:
    from .ollama_http import OllamaHttpProvider
    return OllamaHttpProvider(model=model, base_url=host, **kwargs)

@provider_registry.register("strands-ollama")
def create_strands(model: str, host: str, **kwargs) -> BaseProvider:
    from .strands_ollama import StrandsOllamaProvider
    return StrandsOllamaProvider(model=model, host=host, **kwargs)

@provider_registry.register("mock")
def create_mock(**kwargs) -> BaseProvider:
    from .mock import MockProvider
    return MockProvider()


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
    provider = (provider or "ollama").lower()
    
    if use_strands and provider == "ollama":
        provider = "strands-ollama"

    return provider_registry.create(
        provider,
        model=model,
        host=host,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
