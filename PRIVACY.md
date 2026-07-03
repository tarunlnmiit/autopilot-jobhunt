# Privacy — what leaves your machine

`autopilot-jobhunt` reads your resume and fetches job pages. This page states exactly
where that content goes, so you can pick a setup that matches your comfort level.

## The short version

- **This tool never applies to a job.** It drafts a resume + cover letter locally for
  your review (see [SECURITY.md](SECURITY.md)). You send applications yourself.
- **Two things always leave your machine when you scan:** job page fetches go through
  **TinyFish** (cloud), and your **resume + the job description** go to your chosen
  **LLM provider** for scoring and drafting.
- **The default provider (`openrouter`) is a cloud provider.** Out of the box, your
  resume and the JD transit OpenRouter. Switch to `claude_cli` before your first run if
  you want to keep content on your existing local Claude session.

## What leaves your machine, by LLM provider

Set the provider with `llm_provider` in `config.json` (or `LLM_PROVIDER` in `.env`).

| Provider (`llm_provider`) | Resume + JD content goes to | Key needed | Notes |
|---|---|---|---|
| `claude_cli` | **Your existing local Claude Code / Claude session** | none (uses `claude` CLI login) | No separate cloud upload beyond your existing Anthropic relationship. Best for privacy. |
| `openrouter` **(default)** | **OpenRouter (cloud, third party)** | API key | Routes to whichever model you pick; content transits OpenRouter + the chosen model host. |
| `anthropic` | **Anthropic (cloud)** | API key | Direct Anthropic API. |

> Regardless of provider, **page fetching always uses TinyFish** — job URLs and fetched
> page text transit the TinyFish API. There is no fully-offline mode.

## Other outbound data (opt-in only)

- **Telegram** (configured via `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID`) — sends the top
  matches (title, company, URL, score) to Telegram's servers, into your own chat.
  Notification only; it never applies to anything.

## What is stored locally

- **`state/last_scan.json`** — the most recent scan's scored results. Contains job data,
  not your resume. Gitignored.
- **`output/<company>-<date>/`** — drafted resumes and cover letters. **These contain
  your personal content.** Gitignored.
- **`resume/`** — your resume source (PII). Gitignored except the committed template.
- **`config.json` / `.env`** — your candidate profile, provider choice, and API keys.
  Gitignored in this repo; keep them out of version control in yours too.
- **`scan.log`** — run logs. Gitignored.

## Telemetry

None. This tool sends no analytics, usage pings, or crash reports anywhere.
