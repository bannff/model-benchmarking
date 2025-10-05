# Contributing

Development steps
- Create a virtualenv: `python3 -m venv .venv && source .venv/bin/activate`
- Install dev deps: `pip install -r requirements-dev.txt`
- Run tests: `pytest`

Publish image (optional)
- Create a GitHub Container Registry token and set it as `GHCR_PAT` in repo secrets
- CI will push images on merges if secrets are present
