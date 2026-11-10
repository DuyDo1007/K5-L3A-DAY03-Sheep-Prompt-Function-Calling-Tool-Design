from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def get_repo_inform(
    query: str = "",
    language: str = "",
    sort_by: str = "stars",
    limit: int = 5,
) -> dict[str, Any]:
    """Search public repositories on GitHub via the REST API."""
    query_str = (query or "").strip()
    if not query_str:
        return {"tool": "get_repo_inform", "error": "ValueError", "message": "query cannot be empty"}

    try:
        search_q = query_str
        if language and language.strip():
            search_q = f"{search_q} language:{language.strip()}"

        sort_value = sort_by if sort_by in {"stars", "forks", "updated"} else "stars"
        per_page = min(max(int(limit or 5), 1), 30)

        headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": os.getenv("ARXIV_USER_AGENT", "ResearchAgent/1.0"),
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": search_q, "sort": sort_value, "order": "desc", "per_page": per_page},
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        items = [
            {
                "title": repo.get("full_name") or "",
                "url": repo.get("html_url") or "",
                "summary": (repo.get("description") or "")[:500],
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language") or "",
                "source": "github.com",
            }
            for repo in data.get("items", [])
        ]

        return {
            "tool": "get_repo_inform",
            "query": query_str,
            "language": language,
            "sort_by": sort_value,
            "total_count": data.get("total_count", len(items)),
            "items": items,
        }
    except Exception as exc:
        return err("get_repo_inform", exc)


search_github_repos = get_repo_inform
