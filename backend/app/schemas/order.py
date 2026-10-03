from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.auth import check_phone


class OrderItemIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    menu_item_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=20)


class OrderCreate(BaseModel):
    # extra="forbid": a client that sends prices, totals or a status gets a 422.
    model_config = ConfigDict(extra="forbid")
    customer_name: str = Field(min_length=2, max_length=100)
    customer_phone: str
    delivery_address: str = Field(min_length=10, max_length=500)
    special_instructions: Optional[str] = Field(default=None, max_length=300)
    payment_method: Literal["cod"] = "cod"
    items: List[OrderItemIn] = Field(min_length=1, max_length=40)

    _phone = field_validator("customer_phone")(check_phone)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    menu_item_id: int
    item_name: str = ""
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    order_number: str
    subtotal: Decimal
    delivery_fee: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_method: str
    payment_status: str
    order_status: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    special_instructions: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut]


class StatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"]


class AdminStats(BaseModel):
    total_orders: int
    revenue: Decimal
    customers: int
    menu_items: int
