"""Placement preparation routes for HireVision."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from services.placement_service import (
    analyze_resume_payload,
    analyze_coding_submission,
    build_admin_overview,
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

placement_bp = Blueprint("placement", __name__, url_prefix="/api")


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
                "admin",
                "profile",
            ]
        }
    )


@placement_bp.route("/dashboard/overview", methods=["GET"])
def dashboard_overview():
    user_id = request.args.get("user_id", "demo_student")
    return jsonify(build_dashboard(user_id))


@placement_bp.route("/resume/analyze", methods=["POST"])
def resume_analyze():
    payload = request.get_json(silent=True) or {}
    user_id = request.form.get("user_id") or payload.get("user_id", "demo_student")
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
    payload = request.get_json(silent=True) or {}
    topic = payload.get("topic")
    difficulty = payload.get("difficulty", "medium")
    count = int(payload.get("count", 5))
    return jsonify(generate_mock_module(module_key, topic, difficulty, count=count))


@placement_bp.route("/<module_key>/submit", methods=["POST"])
def submit_module(module_key: str):
    payload = request.get_json(silent=True) or {}
    questions = payload.get("questions", [])
    answers = payload.get("answers", [])
    result = grade_mcq_submission(questions, answers)
    return jsonify({"module": module_key, **result})


@placement_bp.route("/coding/review", methods=["POST"])
def coding_review():
    payload = request.get_json(silent=True) or {}
    return jsonify(
        analyze_coding_submission(
            payload.get("language", "Python"),
            payload.get("code", ""),
            payload.get("problem_statement", ""),
        )
    )


@placement_bp.route("/gd/simulate", methods=["POST"])
def simulate_gd():
    payload = request.get_json(silent=True) or {}
    topic = payload.get("topic", "Emerging technologies")
    transcript = payload.get("transcript", "")
    user_id = payload.get("user_id", "demo_student")
    return jsonify(gd_session_feedback(topic, transcript, user_id))


@placement_bp.route("/company-track/<company>", methods=["GET"])
def company_track(company: str):
    return jsonify(build_company_track(company))


@placement_bp.route("/analytics/summary", methods=["GET"])
def analytics_summary():
    user_id = request.args.get("user_id", "demo_student")
    return jsonify(build_analytics(user_id))


@placement_bp.route("/career-coach", methods=["GET"])
def career_coach():
    user_id = request.args.get("user_id", "demo_student")
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


@placement_bp.route("/admin/overview", methods=["GET"])
def admin_overview():
    return jsonify(build_admin_overview())


@placement_bp.route("/profile/<user_id>", methods=["GET"])
def profile(user_id: str):
    return jsonify(build_profile(user_id))


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
