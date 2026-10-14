"""Analytics service: shows how many clicks each short link got."""
import os

import redis
from fastapi import FastAPI, HTTPException

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

app = FastAPI(title="DeployKit Analytics")
db = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats/{code}")
def stats(code: str):
    url = db.get(f"url:{code}")
    if url is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    return {"code": code, "url": url, "clicks": int(db.get(f"clicks:{code}") or 0)}


@app.get("/top")
def top(limit: int = 5):
    """Most clicked links. scan_iter walks keys without blocking Redis."""
    rows = []
    for key in db.scan_iter(match="clicks:*", count=100):
        code = key.split(":", 1)[1]
        rows.append({"code": code, "url": db.get(f"url:{code}"), "clicks": int(db.get(key) or 0)})
    rows.sort(key=lambda r: r["clicks"], reverse=True)
    return rows[:limit]
