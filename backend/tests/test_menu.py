def test_categories_and_menu_are_public(client):
    cats = client.get("/api/v1/categories").json()
    assert [c["name"] for c in cats] == ["Noodles"]
    items = client.get("/api/v1/menu").json()
    assert len(items) == 3
    assert {"id", "name", "price", "food_type", "is_available", "image_url", "category_id", "description"} <= set(items[0])


def test_menu_filter_by_category(client):
    cid = client.get("/api/v1/categories").json()[0]["id"]
    assert len(client.get(f"/api/v1/menu?category_id={cid}").json()) == 3
    assert client.get("/api/v1/menu?category_id=999").json() == []


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/v1/health").json()["database"] == "ok"


def test_public_config(client):
    c = client.get("/api/v1/config").json()
    assert c["delivery_fee"] == "40.00" and c["tax_percent"] == "5.00" and c["currency"] == "INR"
