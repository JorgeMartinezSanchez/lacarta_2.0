# app/auth/__init__.py  (puede quedar vacío)

# app/auth/routes.py
from flask import Blueprint, render_template

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@bp.route("/profile")
def profile():
    return render_template("profile.html")