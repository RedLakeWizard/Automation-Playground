from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.blueprints.account.forms import ProfileForm
from app.models import Order, User
from app import db

account_bp = Blueprint("account", __name__)


def _require_login():
    if "username" not in session:
        return redirect(url_for("auth.login"))
    return None


@account_bp.route("/dashboard")
def dashboard():
    maybe_redirect = _require_login()
    if maybe_redirect:
        return maybe_redirect
    username = session.get("username")
    user = User.by_username(username) if username else None
    if not user and username:
        user = User(username=username, email=f"{username}@example.com", password_hash="guest")
        db.session.add(user)
        db.session.commit()
    return render_template("dashboard.html", username=username, user=user)


@account_bp.route("/orders")
def orders():
    maybe_redirect = _require_login()
    if maybe_redirect:
        return maybe_redirect

    orders = Order.recent(limit=20).all()
    return render_template("account/orders.html", orders=orders)


@account_bp.route("/profile", methods=["GET", "POST"])
def profile():
    maybe_redirect = _require_login()
    if maybe_redirect:
        return maybe_redirect

    form = ProfileForm.from_request(request)
    username = session.get("username")

    user = User.by_username(username) if username else None
    if not user and username:
        user = User(username=username, email=f"{username}@example.com", password_hash="guest")
        db.session.add(user)
        db.session.commit()

    if request.method == "POST":
        if form.is_valid():
            if user:
                user.username = form.display_name or user.username
                if form.email:
                    user.email = form.email
                db.session.commit()
            session["username"] = form.display_name or username
            flash("Profile updated.", "success")
            return redirect(url_for("account.profile"))
        flash("Please fill out the required fields.", "danger")

    if request.method == "GET":
        form.display_name = user.username if user else (username or "")
        form.email = user.email if user else ""

    return render_template("account/profile.html", form=form, username=username, user=user)
