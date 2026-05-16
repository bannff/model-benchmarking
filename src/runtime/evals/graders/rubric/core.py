from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ...models import GradeResult, Sample, ExtractorSpec
from ..base import BaseGrader, GraderError
from .prompts import DEFAULT_RUBRIC
from .parser import parse_judge_response

class RubricGrader(BaseGrader):
    """
    Grader using an LLM as judge with a scoring rubric.
    """
    def __init__(
        self,
        prompt: Optional[str] = None,
        prompt_file: Optional[str] = None,
        model: str = "gpt-4o-mini",
        provider: Optional[str] = None,
        provider_host: Optional[str] = None,
        temperature: float = 0.0,
        extractor: Optional[ExtractorSpec] = None,
        rubric_vars: Optional[List[str]] = None,
        display_name: Optional[str] = None,
        base_dir: Optional[Path] = None,
    ):
        super().__init__(extractor=extractor, display_name=display_name)
        
        self.model = model
        self.provider_name = provider
        self.provider_host = provider_host
        self.temperature = temperature
        self.rubric_vars = rubric_vars or []
        self.base_dir = base_dir
        
        if prompt:
            self.rubric = prompt
        elif prompt_file:
            prompt_path = Path(prompt_file)
            if not prompt_path.is_absolute() and base_dir:
                prompt_path = base_dir / prompt_path
            try:
                self.rubric = prompt_path.read_text(encoding="utf-8")
            except IOError as e:
                raise GraderError(f"Failed to load rubric file {prompt_path}: {e}")
        else:
            self.rubric = DEFAULT_RUBRIC
        
        self._provider: Any = None
    
    def _get_provider(self) -> Any:
        """Get or create the judge provider."""
        if self._provider is not None:
            return self._provider
        
        from ....providers.factory import make_provider
        
        provider_name = self.provider_name or "ollama"
        host = self.provider_host or "http://localhost:11434"
        
        self._provider = make_provider(
            provider_name,
            model=self.model,
            host=host,
            temperature=self.temperature,
            max_tokens=512,
        )
        return self._provider
    
    def _build_prompt(self, sample: Sample, submission: str) -> str:
        """Build the judge prompt with rubric, input, and submission."""
        rubric = self.rubric
        for var in self.rubric_vars:
            val = sample.rubric_vars.get(var, "")
            rubric = rubric.replace("{{" + var + "}}", str(val)).replace("{" + var + "}", str(val))
        
        return f"## Rubric\n{rubric}\n\n## Input/Question\n{sample.input}\n\n## Expected Answer\n{sample.ground_truth or 'Not provided'}\n\n## Submission\n{submission}\n\n## Evaluation (JSON)\n"

    async def grade(
        self,
        sample: Sample,
        submission: str,
        **kwargs: Any,
    ) -> GradeResult:
        """Grade using the LLM judge (Async)."""
        for var in self.rubric_vars:
            if var not in sample.rubric_vars:
                raise GraderError(f"Sample missing required rubric variable: '{var}'")
        
        provider = self._get_provider()
        prompt = self._build_prompt(sample, submission)
        
        try:
            response = await provider.generate_text(prompt)
        except Exception as e:
            raise GraderError(f"Judge API call failed: {e}")
        
        return parse_judge_response(response)
