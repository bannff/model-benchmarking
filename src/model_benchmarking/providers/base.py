"""
Provider base protocol.

Defines the minimal interface that all model providers must implement to be
usable by the benchmarking pipeline and suite adapters. Concrete providers do
not need to inherit from this class explicitly; they only need to conform to
the protocol (structural subtyping) for type checkers.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class BaseProvider(Protocol):
    """Structural contract for provider implementations.

    Methods:
    - evaluate_question: Answer a single question (typically MCQ) and return
      a dict containing at least 'raw_response' and 'parsed_response'.
    - batch_evaluate: Convenience wrapper to evaluate multiple questions.
    - generate_text: General-purpose text generation for non-MCQ tasks.
    """

    def evaluate_question(
        self,
        question: str,
        options: Optional[List[str]] = None,
        context: str = "",
        question_type: str = "multiple_choice",
    ) -> Dict[str, Any]:
        ...

    def batch_evaluate(
        self, questions: List[Dict[str, Any]], batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        ...

    def generate_text(self, prompt: str) -> str:
        ...
