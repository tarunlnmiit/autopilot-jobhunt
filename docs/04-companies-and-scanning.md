# 04 — Companies & scanning

## `companies.json`

The list of companies to scan ships pre-loaded with 130+ entries and is **committed**
(not gitignored) — edit it freely. Each entry:

```json
{
  "name": "Mistral AI",
  "careers_url": "https://jobs.lever.co/mistral",
  "search_domain": "mistral.ai",
  "location": "Paris / Remote",
  "region": "EU"
}
```

| Field | Used for |
|---|---|
| `name` | display + grouping in results |
| `careers_url` | the page fetched for direct + ATS job links |
| `search_domain` | the `site:` search query for extra postings |
| `location` / `region` | carried onto each job (region tags: EU / US / APAC / Remote / NZ) |

Add a company by appending an entry. Remove ones you don't care about to make scans
faster.

## How a scan works

`autopilot scan` (or the `scan_jobs` MCP tool) runs this per company:

1. **Discover** — fetch `careers_url`, extract direct job links + ATS listing pages
   (Greenhouse, Lever, Workday, SmartRecruiters, Ashby), then expand ATS pages. Also
   runs a `site:<search_domain>` query for senior/staff ML/AI roles.
2. **Deduplicate** — URLs already seen (tracked in `state/seen_jobs.json`) are skipped,
   so each scan surfaces only *new* postings.
3. **Fetch details** — pull each job page's content (first ~3000 chars).
4. **Score** — batch of 10 jobs → LLM → JSON with score (0–100), extracted title,
   stack, location/remote, one-line reason, and `worth_applying`.
5. **Persist** — passing jobs saved to `state/last_scan.json`, appended to
   `state/job_history.json`, and always written to `output/jobs_<date>.csv`.
6. **Notify** — top `top_n` matches ≥ `min_score` sent to Telegram (if configured).

## Pacing — why a scan takes 30–90 minutes

The scanner deliberately sleeps between fetches/searches to stay within TinyFish's free
throughput (~5 searches/min, ~25 fetches/min). This is **expected**, not a hang. Run it
nightly via cron (`bash setup_cron.sh`) and read results in the morning.

- **"No new job URLs found"** — TinyFish returned nothing matching the query for that
  company today. Not an error.
- **"0 jobs saved"** — jobs were found but all scored below your `min_score`.

## Exporting

```bash
autopilot export                 # last scan → output/jobs_<date>.csv
autopilot export --min 70        # only score >= 70
autopilot export --days 7        # from the past 7 days (needs scan history)
```

## Next

- [07 — Config & scoring](07-config-and-scoring.md) to tune `min_score` / `top_n`
- [05 — Integrations](05-integrations.md) for Telegram
