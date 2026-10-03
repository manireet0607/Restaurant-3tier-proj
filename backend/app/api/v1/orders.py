from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut
from app.services import order_service
from app.services.serializers import order_to_out

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(body: OrderCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_to_out(order_service.create_order(db, user, body))


@router.get("", response_model=List[OrderOut])
def my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.scalars(
        select(Order)
        .where(Order.user_id == user.id)
        .options(selectinload(Order.items).selectinload(OrderItem.menu_item))
        .order_by(Order.created_at.desc(), Order.id.desc())
    ).all()
    return [order_to_out(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
def order_detail(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = order_service.get_order(db, order_id)
    # Customers can only see their own orders. Same 404 as "not found" to avoid leaking ids.
    if order.user_id != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return order_to_out(order)
