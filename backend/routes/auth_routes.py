"""Authentication routes for HireVision."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from flask import Blueprint, current_app, jsonify, request

from database.mongo_store import find_user_by_email, find_user_by_id, get_db, update_user, upsert_user
from utils.auth_utils import (
    auth_identity,
    create_access_token,
    create_reset_token,
    hash_password,
    hash_reset_token,
    require_auth,
    verify_password,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _normalize_email(email: str | None) -> str:
    return (email or "").strip().lower()


def _serialize_user(user: dict[str, Any] | None) -> dict[str, Any]:
    if not user:
        return {}
    return {
        "id": user.get("id"),
        "name": user.get("name") or user.get("full_name") or "Student",
        "full_name": user.get("full_name") or user.get("name") or "Student",
        "email": user.get("email") or "",
        "college": user.get("college") or "",
        "department": user.get("department") or "",
        "year": user.get("year") or "",
        "phone": user.get("phone") or "",
        "role": user.get("role") or "student",
        "target_role": user.get("target_role") or "Software Engineer",
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
        "last_login_at": user.get("last_login_at"),
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        payload = request.get_json(silent=True) or {}
        full_name = (payload.get("full_name") or payload.get("name") or "").strip()
        email = _normalize_email(payload.get("email"))
        password = payload.get("password") or ""
        college = (payload.get("college") or "").strip()
        department = (payload.get("department") or "").strip()
        year = (payload.get("year") or "").strip()
        phone = (payload.get("phone") or "").strip()
        target_role = (payload.get("target_role") or payload.get("targetRole") or "Software Engineer").strip()
        remember_me = bool(payload.get("remember_me", True))

        if not full_name or not email or not password:
            return jsonify({"success": False, "error": "Full name, email, and password are required"}), 400
        if not college or not department or not year or not phone:
            return jsonify({"success": False, "error": "College, department, year, and phone are required"}), 400

        existing = find_user_by_email(email)
        if existing:
            return jsonify({"success": False, "error": "An account with this email already exists"}), 409

        user_id = f"user_{uuid.uuid4().hex[:12]}"
        password_hash = hash_password(password)
        timestamp = _now()

        upsert_user(
            user_id=user_id,
            name=full_name,
            email=email,
            role="student",
            target_role=target_role,
            extra_fields={
                "full_name": full_name,
                "password_hash": password_hash,
                "college": college,
                "department": department,
                "year": year,
                "phone": phone,
                "target_role": target_role,
                "created_at": timestamp,
                "updated_at": timestamp,
                "last_login_at": timestamp,
                "role": "student",
            },
        )

        user = find_user_by_id(user_id)
        token = create_access_token(user, remember_me=remember_me)
        return jsonify({"success": True, "token": token, "user": _serialize_user(user), "remember_me": remember_me}), 201
    except Exception as exc:
        current_app.logger.exception(exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        payload = request.get_json(silent=True) or {}
        email = _normalize_email(payload.get("email"))
        password = payload.get("password") or ""
        remember_me = bool(payload.get("remember_me", False))

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400

        user = find_user_by_email(email)
        if not user or not user.get("password_hash"):
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        if not verify_password(password, user["password_hash"]):
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        timestamp = _now()
        update_user(user["id"], {"last_login_at": timestamp, "updated_at": timestamp})
        user = find_user_by_id(user["id"])
        token = create_access_token(user, remember_me=remember_me)
        return jsonify({"success": True, "token": token, "user": _serialize_user(user), "remember_me": remember_me})
    except Exception as exc:
        current_app.logger.exception(exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    try:
        user_id = auth_identity()
        user = find_user_by_id(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        return jsonify({"success": True, "user": _serialize_user(user)})
    except Exception as exc:
        current_app.logger.exception(exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    return jsonify({"success": True, "message": "Logged out successfully"})


@auth_bp.route("/profile", methods=["PUT"])
@require_auth
def update_profile():
    try:
        user_id = auth_identity()
        payload = request.get_json(silent=True) or {}
        updates = {
            "name": (payload.get("full_name") or payload.get("name") or "").strip() or None,
            "full_name": (payload.get("full_name") or payload.get("name") or "").strip() or None,
            "email": _normalize_email(payload.get("email")) or None,
            "college": (payload.get("college") or "").strip() or None,
            "department": (payload.get("department") or "").strip() or None,
            "year": (payload.get("year") or "").strip() or None,
            "phone": (payload.get("phone") or "").strip() or None,
            "target_role": (payload.get("target_role") or payload.get("targetRole") or "").strip() or None,
            "updated_at": _now(),
        }

        password = payload.get("password")
        if password:
            updates["password_hash"] = hash_password(password)

        update_user(user_id, updates)
        user = find_user_by_id(user_id)
        return jsonify({"success": True, "user": _serialize_user(user)})
    except Exception as exc:
        current_app.logger.exception(exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    try:
        payload = request.get_json(silent=True) or {}
        email = _normalize_email(payload.get("email"))
        user = find_user_by_email(email)
        if not user:
            return jsonify({"success": True, "message": "If the account exists, a reset token has been generated."})

        reset_token, reset_token_hash, reset_token_expires = create_reset_token(user["id"])
        update_user(user["id"], {
            "reset_token_hash": reset_token_hash,
            "reset_token_expires": reset_token_expires.isoformat().replace("+00:00", "Z"),
            "updated_at": _now(),
        })

        return jsonify({
            "success": True,
            "message": "Reset token generated. Use it to update your password.",
            "reset_token": reset_token,
        })
    except Exception as exc:
        current_app.logger.exception(exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        payload = request.get_json(silent=True) or {}
        email = _normalize_email(payload.get("email"))
        reset_token = payload.get("reset_token") or ""
        password = payload.get("password") or ""

        if not email or not reset_token or not password:
            return jsonify({"success": False, "error": "Email, reset token, and new password are required"}), 400

        user = find_user_by_email(email)
        if not user:
            return jsonify({"success": False, "error": "Invalid reset request"}), 400

        token_hash = hash_reset_token(reset_token)
        stored_hash = user.get("reset_token_hash")
        expires_at = user.get("reset_token_expires")

        if not stored_hash or stored_hash != token_hash:
            return jsonify({"success": False, "error": "Invalid or expired reset token"}), 400
        if expires_at:
            expires_dt = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            if expires_dt <= datetime.now(tz=expires_dt.tzinfo):
                return jsonify({"success": False, "error": "Reset token expired"}), 400

        update_user(user["id"], {
            "password_hash": hash_password(password),
            "reset_token_hash": None,
            "reset_token_expires": None,
            "updated_at": _now(),
        })
        return jsonify({"success": True, "message": "Password updated successfully"})
    except Exception as exc:
        current_app.logger.exception(exc)
        return jsonify({"success": False, "error": str(exc)}), 500