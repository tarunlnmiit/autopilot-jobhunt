# 08 — Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `config.json not found` | wrong working dir, or MCP `cwd` unset | run `autopilot init` in your working dir, or add `"cwd"` to the MCP entry in `~/.claude.json` ([06](06-mcp-and-skill.md)) |
| `companies.json not found` | same as above | `autopilot init` in the working dir |
| `TINYFISH_API_KEY not set` | key missing/placeholder | add a real key to `.env` or `config.json` ([03](03-api-keys.md)) |
| `All LLM models failed` | wrong key, or all 4 free models hit daily quota | verify `OPENROUTER_API_KEY`; wait for midnight-UTC reset, or add a small OpenRouter credit |
| `claude binary not found in PATH` | Claude CLI not installed / not on PATH | install from [claude.ai/code](https://claude.ai/code); check `which claude` |
| `claude CLI exited 1` | not authenticated | `claude auth login`, then retry; confirm with `claude --print "hi"` |
| `autopilot: command not found` | install incomplete / wrong venv | re-run `pip install -e '.[mcp]'` from the repo, or activate the right venv |
| No Telegram notification | token/chat_id missing or wrong | expected if unset — scan still completes, results in the CSV; if set, re-check both values ([05](05-integrations.md)) |
| Scan takes 30–90 min | normal free-tier pacing | let it run; automate nightly with `bash setup_cron.sh` |
| "No new job URLs found" | TinyFish found nothing new for that company today | not an error |
| "0 jobs saved" | jobs found but all below `min_score` | lower `min_score` in `config.json` if too strict |
| `python3 --version` < 3.11 | Python too old | install 3.11+ via [pyenv](https://github.com/pyenv/pyenv) |
| MCP server not in `claude mcp list` | config not reloaded | open a new terminal / restart Claude Code |

## Cron / MCP + Claude CLI auth

Cron jobs and the MCP server run as background processes and inherit the starting
shell's environment. If you use `llm_provider: claude_cli`, your `claude` login must be
active in that same context. Verify with `claude --print "hi"` from the same user/shell
before scheduling.

## Still stuck?

[Open an issue](https://github.com/tarunlnmiit/autopilot-jobhunt/issues) with the exact
error message and your Python version. Mask any API keys, resume paths, or personal data
first.
