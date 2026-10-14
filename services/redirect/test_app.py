import fakeredis
from fastapi.testclient import TestClient

import app as redirect

redirect.db = fakeredis.FakeRedis(decode_responses=True)
client = TestClient(redirect.app)


def test_redirects_to_real_url():
    redirect.db.set("url:abc123", "https://www.amazon.in/x")
    res = client.get("/abc123", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "https://www.amazon.in/x"


def test_counts_clicks():
    redirect.db.set("url:clk001", "https://example.com")
    client.get("/clk001", follow_redirects=False)
    client.get("/clk001", follow_redirects=False)
    assert redirect.db.get("clicks:clk001") == "2"


def test_unknown_code_404():
    assert client.get("/nope99", follow_redirects=False).status_code == 404
