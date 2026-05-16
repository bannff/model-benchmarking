"""
Local sandbox implementation.

Provides a minimal sandbox for executing shell commands and file operations
within a dedicated working directory. Intended for lightweight simulations
only; not a security boundary. Do not run untrusted code here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional
import os
import shlex
import subprocess
import tempfile

from .base import Sandbox, SandboxResult


class LocalSandbox(Sandbox):
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self._tmp_obj = None
        if base_dir is None:
            self._tmp_obj = tempfile.TemporaryDirectory(prefix="mbx_sbox_")
            self.base_dir = Path(self._tmp_obj.name)
        else:
            self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_file(self, relpath: str, data: bytes) -> Path:
        p = self.base_dir / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def read_file(self, relpath: str) -> bytes:
        p = self.base_dir / relpath
        return p.read_bytes()

    def run(self, command: str, *, timeout: int = 30, cwd: Optional[str] = None) -> SandboxResult:
        # Execute command via bash -lc for simple pipelines; quote cwd if provided
        actual_cwd = str(self.base_dir / cwd) if cwd else str(self.base_dir)
        os.makedirs(actual_cwd, exist_ok=True)
        proc = subprocess.run(
            ["bash", "-lc", command],
            cwd=actual_cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return SandboxResult(
            exit_code=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            cwd=actual_cwd,
        )

    def __del__(self) -> None:  # best-effort cleanup for temp dirs
        try:
            if self._tmp_obj is not None:
                self._tmp_obj.cleanup()
        except Exception:
            pass
