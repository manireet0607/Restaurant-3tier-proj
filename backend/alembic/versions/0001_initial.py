"""initial schema

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

MYSQL_OPTS = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("customer", "admin", name="user_role", native_enum=False, length=20), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        **MYSQL_OPTS,
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        **MYSQL_OPTS,
    )

    op.create_table(
        "menu_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("food_type", sa.Enum("veg", "non_veg", name="food_type", native_enum=False, length=10), nullable=False),
        sa.Column("is_available", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_menu_items_price_nonneg"),
        **MYSQL_OPTS,
    )
    op.create_index("ix_menu_items_category_id", "menu_items", ["category_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("order_number", sa.String(30), nullable=False, unique=True),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("delivery_fee", sa.Numeric(10, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_method", sa.Enum("cod", name="payment_method", native_enum=False, length=20), nullable=False),
        sa.Column("payment_status", sa.Enum("pending", "paid", "failed", name="payment_status", native_enum=False, length=20), nullable=False),
        sa.Column(
            "order_status",
            sa.Enum("pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled",
                    name="order_status", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("customer_name", sa.String(100), nullable=False),
        sa.Column("customer_phone", sa.String(20), nullable=False),
        sa.Column("delivery_address", sa.Text, nullable=False),
        sa.Column("special_instructions", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        **MYSQL_OPTS,
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_order_status", "orders", ["order_status"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("menu_item_id", sa.Integer, sa.ForeignKey("menu_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_qty_positive"),
        **MYSQL_OPTS,
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])


def downgrade() -> None:
    for t in ("order_items", "orders", "menu_items", "categories", "users"):
        op.drop_table(t)
