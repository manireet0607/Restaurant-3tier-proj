from decimal import Decimal

NEW_ITEM = {"category_id": 1, "name": "Spring Rolls", "description": "Crispy", "price": "150.00", "image_url": None, "food_type": "veg", "is_available": True}


def test_admin_menu_crud(client, admin_headers):
    r = client.post("/api/v1/admin/menu", json=NEW_ITEM, headers=admin_headers)
    assert r.status_code == 201
    item = r.json()

    r = client.put(f"/api/v1/admin/menu/{item['id']}", json={**NEW_ITEM, "price": "175.00"}, headers=admin_headers)
    assert r.status_code == 200 and Decimal(r.json()["price"]) == Decimal("175.00")

    r = client.patch(f"/api/v1/admin/menu/{item['id']}/availability", json={"is_available": False}, headers=admin_headers)
    assert r.json()["is_available"] is False

    assert client.delete(f"/api/v1/admin/menu/{item['id']}", headers=admin_headers).status_code == 204
    assert client.delete(f"/api/v1/admin/menu/{item['id']}", headers=admin_headers).status_code == 404


def test_customer_cannot_manage_menu(client, customer_headers):
    assert client.post("/api/v1/admin/menu", json=NEW_ITEM, headers=customer_headers).status_code == 403
    assert client.delete("/api/v1/admin/menu/1", headers=customer_headers).status_code == 403
    assert client.post("/api/v1/admin/menu", json=NEW_ITEM).status_code == 401


def test_admin_menu_validation(client, admin_headers):
    assert client.post("/api/v1/admin/menu", json={**NEW_ITEM, "price": "-5"}, headers=admin_headers).status_code == 422
    assert client.post("/api/v1/admin/menu", json={**NEW_ITEM, "category_id": 999}, headers=admin_headers).status_code == 400
    assert client.post("/api/v1/admin/menu", json={**NEW_ITEM, "food_type": "meat"}, headers=admin_headers).status_code == 422


def test_item_in_past_orders_cannot_be_deleted(client, admin_headers, customer_headers, order_body):
    client.post("/api/v1/orders", json=order_body, headers=customer_headers)
    assert client.delete("/api/v1/admin/menu/1", headers=admin_headers).status_code == 409


def test_admin_category_management(client, admin_headers):
    r = client.post("/api/v1/admin/categories", json={"name": "Soups", "description": "Hot"}, headers=admin_headers)
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.post("/api/v1/admin/categories", json={"name": "Soups"}, headers=admin_headers).status_code == 409
    assert client.put(f"/api/v1/admin/categories/{cid}", json={"name": "Hot Soups"}, headers=admin_headers).json()["name"] == "Hot Soups"
    assert client.delete("/api/v1/admin/categories/1", headers=admin_headers).status_code == 409  # has items
    assert client.delete(f"/api/v1/admin/categories/{cid}", headers=admin_headers).status_code == 204


def test_order_status_workflow(client, admin_headers, customer_headers, order_body):
    oid = client.post("/api/v1/orders", json=order_body, headers=customer_headers).json()["id"]
    url = f"/api/v1/admin/orders/{oid}/status"

    # cannot skip steps
    assert client.patch(url, json={"status": "delivered"}, headers=admin_headers).status_code == 409
    for step in ["confirmed", "preparing", "out_for_delivery", "delivered"]:
        r = client.patch(url, json={"status": step}, headers=admin_headers)
        assert r.status_code == 200 and r.json()["order_status"] == step
    assert r.json()["payment_status"] == "paid"  # cash collected on delivery
    # final state
    assert client.patch(url, json={"status": "cancelled"}, headers=admin_headers).status_code == 409
    assert client.patch(url, json={"status": "bogus"}, headers=admin_headers).status_code == 422


def test_cancellation_rules(client, admin_headers, customer_headers, order_body):
    oid = client.post("/api/v1/orders", json=order_body, headers=customer_headers).json()["id"]
    url = f"/api/v1/admin/orders/{oid}/status"
    assert client.patch(url, json={"status": "cancelled"}, headers=admin_headers).json()["order_status"] == "cancelled"
    assert client.patch(url, json={"status": "confirmed"}, headers=admin_headers).status_code == 409


def test_customer_cannot_change_status(client, customer_headers, order_body):
    oid = client.post("/api/v1/orders", json=order_body, headers=customer_headers).json()["id"]
    r = client.patch(f"/api/v1/admin/orders/{oid}/status", json={"status": "delivered"}, headers=customer_headers)
    assert r.status_code == 403


def test_admin_stats_and_order_list(client, admin_headers, customer_headers, order_body):
    client.post("/api/v1/orders", json=order_body, headers=customer_headers)
    s = client.get("/api/v1/admin/stats", headers=admin_headers).json()
    assert s["total_orders"] == 1 and s["customers"] == 1 and s["menu_items"] == 3
    assert Decimal(s["revenue"]) == Decimal("649.53")
    orders = client.get("/api/v1/admin/orders", headers=admin_headers).json()
    assert len(orders) == 1 and orders[0]["customer_phone"] == "9876543210"
    assert len(client.get("/api/v1/admin/customers", headers=admin_headers).json()) == 1
