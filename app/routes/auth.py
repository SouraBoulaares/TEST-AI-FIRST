from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "validation_error", "message": "email and password are required"}), 422

    try:
        user = User.create(email=email, password=password)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": "validation_error", "message": str(exc)}), 422
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "conflict", "message": "email already registered"}), 409

    token = user.generate_token()

    return (
        jsonify(
            {
                "id": user.id,
                "email": user.email,
                "token": token,
            }
        ),
        201,
        {"Location": f"/api/v1/users/{user.id}"},
    )


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "validation_error", "message": "email and password are required"}), 422

    user = User.query.filter_by(email=User.normalize_email(email)).first()
    if not user or not user.is_active or not user.check_password(password):
        return jsonify({"error": "invalid_credentials", "message": "invalid email or password"}), 401

    token = user.generate_token()

    return jsonify({"token": token, "user": {"id": user.id, "email": user.email}}), 200
