"""Payment providers. Add an online gateway later by implementing PaymentProvider
and registering it in PROVIDERS. The order service only talks to this interface."""
from typing import Dict, Protocol

from app.models.order import Order


class PaymentProvider(Protocol):
    method: str

    def initial_status(self, order: Order) -> str: ...
    def on_delivered(self, order: Order) -> str: ...


class CashOnDelivery:
    method = "cod"

    def initial_status(self, order: Order) -> str:
        return "pending"  # money is collected at the door

    def on_delivered(self, order: Order) -> str:
        return "paid"


PROVIDERS: Dict[str, PaymentProvider] = {"cod": CashOnDelivery()}


def get_provider(method: str) -> PaymentProvider:
    try:
        return PROVIDERS[method]
    except KeyError:
        raise ValueError(f"Unsupported payment method: {method}")
