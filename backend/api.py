from typing import Any, Dict, List

import httpx
from fastapi import HTTPException

from .config import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_REPO_LIMIT


async def _github_client() -> httpx.AsyncClient:
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return httpx.AsyncClient(base_url=GITHUB_API_BASE, headers=headers, timeout=10.0)


async def fetch_github_profile(username: str) -> Dict[str, Any]:
    """
    Fetch GitHub user profile + some repo stats.
    """
    async with await _github_client() as client:
        user_resp = await client.get(f"/users/{username}")
        if user_resp.status_code == 404:
            raise HTTPException(status_code=404, detail="GitHub user not found")
        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"GitHub API error: {user_resp.status_code}",
            )

        user_data = user_resp.json()

        repos_resp = await client.get(
            f"/users/{username}/repos",
            params={"sort": "updated", "per_page": GITHUB_REPO_LIMIT},
        )
        if repos_resp.status_code != 200:
            repos: List[Dict[str, Any]] = []
        else:
            repos = repos_resp.json()

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)

    profile: Dict[str, Any] = {
        "login": user_data.get("login"),
        "name": user_data.get("name"),
        "bio": user_data.get("bio"),
        "avatar_url": user_data.get("avatar_url"),
        "html_url": user_data.get("html_url"),
        "public_repos": user_data.get("public_repos", 0),
        "followers": user_data.get("followers", 0),
        "following": user_data.get("following", 0),
        "created_at": user_data.get("created_at"),
        "updated_at": user_data.get("updated_at"),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "top_repos": [
            {
                "name": r.get("name"),
                "html_url": r.get("html_url"),
                "stargazers_count": r.get("stargazers_count", 0),
                "forks_count": r.get("forks_count", 0),
                "language": r.get("language"),
                "description": r.get("description"),
            }
            for r in repos
        ],
    }

    return profile
