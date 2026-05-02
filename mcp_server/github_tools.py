import httpx
from app.config import GITHUB_TOKEN, GITHUB_USERNAME

_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    **({"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}),
}


def _get(url: str, params: dict = None) -> dict | list:
    r = httpx.get(url, headers=_HEADERS, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def get_recent_activity(username: str = "") -> list[dict]:
    username = username or GITHUB_USERNAME
    events = _get(f"https://api.github.com/users/{username}/events/public", {"per_page": 20})
    results = []
    for e in events:
        results.append({
            "type": e.get("type"),
            "repo": e.get("repo", {}).get("name"),
            "created_at": e.get("created_at"),
            "payload_summary": _summarize_payload(e),
        })
    return results


def search_commits(query: str, username: str = "") -> list[dict]:
    username = username or GITHUB_USERNAME
    q = f"{query} author:{username}" if username else query
    data = _get("https://api.github.com/search/commits", {"q": q, "per_page": 10})
    return [
        {
            "sha": item["sha"][:7],
            "message": item["commit"]["message"].splitlines()[0],
            "repo": item["repository"]["full_name"],
            "date": item["commit"]["author"]["date"],
            "url": item["html_url"],
        }
        for item in data.get("items", [])
    ]


def search_repos(query: str, username: str = "") -> list[dict]:
    username = username or GITHUB_USERNAME
    q = f"{query} user:{username}" if username else query
    data = _get("https://api.github.com/search/repositories", {"q": q, "per_page": 10})
    return [
        {
            "name": r["full_name"],
            "description": r.get("description") or "",
            "stars": r["stargazers_count"],
            "language": r.get("language"),
            "url": r["html_url"],
            "updated_at": r["updated_at"],
        }
        for r in data.get("items", [])
    ]


def _summarize_payload(event: dict) -> str:
    payload = event.get("payload", {})
    etype = event.get("type", "")
    if etype == "PushEvent":
        commits = payload.get("commits", [])
        msgs = [c["message"].splitlines()[0] for c in commits[:3]]
        return f"Pushed {len(commits)} commit(s): {'; '.join(msgs)}"
    if etype == "PullRequestEvent":
        pr = payload.get("pull_request", {})
        return f"{payload.get('action', '')} PR: {pr.get('title', '')}"
    if etype == "IssuesEvent":
        issue = payload.get("issue", {})
        return f"{payload.get('action', '')} issue: {issue.get('title', '')}"
    if etype == "CreateEvent":
        return f"Created {payload.get('ref_type', '')} {payload.get('ref', '')}"
    return etype
