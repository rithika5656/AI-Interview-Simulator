"""MongoDB persistence layer for HireVision."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Iterable

from pymongo import MongoClient

# Use the environment variable for production, fallback to a local URI if not set
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/hirevision")

_client = None
_db = None

def get_db():
    global _client, _db
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Use the database specified in the URI, or default to "hirevision"
        _db = _client.get_default_database("hirevision") 
    return _db

def init_db() -> None:
    # MongoDB creates collections dynamically, but we can ensure indices if needed
    db = get_db()
    db.users.create_index("id", unique=True)
    db.users.create_index("email", unique=True, sparse=True)
    db.users.create_index("reset_token_hash", sparse=True)
    db.resumes.create_index([("user_id", 1), ("created_at", -1)])
    
def seed_demo_data() -> None:
    # Intentionally empty: The user requested no demo mode and no placeholder data.
    pass

def upsert_user(
    user_id: str,
    name: str,
    email: str | None = None,
    role: str = "student",
    target_role: str | None = None,
    skills_json: str | None = None,
    achievements_json: str | None = None,
    extra_fields: dict[str, Any] | None = None,
) -> None:
    db = get_db()
    timestamp = _now()
    
    update_data = {
        "updated_at": timestamp
    }
    
    # Only set these on insert, or update if provided
    set_on_insert = {
        "id": user_id,
        "created_at": timestamp
    }
    
    if name:
        update_data["name"] = name
    if email:
        update_data["email"] = email
    if role:
        update_data["role"] = role
    if target_role:
        update_data["target_role"] = target_role
    if skills_json:
        update_data["skills_json"] = skills_json
    if achievements_json:
        update_data["achievements_json"] = achievements_json

    if extra_fields:
        for key, value in extra_fields.items():
            if value is not None:
                update_data[key] = value
        
    db.users.update_one(
        {"id": user_id},
        {
            "$set": update_data,
            "$setOnInsert": set_on_insert
        },
        upsert=True
    )


def find_user_by_email(email: str) -> dict[str, Any] | None:
    if not email:
        return None
    return fetch_one_mongo("users", {"email": email.strip().lower()})


def find_user_by_id(user_id: str) -> dict[str, Any] | None:
    if not user_id:
        return None
    return fetch_one_mongo("users", {"id": user_id})


def update_user(user_id: str, values: dict[str, Any]) -> None:
    db = get_db()
    values = {key: value for key, value in values.items() if value is not None}
    if not values:
        return
    values.setdefault("updated_at", _now())
    db.users.update_one({"id": user_id}, {"$set": values}, upsert=False)

def save_record(table: str, values: dict[str, Any]) -> None:
    db = get_db()
    if "created_at" not in values:
        values["created_at"] = _now()
        
    if "id" in values:
        db[table].update_one({"id": values["id"]}, {"$set": values}, upsert=True)
    else:
        # Generate an id if it doesn't exist, mainly for resumes
        db[table].insert_one(values)

def fetch_one_mongo(collection: str, query: dict) -> dict[str, Any] | None:
    db = get_db()
    doc = db[collection].find_one(query)
    if doc:
        doc.pop("_id", None)
    return doc

def fetch_all_mongo(collection: str, query: dict, sort_by: list = None) -> list[dict[str, Any]]:
    db = get_db()
    cursor = db[collection].find(query)
    if sort_by:
        cursor = cursor.sort(sort_by)
    docs = list(cursor)
    for doc in docs:
        doc.pop("_id", None)
    return docs

def latest_resume(user_id: str) -> dict[str, Any] | None:
    db = get_db()
    doc = db.resumes.find_one({"user_id": user_id}, sort=[("created_at", -1)])
    if doc:
        doc.pop("_id", None)
    return doc

def latest_by_table(table: str, user_id: str) -> dict[str, Any] | None:
    db = get_db()
    doc = db[table].find_one({"user_id": user_id}, sort=[("created_at", -1)])
    if doc:
        doc.pop("_id", None)
    return doc

def list_recent_activity(user_id: str, limit: int = 6) -> list[dict[str, Any]]:
    activities = []
    table_titles = {
        "interviews": ("interview_type", "Interview"),
        "coding_tests": ("language", "Coding"),
        "aptitude_tests": ("topic", "Aptitude"),
        "logical_tests": ("topic", "Logical"),
        "verbal_tests": ("topic", "Verbal"),
        "technical_tests": ("topic", "Technical"),
        "gd_sessions": ("topic", "GD"),
        "reports": ("report_type", "Report"),
    }

    db = get_db()
    for table, (title_column, label) in table_titles.items():
        records = db[table].find({"user_id": user_id}).sort("created_at", -1).limit(2)
        for record in records:
            activities.append({
                "type": label,
                "title": record.get(title_column, "Unknown"),
                "timestamp": record.get("created_at")
            })

    activities.sort(key=lambda item: item["timestamp"], reverse=True)
    return activities[:limit]

def get_dashboard_metrics(user_id: str) -> dict[str, Any]:
    resume = latest_resume(user_id)
    interview = latest_by_table("interviews", user_id)
    aptitude = latest_by_table("aptitude_tests", user_id)
    coding = latest_by_table("coding_tests", user_id)
    gd = latest_by_table("gd_sessions", user_id)
    technical = latest_by_table("technical_tests", user_id)
    logical = latest_by_table("logical_tests", user_id)
    verbal = latest_by_table("verbal_tests", user_id)

    resume_score = float(resume.get("ats_score", 0.0)) if resume and resume.get("ats_score") is not None else 0.0
    aptitude_score = float(aptitude.get("score", 0.0)) if aptitude and aptitude.get("score") is not None else 0.0
    coding_score = float(coding.get("score", 0.0)) if coding and coding.get("score") is not None else 0.0

    interview_score = 0.0
    if interview and interview.get("scores_json"):
        try:
            interview_score = float(json.loads(interview["scores_json"]).get("overall", 0.0))
        except Exception:
            pass

    gd_score = 0.0
    if gd and gd.get("scores_json"):
        try:
            gd_score = float(json.loads(gd["scores_json"]).get("communication", 0.0))
        except Exception:
            pass

    technical_score = float(technical.get("score", 0.0)) if technical and technical.get("score") is not None else 0.0
    logical_score = float(logical.get("score", 0.0)) if logical and logical.get("score") is not None else 0.0
    verbal_score = float(verbal.get("score", 0.0)) if verbal and verbal.get("score") is not None else 0.0

    placement_readiness = round(
        (resume_score * 0.15)
        + (aptitude_score * 0.12)
        + (coding_score * 0.15)
        + (interview_score * 0.18)
        + (gd_score * 0.08)
        + (technical_score * 0.12)
        + (logical_score * 0.08)
        + (verbal_score * 0.12),
        1,
    )

    return {
        "placement_readiness_score": placement_readiness,
        "resume_score": round(resume_score, 1),
        "aptitude_progress": round(aptitude_score, 1),
        "coding_progress": round(coding_score, 1),
        "interview_score": round(interview_score, 1),
        "gd_score": round(gd_score, 1),
        "technical_score": round(technical_score, 1),
        "logical_score": round(logical_score, 1),
        "verbal_score": round(verbal_score, 1),
    }

def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
