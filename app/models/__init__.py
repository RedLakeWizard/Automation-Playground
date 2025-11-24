from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from slugify import slugify
from sqlalchemy import CheckConstraint, event, or_

from app import bcrypt, db

ORDER_STATUSES = ("pending", "processing", "shipped", "completed", "cancelled")


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.Index("ix_users_username", "username"),
        db.Index("ix_users_email", "email"),
        db.Index("ix_users_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")
    cart_items = db.relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @classmethod
    def by_username(cls, username: str) -> Optional["User"]:
        return cls.query.filter(db.func.lower(cls.username) == username.lower()).first()

    @classmethod
    def by_email(cls, email: str) -> Optional["User"]:
        return cls.query.filter(db.func.lower(cls.email) == email.lower()).first()

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        db.UniqueConstraint("slug", name="uq_categories_slug"),
        db.Index("ix_categories_slug", "slug"),
        db.Index("ix_categories_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    slug = db.Column(db.String(160), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    parent = db.relationship("Category", remote_side=[id], backref="children")
    products = db.relationship("Product", back_populates="category", cascade="all, delete-orphan")

    @classmethod
    def find_by_slug(cls, slug_value: str) -> Optional["Category"]:
        return cls.query.filter_by(slug=slug_value).first()

    @classmethod
    def roots(cls) -> List["Category"]:
        return cls.query.filter(cls.parent_id.is_(None)).order_by(cls.name).all()

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
        db.UniqueConstraint("slug", name="uq_products_slug"),
        db.UniqueConstraint("sku", name="uq_products_sku"),
        db.Index("ix_products_slug", "slug"),
        db.Index("ix_products_sku", "sku"),
        db.Index("ix_products_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False)
    description = db.Column(db.Text)
    price_cents = db.Column(db.Integer, nullable=False)
    compare_price_cents = db.Column(db.Integer)
    sku = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    image_url = db.Column(db.String(500))
    images = db.Column(db.JSON, nullable=False, default=list)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    category = db.relationship("Category", back_populates="products")
    order_items = db.relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    cart_items = db.relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="product", cascade="all, delete-orphan")

    @property
    def in_stock(self) -> bool:
        return self.quantity > 0

    @property
    def price_decimal(self) -> Decimal:
        return Decimal(self.price_cents or 0) / Decimal(100)

    @property
    def compare_price_decimal(self) -> Optional[Decimal]:
        if self.compare_price_cents is None:
            return None
        return Decimal(self.compare_price_cents) / Decimal(100)

    @property
    def price(self) -> Decimal:
        """Alias returning the price in major units as Decimal."""
        return self.price_decimal

    @property
    def compare_price(self) -> Optional[Decimal]:
        return self.compare_price_decimal

    @property
    def discount_cents(self) -> int:
        if self.compare_price_cents and self.compare_price_cents > self.price_cents:
            return self.compare_price_cents - self.price_cents
        return 0

    @property
    def discount_amount(self) -> Decimal:
        return Decimal(self.discount_cents) / Decimal(100)

    @property
    def display_price(self) -> str:
        return f"{self.price_decimal:.2f} GLD"

    @classmethod
    def active(cls):
        return cls.query.filter_by(is_active=True)

    @classmethod
    def featured(cls):
        return cls.active().filter_by(is_featured=True)

    @classmethod
    def find_by_slug(cls, slug_value: str) -> Optional["Product"]:
        return cls.query.filter_by(slug=slug_value).first()

    @classmethod
    def search(cls, term: str):
        ilike_term = f"%{term}%"
        return cls.query.filter(
            or_(cls.name.ilike(ilike_term), cls.description.ilike(ilike_term))
        )

    def __repr__(self) -> str:
        return f"<Product {self.name} ({self.sku}) {self.price_cents}c>"


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','processing','shipped','completed','cancelled')",
            name="ck_orders_status_valid",
        ),
        db.Index("ix_orders_status", "status"),
        db.Index("ix_orders_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(40), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    subtotal_cents = db.Column(db.Integer, nullable=False, default=0)
    tax_cents = db.Column(db.Integer, nullable=False, default=0)
    shipping_cents = db.Column(db.Integer, nullable=False, default=0)
    total_cents = db.Column(db.Integer, nullable=False, default=0)
    shipping_address = db.Column(db.JSON)
    billing_address = db.Column(db.JSON)
    payment_method = db.Column(db.String(40))
    payment_status = db.Column(db.String(20))
    payment_id = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    @property
    def items_total_cents(self) -> int:
        return sum((item.line_total_cents for item in self.items), 0)

    @property
    def items_total(self) -> Decimal:
        return Decimal(self.items_total_cents) / Decimal(100)

    @property
    def computed_total_cents(self) -> int:
        return (self.subtotal_cents or 0) + (self.tax_cents or 0) + (self.shipping_cents or 0)

    @property
    def computed_total(self) -> Decimal:
        return Decimal(self.computed_total_cents) / Decimal(100)

    @property
    def subtotal(self) -> Decimal:
        return Decimal(self.subtotal_cents or 0) / Decimal(100)

    @property
    def tax(self) -> Decimal:
        return Decimal(self.tax_cents or 0) / Decimal(100)

    @property
    def shipping(self) -> Decimal:
        return Decimal(self.shipping_cents or 0) / Decimal(100)

    @property
    def total(self) -> Decimal:
        return Decimal(self.total_cents or 0) / Decimal(100)

    @property
    def is_paid(self) -> bool:
        return (self.payment_status or "").lower() in {"paid", "succeeded", "captured"}

    @classmethod
    def by_status(cls, status: str):
        return cls.query.filter_by(status=status)

    @classmethod
    def for_user(cls, user_id: int):
        return cls.query.filter_by(user_id=user_id)

    @classmethod
    def recent(cls, limit: int = 20):
        return cls.query.order_by(cls.created_at.desc()).limit(limit)

    def __repr__(self) -> str:
        return f"<Order {self.order_number} ({self.status})>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price_cents = db.Column(db.Integer, nullable=False)
    total_cents = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")

    @property
    def line_total_cents(self) -> int:
        return int(self.quantity) * int(self.unit_price_cents or 0)

    @property
    def line_total(self) -> Decimal:
        return Decimal(self.line_total_cents) / Decimal(100)

    def __repr__(self) -> str:
        return f"<OrderItem order={self.order_id} product={self.product_id} qty={self.quantity}>"


class CartItem(db.Model):
    __tablename__ = "cart_items"
    __table_args__ = (db.Index("ix_cart_items_created_at", "created_at"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", back_populates="cart_items")
    product = db.relationship("Product", back_populates="cart_items")

    @classmethod
    def for_user(cls, user_id: int):
        return cls.query.filter_by(user_id=user_id)

    def __repr__(self) -> str:
        return f"<CartItem user={self.user_id} product={self.product_id} qty={self.quantity}>"


class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = (db.Index("ix_reviews_created_at", "created_at"),)

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    product = db.relationship("Product", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    @classmethod
    def recent(cls, limit: int = 10):
        return cls.query.order_by(cls.created_at.desc()).limit(limit)

    def __repr__(self) -> str:
        return f"<Review product={self.product_id} rating={self.rating}>"


def _ensure_product_slug(mapper, connection, target: Product) -> None:
    if target.name:
        target.slug = target.slug or slugify(target.name)
    if not target.slug:
        target.slug = f"product-{int(datetime.now().timestamp())}"


def _ensure_category_slug(mapper, connection, target: Category) -> None:
    if target.name:
        target.slug = target.slug or slugify(target.name)
    if not target.slug:
        target.slug = f"category-{int(datetime.now().timestamp())}"


def _sync_order_item_total(mapper, connection, target: OrderItem) -> None:
    target.total_cents = target.line_total_cents


event.listen(Product, "before_insert", _ensure_product_slug)
event.listen(Product, "before_update", _ensure_product_slug)
event.listen(Category, "before_insert", _ensure_category_slug)
event.listen(Category, "before_update", _ensure_category_slug)
event.listen(OrderItem, "before_insert", _sync_order_item_total)
event.listen(OrderItem, "before_update", _sync_order_item_total)


__all__ = [
    "User",
    "Category",
    "Product",
    "Order",
    "OrderItem",
    "CartItem",
    "Review",
    "ORDER_STATUSES",
]
