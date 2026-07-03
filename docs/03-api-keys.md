# 03 — API keys

Two keys get you scanning. Both have free tiers.

## TinyFish (required · free)

TinyFish fetches careers-page content and runs the search queries. **Every scan uses
it**, whatever LLM provider you pick.

1. Sign up at [agent.tinyfish.ai](https://agent.tinyfish.ai) (no credit card).
2. Dashboard → **API Keys** → **Create key**.
3. Copy the key (starts with `sk-tinyfish-…`).

> Free-tier throughput is generous. The scanner auto-paces to ~5 searches/min and
> ~25 URL fetches/min, so a full 130-company scan takes 30–90 min **by design** — not
> because of a tight cap. See [04 — Companies & scanning](04-companies-and-scanning.md).

## OpenRouter (required unless using Claude CLI · free)

Provides the scoring/drafting models (default backend). Skip this if you use
`llm_provider: claude_cli` — see [02 — Providers](02-providers.md).

1. Sign up at [openrouter.ai](https://openrouter.ai).
2. **Keys** → **Create key**.
3. Copy the key (starts with `sk-or-v1-…`).

## Where the keys go

Put keys in `.env` (gitignored), or directly in `config.json` (also gitignored). `.env`
values override `config.json` — but a placeholder like `your_..._here` never clobbers a
real value in `config.json`.

```bash
# .env
TINYFISH_API_KEY=sk-tinyfish-your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# optional — Telegram (see 05-integrations.md)
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_numeric_chat_id_here
```

> **`.env` and `config.json` are gitignored — never commit them.** If a key is ever
> exposed, rotate it immediately from the service dashboard. Secrets are also scanned in
> CI (gitleaks). See [SECURITY.md](../SECURITY.md).

## Verify

```bash
autopilot scan
```

If a key is missing you get a clear message (e.g. `TINYFISH_API_KEY not set`) — not a
traceback. Fill it in and re-run.

## Next

- [04 — Companies & scanning](04-companies-and-scanning.md)
- [07 — Config & scoring](07-config-and-scoring.md)
