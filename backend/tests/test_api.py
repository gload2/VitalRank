from uuid import uuid4

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _new_user():
    email = f"test_{uuid4().hex[:10]}@vitalrank.ru"
    password = "secret123"
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = resp.json()["access_token"]
    return email, {"Authorization": f"Bearer {token}"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_demo_report():
    r = client.get("/demo/report")
    assert r.status_code == 200
    data = r.json()
    assert data["google_score"] is not None
    assert len(data["issues"]) > 0


def test_register_login_me():
    email, headers = _new_user()
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == email


def test_duplicate_register_rejected():
    email = f"dup_{uuid4().hex[:10]}@vitalrank.ru"
    body = {"email": email, "password": "secret123"}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/register", json=body).status_code == 400


def test_audit_requires_auth():
    r = client.post("/audits", json={"url": "https://example.com/"})
    assert r.status_code == 401


def test_create_audit_flow():
    _, headers = _new_user()
    r = client.post("/audits", json={"url": "https://example.com/"}, headers=headers)
    assert r.status_code == 201
    audit = r.json()
    assert audit["status"] == "pending"

    sites = client.get("/sites", headers=headers).json()
    assert any(s["url"] == "https://example.com/" for s in sites)


def test_ssrf_blocked():
    _, headers = _new_user()
    r = client.post("/audits", json={"url": "http://localhost/"}, headers=headers)
    assert r.status_code == 400


def test_invalid_url_rejected():
    _, headers = _new_user()
    r = client.post("/audits", json={"url": "не-url"}, headers=headers)
    assert r.status_code == 422
