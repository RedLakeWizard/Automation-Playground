from datetime import datetime
from decimal import Decimal

from flask import Flask, redirect, url_for, request, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
admin = Admin(name="Admin Console", url="/admin/console")


def create_app() -> Flask:
    """
    Application factory so routes, extensions, and models initialize in a
    predictable order.
    """
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object("app.config.Config")

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    admin.init_app(app)

    from app.models import (
        CartItem,
        Category,
        Order,
        OrderItem,
        Product,
        Review,
        User,
    )

    admin._views = []
    admin._menu = []
    admin._menu_links = []
    admin.add_view(ModelView(Product, db.session))
    admin.add_view(ModelView(Category, db.session))
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Order, db.session))
    admin.add_view(ModelView(OrderItem, db.session))
    admin.add_view(ModelView(CartItem, db.session))
    admin.add_view(ModelView(Review, db.session))

    def format_currency(value):
        if value is None:
            return "0.00 GLD"
        if isinstance(value, (int, float, str)):
            try:
                value = Decimal(value)
            except Exception:
                return "0.00 GLD"
        if isinstance(value, Decimal):
            return f"{value.quantize(Decimal('0.01'))} GLD"
        return f"{value} GLD"

    def format_date(value, fmt="%Y-%m-%d"):
        if not value:
            return ""
        if isinstance(value, datetime):
            return value.strftime(fmt)
        return str(value)

    app.jinja_env.filters["format_currency"] = format_currency
    app.jinja_env.filters["format_date"] = format_date

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.utcnow().year}

    from app.blueprints.auth import auth_bp
    from app.blueprints.shop import shop_bp
    from app.blueprints.cart import cart_bp
    from app.blueprints.checkout import checkout_bp
    from app.blueprints.account import account_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(shop_bp, url_prefix="/shop")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(checkout_bp, url_prefix="/checkout")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def index():
        return redirect(url_for("shop.index"))

    @app.before_request
    def require_login():
        exempt = {
            "auth.login",
            "auth.register",
            "static",
        }
        endpoint = request.endpoint or ""
        if endpoint.startswith("auth.") or endpoint in exempt:
            return None
        if endpoint.startswith("static"):
            return None
        if "username" not in session:
            return redirect(url_for("auth.login"))

    return app


app = create_app()

__all__ = ["app", "create_app", "db", "admin", "bcrypt", "mail"]
