from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any

import bcrypt
import jwt
from flask import current_app, g, jsonify, request


def _jwt_secret() -> str:
    return os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "hirevision-jwt-secret"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user: dict[str, Any], remember_me: bool = False) -> str:
    expires = _utc_now() + (timedelta(days=30) if remember_me else timedelta(hours=12))
    payload = {
        "sub": user["id"],
        "email": user.get("email"),
        "name": user.get("name") or user.get("full_name"),
        "remember_me": bool(remember_me),
        "exp": expires,
        "iat": _utc_now(),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def create_reset_token(user_id: str) -> tuple[str, str, datetime]:
    token = hashlib.sha256(f"{user_id}:{os.urandom(32).hex()}:{_utc_now().isoformat()}".encode("utf-8")).hexdigest()
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = _utc_now() + timedelta(minutes=30)
    return token, token_hash, expires_at


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_bearer_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return None


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, _jwt_secret(), algorithms=["HS256"])


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = get_bearer_token()
        if not token:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        try:
            g.auth_payload = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "error": "Session expired. Please sign in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "error": "Invalid authentication token"}), 401

        return fn(*args, **kwargs)

    return wrapper


def auth_identity() -> str | None:
    payload = getattr(g, "auth_payload", None) or {}
    return payload.get("sub")
