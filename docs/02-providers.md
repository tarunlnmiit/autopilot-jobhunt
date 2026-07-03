# 02 — LLM providers

The LLM scores each job against your resume and writes your drafts. Pick one backend
via `llm_provider` in `config.json` (or `LLM_PROVIDER` in `.env`). Page **fetching**
always uses TinyFish regardless — see [03 — API keys](03-api-keys.md).

## OpenRouter (default · free)

Access to hosted models on a free tier. autopilot uses a **4-model fallback chain** —
if the primary hits its daily free quota, the next is tried automatically:

| Order | Model | Role |
|---|---|---|
| 1 | `meta-llama/llama-3.3-70b-instruct:free` | primary |
| 2 | `nvidia/nemotron-3-super-120b-a12b:free` | fallback 1 |
| 3 | `google/gemma-4-31b-it:free` | fallback 2 |
| 4 | `qwen/qwen3-coder:free` | fallback 3 |

- **Calls per scan:** ~5–15 (jobs scored in batches of 10). One nightly scan stays
  within all four models' free daily limits.
- **`All LLM models failed`:** every model hit its daily quota — wait for the midnight
  UTC reset, or add a small OpenRouter credit ($1–5) to remove the cap.
- Override the chain in `config.json` with `openrouter_model` and
  `openrouter_fallback_models` (or `OPENROUTER_MODEL` / `OPENROUTER_FALLBACK_MODELS`,
  the latter comma-separated).

```json
"llm_provider": "openrouter",
"openrouter_api_key": "sk-or-v1-...",
```

## Claude CLI (keyless)

Use your local Claude Code login as the LLM — **no API key**.

```bash
claude auth login
claude --print "hi"        # confirm auth works in this shell
```

```json
"llm_provider": "claude_cli",
"claude_cli_model": "sonnet"    // or "opus", "haiku", or a full model id; "" = default
```

Or per-run: `LLM_PROVIDER=claude_cli autopilot scan`.

> **Subscription rate-limit burn.** Each CLI call loads your global Claude Code context
> (~25k–30k tokens even for a short prompt). A nightly scan makes 5–15 such calls
> against your subscription's rate limit. Prefer OpenRouter for nightly automation; use
> Claude CLI for occasional on-demand drafts.

> **Cron / MCP note.** Both run as background processes and inherit the starting shell's
> auth. Run `claude --print "hi"` in that same context before scheduling.

> `temperature` and `max_tokens` are not configurable with Claude CLI — the binary
> doesn't expose them.

## Anthropic API

Direct Anthropic API instead of OpenRouter.

```bash
pip install 'autopilot-jobhunt[claude]'
```

```json
"llm_provider": "anthropic",
"anthropic_api_key": "sk-ant-...",
"anthropic_model": "claude-haiku-4-5-20251001"   // or "claude-sonnet-4-6"
```

- `claude-haiku-4-5-20251001` — fast, affordable, handles JSON scoring well.
- `claude-sonnet-4-6` — higher-quality scores, higher cost.

> When `llm_provider` is `claude_cli` or `anthropic`, `openrouter_api_key` is ignored —
> you can leave it empty.

## Next

- [03 — API keys](03-api-keys.md)
- [07 — Config & scoring](07-config-and-scoring.md)
