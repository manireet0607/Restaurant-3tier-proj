from decimal import Decimal


def test_order_totals_are_calculated_on_the_server(client, customer_headers, order_body):
    r = client.post("/api/v1/orders", json=order_body, headers=customer_headers)
    assert r.status_code == 201, r.text
    o = r.json()
    # 2 x 180.00 + 1 x 220.50 = 580.50 ; tax 5% = 29.03 (rounded) ; delivery 40.00
    assert Decimal(o["subtotal"]) == Decimal("580.50")
    assert Decimal(o["tax_amount"]) == Decimal("29.03")
    assert Decimal(o["delivery_fee"]) == Decimal("40.00")
    assert Decimal(o["total_amount"]) == Decimal("649.53")
    assert o["order_status"] == "pending" and o["payment_method"] == "cod" and o["payment_status"] == "pending"
    assert o["order_number"].startswith("DW-")
    assert [i["item_name"] for i in o["items"]] == ["Veg Hakka Noodles", "Chicken Hakka Noodles"]


def test_client_cannot_send_prices_totals_or_status(client, customer_headers, order_body):
    for field, value in [("total_amount", "1.00"), ("order_status", "delivered"), ("delivery_fee", "0"), ("user_id", 1)]:
        r = client.post("/api/v1/orders", json={**order_body, field: value}, headers=customer_headers)
        assert r.status_code == 422, field
    order_body["items"][0]["unit_price"] = "1.00"
    assert client.post("/api/v1/orders", json=order_body, headers=customer_headers).status_code == 422


def test_unit_price_is_saved_with_the_order(client, customer_headers, admin_headers, order_body):
    oid = client.post("/api/v1/orders", json=order_body, headers=customer_headers).json()["id"]
    item = client.get("/api/v1/menu").json()[0]
    client.put(f"/api/v1/admin/menu/{item['id']}", json={**item, "price": "999.00"}, headers=admin_headers)
    old = client.get(f"/api/v1/orders/{oid}", headers=customer_headers).json()
    assert Decimal(old["items"][0]["unit_price"]) == Decimal("180.00")
    assert Decimal(old["total_amount"]) == Decimal("649.53")


def test_duplicate_lines_are_merged(client, customer_headers, order_body):
    order_body["items"] = [{"menu_item_id": 1, "quantity": 1}, {"menu_item_id": 1, "quantity": 2}]
    o = client.post("/api/v1/orders", json=order_body, headers=customer_headers).json()
    assert len(o["items"]) == 1 and o["items"][0]["quantity"] == 3


def test_invalid_orders_are_rejected(client, customer_headers, order_body):
    def post(**changes):
        return client.post("/api/v1/orders", json={**order_body, **changes}, headers=customer_headers)

    assert post(items=[]).status_code == 422
    assert post(items=[{"menu_item_id": 1, "quantity": 0}]).status_code == 422
    assert post(items=[{"menu_item_id": 1, "quantity": 21}]).status_code == 422
    assert post(items=[{"menu_item_id": 1, "quantity": -1}]).status_code == 422
    assert post(items=[{"menu_item_id": 999, "quantity": 1}]).status_code == 400
    assert post(items=[{"menu_item_id": 3, "quantity": 1}]).status_code == 400  # unavailable
    assert post(customer_phone="abc").status_code == 422
    assert post(delivery_address="short").status_code == 422
    assert post(payment_method="card").status_code == 422


def test_order_requires_login(client, order_body):
    assert client.post("/api/v1/orders", json=order_body).status_code == 401
    assert client.get("/api/v1/orders").status_code == 401


def test_customers_only_see_their_own_orders(client, customer_headers, admin_headers, order_body):
    oid = client.post("/api/v1/orders", json=order_body, headers=customer_headers).json()["id"]
    other = client.post("/api/v1/auth/register", json={"name": "Other Person", "email": "o@test.com", "phone": "9876511111", "password": "Passw0rd99"}).json()
    other_h = {"Authorization": f"Bearer {other['access_token']}"}
    assert client.get(f"/api/v1/orders/{oid}", headers=other_h).status_code == 404
    assert client.get("/api/v1/orders", headers=other_h).json() == []
    assert len(client.get("/api/v1/orders", headers=customer_headers).json()) == 1
    assert client.get(f"/api/v1/orders/{oid}", headers=admin_headers).status_code == 200
