def test_register_and_login(client):
    r = client.post("/api/v1/auth/register", json={"name": "Ravi Kumar", "email": "Ravi@Test.com", "phone": "9876500000", "password": "Passw0rd99"})
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["role"] == "customer"
    assert body["user"]["email"] == "ravi@test.com"
    assert "password" not in str(body)

    r = client.post("/api/v1/auth/login", json={"email": "ravi@test.com", "password": "Passw0rd99"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


def test_register_cannot_choose_role(client):
    r = client.post("/api/v1/auth/register", json={"name": "Evil", "email": "e@test.com", "phone": "9876500000", "password": "Passw0rd99", "role": "admin"})
    assert r.status_code == 422


def test_register_validation_and_duplicates(client):
    bad = {"name": "A", "email": "not-an-email", "phone": "12", "password": "short"}
    assert client.post("/api/v1/auth/register", json=bad).status_code == 422
    ok = {"name": "Ravi Kumar", "email": "r@test.com", "phone": "9876500000", "password": "Passw0rd99"}
    assert client.post("/api/v1/auth/register", json=ok).status_code == 201
    assert client.post("/api/v1/auth/register", json=ok).status_code == 409


def test_login_wrong_password(client, customer_headers):
    r = client.post("/api/v1/auth/login", json={"email": "asha@test.com", "password": "WrongPass1"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Incorrect email or password"


def test_profile_requires_token(client, customer_headers):
    assert client.get("/api/v1/users/me").status_code == 401
    assert client.get("/api/v1/users/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
    r = client.get("/api/v1/users/me", headers=customer_headers)
    assert r.status_code == 200 and r.json()["email"] == "asha@test.com"


def test_admin_routes_are_protected(client, customer_headers, admin_headers):
    assert client.get("/api/v1/admin/stats").status_code == 401
    assert client.get("/api/v1/admin/stats", headers=customer_headers).status_code == 403
    assert client.get("/api/v1/admin/stats", headers=admin_headers).status_code == 200
