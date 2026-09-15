"""Unauthenticated GitHub lookups.

Demo feature: "show me the repos of <user>" and "the content of <repo>".
Anonymous access is rate limited to 60 requests per hour, which is plenty for
a presentation and keeps the app free of another credential.
"""

from __future__ import annotations

import requests

API = "https://api.github.com"
TIMEOUT = 10


def _names(url: str) -> list[str] | None:
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return None
        return [entry["name"] for entry in payload]
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return None


def repos(owner: str) -> str:
    names = _names(f"{API}/users/{owner}/repos")
    if not names:
        return f"I found no public repositories for {owner}."
    return f"{owner} has {len(names)} public repositories:\n" + "\n".join(names)


def contents(owner: str, repo: str) -> str:
    names = _names(f"{API}/repos/{owner}/{repo}/contents")
    if not names:
        return f"I could not read {owner}/{repo}."
    return f"Top level of {owner}/{repo}:\n" + "\n".join(names)
