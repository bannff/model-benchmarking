"""
Deterministic mock provider for tests and CI smoke runs.

Implements the same interface as other providers:
- evaluate_question
- batch_evaluate
- generate_text

This provider does not make any network calls and returns predictable outputs
that are useful for verifying the pipeline end-to-end.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class MockProvider:
    def __init__(self, *, choice: str = "A", text: str = "OK", **_: Any) -> None:
        # Ensure choice is one of A-D
        self.choice = (choice or "A").upper()
        if self.choice not in {"A", "B", "C", "D"}:
            self.choice = "A"
        self.text = text

    async def evaluate_question(
        self,
        question: str,
        options: Optional[List[str]] = None,
        context: str = "",
        question_type: str = "multiple_choice",
    ) -> Dict[str, Any]:
        # Return a fixed multiple-choice answer regardless of input
        parsed = self.choice if (options or question_type == "multiple_choice") else "A"
        return {
            "raw_response": f"MOCK[{self.choice}]",
            "parsed_response": parsed,
            "question_echo": question[:50],
            "context_echo": context[:50],
        }

    async def batch_evaluate(self, questions: List[Dict[str, Any]], batch_size: int = 10) -> List[Dict[str, Any]]:
        return [
            await self.evaluate_question(
                q.get("question", ""),
                q.get("options"),
                q.get("context", ""),
                q.get("question_type", "multiple_choice"),
            )
            for q in questions
        ]

    async def generate_text(self, prompt: str) -> str:
        # Return a short deterministic text including a hash of the prompt length
        return f"{self.text} ({len(prompt)})"
