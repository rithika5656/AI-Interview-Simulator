"""Placement preparation business logic for HireVision."""

from __future__ import annotations

import json
import random
import textwrap
import uuid
from datetime import datetime
from typing import Any

from ai.hirevision_ai import (
    generate_career_coach_snapshot,
    generate_gd_feedback,
    generate_follow_up_question,
    generate_resume_analysis,
    generate_structured_mcq,
)
from database.mongo_store import (
    get_dashboard_metrics,
    latest_by_table,
    latest_resume,
    list_recent_activity,
    save_record,
    upsert_user,
)

APPLIED_TOPICS = {
    "aptitude": [
        "Quantitative Aptitude",
        "Number System",
        "Time & Work",
        "Time & Distance",
        "Probability",
        "Permutation & Combination",
        "Profit & Loss",
        "Percentage",
        "Ratio",
        "Simplification",
    ],
    "logical": [
        "Blood Relation",
        "Seating Arrangement",
        "Coding Decoding",
        "Puzzle",
        "Syllogism",
        "Direction Sense",
        "Statement & Assumption",
    ],
    "verbal": [
        "Synonyms",
        "Antonyms",
        "Reading Comprehension",
        "Grammar",
        "Error Spotting",
        "Sentence Correction",
    ],
    "technical": [
        "Java",
        "Python",
        "C++",
        "DBMS",
        "OOPS",
        "Operating System",
        "Computer Networks",
        "SQL",
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "AI/ML",
    ],
}

COMPANY_TRACKS = {
    "TCS": {"focus": ["Aptitude", "Coding", "HR"], "difficulty": "medium"},
    "Infosys": {"focus": ["Aptitude", "Technical", "HR"], "difficulty": "medium"},
    "Cognizant": {"focus": ["Aptitude", "Coding", "Technical"], "difficulty": "medium"},
    "Wipro": {"focus": ["Aptitude", "Technical", "HR"], "difficulty": "medium"},
    "Zoho": {"focus": ["Coding", "Technical", "HR"], "difficulty": "hard"},
    "Accenture": {"focus": ["Aptitude", "Technical", "Interview"], "difficulty": "medium"},
    "Capgemini": {"focus": ["Aptitude", "Coding", "Interview"], "difficulty": "medium"},
    "Amazon": {"focus": ["Coding", "Technical", "Interview"], "difficulty": "hard"},
    "Microsoft": {"focus": ["Coding", "Technical", "Interview"], "difficulty": "hard"},
    "Google": {"focus": ["Coding", "Technical", "Interview"], "difficulty": "hard"},
}


def ensure_demo_user(user_id: str = "demo_student") -> None:
    upsert_user(user_id=user_id, name="Demo Student", email="demo@example.com")


def build_dashboard(user_id: str) -> dict[str, Any]:
    ensure_demo_user(user_id)
    metrics = get_dashboard_metrics(user_id)
    activities = list_recent_activity(user_id)
    recent_resume = latest_resume(user_id)
    coach = generate_career_coach_snapshot(metrics)

    daily_goals = [
        "Solve 3 aptitude problems",
        "Revise 1 technical topic",
        "Record 1 mock interview answer",
    ]

    upcoming_tests = [
        {"title": "Aptitude Sprint", "module": "Aptitude", "time": "Today 7:00 PM"},
        {"title": "Technical Mock", "module": "Technical Interview", "time": "Tomorrow 6:30 PM"},
        {"title": "Coding Challenge", "module": "Coding", "time": "Friday 8:00 PM"},
    ]

    return {
        "user_id": user_id,
        "metrics": metrics,
        "recent_resume": recent_resume,
        "recent_activities": activities,
        "daily_goals": daily_goals,
        "upcoming_mock_tests": upcoming_tests,
        "career_coach": coach,
        "progress_bars": {
            "resume": metrics["resume_score"],
            "aptitude": metrics["aptitude_progress"],
            "coding": metrics["coding_progress"],
            "interview": metrics["interview_score"],
            "gd": metrics["gd_score"],
        },
    }


def analyze_resume_payload(user_id: str, resume_text: str, filename: str | None = None) -> dict[str, Any]:
    ensure_demo_user(user_id)
    analysis = generate_resume_analysis(resume_text)

    save_record(
        "resumes",
        {
            "user_id": user_id,
            "filename": filename or "uploaded_resume",
            "raw_text": resume_text,
            "skills_json": json.dumps(analysis.get("skills", [])),
            "projects_json": json.dumps(analysis.get("projects", [])),
            "education_json": json.dumps(analysis.get("education", [])),
            "certifications_json": json.dumps(analysis.get("certifications", [])),
            "ats_score": float(analysis.get("ats_score", 0)),
            "missing_keywords_json": json.dumps(analysis.get("missing_keywords", [])),
            "suggestions_json": json.dumps(analysis.get("suggestions", [])),
            "created_at": _now(),
        },
    )

    return {
        "skills": analysis.get("skills", []),
        "projects": analysis.get("projects", []),
        "education": analysis.get("education", []),
        "certifications": analysis.get("certifications", []),
        "ats_score": float(analysis.get("ats_score", 0)),
        "missing_keywords": analysis.get("missing_keywords", []),
        "suggestions": analysis.get("suggestions", []),
        "resume_excerpt": textwrap.shorten(resume_text, width=180, placeholder="..."),
    }


def generate_question_set(module: str, topic: str, difficulty: str, count: int = 5) -> list[dict[str, Any]]:
    questions = []
    for index in range(count):
        question = generate_structured_mcq(module, topic, difficulty)
        question["id"] = str(uuid.uuid4())
        question["order"] = index + 1
        question.setdefault("topic", topic)
        question.setdefault("difficulty", difficulty)
        questions.append(question)
    return questions


def grade_mcq_submission(questions: list[dict[str, Any]], answers: list[int | None]) -> dict[str, Any]:
    scored_items = []
    correct_count = 0

    for index, question in enumerate(questions):
        selected_answer = answers[index] if index < len(answers) else None
        correct_answer = int(question.get("correct_index", question.get("answer_index", 0)))
        is_correct = selected_answer == correct_answer
        if is_correct:
            correct_count += 1

        scored_items.append(
            {
                "id": question.get("id"),
                "question": question.get("question"),
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", ""),
            }
        )

    total_count = len(questions) or 1
    score = round((correct_count / total_count) * 100, 1)
    return {
        "score": score,
        "correct_count": correct_count,
        "total_count": len(questions),
        "items": scored_items,
    }


def gd_session_feedback(topic: str, transcript: str, user_id: str) -> dict[str, Any]:
    ensure_demo_user(user_id)
    feedback = generate_gd_feedback(topic, transcript)
    scores = {
        "communication": feedback.get("communication", 0),
        "confidence": feedback.get("confidence", 0),
        "vocabulary": feedback.get("vocabulary", 0),
        "grammar": feedback.get("grammar", 0),
        "relevance": feedback.get("relevance", 0),
        "fluency": feedback.get("fluency", 0),
    }
    save_record(
        "gd_sessions",
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "topic": topic,
            "transcript": transcript,
            "scores_json": json.dumps(scores),
            "feedback_json": json.dumps(feedback.get("feedback", [])),
            "created_at": _now(),
        },
    )
    return {"scores": scores, "feedback": feedback.get("feedback", [])}


def build_company_track(company: str) -> dict[str, Any]:
    details = COMPANY_TRACKS.get(company, {"focus": ["Aptitude", "Technical", "Interview"], "difficulty": "medium"})
    
    # Pre-defined company-specific interview patterns, HR questions, and coding challenges
    company_data = {
        "TCS": {
            "rounds": [
                "Round 1: Cognitive & Technical Assessment (Aptitude, Coding, Technical MCQs)",
                "Round 2: Technical Interview (Core Engineering, Projects, Coding Questions)",
                "Round 3: HR Interview (Behavioral, Culture Fit, Communication)"
            ],
            "hr_questions": [
                "Why do you want to join TCS?",
                "Are you willing to relocate to other cities in India?",
                "Tell me about a time when you managed a conflict in a project group."
            ],
            "coding_problems": [
                {"title": "Check Prime", "desc": "Determine if a given positive integer is prime."},
                {"title": "Array Rotation", "desc": "Rotate an array of size N to the left by D positions."}
            ]
        },
        "Infosys": {
            "rounds": [
                "Round 1: Online Test (Analytical Reasoning, Technical MCQs, Pseudocode)",
                "Round 2: Technical & HR Interview (Coding, Resume Walkthrough, HR Questions)"
            ],
            "hr_questions": [
                "What makes you suitable for the Systems Engineer role at Infosys?",
                "How do you handle high-pressure deadlines?",
                "Describe your biggest academic or extracurricular achievement."
            ],
            "coding_problems": [
                {"title": "Palindrome String", "desc": "Check if a given string is a palindrome without ignoring case."},
                {"title": "Find Substring", "desc": "Find the index of the first occurrence of a needle in a haystack."}
            ]
        },
        "Zoho": {
            "rounds": [
                "Round 1: Written MCQ (Aptitude and C/Java Output Questions)",
                "Round 2: Programming Round (5-6 coding problems to solve in 3 hours)",
                "Round 3: Advanced Programming Round (Design a system/console app, e.g. Library Management)",
                "Round 4: Technical & HR Interviews"
            ],
            "hr_questions": [
                "Why Zoho? How do you align with our culture of self-learning?",
                "If you get a higher paying offer, why would you stay at Zoho?",
                "What is your approach to learning technologies you've never used before?"
            ],
            "coding_problems": [
                {"title": "Look and Say Sequence", "desc": "Generate the N-th term of the look-and-say sequence."},
                {"title": "Pattern Printing", "desc": "Print an X pattern of characters from a string of odd length."}
            ]
        },
        "Amazon": {
            "rounds": [
                "Round 1: Online Assessment (Coding + Work Style Assessment)",
                "Round 2: Technical Interview 1 (DS & Algorithms + Leadership Principles)",
                "Round 3: Technical Interview 2 (System Design + Leadership Principles)",
                "Round 4: Bar Raiser Interview (Deep Dive + Cultural Assessment)"
            ],
            "hr_questions": [
                "Describe a time when you took a risk and failed. What did you learn?",
                "Tell me about a time when you disagreed with a manager/peer. How did you resolve it?",
                "How have you gone above and beyond to satisfy a customer or project objective?"
            ],
            "coding_problems": [
                {"title": "LRU Cache", "desc": "Design and implement a Least Recently Used (LRU) Cache."},
                {"title": "Merge K Sorted Lists", "desc": "Merge K sorted linked lists and return it as one sorted list."}
            ]
        },
        "Google": {
            "rounds": [
                "Round 1: Online Coding Challenge (2 algorithmic problems)",
                "Round 2: Technical Phone Screen (DS & Algorithms coding)",
                "Round 3: Onsite Interviews (3 coding rounds + 1 System Design round)",
                "Round 4: Googleyness & Leadership Interview"
            ],
            "hr_questions": [
                "How do you maintain focus and innovate when faced with ambiguous requirements?",
                "Tell me about a time you helped a teammate who was struggling.",
                "What is your dream project and why does it interest you?"
            ],
            "coding_problems": [
                {"title": "Median of Two Sorted Arrays", "desc": "Find the median of two sorted arrays of sizes M and N in O(log(M+N)) time."},
                {"title": "Word Ladder", "desc": "Find the length of shortest transformation sequence from a begin word to an end word."}
            ]
        }
    }

    # Fallback/Default for other companies
    default_company_data = {
        "rounds": [
            "Round 1: Online Aptitude & Pseudocode Test",
            "Round 2: Technical Interview (Coding, DSA, Databases)",
            "Round 3: HR & General Interview"
        ],
        "hr_questions": [
            "Tell me about yourself.",
            "Why do you want to join our company?",
            "Where do you see yourself in 5 years?"
        ],
        "coding_problems": [
            {"title": "Reverse Array", "desc": "Reverse an array in-place without using extra memory."},
            {"title": "Two Sum", "desc": "Given an array of integers, return indices of the two numbers that add up to target."}
        ]
    }

    info = company_data.get(company, default_company_data)

    return {
        "company": company,
        "focus_areas": details["focus"],
        "difficulty": details["difficulty"],
        "interview_patterns": info["rounds"],
        "hr_questions": info["hr_questions"],
        "coding_problems": info["coding_problems"],
        "modules": {
            "aptitude": generate_question_set("aptitude", random.choice(APPLIED_TOPICS["aptitude"]), details["difficulty"], count=3),
            "technical": generate_question_set("technical", random.choice(APPLIED_TOPICS["technical"]), details["difficulty"], count=3),
        },
        "interview_focus": f"Prepare company-specific questions for {company} and tailor examples to the role.",
    }


def build_career_coach(user_id: str) -> dict[str, Any]:
    metrics = get_dashboard_metrics(user_id)
    return generate_career_coach_snapshot(metrics)


def build_profile(user_id: str) -> dict[str, Any]:
    from database.mongo_store import fetch_one_mongo, fetch_all_mongo
    user = fetch_one_mongo("users", {"id": user_id})
    if not user:
        ensure_demo_user(user_id)
        user = fetch_one_mongo("users", {"id": user_id})

    resume = latest_resume(user_id)
    interview_history = fetch_all_mongo("interviews", {"user_id": user_id}, sort_by=[("created_at", -1)])
    coding_history = fetch_all_mongo("coding_tests", {"user_id": user_id}, sort_by=[("created_at", -1)])
    aptitude_history = fetch_all_mongo("aptitude_tests", {"user_id": user_id}, sort_by=[("created_at", -1)])
    logical_history = fetch_all_mongo("logical_tests", {"user_id": user_id}, sort_by=[("created_at", -1)])
    verbal_history = fetch_all_mongo("verbal_tests", {"user_id": user_id}, sort_by=[("created_at", -1)])
    technical_mcq_history = fetch_all_mongo("technical_tests", {"user_id": user_id}, sort_by=[("created_at", -1)])
    gd_history = fetch_all_mongo("gd_sessions", {"user_id": user_id}, sort_by=[("created_at", -1)])

    skills = []
    achievements = []
    if user and user.get("skills_json"):
        try:
            skills = json.loads(user["skills_json"])
        except Exception:
            pass
    if user and user.get("achievements_json"):
        try:
            achievements = json.loads(user["achievements_json"])
        except Exception:
            pass

    return {
        "user_id": user_id,
        "name": user.get("name") if user else "Student",
        "email": user.get("email") if user else "",
        "role": user.get("role") if user else "student",
        "target_role": user.get("target_role") if user else "Software Engineer",
        "skills": skills,
        "achievements": achievements,
        "resume": resume,
        "interview_history": interview_history,
        "coding_history": coding_history,
        "aptitude_history": aptitude_history,
        "logical_history": logical_history,
        "verbal_history": verbal_history,
        "technical_mcq_history": technical_mcq_history,
        "gd_history": gd_history,
        "placement_score": get_dashboard_metrics(user_id)["placement_readiness_score"],
    }


def build_analytics(user_id: str) -> dict[str, Any]:
    metrics = get_dashboard_metrics(user_id)
    base = metrics["placement_readiness_score"]
    return {
        "daily_progress": [max(base - 6, 0), max(base - 2, 0), base],
        "weekly_progress": [max(base - 12, 0), max(base - 7, 0), max(base - 3, 0), base],
        "monthly_progress": [max(base - 15, 0), max(base - 10, 0), max(base - 5, 0), base],
        "interview_trend": [68, 70, 72, metrics["interview_score"]],
        "coding_accuracy": [58, 61, 65, metrics["coding_progress"]],
        "aptitude_accuracy": [60, 63, 66, metrics["aptitude_progress"]],
        "technical_accuracy": [62, 65, 68, metrics["interview_score"]],
    }


def analyze_coding_submission(language: str, code: str, problem_statement: str = "") -> dict[str, Any]:
    from ai.hirevision_ai import evaluate_coding_code
    return evaluate_coding_code(language, code, problem_statement)


def generate_technical_interview_question(technology: str, resume_skills: list[str] | None = None, job_description: str | None = None) -> dict[str, Any]:
    resume_skills = resume_skills or []
    context = ", ".join(resume_skills[:5]) or technology
    question = generate_follow_up_question(
        f"technical interview on {technology} with skills {context}",
        previous_response=job_description,
    )
    return {
        "technology": technology,
        "question": question,
        "follow_up_hint": f"Tailor your answer to {context} and the job requirements.",
    }


def generate_mock_module(module_key: str, topic: str | None, difficulty: str, count: int = 5) -> dict[str, Any]:
    topic = topic or random.choice(APPLIED_TOPICS.get(module_key, [module_key.title()]))
    questions = generate_question_set(module_key, topic, difficulty, count=count)
    return {
        "module": module_key,
        "topic": topic,
        "difficulty": difficulty,
        "questions": questions,
    }


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"