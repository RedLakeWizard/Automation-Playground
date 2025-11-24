from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from flask import session

from app import db
from app.models import CartItem, Product, User


def _get_or_create_user(username: str) -> User:
    user = User.by_username(username)
    if not user:
        user = User(username=username, email=f"{username}@example.com", password_hash="!")
        db.session.add(user)
        db.session.commit()
    return user


class CartService:
    """
    Cart service that stores items in session for guests and in the database for authenticated users.
    """

    session_key = "cart"

    def __init__(self, username: Optional[str] = None):
        self.user: Optional[User] = _get_or_create_user(username) if username else None

    def _session_cart(self) -> List[Dict]:
        cart = session.get(self.session_key, [])
        if not isinstance(cart, list):
            cart = []
        return cart

    def _save_session_cart(self, cart: List[Dict]) -> None:
        session[self.session_key] = cart

    def add_item(self, product_id: int, quantity: int) -> Tuple[bool, str]:
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return False, "Product not found."

        quantity = max(int(quantity or 0), 1)
        if product.quantity is not None and quantity > product.quantity:
            return False, "Not enough stock available."

        if self.user:
            item = CartItem.query.filter_by(user_id=self.user.id, product_id=product_id).first()
            if not item:
                item = CartItem(user_id=self.user.id, product_id=product_id, quantity=0)
                db.session.add(item)
            new_qty = item.quantity + quantity
            if product.quantity is not None:
                new_qty = min(new_qty, product.quantity)
            item.quantity = new_qty
            db.session.commit()
        else:
            cart = self._session_cart()
            existing = next((c for c in cart if c.get("product_id") == product_id), None)
            if existing:
                new_qty = existing.get("quantity", 0) + quantity
                if product.quantity is not None:
                    new_qty = min(new_qty, product.quantity)
                existing["quantity"] = new_qty
                existing["price_cents"] = product.price_cents
            else:
                cart.append({"product_id": product_id, "quantity": quantity, "price_cents": product.price_cents})
            self._save_session_cart(cart)
        return True, "Added to cart."

    def update_quantity(self, product_id: int, quantity: int) -> Tuple[bool, str]:
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return False, "Product not found."

        quantity = max(int(quantity or 0), 0)
        if quantity == 0:
            return self.remove_item(product_id)

        if product.quantity is not None and quantity > product.quantity:
            return False, "Not enough stock available."

        if self.user:
            item = CartItem.query.filter_by(user_id=self.user.id, product_id=product_id).first()
            if not item:
                return False, "Item not in cart."
            item.quantity = quantity
            db.session.commit()
        else:
            cart = self._session_cart()
            for c in cart:
                if c.get("product_id") == product_id:
                    c["quantity"] = quantity
                    c["price_cents"] = product.price_cents
                    break
            else:
                return False, "Item not in cart."
            self._save_session_cart(cart)
        return True, "Cart updated."

    def remove_item(self, product_id: int) -> Tuple[bool, str]:
        if self.user:
            item = CartItem.query.filter_by(user_id=self.user.id, product_id=product_id).first()
            if not item:
                return False, "Item not in cart."
            db.session.delete(item)
            db.session.commit()
        else:
            cart = [c for c in self._session_cart() if c.get("product_id") != product_id]
            self._save_session_cart(cart)
        return True, "Removed."

    def clear_cart(self) -> None:
        if self.user:
            CartItem.query.filter_by(user_id=self.user.id).delete()
            db.session.commit()
        else:
            session.pop(self.session_key, None)

    def get_cart_items(self) -> List[Dict]:
        items: List[Dict] = []
        if self.user:
            cart_items = (
                CartItem.query.join(Product, Product.id == CartItem.product_id)
                .filter(CartItem.user_id == self.user.id)
                .all()
            )
            for ci in cart_items:
                product = ci.product
                line_total_cents = (product.price_cents or 0) * ci.quantity
                items.append(
                    {
                        "product": product,
                        "quantity": ci.quantity,
                        "price_cents": product.price_cents,
                        "line_total_cents": line_total_cents,
                        "line_total": Decimal(line_total_cents) / Decimal(100),
                    }
                )
        else:
            for entry in self._session_cart():
                product = Product.query.get(entry.get("product_id"))
                if not product:
                    continue
                quantity = int(entry.get("quantity", 0))
                line_total_cents = (product.price_cents or 0) * quantity
                items.append(
                    {
                        "product": product,
                        "quantity": quantity,
                        "price_cents": product.price_cents,
                        "line_total_cents": line_total_cents,
                        "line_total": Decimal(line_total_cents) / Decimal(100),
                    }
                )
        return items

    def get_cart_total(self) -> Decimal:
        return sum((item["line_total"] for item in self.get_cart_items()), Decimal("0"))

    def get_cart_count(self) -> int:
        return sum((item["quantity"] for item in self.get_cart_items()), 0)

    def merge_session_cart(self, session_cart) -> None:
        """
        Merge a guest cart (stored in session) into the user's cart.
        """
        if not self.user or not session_cart:
            return

        normalized: List[Dict] = []
        if isinstance(session_cart, dict):
            for pid, qty in session_cart.items():
                normalized.append({"product_id": pid, "quantity": qty})
        elif isinstance(session_cart, list):
            normalized = session_cart
        else:
            return

        for entry in normalized:
            if not isinstance(entry, dict):
                continue
            product_id = entry.get("product_id")
            quantity = entry.get("quantity", 0)
            if product_id is None:
                continue
            self.add_item(int(product_id), int(quantity))
        session.pop(self.session_key, None)
