"""`autopilot mcp` launches the stdio server without needing config.json.

The mcp branch must return before load_config(), so the server can start on a fresh
machine (it loads config lazily per tool call). We inject a fake mcp_server module so
the test doesn't require the optional [mcp] extra.
"""
import sys
import types

import pytest

from job_hunt import main


def test_mcp_command_runs_server_without_config(monkeypatch):
    ran = {}
    fake = types.ModuleType("job_hunt.mcp_server")
    fake.mcp = types.SimpleNamespace(run=lambda: ran.setdefault("ok", True))
    monkeypatch.setitem(sys.modules, "job_hunt.mcp_server", fake)
    monkeypatch.setattr(sys, "argv", ["autopilot", "mcp"])
    # No config.json in cwd — must NOT raise SystemExit from load_config().
    monkeypatch.setattr(main, "load_config", lambda: pytest.fail("mcp must not load_config"))

    main.main()

    assert ran.get("ok") is True
