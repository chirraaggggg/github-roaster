import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .roast import generate_roast, RoastGenerationError
from .api import fetch_github_profile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Roaster",
    version="1.0.0",
)

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("An unexpected error occurred")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

@app.post("/roast")
async def roast_user(payload: dict):
    """
    Expected JSON body: { "username": "<github-username>" }
    """
    try:
        username = payload.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")

        logger.info(f"Fetching GitHub profile for user: {username}")
        profile = await fetch_github_profile(username)
        
        if not profile:
            raise HTTPException(status_code=404, detail="GitHub profile not found")

        logger.info("Generating roast...")
        roast = await generate_roast(profile)
        
        if not roast:
            raise HTTPException(status_code=500, detail="Failed to generate roast: Empty response from Groq API")

        return {
            "profile": profile,
            "roast": roast,
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
        
    except Exception as exc:
        logger.exception("Error in roast_user endpoint")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate roast: {str(exc)}"
        )
