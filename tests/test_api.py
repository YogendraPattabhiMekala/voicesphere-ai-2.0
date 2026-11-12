from tests.conftest import auth_headers


def test_login_me_and_dashboard(client):
    h = auth_headers(client)
    assert client.get("/api/auth/me", headers=h).json()["email"] == "a@example.test"
    d = client.get("/api/dashboard", headers=h).json()
    assert d["metrics"]["customers"] == 1 and d["metrics"]["orders"] == 1


def test_verification_required_for_order_lookup(client):
    h = auth_headers(client)
    blocked = client.get("/api/tools/orders/ORD-1", headers=h)
    assert blocked.status_code == 422
    bad = client.post(
        "/api/tools/verify-customer",
        headers=h,
        json={"email": "customer@example.test", "last4": "0000"},
    )
    assert bad.status_code == 401
    ok = client.post(
        "/api/tools/verify-customer",
        headers=h,
        json={"email": "customer@example.test", "last4": "1234"},
    )
    assert ok.status_code == 200
    token = ok.json()["verification_token"]
    good = client.get(
        "/api/tools/orders/ORD-1",
        headers={**h, "X-Customer-Verification": token},
    )
    assert good.status_code == 200 and good.json()["status"] == "in_transit"


def test_tenant_isolation_on_customer_and_order_access(client):
    h = auth_headers(client)
    customer_data = client.get("/api/customers", headers=h).json()
    assert (
        len(customer_data) == 1 and customer_data[0]["email"] == "customer@example.test"
    )
    verified = client.post(
        "/api/tools/verify-customer",
        headers=h,
        json={"email": "other@example.test", "last4": "9999"},
    )
    assert verified.status_code == 401


def test_ticket_write_and_agent_lifecycle(client):
    h = auth_headers(client)
    response = client.post(
        "/api/tools/tickets",
        headers=h,
        json={
            "customer_id": 1,
            "subject": "Where is my package?",
            "description": "Customer asked for shipping help.",
        },
    )
    assert response.status_code == 201
    assert (
        client.post(
            "/api/tools/tickets",
            headers=h,
            json={
                "customer_id": 999,
                "subject": "Not found customer",
                "description": "Must not cross tenant.",
            },
        ).status_code
        == 404
    )
    agent = client.post("/api/agents", headers=h, json={"name": "Returns Helper"})
    assert agent.status_code == 201
    published = client.patch(f"/api/agents/{agent.json()['id']}/publish", headers=h)
    assert published.json()["status"] == "published"


def test_voice_session_labels_mock_mode(client):
    h = auth_headers(client)
    r = client.post("/api/voice/sessions", headers=h)
    assert r.status_code == 201 and r.json()["mode"] == "mock"
    assert "no microphone" in r.json()["warning"]


def test_unauthenticated_routes_rejected(client):
    assert client.get("/api/customers").status_code == 401


def test_voice_session_can_end_and_stays_tenant_scoped(client):
    headers = auth_headers(client)
    created = client.post("/api/voice/sessions", headers=headers).json()
    ended = client.post(
        f"/api/voice/sessions/{created['conversation_id']}/end", headers=headers
    )
    assert ended.status_code == 200 and ended.json()["status"] == "ended"
    assert (
        client.post("/api/voice/sessions/9999/end", headers=headers).status_code == 404
    )


def test_livekit_token_includes_agent_dispatch(client, monkeypatch):
    from apps.api.voicesphere.config import settings

    monkeypatch.setattr(settings, "voice_mode", "livekit")
    monkeypatch.setattr(settings, "livekit_url", "wss://demo.livekit.invalid")
    monkeypatch.setattr(settings, "livekit_api_key", "test-api-key")
    monkeypatch.setattr(
        settings, "livekit_api_secret", "test-secret-key-long-enough-for-testing-only"
    )
    headers = auth_headers(client)
    response = client.post("/api/voice/sessions", headers=headers)
    assert response.status_code == 201
    payload = __import__("jwt").decode(
        response.json()["token"], options={"verify_signature": False}
    )
    assert payload["video"]["roomJoin"] is True
    assert payload["roomConfig"]["agents"][0]["agentName"] == "voicesphere-support"
