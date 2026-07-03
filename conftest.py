"""Shared pytest fixtures for autopilot-jobs.

The suite must make **no** network or real-LLM calls. Every test that exercises
scanner/drafter stubs the one seam — `job_hunt.llm_utils.chat_with_llm`, imported
as a module-level name into `scanner` and `drafter`. `fake_llm` patches it in place;
`clean_env` strips host API keys so a developer's shell can't leak into assertions.
"""
import pytest

# Every credential/config env var that could leak from the host shell into a test.
_ENV_KEYS = (
    "TINYFISH_API_KEY",
    "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL",
    "LLM_PROVIDER",
    "TELEGRAM_TOKEN",
    "TELEGRAM_CHAT_ID",
    "LOG_LEVEL",
)


@pytest.fixture
def clean_env(monkeypatch):
    """Remove all autopilot env vars so tests assert on config.json/defaults only."""
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    return monkeypatch


@pytest.fixture
def fake_llm(monkeypatch):
    """Patch `chat_with_llm` in a target module with canned responses — no LLM calls.

    Usage:
        def test_x(fake_llm):
            calls = fake_llm("job_hunt.scanner", ['{"score": 9}'])
            ...
            assert calls[0]["messages"][0]["role"] == "system"

    Pass a single string (returned for every call) or a list (dequeued per call;
    the last item repeats once exhausted). Returns the recorded-calls list.
    """

    def _install(module_path, responses):
        queue = [responses] if isinstance(responses, str) else list(responses)
        calls: list[dict] = []

        def _fake(config, messages, temperature=0.1, max_tokens=4096):
            calls.append(
                {
                    "config": config,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            )
            return queue.pop(0) if len(queue) > 1 else queue[0]

        monkeypatch.setattr(f"{module_path}.chat_with_llm", _fake)
        return calls

    return _install


@pytest.fixture
def sample_config():
    """Minimal valid config dict (OpenRouter provider) for scanner/drafter tests."""
    return {
        "tinyfish_api_key": "sk-test-tinyfish",
        "llm_provider": "openrouter",
        "openrouter_api_key": "sk-test-openrouter",
        "openrouter_model": "test/model:free",
        "openrouter_fallback_models": [],
        "candidate": {
            "name": "Test Candidate",
            "resume_path": "resume/YOUR_RESUME.md",
        },
        "min_score": 7,
        "top_n": 5,
    }


@pytest.fixture
def sample_job():
    """One job record in the `state/last_scan.json` shape."""
    return {
        "url": "https://example.co/jobs/1",
        "title": "Senior ML Engineer",
        "extracted_title": "Senior ML Engineer",
        "company": "Example Co",
        "location": "Remote",
        "region": "Remote",
        "score": 9,
    }
