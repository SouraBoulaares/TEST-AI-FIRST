from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from email_validator import EmailNotValidError, validate_email
from flask import current_app
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def set_password(self, password: str) -> None:
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def normalize_email(raw_email: str) -> str:
        try:
            valid = validate_email(raw_email, check_deliverability=False)
            return valid.normalized
        except EmailNotValidError as exc:
            raise ValueError(f"Invalid email: {exc}") from exc

    def generate_token(self, expires_in: Optional[int] = None) -> str:
        secret_key = current_app.config["SECRET_KEY"]
        algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
        ttl = expires_in or int(current_app.config.get("TOKEN_EXPIRES_IN", 3600))
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": str(self.id),
            "email": self.email,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=ttl)).timestamp()),
        }
        return jwt.encode(payload, secret_key, algorithm=algorithm)

    @staticmethod
    def verify_token(token: str) -> Optional["User"]:
        if not token:
            return None
        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=[current_app.config.get("JWT_ALGORITHM", "HS256")],
            )
            user_id = int(payload.get("sub"))
        except Exception:
            return None
        return db.session.get(User, user_id)

    @classmethod
    def create(cls, email: str, password: str) -> "User":
        normalized_email = cls.normalize_email(email)
        user = cls(email=normalized_email)
        user.set_password(password)
        db.session.add(user)
        return user
