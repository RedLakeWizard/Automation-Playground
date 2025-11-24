from flask import Blueprint, render_template, request, abort, redirect, url_for

from app.blueprints.cart.forms import CartAddForm
from app.blueprints.shop.forms import ProductSearchForm
from app.models import Category, Product

shop_bp = Blueprint("shop", __name__)

PER_PAGE = 12


@shop_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "newest")
    category_slug = request.args.get("category")
    search_form = ProductSearchForm.from_request(request)

    query = Product.active()

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter_by(category_id=category.id)

    if sort == "price_asc":
        query = query.order_by(Product.price_cents.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price_cents.desc())
    elif sort == "name":
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    if search_form.query:
        query = query.filter(
            Product.name.ilike(f"%{search_form.query}%")
            | Product.description.ilike(f"%{search_form.query}%")
        )

    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    products = pagination.items

    return render_template(
        "shop/index.html",
        products=products,
        pagination=pagination,
        search_form=search_form,
        sort=sort,
        selected_category=category_slug,
        categories=Category.query.order_by(Category.name.asc()).all(),
        add_to_cart_form=CartAddForm(),
    )


@shop_bp.route("/product/<path:slug_or_id>")
def product(slug_or_id: str):
    product = Product.query.filter_by(slug=slug_or_id).first()
    if not product and slug_or_id.isdigit():
        product = Product.query.get(int(slug_or_id))
    if not product:
        abort(404)

    related = []
    if product.category_id:
        related = (
            Product.active()
            .filter(Product.category_id == product.category_id, Product.id != product.id)
            .order_by(Product.created_at.desc())
            .limit(4)
            .all()
        )

    return render_template(
        "shop/product.html",
        product=product,
        related_products=related,
        add_to_cart_form=CartAddForm(),
    )


@shop_bp.route("/category/<slug>")
def category(slug: str):
    args = request.args.to_dict(flat=True)
    args["category"] = slug
    return redirect(url_for("shop.index", **args))


@shop_bp.route("/search")
def search():
    return index()
