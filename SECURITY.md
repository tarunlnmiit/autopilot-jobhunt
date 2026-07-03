# Security Policy

`autopilot-jobhunt` fetches third-party job pages, sends your resume to an LLM, and
optionally posts to Telegram. This document states the guarantees, the trust
boundaries, and how to report a vulnerability.

## The never-apply invariant

**This tool never applies to a job or submits anything on your behalf.** It only:

- scans configured careers pages and scores them,
- writes a tailored resume + cover letter to `output/` for a role you pick,
- (optionally) posts the top matches to your own Telegram chat.

There is no "apply", "submit", or form-filling capability anywhere in the codebase.
Every application is a local draft for you to review, edit, and send yourself. Do not
extend the tool to auto-apply.

## Trust boundaries

- **API keys** (`TINYFISH_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`) and your
  `config.json` live locally in `.env` / `config.json`. Both are gitignored and scanned
  in CI (gitleaks). They must never be committed. Rotate any key that may have leaked.
- **Your resume is PII.** It is read from `resume/` and sent to your chosen LLM provider
  for scoring and drafting. Personal résumé files are gitignored; keep them out of
  version control.
- **Page fetching goes through TinyFish.** Job URLs and the fetched page contents transit
  the TinyFish API (cloud). Scored results are stored locally in `state/last_scan.json`.
- **LLM providers.** Depending on `llm_provider`, your resume and job descriptions may be
  transmitted to a third-party cloud. See [PRIVACY.md](PRIVACY.md) for the exact
  per-provider breakdown. Use `claude_cli` to keep content on your existing local Claude
  session.
- **Telegram (opt-in).** If configured, match summaries (title, company, URL, score) are
  sent to Telegram's servers into your own chat.

## Scraping and terms of service

Scanning fetches pages from company careers sites. **You are responsible for respecting
each target site's Terms of Service, `robots.txt`, and rate limits.** The default cadence
is conservative (nightly, batched), but the operator — not this tool — is accountable for
lawful, courteous use.

## Prompt injection

Scraped job descriptions flow into the scoring and cover-letter prompts. A hostile or
manipulative posting can attempt to steer its own score or the text of a drafted letter
(prompt injection). The design mitigates the worst case: the tool **never applies
automatically** and **never treats scraped content as commands** — every draft is a local
file for human review, and scoring only produces a number + one-line rationale. Do not
extend the tool to execute instructions found inside scraped content.

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue for an
exploitable vulnerability.

- Use GitHub's **[private vulnerability reporting](https://github.com/tarunlnmiit/autopilot-jobhunt/security/advisories/new)**
  (Security → Report a vulnerability), or
- open a minimal public issue asking for a private contact channel if the above is
  unavailable.

Please include: affected version, reproduction steps, and impact. We aim to acknowledge
within a few days. Coordinated disclosure is appreciated — give us a chance to ship a fix
before public details.

## Supported versions

This is a young project; only the latest published version on PyPI receives fixes.
