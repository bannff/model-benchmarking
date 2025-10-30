"""
Agent workflow base interfaces.

Defines a simple Workflow protocol and a minimal data contract for sandboxed
execution so we can plug different agent runtimes (e.g., Strands) without
coupling the rest of the pipeline to a specific framework.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Protocol


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    cwd: str


class Sandbox(Protocol):
    """Sandbox for executing simple commands and file operations in isolation."""

    base_dir: Path

    def write_file(self, relpath: str, data: bytes) -> Path:
        ...

    def read_file(self, relpath: str) -> bytes:
        ...

    def run(self, command: str, *, timeout: int = 30, cwd: Optional[str] = None) -> SandboxResult:
        ...


class Workflow(Protocol):
    """Agent workflow contract.

    A workflow receives a task dictionary and may interact with a sandbox to
    produce artifacts (e.g., PoCs) and an action log. The meaning of the
    fields is benchmark-specific.
    """

    def run_task(self, task: Dict[str, Any], *, sandbox: Optional[Sandbox] = None) -> Dict[str, Any]:
        ...
