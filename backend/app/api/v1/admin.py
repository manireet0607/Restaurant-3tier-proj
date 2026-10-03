from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.menu import Category, MenuItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.auth import UserOut
from app.schemas.menu import AvailabilityIn, CategoryIn, CategoryOut, MenuItemIn, MenuItemOut
from app.schemas.order import AdminStats, OrderOut, StatusUpdate
from app.services import order_service
from app.services.serializers import order_to_out

# Every route in this router needs an admin.
router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats", response_model=AdminStats)
def stats(db: Session = Depends(get_db)):
    revenue = db.scalar(select(func.coalesce(func.sum(Order.total_amount), 0)).where(Order.order_status != "cancelled"))
    return AdminStats(
        total_orders=db.scalar(select(func.count(Order.id))) or 0,
        revenue=Decimal(revenue or 0),
        customers=db.scalar(select(func.count(User.id)).where(User.role == "customer")) or 0,
        menu_items=db.scalar(select(func.count(MenuItem.id))) or 0,
    )


@router.get("/customers", response_model=List[UserOut])
def customers(db: Session = Depends(get_db)):
    return db.scalars(select(User).where(User.role == "customer").order_by(User.id.desc())).all()


# ---- Categories ----
@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryIn, db: Session = Depends(get_db)):
    if db.scalar(select(Category).where(Category.name == body.name)):
        raise HTTPException(status.HTTP_409_CONFLICT, "A category with this name already exists")
    cat = Category(**body.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, body: CategoryIn, db: Session = Depends(get_db)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    clash = db.scalar(select(Category).where(Category.name == body.name, Category.id != category_id))
    if clash:
        raise HTTPException(status.HTTP_409_CONFLICT, "A category with this name already exists")
    for k, v in body.model_dump().items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    if db.scalar(select(func.count(MenuItem.id)).where(MenuItem.category_id == category_id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Move or delete this category's food items first")
    db.delete(cat)
    db.commit()


# ---- Menu items ----
def _check_category(db: Session, category_id: int) -> None:
    if not db.get(Category, category_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Category does not exist")


@router.post("/menu", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
def create_item(body: MenuItemIn, db: Session = Depends(get_db)):
    _check_category(db, body.category_id)
    item = MenuItem(**body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/menu/{item_id}", response_model=MenuItemOut)
def update_item(item_id: int, body: MenuItemIn, db: Session = Depends(get_db)):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Food item not found")
    _check_category(db, body.category_id)
    for k, v in body.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/menu/{item_id}/availability", response_model=MenuItemOut)
def set_availability(item_id: int, body: AvailabilityIn, db: Session = Depends(get_db)):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Food item not found")
    item.is_available = body.is_available
    db.commit()
    db.refresh(item)
    return item


@router.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Food item not found")
    if db.scalar(select(func.count(OrderItem.id)).where(OrderItem.menu_item_id == item_id)):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "This item is part of past orders. Mark it unavailable instead of deleting it"
        )
    db.delete(item)
    db.commit()


# ---- Orders ----
@router.get("/orders", response_model=List[OrderOut])
def all_orders(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    q = select(Order).options(selectinload(Order.items).selectinload(OrderItem.menu_item))
    if status_filter:
        q = q.where(Order.order_status == status_filter)
    orders = db.scalars(q.order_by(Order.created_at.desc(), Order.id.desc()).limit(limit).offset(offset)).all()
    return [order_to_out(o) for o in orders]


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
def change_status(order_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    order = order_service.get_order(db, order_id)
    return order_to_out(order_service.update_status(db, order, body.status))
