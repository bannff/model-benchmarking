# Security Policy

## Reporting a Vulnerability

If you find a security issue in `model-benchmarking`, please **do not** open a
public GitHub issue. Instead, report it privately via [GitHub Security
Advisories](https://github.com/bannff/model-benchmarking/security/advisories/new)
or email the maintainer. We aim to acknowledge reports within 72 hours.

## Intentional Vulnerable Content

This repository contains **intentionally vulnerable code and fixtures** for
research and evaluation purposes, used by suites like CVE-Bench and CyberGym.
The clearest example is the Cacti SQL fixtures under
`sanitized_db/src/cvebench/challenges/CVE-2024-25641/db/db.sql` and
`CVE-2024-34340/db/db.sql`, which embed Cacti's default RSA install keys
inside a `settings` table dump. Those keys are bait for the model under test,
not real credentials, and should not be flagged as leaks. Secret scanners
should allowlist `sanitized_db/**`.

Never run these benchmarks against production systems. Use the provided
Docker isolation primitives.

## Disclosed and Rotated Tokens

History was rewritten on **2026-05-17** to remove the following secrets that
were committed by mistake. Both have since been revoked and are no longer
valid:

- A HuggingFace `hf_*` fine-grained token, previously located in
  `scripts/integrate_primus_datasets.py`. Auto-revoked by HuggingFace's
  push-time secret detection.
- A GitHub `github_pat_*` fine-grained token, previously located in
  `.continue/mcpServers/new-mcp-server-3.yaml`. Manually revoked by the
  maintainer.

Anyone with a clone or fork from before the rewrite should re-clone:

```bash
git fetch --all --prune
git reset --hard origin/main
```

## Secret Hygiene Going Forward

- All credentials live in environment variables or a secret manager. Never
  commit literal token values.
- `.gitignore` excludes `.env*`, `*.pem`, `*.key`, `id_rsa*`, `.continue/`,
  and similar patterns by default.
- A `gitleaks` pre-commit hook is configured in `.pre-commit-config.yaml` to
  block commits containing high-entropy secrets or known token prefixes.
- The intentional vulnerable content under `sanitized_db/` is allowlisted in
  `.gitleaks.toml`.

If you suspect a secret has been committed despite these guards, follow the
[GitHub guide for removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
and contact GitHub Support to purge cached views.
