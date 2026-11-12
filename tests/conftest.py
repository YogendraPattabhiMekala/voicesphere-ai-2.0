import os

os.environ["DATABASE_URL"] = "sqlite:////tmp/voicesphere-test.db"
os.environ["APP_SECRET_KEY"] = "testing-secret-key-must-be-at-least-32-characters"
from fastapi.testclient import TestClient
from apps.api.voicesphere.db import Base, engine, SessionLocal
from apps.api.voicesphere.main import app
from apps.api.voicesphere.models import Organization, User, Membership, Customer, Order
from apps.api.voicesphere.security import hash_password
import pytest


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()
    a = Organization(name="Tenant A")
    b = Organization(name="Tenant B")
    db.add_all([a, b])
    db.flush()
    u = User(
        email="a@example.test",
        full_name="User A",
        password_hash=hash_password("password-123"),
    )
    db.add(u)
    db.flush()
    db.add(Membership(organization_id=a.id, user_id=u.id, role="org_admin"))
    c = Customer(
        organization_id=a.id,
        name="Test Customer",
        email="customer@example.test",
        phone="555",
        verification_last4="1234",
    )
    db.add(c)
    db.flush()
    db.add(
        Order(
            organization_id=a.id,
            customer_id=c.id,
            order_number="ORD-1",
            item="Laptop",
            status="in_transit",
            estimated_delivery="Friday",
        )
    )
    foreign = Customer(
        organization_id=b.id,
        name="Other Tenant",
        email="other@example.test",
        verification_last4="9999",
    )
    db.add(foreign)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def auth_headers(client):
    r = client.post(
        "/api/auth/login",
        data={"username": "a@example.test", "password": "password-123"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
