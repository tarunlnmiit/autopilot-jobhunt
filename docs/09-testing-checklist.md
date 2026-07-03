# 09 — Testing checklist

A reproducible pass to confirm autopilot-jobhunt works end-to-end — clean install, key
gating, each provider. Related: the committed
`skills/verify-package-install` skill automates the packaging half of this.

## 1. Clean-environment install

```bash
python3 -m venv /tmp/apj-check
/tmp/apj-check/bin/pip install --upgrade pip
/tmp/apj-check/bin/pip install -e '.[dev]'      # from the repo root
```

## 2. Lint, types, tests (dev flow)

```bash
/tmp/apj-check/bin/ruff check job_hunt/          # expect: no issues
/tmp/apj-check/bin/mypy                           # expect: No issues found
/tmp/apj-check/bin/pytest --cov=job_hunt          # expect: pass, coverage >= 85%
```

These mirror CI (`.github/workflows/ci.yml`), which runs the same three on Python 3.11,
3.12, and 3.13 plus a gitleaks secret scan.

## 3. CLI smoke tests (no API keys)

Run in a scratch dir so `init` scaffolding is exercised for real:

```bash
mkdir -p /tmp/apj-work && cd /tmp/apj-work
/tmp/apj-check/bin/autopilot --help              # usage, exit 0
/tmp/apj-check/bin/autopilot init                # creates companies.json, config.json, .env, resume/
/tmp/apj-check/bin/autopilot export ; echo $?    # "No scan found. Run: autopilot scan", exit nonzero (no traceback)
```

Key-gating check — proves a missing key fails cleanly, not with a stack trace:

```bash
/tmp/apj-check/bin/autopilot scan ; echo $?
# Expect: "TINYFISH_API_KEY not set" message, not a traceback.
```

## 4. MCP server

```bash
/tmp/apj-check/bin/autopilot mcp                 # starts the stdio server (Ctrl-C to stop)
# or: /tmp/apj-check/bin/python -m job_hunt.mcp_server
```

Then from Claude Code, confirm `scan_jobs`, `draft_application`, `export_jobs` are
listed ([06](06-mcp-and-skill.md)).

## 5. Provider matrix (with real keys)

For each backend you support, set `llm_provider` and run a small scan (or a single
`autopilot draft <url>`), confirming a scored result / drafted file appears:

| `llm_provider` | Prereq |
|---|---|
| `openrouter` | `OPENROUTER_API_KEY` set |
| `claude_cli` | `claude auth login` done; `claude --print "hi"` works |
| `anthropic` | `pip install '.[claude]'`; `ANTHROPIC_API_KEY` set |

## 6. Drafts-only invariant

Confirm `autopilot draft <url>` writes files under `output/<company>-<date>/`
(tailored resume, cover letter, application info) and **never** submits anywhere. Review
the drafts; you send applications yourself.

## 7. Tear down

```bash
rm -rf /tmp/apj-check /tmp/apj-work
```

Report: install source, lint/type/test results, smoke + gating outcomes, MCP tool
listing, and which providers you exercised.
