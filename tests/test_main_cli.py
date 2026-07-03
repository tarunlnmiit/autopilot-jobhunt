"""CLI dispatch + export/config helpers. No API keys, no network."""
import json

import pytest

from job_hunt import main


def _argv(monkeypatch, *args):
    monkeypatch.setattr("sys.argv", ["autopilot", *args])


def test_help_exits_zero(monkeypatch, capsys):
    _argv(monkeypatch)
    with pytest.raises(SystemExit) as e:
        main.main()
    assert e.value.code == 0


def test_init_dispatch(monkeypatch):
    called = {}
    monkeypatch.setattr(main, "init_project", lambda: called.setdefault("ok", True))
    _argv(monkeypatch, "init")
    main.main()
    assert called["ok"]


def test_scan_dispatch(monkeypatch):
    monkeypatch.setattr(main, "load_config", lambda: {"c": 1})
    monkeypatch.setattr(main, "load_companies", lambda: ["co"])
    ran = {}
    monkeypatch.setattr("job_hunt.scanner.run_scan", lambda cfg, co: ran.update(cfg=cfg, co=co))
    _argv(monkeypatch, "scan")
    main.main()
    assert ran["cfg"] == {"c": 1} and ran["co"] == ["co"]


def test_draft_dispatch(monkeypatch):
    monkeypatch.setattr(main, "load_config", lambda: {})
    got = {}
    monkeypatch.setattr("job_hunt.drafter.draft_application", lambda cfg, ref: got.update(ref=ref))
    _argv(monkeypatch, "draft", "#3")
    main.main()
    assert got["ref"] == "#3"


def test_draft_requires_arg(monkeypatch):
    monkeypatch.setattr(main, "load_config", lambda: {})
    _argv(monkeypatch, "draft")
    with pytest.raises(SystemExit):
        main.main()


def test_export_dispatch(monkeypatch):
    got = {}
    monkeypatch.setattr(main, "export_jobs", lambda min_score, days: got.update(m=min_score, d=days))
    _argv(monkeypatch, "export", "--min", "70", "--days", "7")
    main.main()
    assert got == {"m": 70, "d": 7}


def test_unknown_command(monkeypatch):
    monkeypatch.setattr(main, "load_config", lambda: {})
    _argv(monkeypatch, "frobnicate")
    with pytest.raises(SystemExit):
        main.main()


# --- _parse_export_args --------------------------------------------------------

def test_parse_export_args_defaults():
    assert main._parse_export_args(["autopilot", "export"]) == (0, 0)


def test_parse_export_args_bad_min():
    with pytest.raises(SystemExit):
        main._parse_export_args(["autopilot", "export", "--min", "abc"])


def test_parse_export_args_bad_days():
    with pytest.raises(SystemExit):
        main._parse_export_args(["autopilot", "export", "--days"])


# --- export_jobs ---------------------------------------------------------------

def test_export_jobs_no_scan(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "LAST_SCAN_FILE", main.Path("state/last_scan.json"))
    with pytest.raises(SystemExit):
        main.export_jobs()


def test_export_jobs_from_last_scan(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "last_scan.json").write_text(json.dumps(
        [{"company": "Acme", "title": "MLE", "url": "u", "score": 90},
         {"company": "Beta", "title": "SWE", "url": "v", "score": 30}]))
    monkeypatch.setattr(main, "LAST_SCAN_FILE", main.Path("state/last_scan.json"))
    main.export_jobs(min_score=50)
    out = capsys.readouterr().out
    assert "Exported 1 jobs" in out


def test_export_jobs_days_no_history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "JOB_HISTORY_FILE", main.Path("state/job_history.json"))
    with pytest.raises(SystemExit):
        main.export_jobs(days=7)


# --- load_config / load_companies ---------------------------------------------

def test_load_companies_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        main.load_companies()


def test_load_config_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        main.load_config()


def test_load_config_env_override(tmp_path, monkeypatch, clean_env):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({"tinyfish_api_key": "sk-config"}))
    monkeypatch.setenv("TINYFISH_API_KEY", "sk-env-real")
    cfg = main.load_config()
    assert cfg["tinyfish_api_key"] == "sk-env-real"


def test_load_config_placeholder_does_not_clobber(tmp_path, monkeypatch, clean_env):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({"tinyfish_api_key": "sk-config-real"}))
    monkeypatch.setenv("TINYFISH_API_KEY", "your_tinyfish_api_key_here")
    cfg = main.load_config()
    assert cfg["tinyfish_api_key"] == "sk-config-real"


def test_load_config_telegram_and_candidate_env(tmp_path, monkeypatch, clean_env):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({"tinyfish_api_key": "sk-real"}))
    monkeypatch.setenv("TELEGRAM_TOKEN", "tok")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    monkeypatch.setenv("CANDIDATE_NAME", "Ada")
    monkeypatch.setenv("MIN_SCORE", "70")
    monkeypatch.setenv("TOP_N", "3")
    monkeypatch.setenv("OPENROUTER_FALLBACK_MODELS", "a/b:free, c/d:free")
    cfg = main.load_config()
    assert cfg["telegram"] == {"token": "tok", "chat_id": "42"}
    assert cfg["candidate"]["name"] == "Ada"
    assert cfg["candidate"]["min_score"] == 70 and cfg["candidate"]["top_n"] == 3
    assert cfg["openrouter_fallback_models"] == ["a/b:free", "c/d:free"]


def test_load_config_missing_tinyfish_key_exits(tmp_path, monkeypatch, clean_env):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({"name": "x"}))
    with pytest.raises(SystemExit):
        main.load_config()


def test_export_jobs_days_with_history(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "job_history.json").write_text(json.dumps(
        [{"company": "Acme", "title": "MLE", "url": "u", "score": 90, "scan_date": "9999-01-01"}]))
    monkeypatch.setattr(main, "JOB_HISTORY_FILE", main.Path("state/job_history.json"))
    main.export_jobs(days=7)
    assert "Exported 1 jobs" in capsys.readouterr().out


def test_init_project_scaffolds(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    main.init_project()
    assert (tmp_path / "companies.json").exists()
    assert (tmp_path / "config.json").exists()
    assert (tmp_path / ".env").exists()
    assert (tmp_path / "resume" / "YOUR_RESUME.md").exists()
    assert (tmp_path / "state").is_dir() and (tmp_path / "output").is_dir()
    # idempotent — second run skips without error
    main.init_project()
    assert "already exists" in capsys.readouterr().out
