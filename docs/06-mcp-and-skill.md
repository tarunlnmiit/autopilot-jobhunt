# 06 — MCP server & Skill

autopilot ships an MCP server so you can run the whole hunt from inside Claude Code
(or any MCP client) in natural language.

## Register with Claude Code

The server reads `config.json` and `companies.json` from its **working directory**, so
you must point it at your repo with `cwd`.

### Option A — one command, then add `cwd`

```bash
claude mcp add autopilot-jobhunt \
  --env TINYFISH_API_KEY=sk-tinyfish-your-key \
  --env OPENROUTER_API_KEY=sk-or-v1-your-key \
  --env TELEGRAM_TOKEN=your_token \
  --env TELEGRAM_CHAT_ID=your_chat_id \
  -- autopilot mcp
```

Then open `~/.claude.json`, find the `autopilot-jobhunt` entry, and add:

```json
"cwd": "/absolute/path/to/your/working-dir"
```

(Omit the two Telegram `--env` lines if you're not using Telegram.)

### Option B — edit `~/.claude.json` directly

```json
{
  "mcpServers": {
    "autopilot-jobhunt": {
      "command": "autopilot",
      "args": ["mcp"],
      "cwd": "/absolute/path/to/your/working-dir",
      "env": {
        "TINYFISH_API_KEY": "sk-tinyfish-your-key",
        "OPENROUTER_API_KEY": "sk-or-v1-your-key"
      }
    }
  }
}
```

> `autopilot mcp` and `python -m job_hunt.mcp_server` are equivalent entry points — use
> whichever suits your setup. From a pip install, `autopilot mcp` is simplest.

### Confirm

```bash
claude mcp list          # autopilot-jobhunt should appear
```

Then in a Claude Code session: *"List the tools from autopilot-jobhunt"* → you should
see `scan_jobs`, `draft_application`, `export_jobs`.

## Tools

| Tool | Does |
|---|---|
| `scan_jobs()` | full scan + score, saves results, sends Telegram |
| `draft_application(job_ref)` | draft resume + cover letter for `#N` or a job URL |
| `export_jobs(min_score, days)` | export matches to CSV |

## The usage skill

A committed Claude Code skill (`skills/autopilot-jobhunt/SKILL.md`) drives these tools
end-to-end: scan → rank the matches → let you pick roles → draft → review. Invoke it
with `/autopilot-jobhunt` or "scan for jobs matching my profile". It enforces the
**drafts-only, never-applies** invariant and treats scraped job descriptions as
untrusted input.

## Example prompts

```
"Scan for new jobs matching my profile"
"Draft an application for job #1 from the last scan"
"Draft a cover letter for this job: https://company.com/jobs/ml-engineer"
"Export all jobs with score above 70 from the past week"
```

## Next

- [08 — Troubleshooting](08-troubleshooting.md)
