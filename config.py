import os
from dotenv import load_dotenv

load_dotenv()

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")

# Groq (LLM) instead of OpenAI
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

GITHUB_RATE_LIMIT = 60
GITHUB_REPO_LIMIT = 100
CACHE_TTL_SECONDS = 300
MAX_ROAST_LENGTH = 500
ROAST_TEMPERATURE = 0.9

VALID_USERNAME_PATTERN = r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,38}[a-zA-Z0-9])?$"