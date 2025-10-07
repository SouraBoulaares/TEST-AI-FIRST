from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import Blueprint, jsonify, request

from app.models.user import User


users_bp = Blueprint("users", __name__)


def requires_auth(view_func: Callable):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            user = User.verify_token(token)
            if user and user.is_active:
                return view_func(current_user=user, *args, **kwargs)
        return jsonify({"error": "unauthorized", "message": "invalid or missing token"}), 401

    return wrapper


@users_bp.get("/")
@requires_auth
def list_users(current_user: User):
    # Simple listing; in real apps add pagination and authorization
    users = User.query.order_by(User.id.asc()).all()
    return jsonify(
        [
            {
                "id": u.id,
                "email": u.email,
                "is_active": u.is_active,
            }
            for u in users
        ]
    )


@users_bp.get("/<int:user_id>")
@requires_auth
def get_user(user_id: int, current_user: User):
    user = User.query.get_or_404(user_id)
    return jsonify({"id": user.id, "email": user.email, "is_active": user.is_active})
