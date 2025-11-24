from app.blueprints.shop import shop_bp
from app.blueprints.cart import cart_bp
from app.blueprints.checkout import checkout_bp
from app.blueprints.auth import auth_bp
from app.blueprints.account import account_bp
from app.blueprints.admin import admin_bp

__all__ = [
    "shop_bp",
    "cart_bp",
    "checkout_bp",
    "auth_bp",
    "account_bp",
    "admin_bp",
]
