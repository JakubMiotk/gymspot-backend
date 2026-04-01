from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.api_v1 import api_router

app = FastAPI(title="GymSpot API") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/avatars", StaticFiles(directory="uploads/avatars"), name="avatars")
app.include_router(api_router, prefix="/api/v1")
