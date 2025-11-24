from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app import db
from app.blueprints.admin.forms import AdminProductForm
from app.blueprints.admin.utils import save_product_image
from app.models import Order, Product

admin_bp = Blueprint("admin_panel", __name__)


def _require_admin():
    if session.get("username") != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("auth.login"))
    return None


@admin_bp.route("/dashboard")
def dashboard():
    maybe_redirect = _require_admin()
    if maybe_redirect:
        return maybe_redirect

    product_count = Product.query.count()
    order_count = Order.query.count()
    return render_template(
        "admin/dashboard.html",
        product_count=product_count,
        order_count=order_count,
    )


@admin_bp.route("/products", methods=["GET", "POST"])
def products():
    maybe_redirect = _require_admin()
    if maybe_redirect:
        return maybe_redirect

    form = AdminProductForm()
    products = Product.query.order_by(Product.created_at.desc()).all()

    if form.validate_on_submit():
        image_url = ""
        if form.image.data:
            image_url = save_product_image(form.image.data)

        product = Product(
            name=form.name.data,
            price_cents=form.price_cents,
            compare_price_cents=form.compare_price_cents or None,
            sku=form.sku.data,
            quantity=form.quantity.data or 0,
            is_active=bool(form.is_active.data),
            image_url=image_url,
        )
        db.session.add(product)
        db.session.commit()
        flash("Product created.", "success")
        return redirect(url_for("admin_panel.products"))
    elif request.method == "POST":
        flash("Please fix the errors in the form.", "danger")

    return render_template("admin/products.html", products=products, form=form)


@admin_bp.route("/orders")
def orders():
    maybe_redirect = _require_admin()
    if maybe_redirect:
        return maybe_redirect

    orders = Order.recent(limit=50).all()
    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id: int):
    maybe_redirect = _require_admin()
    if maybe_redirect:
        return maybe_redirect

    product = Product.query.get_or_404(product_id)
    form = AdminProductForm(obj=product)

    if form.validate_on_submit():
        product.name = form.name.data
        product.price_cents = form.price_cents
        product.compare_price_cents = form.compare_price_cents or None
        product.sku = form.sku.data
        product.quantity = form.quantity.data or 0
        product.is_active = bool(form.is_active.data)

        if form.image.data:
            product.image_url = save_product_image(form.image.data)

        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin_panel.products"))
    elif request.method == "POST":
        flash("Please fix the errors in the form.", "danger")

    return render_template("admin/edit_product.html", product=product, form=form)
