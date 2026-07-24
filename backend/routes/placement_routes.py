"""Placement preparation routes for HireVision."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from services.placement_service import (
    analyze_resume_payload,
    analyze_coding_submission,
    build_analytics,
    build_career_coach,
    build_company_track,
    build_dashboard,
    build_profile,
    generate_mock_module,
    generate_technical_interview_question,
    grade_mcq_submission,
    gd_session_feedback,
)
import uuid
import json
from database.mongo_store import save_record
from datetime import datetime

placement_bp = Blueprint("placement", __name__, url_prefix="/api")


def _now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


TEST_TABLE_MAP = {
    "aptitude": "aptitude_tests",
    "logical": "logical_tests",
    "verbal": "verbal_tests",
    "technical": "technical_tests",
    "technical-mcq": "technical_tests",
}

@placement_bp.route("/modules", methods=["GET"])
def list_modules():
    return jsonify(
        {
            "modules": [
                "dashboard",
                "resume",
                "aptitude",
                "logical",
                "verbal",
                "technical-mcq",
                "coding",
                "gd",
                "hr-interview",
                "technical-interview",
                "company-wise",
                "analytics",
                "career-coach",
                "profile",
            ]
        }
    )


@placement_bp.route("/dashboard/overview", methods=["GET"])
def dashboard_overview():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    return jsonify(build_dashboard(user_id))


@placement_bp.route("/resume/analyze", methods=["POST"])
def resume_analyze():
    payload = request.get_json(silent=True) or {}
    user_id = request.form.get("user_id") or payload.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    filename = None
    resume_text = ""

    if request.files and "resume" in request.files:
        resume_file = request.files["resume"]
        filename = resume_file.filename
        resume_text = _extract_text_from_upload(resume_file)
    else:
        resume_text = payload.get("resume_text", "")
        filename = payload.get("filename")

    if not resume_text.strip():
        return jsonify({"error": "Resume text is required"}), 400

    return jsonify(analyze_resume_payload(user_id, resume_text, filename))


@placement_bp.route("/<module_key>/generate", methods=["POST"])
def generate_module(module_key: str):
    try:
        payload = request.get_json(silent=True) or {}
        topic = payload.get("topic")
        difficulty = payload.get("difficulty", "medium")
        user_id = payload.get("user_id") or request.args.get("user_id")
        return jsonify(generate_mock_module(module_key, topic, difficulty, count=20, user_id=user_id))
    except Exception as e:
        from flask import current_app

        current_app.logger.exception(e)
        return jsonify({"success": False, "error": str(e)}), 500


@placement_bp.route("/<module_key>/submit", methods=["POST"])
def submit_module(module_key: str):
    try:
        payload = request.get_json(silent=True) or {}
        questions = payload.get("questions", [])
        answers = payload.get("answers", [])
        topic = payload.get("topic", "General")
        difficulty = payload.get("difficulty", "medium")
        user_id = payload.get("user_id")
        result = grade_mcq_submission(questions, answers)

        table_name = TEST_TABLE_MAP.get(module_key)
        if table_name:
            save_record(table_name, {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "topic": topic,
                "difficulty": difficulty,
                "questions_json": json.dumps(questions),
                "score": result.get("score"),
                "correct_count": result.get("correct_count"),
                "total_count": result.get("total_count"),
                "created_at": _now(),
            })

        return jsonify({"module": module_key, **result})
    except Exception as e:
        from flask import current_app

        current_app.logger.exception(e)
        return jsonify({"success": False, "error": str(e)}), 500


@placement_bp.route("/coding/problem", methods=["GET"])
def coding_problem():
    user_id = request.args.get("user_id", "default_user")
    difficulty = request.args.get("difficulty", "easy").lower()
    from services.placement_service import get_random_coding_problem
    return jsonify(get_random_coding_problem(user_id, difficulty))


@placement_bp.route("/coding/review", methods=["POST"])
def coding_review():
    payload = request.get_json(silent=True) or {}
    result = analyze_coding_submission(
        payload.get("language", "Python"),
        payload.get("code", ""),
        payload.get("problem_statement", ""),
    )
    
    user_id = payload.get("user_id")
    save_record("coding_tests", {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "language": result.get("language"),
        "code": payload.get("code", ""),
        "hidden_tests_json": json.dumps(result.get("hidden_tests", [])),
        "score": result.get("score"),
        "complexity_analysis": result.get("complexity_analysis"),
        "ai_review": result.get("ai_review"),
        "created_at": _now(),
    })

    return jsonify(result)


@placement_bp.route("/gd/simulate", methods=["POST"])
def simulate_gd():
    payload = request.get_json(silent=True) or {}
    topic = payload.get("topic", "Emerging technologies")
    transcript = payload.get("transcript", "")
    user_id = payload.get("user_id")
    return jsonify(gd_session_feedback(topic, transcript, user_id))


@placement_bp.route("/gd/generate-topic", methods=["POST"])
def generate_gd_topic_route():
    payload = request.get_json(silent=True) or {}
    exclude_topics = payload.get("exclude_topics", [])
    from ai.hirevision_ai import generate_gd_topic
    topic = generate_gd_topic(exclude_topics)
    return jsonify({"topic": topic})


@placement_bp.route("/company-track/<company>", methods=["GET"])
def company_track(company: str):
    return jsonify(build_company_track(company))


@placement_bp.route("/analytics/summary", methods=["GET"])
def analytics_summary():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    return jsonify(build_analytics(user_id))


@placement_bp.route("/career-coach", methods=["GET"])
def career_coach():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    return jsonify(build_career_coach(user_id))


@placement_bp.route("/technical-interview/question", methods=["POST"])
def technical_interview_question():
    payload = request.get_json(silent=True) or {}
    resume_skills = payload.get("resume_skills", [])
    if not isinstance(resume_skills, list):
        resume_skills = []
    return jsonify(
        generate_technical_interview_question(
            payload.get("technology", "Python"),
            resume_skills=resume_skills,
            job_description=payload.get("job_description"),
        )
    )


@placement_bp.route("/profile/<user_id>", methods=["GET"])
def profile(user_id: str):
    return jsonify(build_profile(user_id))


@placement_bp.route("/profile/save", methods=["POST"])
def profile_save():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    name = payload.get("name", "Student")
    email = payload.get("email")
    role = payload.get("role", "student")
    target_role = payload.get("target_role", "Software Engineer")
    skills = payload.get("skills", [])
    achievements = payload.get("achievements", [])
    
    from database.mongo_store import upsert_user
    upsert_user(
        user_id=user_id,
        name=name,
        email=email,
        role=role,
        target_role=target_role,
        skills_json=json.dumps(skills),
        achievements_json=json.dumps(achievements)
    )
    
    return jsonify({"success": True, "message": "Profile updated successfully"})


@placement_bp.route("/technical-interview/submit", methods=["POST"])
def technical_interview_submit():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    technology = payload.get("technology", "Python")
    question = payload.get("question", "")
    response = payload.get("response", "")
    
    if not question.strip():
        return jsonify({"error": "Question is required"}), 400
        
    from ai.hirevision_ai import evaluate_technical_response
    result = evaluate_technical_response(technology, question, response)
    
    save_record("interviews", {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "interview_type": "technical",
        "domain": technology,
        "company": "General Practice",
        "questions_json": json.dumps([question]),
        "responses_json": json.dumps([response]),
        "scores_json": json.dumps({
            "overall": result.get("score", 70),
            "communication": result.get("clarity_score", 70),
            "technical": result.get("depth_score", 70)
        }),
        "transcript_json": json.dumps([{"question": question, "answer": response, "feedback": result.get("feedback", "")}]),
        "created_at": _now(),
        "updated_at": _now()
    })
    
    return jsonify(result)


def _extract_text_from_upload(uploaded_file) -> str:
    filename = (uploaded_file.filename or "").lower()
    raw_bytes = uploaded_file.read()

    if filename.endswith(".txt"):
        return raw_bytes.decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        try:
            import io

            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(raw_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            pass

    if filename.endswith(".docx"):
        try:
            import io

            from docx import Document

            document = Document(io.BytesIO(raw_bytes))
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        except Exception:
            pass

    return raw_bytes.decode("utf-8", errors="ignore")

