from typing import Any, Dict

from groq import AsyncGroq  

from .config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    ROAST_TEMPERATURE,
    MAX_ROAST_LENGTH,
)

# Enforce a fixed word limit for roasts
ROAST_WORD_LIMIT = 100


class RoastGenerationError(Exception):
    pass


def _enforce_word_limit(text: str, limit: int = ROAST_WORD_LIMIT) -> str:
    words = text.split()
    return " ".join(words[:limit]).strip()


def _format_profile_for_prompt(profile: Dict[str, Any]) -> str:
    """Format the GitHub profile data into a string for the prompt."""
    name = profile.get("name") or profile.get("login")
    bio = profile.get("bio") or "No bio"
    public_repos = profile.get("public_repos", 0)
    followers = profile.get("followers", 0)
    total_stars = profile.get("total_stars", 0)
    total_forks = profile.get("total_forks", 0)

    lines = [
        f"Username: {profile.get('login')}",
        f"Name: {name}",
        f"Bio: {bio}",
        f"Public repos: {public_repos}",
        f"Followers: {followers}",
        f"Total stars: {total_stars}",
        f"Total forks: {total_forks}",
        "",
        "Top repos:",
    ]

    for repo in profile.get("top_repos", []):
        lines.append(
            f"- {repo.get('name')} | stars={repo.get('stargazers_count', 0)}, "
            f"forks={repo.get('forks_count', 0)}, lang={repo.get('language') or 'N/A'}, "
            f"desc={repo.get('description') or 'No description'}"
        )

    return "\n".join(lines)


async def generate_roast(profile: Dict[str, Any]) -> str:
    if not GROQ_API_KEY:
        raise RoastGenerationError("GROQ_API_KEY is not set")

    # use the async client
    client = AsyncGroq(api_key=GROQ_API_KEY)

    profile_text = _format_profile_for_prompt(profile)

    system_prompt = (
        "You are a sarcastic but playful GitHub roast bot. "
        "Given details about a developer's GitHub profile and repositories, "
        "write a short, humorous roast about their coding style, activity, and habits. "
        "Stay light-hearted, avoid anything offensive or personal beyond the data provided. "
        f"Keep the roast to exactly {ROAST_WORD_LIMIT} words."
    )

    user_prompt = (
        "Here is the GitHub user data:\n\n"
        f"{profile_text}\n\n"
        "Write the roast now."
    )

    try:
        chat_completion = await client.chat.completions.create(  # <-- await works now
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=ROAST_TEMPERATURE,
            max_tokens=MAX_ROAST_LENGTH,
        )
    except Exception as exc:
        raise RoastGenerationError(f"Groq API error: {exc}") from exc

    try:
        content = chat_completion.choices[0].message.content
    except Exception as exc:
        raise RoastGenerationError(f"Unexpected Groq response format: {exc}") from exc

    return _enforce_word_limit(content.strip(), ROAST_WORD_LIMIT)
