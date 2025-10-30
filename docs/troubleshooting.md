## Troubleshooting

### Pylance: "Import could not be resolved"

If you see errors like:

- Import "pydantic" could not be resolved
- Import "click.testing" could not be resolved
- Import "pytest" could not be resolved

they typically indicate that VS Code is using the wrong Python interpreter or that dev dependencies aren’t installed in the active environment.

Try the following steps:

1) Ensure dependencies are installed

Install both runtime and dev dependencies in your environment:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

2) Select the correct interpreter in VS Code

- Open the Command Palette → “Python: Select Interpreter”.
- Choose the interpreter where you installed the packages (inside the dev container, typically /usr/bin/python3).

3) Project settings for quieter, accurate analysis

- We include `pyrightconfig.json` and `.vscode/settings.json` to:
  - Add `./src` to `extraPaths` so imports like `model_benchmarking.*` resolve.
  - Use type-checking mode “basic” for less noise.
  - Downgrade missing import diagnostics to warnings.

If you still see missing-import warnings for tests, confirm `pytest` is installed (requirements-dev.txt) and that the interpreter is set. You can also temporarily exclude `tests/` from analysis by adding it to `exclude` in `pyrightconfig.json`.

4) Common gotchas

- If you just created a virtual environment, reload VS Code after selecting it.
- For dev containers, ensure the container has pip-installed dependencies (step 1) and that `python.defaultInterpreterPath` points to the container’s Python.
- If you use a virtualenv at `.venv`, set `python.defaultInterpreterPath` to `.venv/bin/python` and consider adding `.venv` to `venvPath` in `pyrightconfig.json`.

### Running tests locally

We’ve configured VS Code to use pytest. You can also run it manually:

```bash
pytest -q
```

If imports fail during tests, re-run step (1) and (2) above.
