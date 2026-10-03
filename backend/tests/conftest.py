import os

# Tests use a throwaway SQLite file. Set before the app is imported.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-0123456789"
os.environ["APP_ENV"] = "development"
os.environ["DELIVERY_FEE"] = "40.00"
os.environ["TAX_PERCENT"] = "5.00"

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models import Category, MenuItem, User


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        cat = Category(name="Noodles", description="Wok noodles")
        db.add(cat)
        db.flush()
        db.add_all([
            MenuItem(category_id=cat.id, name="Veg Hakka Noodles", description="d", price="180.00", food_type="veg", is_available=True),
            MenuItem(category_id=cat.id, name="Chicken Hakka Noodles", description="d", price="220.50", food_type="non_veg", is_available=True),
            MenuItem(category_id=cat.id, name="Sold Out Noodles", description="d", price="99.00", food_type="veg", is_available=False),
        ])
        db.add(User(name="Admin", email="admin@test.com", phone="9999999999", password_hash=hash_password("Admin1234"), role="admin"))
        db.commit()
    yield
    engine.dispose()


@pytest.fixture
def client():
    return TestClient(app)


def _login(client, email, password):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def customer_headers(client):
    r = client.post("/api/v1/auth/register", json={"name": "Asha Verma", "email": "asha@test.com", "phone": "9876543210", "password": "Secret1234"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin_headers(client):
    return _login(client, "admin@test.com", "Admin1234")


ORDER_BODY = {
    "customer_name": "Asha Verma",
    "customer_phone": "9876543210",
    "delivery_address": "12 MG Road, New Delhi 110001",
    "payment_method": "cod",
    "items": [{"menu_item_id": 1, "quantity": 2}, {"menu_item_id": 2, "quantity": 1}],
}


@pytest.fixture
def order_body():
    return {**ORDER_BODY, "items": [dict(i) for i in ORDER_BODY["items"]]}
