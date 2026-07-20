"""SQLite persistence layer for HireVision.

This module adds durable storage for the existing interview flow and the new
placement-preparation modules without introducing a heavy ORM.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

DB_PATH = Path(__file__).resolve().parent / "hirevision.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL DEFAULT 'student',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                filename TEXT,
                raw_text TEXT,
                skills_json TEXT,
                projects_json TEXT,
                education_json TEXT,
                certifications_json TEXT,
                ats_score REAL,
                missing_keywords_json TEXT,
                suggestions_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS interviews (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                interview_type TEXT NOT NULL,
                domain TEXT,
                company TEXT,
                questions_json TEXT,
                responses_json TEXT,
                scores_json TEXT,
                transcript_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS coding_tests (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                language TEXT NOT NULL,
                problem_id TEXT,
                code TEXT,
                hidden_tests_json TEXT,
                score REAL,
                complexity_analysis TEXT,
                ai_review TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS aptitude_tests (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                questions_json TEXT,
                score REAL,
                correct_count INTEGER,
                total_count INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS logical_tests (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                questions_json TEXT,
                score REAL,
                correct_count INTEGER,
                total_count INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS verbal_tests (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                questions_json TEXT,
                score REAL,
                correct_count INTEGER,
                total_count INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS technical_tests (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                questions_json TEXT,
                score REAL,
                correct_count INTEGER,
                total_count INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS gd_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                topic TEXT NOT NULL,
                transcript TEXT,
                scores_json TEXT,
                feedback_json TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                report_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS analytics (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                period TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            );
            """
        )


def seed_demo_data() -> None:
    with get_connection() as connection:
        cursor = connection.execute("SELECT COUNT(*) AS count FROM users")
        if cursor.fetchone()["count"]:
            return

        now = _now()
        connection.execute(
            """
            INSERT INTO users (id, name, email, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("demo_student", "Demo Student", "demo@example.com", "student", now, now),
        )
        connection.execute(
            """
            INSERT INTO resumes (
                user_id, filename, raw_text, skills_json, projects_json, education_json,
                certifications_json, ats_score, missing_keywords_json, suggestions_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "demo_student",
                "demo_resume.txt",
                "Python, Java, SQL, React, Flask, ML projects, B.Tech in Computer Science",
                json.dumps(["Python", "Java", "SQL", "React", "Flask", "Machine Learning"]),
                json.dumps(["Placement portal", "Resume analyzer", "Interview simulator"]),
                json.dumps(["B.Tech CSE - 2026"]),
                json.dumps(["N/A"]),
                82,
                json.dumps(["Data Structures", "System Design", "Docker"]),
                json.dumps(["Add measurable impact in project descriptions", "Highlight internship outcomes"]),
                now,
            ),
        )
        connection.execute(
            """
            INSERT INTO interviews (
                id, user_id, interview_type, domain, company, questions_json, responses_json,
                scores_json, transcript_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "demo_hr_interview",
                "demo_student",
                "hr",
                "software-engineering",
                "TCS",
                json.dumps(["Tell me about yourself", "Why HireVision?", "Describe a challenge you solved"]),
                json.dumps([]),
                json.dumps({"overall": 76, "communication": 80, "technical": 71}),
                json.dumps([]),
                now,
                now,
            ),
        )
        connection.execute(
            """
            INSERT INTO aptitude_tests (
                id, user_id, topic, difficulty, questions_json, score, correct_count, total_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "demo_aptitude_1",
                "demo_student",
                "Percentage",
                "medium",
                json.dumps([]),
                68,
                17,
                25,
                now,
            ),
        )
        connection.execute(
            """
            INSERT INTO coding_tests (
                id, user_id, language, problem_id, code, hidden_tests_json, score,
                complexity_analysis, ai_review, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "demo_code_1",
                "demo_student",
                "Python",
                "two_sum",
                "def two_sum(nums, target): return []",
                json.dumps([{"input": [2, 7, 11, 15], "output": [0, 1]}]),
                54,
                "O(n) for the optimal hashmap solution",
                "Add edge-case handling and return indices instead of values.",
                now,
            ),
        )
        connection.execute(
            """
            INSERT INTO gd_sessions (id, user_id, topic, transcript, scores_json, feedback_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "demo_gd_1",
                "demo_student",
                "AI in education",
                "Discussed practical learning outcomes and ethical concerns.",
                json.dumps({"communication": 78, "confidence": 74, "fluency": 76}),
                json.dumps(["Support points with examples", "Speak with tighter structure"]),
                now,
            ),
        )
        connection.commit()


def upsert_user(user_id: str, name: str, email: str | None = None, role: str = "student", is_admin: bool = False) -> None:
    timestamp = _now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (id, name, email, role, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                email=COALESCE(excluded.email, users.email),
                role=excluded.role,
                is_admin=excluded.is_admin,
                updated_at=excluded.updated_at
            """,
            (user_id, name, email, role, int(is_admin), timestamp, timestamp),
        )
        connection.commit()


def save_record(table: str, values: dict[str, Any]) -> None:
    columns = ", ".join(values.keys())
    placeholders = ", ".join("?" for _ in values)
    with get_connection() as connection:
        connection.execute(
            f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})",
            tuple(values.values()),
        )
        connection.commit()


def fetch_one(query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    with get_connection() as connection:
        cursor = connection.execute(query, tuple(params))
        row = cursor.fetchone()
        return dict(row) if row else None


def fetch_all(query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    with get_connection() as connection:
        cursor = connection.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]


def latest_resume(user_id: str) -> dict[str, Any] | None:
    return fetch_one(
        "SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
        (user_id,),
    )


def latest_by_table(table: str, user_id: str) -> dict[str, Any] | None:
    return fetch_one(
        f"SELECT * FROM {table} WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,),
    )


def list_recent_activity(user_id: str, limit: int = 6) -> list[dict[str, Any]]:
    activities = []
    table_titles = {
        "interviews": ("interview_type", "Interview"),
        "coding_tests": ("language", "Coding"),
        "aptitude_tests": ("topic", "Aptitude"),
        "logical_tests": ("topic", "Logical"),
        "technical_tests": ("topic", "Technical"),
        "gd_sessions": ("topic", "GD"),
        "reports": ("report_type", "Report"),
    }

    for table, (title_column, label) in table_titles.items():
        try:
            records = fetch_all(
                f"SELECT created_at, {title_column} AS title FROM {table} WHERE user_id = ? ORDER BY created_at DESC LIMIT 2",
                (user_id,),
            )
        except sqlite3.OperationalError:
            records = []
        for record in records:
            activities.append({
                "type": label,
                "title": record["title"],
                "timestamp": record["created_at"],
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

    resume_score = float(resume["ats_score"]) if resume and resume.get("ats_score") is not None else 72.0
    aptitude_score = float(aptitude["score"]) if aptitude and aptitude.get("score") is not None else 65.0
    coding_score = float(coding["score"]) if coding and coding.get("score") is not None else 61.0

    interview_score = 70.0
    if interview and interview.get("scores_json"):
        try:
            interview_score = float(json.loads(interview["scores_json"]).get("overall", 70))
        except Exception:
            interview_score = 70.0

    gd_score = 68.0
    if gd and gd.get("scores_json"):
        try:
            gd_score = float(json.loads(gd["scores_json"]).get("communication", 68))
        except Exception:
            gd_score = 68.0

    technical_score = float(technical["score"]) if technical and technical.get("score") is not None else 69.0
    logical_score = float(logical["score"]) if logical and logical.get("score") is not None else 64.0
    verbal_score = float(verbal["score"]) if verbal and verbal.get("score") is not None else 66.0

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