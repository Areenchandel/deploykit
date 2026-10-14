"""Redirect service: someone opens a short link -> send them to the real URL."""
import os

import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

app = FastAPI(title="DeployKit Redirect")
db = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/{code}")
def go(code: str):
    url = db.get(f"url:{code}")
    if url is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    db.incr(f"clicks:{code}")  # count every click (analytics service will read this)
    return RedirectResponse(url, status_code=302)
