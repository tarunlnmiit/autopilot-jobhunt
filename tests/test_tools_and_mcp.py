"""Tool layer + MCP server — scanner/drafter/export stubbed; assert cwd is restored."""
import json
from pathlib import Path

import pytest

from job_hunt import tools


def test_tool_scan_reports_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "load_config", lambda: {"ok": True})
    monkeypatch.setattr(tools, "load_companies", lambda: [])

    def fake_run(cfg, companies):
        Path("state").mkdir(exist_ok=True)
        Path("state/last_scan.json").write_text(json.dumps(
            [{"score": 9}, {"score": 0}, {}]))

    monkeypatch.setattr(tools, "run_scan", fake_run)
    out = tools.tool_scan(config_path=str(tmp_path / "config.json"))
    assert "3 jobs found, 1 scored" in out


def test_tool_scan_no_results(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "load_config", lambda: {})
    monkeypatch.setattr(tools, "load_companies", lambda: [])
    monkeypatch.setattr(tools, "run_scan", lambda c, co: None)
    out = tools.tool_scan(config_path=str(tmp_path / "config.json"))
    assert "No results file" in out


def test_tool_scan_restores_cwd(tmp_path, monkeypatch):
    before = Path.cwd()
    monkeypatch.setattr(tools, "load_config", lambda: {})
    monkeypatch.setattr(tools, "load_companies", lambda: [])
    monkeypatch.setattr(tools, "run_scan", lambda c, co: None)
    tools.tool_scan(config_path=str(tmp_path / "config.json"))
    assert Path.cwd() == before


def test_tool_draft(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "load_config", lambda: {})
    called = {}
    monkeypatch.setattr(tools, "draft_application", lambda cfg, ref: called.update(ref=ref))
    out = tools.tool_draft("#2", config_path=str(tmp_path / "config.json"))
    assert called["ref"] == "#2" and "output/" in out


def test_tool_export(tmp_path, monkeypatch):
    called = {}
    monkeypatch.setattr(tools, "export_jobs", lambda min_score, days: called.update(m=min_score, d=days))
    out = tools.tool_export(min_score=70, days=7, config_path=str(tmp_path / "config.json"))
    assert called == {"m": 70, "d": 7} and "Export complete" in out


def test_mcp_server_tools_delegate(monkeypatch):
    mcp_server = pytest.importorskip("job_hunt.mcp_server")
    monkeypatch.setattr(mcp_server, "tool_scan", lambda: "scanned")
    monkeypatch.setattr(mcp_server, "tool_draft", lambda ref: f"drafted {ref}")
    monkeypatch.setattr(mcp_server, "tool_export", lambda min_score, days: f"exported {min_score}/{days}")
    assert mcp_server.scan_jobs() == "scanned"
    assert mcp_server.draft_application("#1") == "drafted #1"
    assert mcp_server.export_jobs(50, 3) == "exported 50/3"
