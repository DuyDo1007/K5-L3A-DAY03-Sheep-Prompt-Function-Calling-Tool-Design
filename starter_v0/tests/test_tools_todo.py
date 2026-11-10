"""Tool Unit Tests for Research Agent.

All tests are implemented offline using fixtures (fake_http, monkeypatch).
Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
github_search_tool = TOOL_FUNCTIONS["github_search"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify_tool(question="Select option", response_type="choice", options=["Option A", "Option B"])
    assert result["options"] == ["Option A", "Option B"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Item 1", "section": "A"},
        {"title": "Item 2", "section": "B"},
        {"title": "Item 3", "section": "A"},
    ]
    result = format_tool(items=items, template="sections")
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [
        {"title": "First tweet"},
        {"title": "Second tweet"},
    ]
    result = format_tool(items=items, template="thread")
    assert "1/" in result["markdown"]
    assert "2/" in result["markdown"]


def test_format_empty_items_does_not_crash() -> None:
    res_none = format_tool(items=None)
    assert res_none["item_count"] == 0
    res_empty = format_tool(items=[])
    assert res_empty["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100123456")
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="Bản tin tổng hợp", confirmed=True)
    assert len(calls) == 1
    assert "fake-token-123" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100123456"
    assert calls[0]["json"]["text"] == "Bản tin tổng hợp"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="Test", confirmed=True)
    assert result["error"] == "RuntimeError"
    assert len(calls) == 0


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))
    lookup_tool(query="AI", timeframe=None)
    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "# Title\nArticle body",
            "metadata": {"title": "T", "sourceURL": "https://example.com/news"},
        }
    }))
    result = fetch_tool(url="https://example.com/news")
    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["title"] == "T"
    assert item["url"] == "https://example.com/news"
    assert item["source"] == "example.com"
    assert "# Title\nArticle body" in item["summary"]


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "m" * 5000,
            "metadata": {"title": "T", "sourceURL": "https://example.com"},
        }
    }))
    result = fetch_tool(url="https://example.com")
    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    timeline_items = [
        {"text": "missing id"},
        *[{"tweet_id": str(i), "screen_name": "testuser", "text": f"tweet {i}"} for i in range(6)],
    ]
    fake_http(FakeResponse({"timeline": timeline_items}))
    result = timeline_tool(screenname="testuser", limit=3)
    assert len(result["items"]) == 3
    for item in result["items"]:
        assert item["url"].startswith("https://x.com/testuser/status/")


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"tweets": []}))
    social_search_tool(query="OpenAI", search_type="Top")
    assert calls[0]["params"]["query"] == "OpenAI"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = policy_tool(query="")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="privacy data customer API key", policy_area="data_privacy")
    assert len(result["results"]) > 0
    for hit in result["results"]:
        assert hit["policy_area"] == "data_privacy"


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="injection probe", policy_area="source_citation", top_k=5)
    injection_hits = [h for h in result["results"] if h["section"] == "Injection probe"]
    assert len(injection_hits) > 0
    hit = injection_hits[0]
    assert any("ignore the citation policy" in line for line in hit["untrusted_text"])
    assert "ignore the citation policy" not in hit["facts"]


# ---------------- YOUR NEW TOOL(S) ----------------

def test_github_search_happy_path(monkeypatch, fake_http) -> None:
    calls = fake_http(FakeResponse({
        "total_count": 1,
        "items": [
            {
                "full_name": "openai/whisper",
                "html_url": "https://github.com/openai/whisper",
                "description": "Robust Speech Recognition via Large-Scale Weak Supervision",
                "stargazers_count": 75000,
                "forks_count": 9000,
                "language": "Python",
            }
        ],
    }))

    result = github_search_tool(query="whisper", language="python", sort_by="stars", limit=3)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"]["q"] == "whisper language:python"
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 3
    assert result["total_count"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0] == {
        "title": "openai/whisper",
        "url": "https://github.com/openai/whisper",
        "summary": "Robust Speech Recognition via Large-Scale Weak Supervision",
        "stars": 75000,
        "forks": 9000,
        "language": "Python",
        "source": "github.com",
    }


def test_github_search_bad_input_from_model() -> None:
    result = github_search_tool(query="")
    assert result["error"] == "ValueError"
    assert "query cannot be empty" in result["message"]

    result_whitespace = github_search_tool(query="   ")
    assert result_whitespace["error"] == "ValueError"


def test_github_search_failure_returns_error_dict(monkeypatch, fake_http) -> None:
    fake_http(FakeResponse(status_code=500))
    result = github_search_tool(query="whisper")
    assert result["error"] == "HTTPError"
