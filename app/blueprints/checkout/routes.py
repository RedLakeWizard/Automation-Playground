from flask import Blueprint, flash, redirect, render_template, url_for

from app.blueprints.checkout.forms import CheckoutPlaceholderForm

checkout_bp = Blueprint("checkout", __name__)


@checkout_bp.route("/", methods=["GET", "POST"])
def checkout():
    form = CheckoutPlaceholderForm()
    if form.validate_on_submit():
        flash("Checkout is currently a work in progress feature!.", "success")
        return redirect(url_for("cart.view_cart"))
    return render_template("checkout/wip.html", form=form)
