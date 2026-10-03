import secrets
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.menu import MenuItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate
from app.services.payments import get_provider

CENT = Decimal("0.01")
# Allowed status moves. Anything else is rejected.
TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"preparing", "cancelled"},
    "preparing": {"out_for_delivery", "cancelled"},
    "out_for_delivery": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def money(v: Decimal) -> Decimal:
    return v.quantize(CENT, rounding=ROUND_HALF_UP)


def new_order_number() -> str:
    suffix = "".join(secrets.choice(_ALPHABET) for _ in range(6))
    return f"DW-{datetime.now(timezone.utc):%Y%m%d}-{suffix}"


def create_order(db: Session, user: User, payload: OrderCreate) -> Order:
    settings = get_settings()

    # Merge duplicate lines for the same item.
    qty: Dict[int, int] = {}
    for line in payload.items:
        qty[line.menu_item_id] = qty.get(line.menu_item_id, 0) + line.quantity
    if any(q > 20 for q in qty.values()):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Maximum 20 of one item per order")

    menu = {m.id: m for m in db.scalars(select(MenuItem).where(MenuItem.id.in_(qty.keys())))}
    missing = set(qty) - set(menu)
    if missing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Some items are no longer on the menu")
    for m in menu.values():
        if not m.is_available:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{m.name} is currently unavailable")

    # All money is computed here, from current database prices.
    items = []
    subtotal = Decimal("0.00")
    for item_id, q in qty.items():
        m = menu[item_id]
        line_total = money(m.price * q)
        subtotal += line_total
        items.append(OrderItem(menu_item_id=m.id, quantity=q, unit_price=m.price, subtotal=line_total))
    delivery_fee = money(settings.DELIVERY_FEE)
    tax = money(subtotal * settings.TAX_PERCENT / Decimal(100))
    total = money(subtotal + delivery_fee + tax)

    provider = get_provider(payload.payment_method)
    order = Order(
        user_id=user.id,
        order_number=new_order_number(),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        tax_amount=tax,
        total_amount=total,
        payment_method=provider.method,
        payment_status="pending",
        order_status="pending",
        customer_name=payload.customer_name.strip(),
        customer_phone=payload.customer_phone,
        delivery_address=payload.delivery_address.strip(),
        special_instructions=(payload.special_instructions or "").strip() or None,
        items=items,
    )
    order.payment_status = provider.initial_status(order)
    db.add(order)
    db.commit()
    return get_order(db, order.id)


def get_order(db: Session, order_id: int) -> Order:
    order = db.scalar(
        select(Order).where(Order.id == order_id).options(selectinload(Order.items).selectinload(OrderItem.menu_item))
    )
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return order


def update_status(db: Session, order: Order, new_status: str) -> Order:
    if new_status not in TRANSITIONS[order.order_status]:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Cannot change an order from '{order.order_status}' to '{new_status}'"
        )
    order.order_status = new_status
    if new_status == "delivered":
        order.payment_status = get_provider(order.payment_method).on_delivered(order)
    db.commit()
    return get_order(db, order.id)
