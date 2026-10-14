import fakeredis
from fastapi.testclient import TestClient

import app as analytics

analytics.db = fakeredis.FakeRedis(decode_responses=True)
client = TestClient(analytics.app)


def setup_function():
    analytics.db.flushall()
    analytics.db.set("url:aaa111", "https://a.com")
    analytics.db.set("url:bbb222", "https://b.com")
    analytics.db.set("clicks:aaa111", 3)
    analytics.db.set("clicks:bbb222", 7)


def test_stats_for_one_link():
    assert client.get("/stats/aaa111").json() == {"code": "aaa111", "url": "https://a.com", "clicks": 3}


def test_link_with_no_clicks_shows_zero():
    analytics.db.set("url:new000", "https://n.com")
    assert client.get("/stats/new000").json()["clicks"] == 0


def test_unknown_code_404():
    assert client.get("/stats/nope99").status_code == 404


def test_top_sorted_by_clicks():
    codes = [r["code"] for r in client.get("/top").json()]
    assert codes == ["bbb222", "aaa111"]
