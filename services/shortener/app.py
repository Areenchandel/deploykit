"""Shortener service: takes a long URL, saves it in Redis, returns a short code."""
import os
import secrets
import string

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
ALPHABET = string.ascii_letters + string.digits

app = FastAPI(title="DeployKit Shortener")
db = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


class ShortenRequest(BaseModel):
    url: HttpUrl


def new_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten")
def shorten(req: ShortenRequest):
    for _ in range(5):  # retry if code already taken
        code = new_code()
        # nx=True -> only save if this code doesn't exist yet
        if db.set(f"url:{code}", str(req.url), nx=True):
            return {"code": code, "short_url": f"{BASE_URL}/{code}"}
    raise HTTPException(status_code=500, detail="Could not generate a unique code")
