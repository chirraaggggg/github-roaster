import logging
from groq import Groq  # Groq client (OpenAI-style)
from config import GROQ_API_KEY, GROQ_MODEL, ROAST_TEMPERATURE, MAX_ROAST_LENGTH

logger = logging.getLogger(__name__)

class RoastGenerationError(Exception):
    pass

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def build_roast_prompt(profile: dict) -> str:
    """Build a detailed prompt from a GitHub profile."""
    repos_str = ", ".join(
        [f"{r['name']} ({r['stars']}⭐)" for r in profile.get("top_repos", [])[:3]]
    )
    langs_str = ", ".join(
        [f"{lang[0]} ({lang[1]})" for lang in profile.get("top_languages", [])]
    )

    prompt = f"""You are a hilarious comedian roasting GitHub profiles.
Create a fun, light-hearted roast for this developer:

Profile Info:
- Name: {profile['name']}
- Username: @{profile['username']}
- Repositories: {profile['public_repos']}
- Followers: {profile['followers']}
- Following: {profile['following']}
- Years on GitHub: {profile['years_on_github']}
- Bio: {profile['bio'][:100]}
- Top Repos: {repos_str or 'None worth mentioning'}
- Languages: {langs_str or 'Mystery languages'}
- Location: {profile['location']}

Requirements:
1. Reference specific stats from the profile.
2. Be playful, not mean.
3. Use 4–6 sentences.
4. End with something positive or encouraging.
5. Use developer/tech humor where possible.

Generate the roast now:"""
    return prompt

def generate_roast(profile: dict) -> str:
    """Generate a roast using Groq LLM."""
    if not GROQ_API_KEY:
        raise RoastGenerationError("GROQ_API_KEY not configured in .env")

    try:
        prompt = build_roast_prompt(profile)

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly, witty comedian who roasts GitHub profiles. Keep it fun!",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=ROAST_TEMPERATURE,
            max_tokens=300,
            top_p=0.95,
        )

        roast = response.choices[0].message.content.strip()

        if len(roast) > MAX_ROAST_LENGTH:
            roast = roast[:MAX_ROAST_LENGTH].rsplit(" ", 1)[0] + "..."

        logger.info(f"Generated roast for {profile['username']}")
        return roast

    except Exception as e:
        logger.error(f"Error generating roast: {e}")
        raise RoastGenerationError(f"Failed to generate roast: {e}")

if __name__ == "__main__":
    from api import get_complete_profile

    try:
        profile = get_complete_profile("torvalds")
        roast = generate_roast(profile)
        print("🔥 Roast:\n", roast)
    except Exception as e:
        print("Error:", e)
