import fakeredis
from fastapi.testclient import TestClient

import app as shortener

shortener.db = fakeredis.FakeRedis(decode_responses=True)
client = TestClient(shortener.app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_shorten_saves_url():
    res = client.post("/shorten", json={"url": "https://www.amazon.in/some-long-link"})
    assert res.status_code == 200
    code = res.json()["code"]
    assert len(code) == 6
    assert shortener.db.get(f"url:{code}") == "https://www.amazon.in/some-long-link"


def test_invalid_url_rejected():
    res = client.post("/shorten", json={"url": "not-a-link"})
    assert res.status_code == 422
