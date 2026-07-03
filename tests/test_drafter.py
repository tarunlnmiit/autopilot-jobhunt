"""Drafter — TinyFish fetch + LLM mocked; asserts files written, never submits."""
import json
import types

import pytest

from job_hunt import drafter


@pytest.fixture
def draft_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "resume").mkdir()
    (tmp_path / "resume" / "r.md").write_text("Ada Lovelace — ML engineer, 10 YOE.")

    fetch = types.SimpleNamespace(get_contents=lambda urls, **k: types.SimpleNamespace(
        results=[types.SimpleNamespace(url=urls[0], text="Job description body")], errors=[]))
    monkeypatch.setattr(drafter, "TinyFish", lambda **_: types.SimpleNamespace(fetch=fetch))
    monkeypatch.setattr(drafter, "chat_with_llm", lambda config, messages, **k: "LLM OUTPUT")

    cfg = {"tinyfish_api_key": "k",
           "candidate": {"name": "Ada", "resume_path": "resume/r.md"}}
    return cfg


def test_draft_from_url_writes_three_files(draft_env):
    drafter.draft_application(draft_env, "https://acme.co/jobs/mle")
    from pathlib import Path
    out_dirs = list(Path("output").glob("company-*"))
    assert out_dirs
    files = {p.name for p in out_dirs[0].iterdir()}
    assert any(f.startswith("resume_") for f in files)
    assert any(f.startswith("cover_letter_") for f in files)
    assert "application_info.txt" in files


def test_resolve_job_by_index(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "last_scan.json").write_text(json.dumps(
        [{"url": "https://acme.co/jobs/1", "company": "Acme Co", "title": "MLE"}]))
    monkeypatch.setattr(drafter, "LAST_SCAN_FILE", drafter.Path("state/last_scan.json"))
    url, slug = drafter._resolve_job("#1")
    assert url == "https://acme.co/jobs/1" and slug == "acme_co"


def test_resolve_job_out_of_range(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "last_scan.json").write_text(json.dumps([]))
    monkeypatch.setattr(drafter, "LAST_SCAN_FILE", drafter.Path("state/last_scan.json"))
    with pytest.raises(ValueError):
        drafter._resolve_job("#3")


def test_resolve_job_no_scan(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(drafter, "LAST_SCAN_FILE", drafter.Path("state/missing.json"))
    with pytest.raises(FileNotFoundError):
        drafter._resolve_job("#1")


def test_slug():
    assert drafter._slug("Acme Co, Inc.") == "acme_co_inc"
