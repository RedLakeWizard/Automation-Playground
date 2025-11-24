from decimal import Decimal

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.blueprints.cart.forms import CartAddForm, CartUpdateForm
from app.models import Product
from app.services.cart import CartService

cart_bp = Blueprint("cart", __name__)


def _current_username() -> str | None:
    return session.get("username")


def _cart_service() -> CartService:
    return CartService(username=_current_username())


@cart_bp.app_context_processor
def inject_cart_count():
    service = _cart_service()
    return {"cart_count": service.get_cart_count()}


@cart_bp.route("/")
def view_cart():
    service = _cart_service()
    items = service.get_cart_items()
    subtotal = service.get_cart_total()
    tax = subtotal * Decimal("0.10")
    shipping = Decimal("5.00") if subtotal > 0 else Decimal("0.00")
    total = subtotal + tax + shipping

    return render_template(
        "cart/index.html",
        items=items,
        subtotal=subtotal,
        tax=tax,
        shipping=shipping,
        total=total,
        add_to_cart_form=CartAddForm(),
        update_form=CartUpdateForm(),
    )


@cart_bp.post("/add/<int:product_id>")
def add_item(product_id: int):
    form = CartAddForm()
    quantity = (
        request.json.get("quantity", 1)
        if request.is_json and isinstance(request.json, dict)
        else form.quantity.data
    )

    if not form.validate_on_submit() and not request.is_json:
        flash("Invalid quantity.", "danger")
        return redirect(request.referrer or url_for("shop.product", slug_or_id=product_id))

    service = _cart_service()
    success, message = service.add_item(product_id, quantity)

    if request.is_json:
        status = 200 if success else 400
        return (
            jsonify(
                {
                    "success": success,
                    "message": message,
                    "cart_count": service.get_cart_count(),
                }
            ),
            status,
        )

    flash(message, "success" if success else "danger")
    next_url = request.referrer or url_for("shop.product", slug_or_id=product_id)
    return redirect(next_url)


@cart_bp.post("/update/<int:product_id>")
def update_item(product_id: int):
    form = CartUpdateForm()
    quantity = (
        request.json.get("quantity", 0)
        if request.is_json and isinstance(request.json, dict)
        else form.quantity.data
    )

    if not form.validate_on_submit() and not request.is_json:
        flash("Invalid quantity.", "danger")
        return redirect(request.referrer or url_for("cart.view_cart"))

    service = _cart_service()
    success, message = service.update_quantity(product_id, quantity)

    if request.is_json:
        status = 200 if success else 400
        return (
            jsonify(
                {
                    "success": success,
                    "message": message,
                    "cart_count": service.get_cart_count(),
                }
            ),
            status,
        )

    flash(message, "success" if success else "danger")
    return redirect(request.referrer or url_for("cart.view_cart"))


@cart_bp.post("/remove/<int:product_id>")
def remove_item(product_id: int):
    form = CartUpdateForm()
    service = _cart_service()
    if not form.validate_on_submit() and not request.is_json:
        flash("Invalid request.", "danger")
        return redirect(request.referrer or url_for("cart.view_cart"))

    success, message = service.remove_item(product_id)

    if request.is_json:
        status = 200 if success else 400
        return (
            jsonify(
                {
                    "success": success,
                    "message": message,
                    "cart_count": service.get_cart_count(),
                }
            ),
            status,
        )

    flash(message, "success" if success else "danger")
    return redirect(request.referrer or url_for("cart.view_cart"))


@cart_bp.post("/clear")
def clear_cart():
    service = _cart_service()
    service.clear_cart()
    if request.is_json:
        return jsonify({"success": True, "cart_count": 0})
    flash("Cart cleared.", "info")
    return redirect(url_for("cart.view_cart"))
