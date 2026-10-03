from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class CategoryOut(CategoryIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class MenuItemIn(BaseModel):
    category_id: int
    name: str = Field(min_length=2, max_length=150)
    description: str = Field(default="", max_length=1000)
    price: Decimal = Field(ge=0, le=100000, max_digits=10, decimal_places=2)
    image_url: Optional[str] = Field(default=None, max_length=500)
    food_type: Literal["veg", "non_veg"]
    is_available: bool = True


class AvailabilityIn(BaseModel):
    is_available: bool


class MenuItemOut(MenuItemIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
