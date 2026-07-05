# Summary

<!-- What does this PR change and why? -->

## Checklist

- [ ] Tests pass locally (`pytest tests/ --cov=job_hunt`) and new behavior has tests
- [ ] Lint clean (`ruff check job_hunt/ tests/ conftest.py`) and types clean (`mypy`)
- [ ] **Drafts-only invariant intact** — the tool never submits applications; every
      draft goes through human review (see [SECURITY.md](../SECURITY.md))
- [ ] No secrets or personal data in the diff (`.env`, `config.json`, `resume/`,
      `state/`, `output/` stay untracked)
- [ ] Docs updated if user-facing behavior changed (README / docs/ / CHANGELOG.md)
