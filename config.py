import os
from dotenv import load_dotenv

# This initializes dotenv, so any variables defined in an external .env file (like GITHUB_TOKEN=xyz) become accessible via os.getenv()
load_dotenv()

# defining API keys and endpoints
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")


# github settings
GITHUB_RATE_LIMIT = 60          # unauthenticated; token gives a lot more (5000/hour)
GITHUB_REPO_LIMIT = 100         # max repos per user to inspect

# application behavior settings
CACHE_TTL_SECONDS = 300
MAX_ROAST_LENGTH = 500
ROAST_TEMPERATURE = 0.9

# GitHub Username Validation Pattern
VALID_USERNAME_PATTERN = r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,38}[a-zA-Z0-9])?$"
