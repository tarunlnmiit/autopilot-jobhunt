# autopilot-jobhunt — Documentation

One command runs your job hunt: **scan careers pages → score every role against your
resume → alert the top matches → draft a tailored resume + cover letter**. It writes
drafts for you to review — it **never applies or submits** on your behalf.

> 🔒 **Drafts only — never applies.** There is no submit/apply capability anywhere.
> You review every drafted resume and cover letter and send applications yourself.

## Guides

| # | Guide | What it covers |
|---|-------|----------------|
| 01 | [Install](01-install.md) | pip / from source / `autopilot init` scaffolding |
| 02 | [LLM providers](02-providers.md) | OpenRouter fallback chain, Claude CLI (keyless), Anthropic API |
| 03 | [API keys](03-api-keys.md) | Get your TinyFish + OpenRouter keys; where each one goes |
| 04 | [Companies & scanning](04-companies-and-scanning.md) | `companies.json`, how discovery + scoring work, scan pacing |
| 05 | [Integrations](05-integrations.md) | Telegram notifications |
| 06 | [MCP server & Skill](06-mcp-and-skill.md) | Drive the hunt from Claude Code |
| 07 | [Config & scoring](07-config-and-scoring.md) | Candidate profile, `min_score`, `top_n`, provider selection |
| 08 | [Troubleshooting](08-troubleshooting.md) | Every error we've hit, and the fix |
| 09 | [Testing checklist](09-testing-checklist.md) | Reproducible independent test — install, gating, every provider |

## Provider matrix

Set with `llm_provider` in `config.json` (or `LLM_PROVIDER` in `.env`).

| `llm_provider` | Key needed | Runs on | Best for |
|---|---|---|---|
| `openrouter` **(default)** | `OPENROUTER_API_KEY` | OpenRouter cloud (free tier) | zero-cost nightly automation |
| `claude_cli` | none (local `claude` login) | your Claude subscription | keyless / on-demand drafts |
| `anthropic` | `ANTHROPIC_API_KEY` | Anthropic cloud | highest-quality scoring |

> Page fetching **always** uses TinyFish (cloud) regardless of LLM provider — there is
> no fully-offline mode. See [PRIVACY.md](../PRIVACY.md).

## 60-second start

```bash
pip install 'autopilot-jobhunt[mcp]'
mkdir my-job-hunt && cd my-job-hunt
autopilot init          # scaffolds config.json, companies.json, .env, resume/
autopilot export        # smoke test — prints "No scan found" (no keys needed yet)
```

Then follow [01-install](01-install.md) → [03-api-keys](03-api-keys.md) →
[07-config-and-scoring](07-config-and-scoring.md) → `autopilot scan`.
