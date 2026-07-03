"""Scanner pipeline — TinyFish + LLM mocked, filesystem in tmp_path."""
import json
import types

import pytest

from job_hunt import scanner


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(scanner.time, "sleep", lambda *_: None)


# --- pure helpers --------------------------------------------------------------

def test_is_job_url():
    assert scanner.is_job_url("https://x.co/jobs/ml-engineer-123")
    assert scanner.is_job_url("https://boards.greenhouse.io/acme/jobs/456789")
    assert not scanner.is_job_url("https://x.co/about")


def test_is_ats_listing():
    assert scanner.is_ats_listing("https://jobs.lever.co/acme")
    assert not scanner.is_ats_listing("https://x.co/careers")


def test_build_candidate_profile():
    cfg = {"candidate": {"name": "Ada", "profile": "ML eng", "seeking": "remote",
                         "not_suitable": "junior"}}
    out = scanner._build_candidate_profile(cfg)
    assert "- Ada" in out and "Seeking: remote" in out and "NOT suitable: junior" in out


def test_format_telegram_message():
    jobs = [{"company": "Acme", "title": "T", "extracted_title": "ML Eng", "location": "NY",
             "location_remote": "Remote", "stack": "Python", "reason": "fits", "url": "u"}]
    msg = scanner.format_telegram_message(jobs, "01 Jan 2026")
    assert "ML Eng" in msg and "Apply" in msg and "1 matches" in msg


# --- state ---------------------------------------------------------------------

def test_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert scanner.load_state() == {"seen_urls": []}
    scanner.save_state({"seen_urls": ["a", "b"]})
    assert scanner.load_state()["seen_urls"] == ["a", "b"]


# --- score_jobs ----------------------------------------------------------------

def test_score_jobs_empty():
    assert scanner.score_jobs([], "resume", {}) == []


def test_score_jobs_parses_and_filters(monkeypatch):
    jobs = [{"company": "Acme", "location": "Remote", "title": "MLE", "url": "u1"},
            {"company": "Beta", "location": "NY", "title": "SWE", "url": "u2"}]
    raw = json.dumps([
        {"job_number": 1, "score": 90, "title": "ML Engineer", "worth_applying": True,
         "stack": "Python", "reason": "great"},
        {"job_number": 2, "score": 20, "title": "Frontend", "worth_applying": False},
    ])
    monkeypatch.setattr(scanner, "chat_with_llm", lambda *a, **k: "noise " + raw + " tail")
    out = scanner.score_jobs(jobs, "resume", {"candidate": {"min_score": 55}})
    assert len(out) == 1 and out[0]["score"] == 90 and out[0]["extracted_title"] == "ML Engineer"


def test_score_jobs_no_json(monkeypatch):
    monkeypatch.setattr(scanner, "chat_with_llm", lambda *a, **k: "sorry no json")
    assert scanner.score_jobs([{"company": "A", "location": "L", "title": "T", "url": "u"}], "r", {}) == []


def test_score_jobs_llm_raises(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("llm down")

    monkeypatch.setattr(scanner, "chat_with_llm", boom)
    assert scanner.score_jobs([{"company": "A", "location": "L", "title": "T", "url": "u"}], "r", {}) == []


# --- discover / fetch (fake TinyFish) -----------------------------------------

def _fake_tf(links=None, search_urls=None, contents=None):
    links = links or []
    search_urls = search_urls or []
    contents = contents or {}

    def get_contents(urls, **kwargs):
        results = []
        for u in urls:
            results.append(types.SimpleNamespace(
                url=u, links=links, text=contents.get(u, "JD text"), title="Fetched Title"))
        return types.SimpleNamespace(results=results, errors=[])

    def query(q, **kwargs):
        return types.SimpleNamespace(results=[types.SimpleNamespace(url=u) for u in search_urls])

    return types.SimpleNamespace(
        fetch=types.SimpleNamespace(get_contents=get_contents),
        search=types.SimpleNamespace(query=query),
    )


def test_discover_job_urls(monkeypatch):
    tf = _fake_tf(links=["https://x.co/jobs/ml-engineer-abcd"],
                  search_urls=["https://x.co/jobs/staff-ai-wxyz"])
    company = {"name": "Acme", "careers_url": "https://x.co/careers",
               "search_domain": "x.co", "location": "Remote", "region": "EU"}
    out = scanner.discover_job_urls(tf, company, set())
    urls = {j["url"] for j in out}
    assert "https://x.co/jobs/ml-engineer-abcd" in urls
    assert "https://x.co/jobs/staff-ai-wxyz" in urls
    assert all(j["company"] == "Acme" for j in out)


def test_fetch_job_details(monkeypatch):
    tf = _fake_tf(contents={"https://x.co/jobs/1": "Full job description here"})
    jobs = [{"url": "https://x.co/jobs/1", "title": "old"}]
    out = scanner.fetch_job_details(tf, jobs)
    assert out[0]["content"].startswith("Full job") and out[0]["title"] == "Fetched Title"


# --- export --------------------------------------------------------------------

def test_export_to_csv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    jobs = [{"company": "Acme", "extracted_title": "MLE", "url": "u", "score": 88,
             "worth_applying": True, "scan_date": "2026-01-01"}]
    path = scanner._export_to_csv(jobs, "test")
    text = path.read_text()
    assert "Acme" in text and "MLE" in text and "Yes" in text


# --- run_scan integration ------------------------------------------------------

@pytest.fixture
def scan_setup(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "resume.md").write_text("Senior ML engineer, 10 YOE.")
    monkeypatch.setattr(scanner, "TinyFish", lambda **_: object())
    monkeypatch.setattr(scanner, "discover_job_urls", lambda tf, co, seen: [
        {"url": "https://x.co/jobs/1", "title": "MLE", "company": co["name"],
         "location": co["location"], "region": co["region"]}])
    monkeypatch.setattr(scanner, "fetch_job_details", lambda tf, jobs: jobs)
    monkeypatch.setattr(scanner, "score_jobs", lambda jobs, resume, cfg: [
        {**jobs[0], "score": 90, "extracted_title": "MLE", "reason": "fit", "stack": "Py"}])
    cfg = {"tinyfish_api_key": "k", "candidate": {"name": "Ada", "resume_path": "resume.md",
                                                  "min_score": 55, "top_n": 5}}
    companies = [{"name": "Acme", "careers_url": "c", "search_domain": "x.co",
                  "location": "Remote", "region": "EU"}]
    return cfg, companies


def test_run_scan_no_telegram_writes_csv(scan_setup, monkeypatch):
    sent = []
    monkeypatch.setattr(scanner, "send_telegram", lambda *a: sent.append(a))
    cfg, companies = scan_setup
    scanner.run_scan(cfg, companies)
    assert not sent  # no telegram configured
    assert json.loads(scanner.LAST_SCAN_FILE.read_text())[0]["score"] == 90
    from pathlib import Path
    assert list(Path("output").glob("jobs_*.csv"))


def test_run_scan_with_telegram(scan_setup, monkeypatch):
    sent = []
    monkeypatch.setattr(scanner, "send_telegram", lambda tok, chat, msg: sent.append(msg) or True)
    cfg, companies = scan_setup
    cfg["telegram"] = {"token": "t", "chat_id": "c"}
    scanner.run_scan(cfg, companies)
    assert sent and "matches" in sent[0]


def test_run_scan_scoring_failure_fallback(scan_setup, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("score boom")

    monkeypatch.setattr(scanner, "score_jobs", boom)
    monkeypatch.setattr(scanner, "send_telegram", lambda *a: True)
    cfg, companies = scan_setup
    scanner.run_scan(cfg, companies)
    saved = json.loads(scanner.LAST_SCAN_FILE.read_text())
    assert saved  # unscored fallback saved
