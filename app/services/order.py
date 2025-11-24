from __future__ import annotations

import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from app import db, mail
from app.models import Order, OrderItem, Product, User
from app.services.cart import CartService
from flask_mail import Message


def _get_or_create_user(email: str, username: Optional[str] = None) -> User:
    user = User.by_email(email)
    if user:
        return user
    if username:
        user = User.by_username(username)
        if user:
            return user

    new_username = username or email.split("@")[0]
    user = User(username=new_username, email=email, password_hash="guest")
    db.session.add(user)
    db.session.commit()
    return user


class OrderService:
    SHIPPING_RATES = {
        "standard": Decimal("5.00"),
        "express": Decimal("15.00"),
    }

    def __init__(self, cart_service: CartService, user_email: str, username: Optional[str] = None):
        self.cart_service = cart_service
        self.user_email = user_email
        self.username = username
        self.user: Optional[User] = None

    @staticmethod
    def tax_rate(country: str, state: str) -> Decimal:
        country = (country or "").upper()
        state = (state or "").upper()
        if country == "US" and state == "CA":
            return Decimal("0.0875")
        if country == "US":
            return Decimal("0.065")
        return Decimal("0.05")

    def _ensure_user(self) -> User:
        if not self.user:
            self.user = _get_or_create_user(self.user_email, username=self.username)
        return self.user

    def _generate_order_number(self) -> str:
        return f"ORD-{datetime.utcnow():%Y%m%d}-{random.randint(10000, 99999)}"

    def _shipping_amount(self, method: str) -> Decimal:
        return self.SHIPPING_RATES.get(method or "standard", Decimal("5.00"))

    def create_order(self, form) -> Order:
        items = self.cart_service.get_cart_items()
        if not items:
            raise ValueError("Cart is empty.")

        user = self._ensure_user()

        subtotal_cents = 0
        for item in items:
            product: Product = item["product"]
            qty = int(item["quantity"])
            if product.quantity is not None and qty > product.quantity:
                raise ValueError(f"Insufficient stock for {product.name}.")
            subtotal_cents += (product.price_cents or 0) * qty

        shipping_dec = self._shipping_amount(form.shipping_method.data)
        shipping_cents = int(shipping_dec * Decimal(100))

        tax_rate = self.tax_rate(form.country.data, form.state.data)
        tax_cents = int((Decimal(subtotal_cents) * tax_rate).quantize(Decimal("1")))

        total_cents = subtotal_cents + tax_cents + shipping_cents

        order = Order(
            order_number=self._generate_order_number(),
            user_id=user.id,
            status="processing",
            subtotal_cents=subtotal_cents,
            tax_cents=tax_cents,
            shipping_cents=shipping_cents,
            total_cents=total_cents,
            shipping_address={
                "full_name": form.full_name.data,
                "address": form.address.data,
                "city": form.city.data,
                "state": form.state.data,
                "zip": form.zip_code.data,
                "country": form.country.data,
                "phone": form.phone.data,
                "shipping_method": form.shipping_method.data,
            },
            billing_address={
                "email": form.email.data,
                "full_name": form.full_name.data,
                "address": form.address.data,
                "city": form.city.data,
                "state": form.state.data,
                "zip": form.zip_code.data,
                "country": form.country.data,
                "phone": form.phone.data,
            },
            payment_method="card",
            payment_status="paid",
            payment_id="demo-payment",
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            product: Product = item["product"]
            qty = int(item["quantity"])
            unit_price_cents = product.price_cents or 0
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                unit_price_cents=unit_price_cents,
                total_cents=unit_price_cents * qty,
            )
            db.session.add(order_item)
            if product.quantity is not None:
                product.quantity = max(product.quantity - qty, 0)

        db.session.commit()
        self.cart_service.clear_cart()
        return order

    def send_confirmation_email(self, order: Order) -> None:
        try:
            msg = Message(
                subject=f"Order Confirmation {order.order_number}",
                recipients=[self.user_email],
                body=f"Thanks for your order {order.order_number}! Total: {Decimal(order.total_cents) / Decimal(100):.2f} GLD",
            )
            mail.send(msg)
        except Exception:
            pass

    @staticmethod
    def estimated_delivery(shipping_method: str) -> datetime:
        days = 2 if shipping_method == "express" else 5
        return datetime.utcnow() + timedelta(days=days)
