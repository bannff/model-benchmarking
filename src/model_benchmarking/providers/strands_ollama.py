"""
Strands-backed Ollama provider adapter.

This wraps Strands Agents' OllamaModel with a simple interface compatible
with our CS-Eval runner (evaluate_question/batch_evaluate).

Imports are done lazily so the base package can be used without installing
Strands. If the user selects this provider at runtime and Strands is not
installed, a clear error is raised.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class StrandsOllamaProvider:
    """Adapter implementing evaluate_question/batch_evaluate using Strands."""

    def __init__(
        self,
        model: str,
        host: str = "http://localhost:11434",
        temperature: float = 0.1,
        top_p: float = 0.9,
        max_tokens: int = 256,
        callback_handler: Optional[object] = None,
    ) -> None:
        try:
            # Lazy import to avoid hard dependency at import time
            from strands import Agent  # type: ignore
            from strands.models.ollama import OllamaModel  # type: ignore
        except Exception as e:  # pragma: no cover - env-dependent
            raise RuntimeError(
                "Strands SDK is required for 'strands-ollama' provider. Install with: pip install 'strands-agents[ollama,otel]' strands-agents-tools"
            ) from e

        host = host.rstrip("/")
        # Prepare an Agent instance backed by Ollama
        self._agent: Any = Agent(
            model=OllamaModel(
                host=host,
                model_id=model,
                temperature=temperature,
                options={"top_p": top_p, "num_predict": max_tokens},
            ),
            callback_handler=callback_handler,
        )

    @staticmethod
    def _ensure_choice(text: str, options: Optional[List[str]]) -> str:
        for ch in ("A", "B", "C", "D"):
            if ch in (text or "").upper():
                return ch
        return "A"

    def evaluate_question(
        self,
        question: str,
        options: Optional[List[str]] = None,
        context: str = "",
        question_type: str = "multiple_choice",
    ) -> Dict[str, Any]:
        prompt = "Answer the following cybersecurity question by returning only the letter of the best choice (A, B, C, or D).\n\n"
        prompt += f"Question: {question}\n"
        if options:
            for i, opt in enumerate(options):
                prompt += f"{chr(65+i)}. {opt}\n"
        if context:
            prompt += f"\nContext: {context}\n"
        prompt += "\nAnswer:"

        try:
            result = self._agent(prompt)
            text = (getattr(result, "text", None) or getattr(result, "message", None) or str(result)).strip()
        except Exception as e:  # pragma: no cover - runtime dependent
            text = f"ERROR: {e}"

        parsed = self._ensure_choice(text, options)
        return {"raw_response": text, "parsed_response": parsed}

    def batch_evaluate(self, questions: List[Dict[str, Any]], batch_size: int = 10) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for q in questions:
            r = self.evaluate_question(
                q.get("question", ""),
                q.get("options"),
                q.get("context", ""),
                q.get("question_type", "multiple_choice"),
            )
            results.append(r)
        return results
