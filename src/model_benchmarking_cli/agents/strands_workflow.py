"""
Strands-powered agent workflow.

Wraps a Strands Agent with a few simple tools that interact with a LocalSandbox
so agent plans can "do" things: write/read files and run shell commands.

This is optional and only active when Strands is installed and selected.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .base import Workflow, Sandbox


class StrandsWorkflow(Workflow):
    def __init__(self, *, model: str, host: str = "http://localhost:11434", temperature: float = 0.1, top_p: float = 0.9, max_tokens: int = 256) -> None:
        try:
            from strands import Agent  # type: ignore
            from strands.models.ollama import OllamaModel  # type: ignore
            from strands.tools import tool  # type: ignore
        except Exception as e:  # pragma: no cover - optional dep
            raise RuntimeError("Strands SDK is required for StrandsWorkflow. Install strands-agents and strands-agents-tools.") from e

        # Define tools bound at runtime to a provided sandbox
        sbox_ref: Dict[str, Optional[Sandbox]] = {"sb": None}

        @tool(description="Write a file within the sandbox")
        def write_file(path: str, content: str) -> str:  # type: ignore
            sb = sbox_ref["sb"]
            assert sb is not None, "sandbox not set"
            p = sb.write_file(path, content.encode("utf-8", errors="ignore"))
            return f"WROTE {p}"

        @tool(description="Read a file from the sandbox")
        def read_file(path: str) -> str:  # type: ignore
            sb = sbox_ref["sb"]
            assert sb is not None, "sandbox not set"
            data = sb.read_file(path)
            return data.decode("utf-8", errors="ignore")

        @tool(description="Run a shell command in the sandbox working directory")
        def run_shell(cmd: str) -> dict:  # type: ignore
            sb = sbox_ref["sb"]
            assert sb is not None, "sandbox not set"
            res = sb.run(cmd)
            return {"exit_code": res.exit_code, "stdout": res.stdout[-4000:], "stderr": res.stderr[-4000:], "cwd": res.cwd}

        self._Agent = Agent  # type: ignore[assignment]
        self._OllamaModel = OllamaModel  # type: ignore[assignment]
        self._tools = [write_file, read_file, run_shell]  # type: ignore[list-item]
        self._model_args = dict(model_id=model, host=host, temperature=temperature, top_p=top_p, max_tokens=max_tokens)
        self._sbox_ref = sbox_ref

    def run_task(self, task: Dict[str, Any], *, sandbox: Optional[Sandbox] = None) -> Dict[str, Any]:
        # Set sandbox for tools
        self._sbox_ref["sb"] = sandbox

        agent = self._Agent(model=self._OllamaModel(**self._model_args), tools=self._tools)  # type: ignore[arg-type]
        system = task.get("system", "You are a cybersecurity agent. Use tools to create minimal, safe PoC artifacts.")
        prompt = task.get("prompt") or task.get("description") or ""
        result = agent(system=system, prompt=prompt)  # type: ignore[call-arg]
        text = (getattr(result, "text", None) or getattr(result, "message", None) or str(result)).strip()
        return {"final": text}
