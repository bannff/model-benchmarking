"""
Lightweight Ollama HTTP provider.

Used as a fallback when Strands SDK isn't desired. Implements the same
evaluate_question/batch_evaluate contract expected by our runners.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import requests
import httpx


from runtime.constants import (
    DEFAULT_OLLAMA_HOST,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_TOKENS,
)


class OllamaHttpProvider:
    def __init__(
        self,
        model: str,
        base_url: str = DEFAULT_OLLAMA_HOST,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        timeout: int = 60,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.timeout = timeout

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
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": {
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "num_predict": self.max_tokens,
                    },
                    "stream": False,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "").strip()
        except Exception as e:
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

    def generate_text(self, prompt: str) -> str:
        """Generic text generation for non-MCQ tasks.

        Returns the raw model text or an error string prefixed with 'ERROR: '.
        """
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": {
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "num_predict": self.max_tokens,
                    },
                    "stream": False,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return (data.get("response", "") or "").strip()
        except Exception as e:
            return f"ERROR: {e}"

    async def generate_text_async(self, prompt: str) -> str:
        """Generic text generation for non-MCQ tasks (Async)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "options": {
                            "temperature": self.temperature,
                            "top_p": self.top_p,
                            "num_predict": self.max_tokens,
                        },
                        "stream": False,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return (data.get("response", "") or "").strip()
        except Exception as e:
            return f"ERROR: {e}"
