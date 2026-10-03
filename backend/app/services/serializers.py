from app.models.order import Order
from app.schemas.order import OrderItemOut, OrderOut


def order_to_out(order: Order) -> OrderOut:
    out = OrderOut.model_validate(order)
    out.items = [
        OrderItemOut(
            id=i.id, menu_item_id=i.menu_item_id, item_name=i.menu_item.name if i.menu_item else "",
            quantity=i.quantity, unit_price=i.unit_price, subtotal=i.subtotal,
        )
        for i in order.items
    ]
    return out
