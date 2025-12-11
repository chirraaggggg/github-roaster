# backend/api.py

import requests
import logging
from collections import Counter
from datetime import datetime

from .config import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_REPO_LIMIT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Custom exception for GitHub-related errors."""
    pass


def get_headers():
    """Headers for GitHub API (with token if available)."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "github-roaster-app",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def validate_username(username: str) -> bool:
    """Validate GitHub username with regex and length rules."""
    import re
    from .config import VALID_USERNAME_PATTERN

    if not username or len(username) > 39:
        return False
    return bool(re.match(VALID_USERNAME_PATTERN, username))


def get_user_profile(username: str) -> dict:
    """Fetch basic user profile from GitHub."""
    if not validate_username(username):
        raise GitHubAPIError(f"Invalid username: {username}")

    url = f"{GITHUB_API_BASE}/users/{username}"
    headers = get_headers()

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "username": data["login"],
            "name": data.get("name") or username,
            "avatar_url": data["avatar_url"],
            "bio": data.get("bio") or "No bio.",
            "company": data.get("company") or "Not specified",
            "location": data.get("location") or "Planet Earth",
            "blog": data.get("blog") or "No blog",
            "public_repos": data["public_repos"],
            "followers": data["followers"],
            "following": data["following"],
            "created_at": data["created_at"],
        }
    except requests.exceptions.Timeout:
        raise GitHubAPIError("GitHub request timed out")
    except requests.exceptions.HTTPError:
        if resp.status_code == 404:
            raise GitHubAPIError(f"User '{username}' not found")
        elif resp.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit exceeded")
        else:
            raise GitHubAPIError(f"GitHub error: {resp.status_code}")
    except Exception as e:
        logger.error(f"Error fetching {username}: {e}")
        raise GitHubAPIError(f"Failed to fetch profile: {e}")


def get_user_repos(username: str, limit: int | None = None) -> list:
    """Fetch top repositories by stars for a user."""
    if limit is None:
        limit = GITHUB_REPO_LIMIT

    url = f"{GITHUB_API_BASE}/users/{username}/repos"
    headers = get_headers()
    params = {
        "per_page": min(limit, 100),
        "sort": "stars",
        "direction": "desc",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        repos = resp.json()

        top_repos = []
        for repo in repos[:5]:
            top_repos.append(
                {
                    "name": repo["name"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "language": repo["language"] or "Unknown",
                    "url": repo["html_url"],
                    "description": repo["description"] or "No description",
                }
            )
        return top_repos
    except Exception as e:
        logger.warning(f"Failed to fetch repos for {username}: {e}")
        return []


def get_user_languages(username: str, limit: int = 3) -> list:
    """Count languages across user's repos."""
    url = f"{GITHUB_API_BASE}/users/{username}/repos"
    headers = get_headers()
    params = {"per_page": 100}

    language_counter = Counter()
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        repos = resp.json()
        for repo in repos:
            if repo["language"]:
                language_counter[repo["language"]] += 1
        return language_counter.most_common(limit)
    except Exception as e:
        logger.warning(f"Failed to fetch languages for {username}: {e}")
        return []


def get_complete_profile(username: str) -> dict:
    """Combine basic profile + top repos + top languages + years on GitHub."""
    profile = get_user_profile(username)
    profile["top_repos"] = get_user_repos(username, limit=5)
    profile["top_languages"] = get_user_languages(username, limit=3)

    created = datetime.fromisoformat(profile["created_at"].replace("Z", "+00:00"))
    years = (datetime.now(created.tzinfo) - created).days // 365
    profile["years_on_github"] = max(years, 0)

    logger.info(f"Fetched complete profile for {username}")
    return profile


if __name__ == "__main__":
    try:
        p = get_complete_profile("torvalds")
        print("Name:", p["name"])
        print("Repos:", p["public_repos"], "Followers:", p["followers"])
        print("Languages:", p["top_languages"])
    except GitHubAPIError as e:
        print("Error:", e)
