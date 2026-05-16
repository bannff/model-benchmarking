"""
Generic registry utility for dynamic component lookup and registration.
"""
from __future__ import annotations

from typing import Dict, Generic, Type, TypeVar, Optional, Callable

T = TypeVar("T")

class Registry(Generic[T]):
    """
    A generic registry for mapping keys to types or factory functions.
    """
    def __init__(self, name: str):
        self.name = name
        self._registry: Dict[str, Type[T] | Callable[..., T]] = {}

    def register(self, key: str):
        """Decorator to register a type or factory."""
        def wrapper(item: Type[T] | Callable[..., T]):
            self._registry[key.lower()] = item
            return item
        return wrapper

    def get(self, key: str) -> Optional[Type[T] | Callable[..., T]]:
        """Retrieve a registered item by key."""
        return self._registry.get(key.lower())

    def create(self, key: str, **kwargs) -> T:
        """Create an instance of a registered item."""
        item = self.get(key)
        if not item:
            raise ValueError(f"No item registered under '{key}' in {self.name} registry")
        return item(**kwargs)

    def list_keys(self) -> list[str]:
        """List all registered keys."""
        return list(self._registry.keys())
