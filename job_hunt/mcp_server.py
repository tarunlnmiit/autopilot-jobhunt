"""
MCP server for autopilot-jobs.

Register with Claude Code (one command):
  claude mcp add autopilot-jobs \\
    --env TINYFISH_API_KEY=your_key \\
    --env OPENROUTER_API_KEY=your_key \\
    --env TELEGRAM_TOKEN=your_token \\
    --env TELEGRAM_CHAT_ID=your_chat_id \\
    -- python -m job_hunt.mcp_server

Or add to ~/.claude.json manually — see README for full JSON block.

cwd must be the cloned repo root (config.json and companies.json are read from there).
"""
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise ImportError(
        "MCP SDK not installed. Run: pip install 'autopilot-jobs[mcp]'\n"
        "Or: pip install mcp"
    )

from job_hunt.tools import tool_scan, tool_draft, tool_export

mcp = FastMCP("autopilot-jobs")


@mcp.tool()
def scan_jobs() -> str:
    """
    Scan all configured company careers pages for new job postings,
    score them with AI against your resume, and send a Telegram notification
    with the top matches. Reads config.json and companies.json from the
    working directory.
    """
    return tool_scan()


@mcp.tool()
def draft_application(job_ref: str) -> str:
    """
    Draft a tailored resume and cover letter for a specific job.

    Args:
        job_ref: Job reference — '#1' or '1' (from last scan), or a full job URL.

    Returns a summary of where the output files were saved.
    """
    return tool_draft(job_ref)


@mcp.tool()
def export_jobs(min_score: int = 0, days: int = 0) -> str:
    """
    Export job scan results to a CSV file in the output/ directory.

    Args:
        min_score: Only include jobs with score >= this value (0 = all).
        days: Export from the last N days of history (0 = last scan only).

    Returns a summary of the export.
    """
    return tool_export(min_score=min_score, days=days)


if __name__ == "__main__":
    mcp.run()
