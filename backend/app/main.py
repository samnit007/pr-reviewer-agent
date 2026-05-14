import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import review

app = FastAPI(title="PR Reviewer Agent", version="1.0.0")

_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
