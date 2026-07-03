# 01 — Install

## Prerequisites

```bash
python3 --version   # must be 3.11 or higher
git --version       # any recent version
```

If Python is below 3.11, install via [pyenv](https://github.com/pyenv/pyenv) or
[python.org](https://www.python.org/downloads/).

## Option A — pip install (quickest)

```bash
pip install 'autopilot-jobhunt[mcp]'   # [mcp] adds Claude Code MCP support
mkdir my-job-hunt && cd my-job-hunt
autopilot init
```

`autopilot init` seeds the working directory:

```
✓ companies.json created (130+ companies pre-loaded)
✓ config.json created — fill in your API keys and profile
✓ .env created — fill in your API keys
✓ resume/YOUR_RESUME.md created — replace with your resume
```

It also creates empty `state/` and `output/` directories.

> **Always run `autopilot` commands from the directory where you ran `autopilot init`.**
> The tool reads `config.json` and `companies.json` from the current working directory.

If you only want the CLI (no Claude Code integration), drop the extra:
`pip install autopilot-jobhunt`.

## Option B — from source (customize companies / contribute)

```bash
git clone https://github.com/tarunlnmiit/autopilot-jobhunt.git
cd autopilot-jobhunt
pip install -e '.[mcp]'
```

For development work (tests, lint, type-check) install the dev extra instead:

```bash
pip install -e '.[dev]'
```

## Verify the install

`autopilot export` reads local scan state only — it needs **no API keys** and makes
**no** network calls:

```bash
autopilot export
```

Expected before your first scan:

```
No scan found. Run: autopilot scan
```

Seeing that message means the CLI is on your PATH and the bundled data files shipped
correctly. If you see `autopilot: command not found`, re-run the install from inside
the repo (Option B) or check your virtualenv.

## Next

- [03 — API keys](03-api-keys.md) to get scanning
- [02 — LLM providers](02-providers.md) to choose your scoring backend
