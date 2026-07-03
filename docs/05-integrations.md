# 05 — Integrations

## Telegram notifications (optional)

After each scan, autopilot can message you the top matches. **Entirely optional** — if
you skip it, results still save to CSV and print to the terminal; nothing crashes.

### Set it up

1. Open Telegram, message **@BotFather**, send `/newbot`, follow the prompts.
2. Copy the **bot token** (looks like `8024470769:AAFw…`).
3. Message **@userinfobot** to get your numeric **chat_id** (e.g. `123456789`).

### Configure

Add both to `.env` (or the `telegram` block in `config.json`):

```bash
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_numeric_chat_id_here
```

Only when **both** are present are notifications enabled. What gets sent: the top `top_n`
matches — company, title, location/remote, stack, one-line reason, and the apply link.
Scan errors (if any) are sent as a separate message.

> **What leaves your machine:** match summaries go to Telegram's servers, into your own
> chat. It's a notification only — autopilot never applies to anything. See
> [PRIVACY.md](../PRIVACY.md).

### Verify

Run a scan with Telegram configured — you should receive a "Job Hunt — <date>" message.
If not, check [08 — Troubleshooting](08-troubleshooting.md); a missing/incorrect token
just means the scan completes without a notification (results still in the CSV).

## Next

- [06 — MCP server & Skill](06-mcp-and-skill.md)
