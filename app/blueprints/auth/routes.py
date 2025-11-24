from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.blueprints.auth.constants import USERS
from app.blueprints.auth.forms import LoginForm
from app.services.cart import CartService
from app.models import User
from app import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session and request.method == "GET":
        return redirect(url_for("account.dashboard"))

    error = None
    form = LoginForm.from_request(request)

    if request.method == "POST":
        if not form.is_valid():
            error = "Invalid username or password"
        elif form.username in USERS and USERS[form.username]["password"] == form.password:
            session["username"] = form.username

            user = User.by_username(form.username)
            meta = USERS[form.username]
            if not user:
                user = User(username=form.username, email=meta.get("email", ""), role=meta.get("role", "customer"), password_hash="seeded")
                db.session.add(user)
                db.session.commit()
            else:
                updated = False
                if meta.get("email") and user.email != meta["email"]:
                    user.email = meta["email"]
                    updated = True
                if meta.get("role") and user.role != meta["role"]:
                    user.role = meta["role"]
                    updated = True
                if updated:
                    db.session.commit()

            CartService(username=form.username).merge_session_cart(session.get("cart", []))

            if user.is_admin:
                return redirect(url_for("admin_panel.dashboard"))
            return redirect(url_for("account.dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("auth.login"))
