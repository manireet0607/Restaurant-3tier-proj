from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.menu import Category, MenuItem
from app.schemas.menu import CategoryOut, MenuItemOut

router = APIRouter(tags=["menu"])


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.id)).all()


@router.get("/menu", response_model=List[MenuItemOut])
def list_menu(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = select(MenuItem).order_by(MenuItem.category_id, MenuItem.id)
    if category_id is not None:
        q = q.where(MenuItem.category_id == category_id)
    return db.scalars(q).all()


@router.get("/config")
def public_config():
    """Fees shown in the cart. Display only: the server recalculates at checkout."""
    from app.core.config import get_settings

    s = get_settings()
    return {"delivery_fee": str(s.DELIVERY_FEE), "tax_percent": str(s.TAX_PERCENT), "currency": "INR"}
