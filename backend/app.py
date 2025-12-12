from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .roast import generate_roast, RoastGenerationError
from .api import fetch_github_profile

app = FastAPI(
    title="GitHub Roaster",
    version="1.0.0",
)

# CORS so Vite frontend (localhost:5173) can call this API
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # or ["*"] during local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/roast")
async def roast_user(payload: dict):
    """
    Expected JSON body: { "username": "<github-username>" }
    """
    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    # 1. Fetch GitHub profile
    try:
        profile = await fetch_github_profile(username)
    except HTTPException:
        # Re-raise if your fetch_github_profile already throws HTTPException
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch GitHub profile")

    # 2. Generate roast with Groq / LLM
    try:
        roast = await generate_roast(profile)
    except RoastGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate roast")

    return {
        "profile": profile,
        "roast": roast,
    }
