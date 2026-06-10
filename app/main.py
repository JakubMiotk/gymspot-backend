import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.api_v1 import api_router

def _get_allowed_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
    if configured_origins.strip():
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://gymspot.pl",
        "https://www.gymspot.pl",
        "https://app.gymspot.pl",
    ]


app = FastAPI(title="GymSpot API")

os.makedirs("uploads/video", exist_ok=True)
app.mount("/avatars", StaticFiles(directory="uploads/avatars"), name="avatars")
app.mount("/video", StaticFiles(directory="uploads/video"), name="video")
app.include_router(api_router, prefix="/api/v1")

# Wrap the whole ASGI app so CORS headers are also present on unhandled 500 responses.
app = CORSMiddleware(
    app=app,
    allow_origins=_get_allowed_origins(),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
