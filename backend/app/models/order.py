from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

ORDER_STATUSES = ("pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled")
PAYMENT_METHODS = ("cod",)
PAYMENT_STATUSES = ("pending", "paid", "failed")


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_user_id", "user_id"), Index("ix_orders_order_status", "order_status"))

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    order_number: Mapped[str] = mapped_column(String(30), unique=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    payment_method: Mapped[str] = mapped_column(Enum(*PAYMENT_METHODS, name="payment_method", native_enum=False, length=20), default="cod")
    payment_status: Mapped[str] = mapped_column(Enum(*PAYMENT_STATUSES, name="payment_status", native_enum=False, length=20), default="pending")
    order_status: Mapped[str] = mapped_column(Enum(*ORDER_STATUSES, name="order_status", native_enum=False, length=20), default="pending")
    customer_name: Mapped[str] = mapped_column(String(100))
    customer_phone: Mapped[str] = mapped_column(String(20))
    delivery_address: Mapped[str] = mapped_column(Text)
    special_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_qty_positive"),
        Index("ix_order_items_order_id", "order_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id", ondelete="RESTRICT"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # price at the time of order
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
