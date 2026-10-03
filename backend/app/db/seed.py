"""Seeds sample menu data and the first admin. Safe to run many times.
Usage: python -m app.db.seed"""
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.menu import Category, MenuItem
from app.models.user import User

log = logging.getLogger("dragonwok.seed")

CATEGORIES = [
    ("Chinese Starters", "Crispy and spicy openers", "starters"),
    ("Noodles", "Wok-tossed Hakka noodles", "noodles"),
    ("Fried Rice", "Smoky wok fried rice", "rice"),
    ("Chinese Main Course", "Rich gravies and dry dishes", "main"),
    ("Soups", "Hot and comforting bowls", "soups"),
    ("Momos", "Steamed and fried dumplings", "momos"),
    ("Desserts", "Sweet endings", "desserts"),
    ("Beverages", "Cool drinks", "beverages"),
]

# (category, name, description, price, food_type)
ITEMS = [
    ("Noodles", "Veg Hakka Noodles", "Wok-tossed noodles with crunchy cabbage, carrot and capsicum.", "180", "veg"),
    ("Noodles", "Chicken Hakka Noodles", "Smoky noodles tossed with tender chicken and vegetables.", "220", "non_veg"),
    ("Fried Rice", "Veg Fried Rice", "Fragrant rice fried on high heat with fresh vegetables.", "170", "veg"),
    ("Fried Rice", "Chicken Fried Rice", "Wok fried rice with egg, chicken and spring onion.", "210", "non_veg"),
    ("Chinese Starters", "Chilli Paneer", "Crispy paneer cubes in a spicy garlic soy glaze.", "240", "veg"),
    ("Chinese Starters", "Chilli Chicken", "Crispy chicken tossed with capsicum and green chilli.", "280", "non_veg"),
    ("Chinese Starters", "Spring Rolls", "Golden crispy rolls filled with vegetables, with sweet chilli dip.", "150", "veg"),
    ("Chinese Main Course", "Veg Manchurian", "Vegetable dumplings in a rich Manchurian gravy.", "200", "veg"),
    ("Chinese Main Course", "Chicken Manchurian", "Chicken balls simmered in a tangy, garlicky Manchurian gravy.", "260", "non_veg"),
    ("Soups", "Hot and Sour Soup", "Peppery and tangy soup with vegetables and tofu.", "130", "veg"),
    ("Momos", "Veg Momos", "Steamed dumplings stuffed with cabbage, carrot and herbs.", "120", "veg"),
    ("Momos", "Chicken Momos", "Juicy steamed dumplings with spiced chicken filling.", "150", "non_veg"),
    ("Desserts", "Chocolate Brownie", "Warm fudgy brownie with chocolate sauce.", "140", "veg"),
    ("Beverages", "Cold Coffee", "Chilled creamy coffee blended with ice cream.", "110", "veg"),
]


def run() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        slugs = {}
        for name, desc, slug in CATEGORIES:
            cat = db.scalar(select(Category).where(Category.name == name))
            if not cat:
                cat = Category(name=name, description=desc)
                db.add(cat)
                db.flush()
            slugs[cat.id] = slug
        db.commit()

        cats = {c.name: c for c in db.scalars(select(Category))}
        slug_by_name = {name: slug for name, _, slug in CATEGORIES}
        for cat_name, name, desc, price, ftype in ITEMS:
            if db.scalar(select(MenuItem).where(MenuItem.name == name)):
                continue
            db.add(MenuItem(
                category_id=cats[cat_name].id, name=name, description=desc, price=Decimal(price),
                food_type=ftype, image_url=f"/images/{slug_by_name[cat_name]}.svg", is_available=True,
            ))
        db.commit()

        if settings.ADMIN_PASSWORD:
            email = settings.ADMIN_EMAIL.lower()
            if not db.scalar(select(User).where(User.email == email)):
                db.add(User(name="Dragon Wok Admin", email=email, phone="0000000000",
                            password_hash=hash_password(settings.ADMIN_PASSWORD), role="admin"))
                db.commit()
                log.info("admin user created: %s", email)
        else:
            log.warning("ADMIN_PASSWORD not set: no admin user created")


if __name__ == "__main__":
    from app.core.logging import setup_logging
    setup_logging(get_settings().LOG_LEVEL)
    run()
