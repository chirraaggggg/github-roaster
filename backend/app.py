# backend/app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .api import get_complete_profile, GitHubAPIError
from .roast import generate_roast, RoastGenerationError


app = FastAPI(
    title="GitHub Roaster API",
    description="Backend for roasting GitHub profiles using Groq LLM",
    version="1.0.0",
)

# CORS so your React app can call this API from another origin
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Create React App / Next.js dev
    "*",                      # relax during development; tighten in prod
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RoastRequest(BaseModel):
    username: str


class RoastResponse(BaseModel):
    profile: dict
    roast: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/roast", response_model=RoastResponse)
async def roast_endpoint(payload: RoastRequest):
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    # 1) GitHub profile + stats
    try:
        profile = get_complete_profile(username)
    except GitHubAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2) Roast from Groq LLM
    try:
        roast = generate_roast(profile)
    except RoastGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RoastResponse(profile=profile, roast=roast)
