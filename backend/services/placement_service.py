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




def build_dashboard(user_id: str) -> dict[str, Any]:

    metrics = get_dashboard_metrics(user_id)
    activities = list_recent_activity(user_id)
    recent_resume = latest_resume(user_id)

    # Check if the user is a brand new user
    is_new = (len(activities) == 0 and recent_resume is None)

    if is_new:
        coach = {
            "strengths": ["No activity yet"],
            "weaknesses": ["No analytics available"],
            "learning_plan": [],
            "recommended_topics": [],
            "placement_readiness": 0.0,
        }
        daily_goals = []
        upcoming_tests = []
    else:
        coach = generate_career_coach_snapshot(metrics)
        daily_goals = []
        if metrics["aptitude_progress"] < 80:
            daily_goals.append("Practice 3 Aptitude questions to improve your score")
        if metrics["coding_progress"] < 80:
            daily_goals.append("Solve 1 new Coding problem today")
        if metrics["interview_score"] < 80:
            daily_goals.append("Record 1 HR Interview response")
        if len(daily_goals) < 3:
            daily_goals.append("Review a Company Preparation Track")
            
        upcoming_tests = []
        if metrics["aptitude_progress"] < 90:
            upcoming_tests.append({"title": "Aptitude Refresher", "module": "Aptitude", "time": "Recommended Today"})
        if metrics["coding_progress"] < 90:
            upcoming_tests.append({"title": "Coding Challenge", "module": "Coding", "time": "Recommended Tomorrow"})
        if not upcoming_tests:
            upcoming_tests.append({"title": "Mastery Assessment", "module": "Technical Interview", "time": "Anytime"})

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
            "experience_json": json.dumps(analysis.get("experience", [])),
            "achievements_json": json.dumps(analysis.get("achievements", [])),
            "internships_json": json.dumps(analysis.get("internships", [])),
            "languages_json": json.dumps(analysis.get("languages", [])),
            "ats_score": float(analysis.get("ats_score", 0)),
            "missing_keywords_json": json.dumps(analysis.get("missing_keywords", [])),
            "suggestions_json": json.dumps(analysis.get("suggestions", [])),
            "created_at": _now(),
        },
    )

    return {
        "name": analysis.get("name", "Demo Student"),
        "email": analysis.get("email", ""),
        "phone": analysis.get("phone", ""),
        "skills": analysis.get("skills", []),
        "projects": analysis.get("projects", []),
        "education": analysis.get("education", []),
        "certifications": analysis.get("certifications", []),
        "experience": analysis.get("experience", []),
        "achievements": analysis.get("achievements", []),
        "internships": analysis.get("internships", []),
        "languages": analysis.get("languages", []),
        "ats_score": float(analysis.get("ats_score", 0)),
        "missing_keywords": analysis.get("missing_keywords", []),
        "suggestions": analysis.get("suggestions", []),
        "resume_excerpt": textwrap.shorten(resume_text, width=180, placeholder="..."),
    }


def get_random_bank_question(module: str, topic: str, difficulty: str, company: str = None, exclude_texts: list[str] = None) -> dict[str, Any]:
    from database.question_bank import QUESTION_BANK
    import random
    import copy
    
    # Try finding exact topic
    m_key = module.lower()
    if m_key == "technical-mcq":
        m_key = "technical"
    elif m_key == "logical reasoning":
        m_key = "logical"
    elif m_key == "verbal ability":
        m_key = "verbal"
        
    m_bank = QUESTION_BANK.get(m_key, {})
    t_bank = m_bank.get(topic)
    
    if not t_bank:
        # Get all questions under module
        all_questions = []
        for q_list in m_bank.values():
            all_questions.extend(q_list)
        t_bank = all_questions
        
    if not t_bank:
        # Complete fallback
        t_bank = [{
            "question": f"What is a key concept in {topic}?",
            "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
            "correct_index": 0,
            "explanation": "This is a generic concept explanation."
        }]
        
    # Exclude already generated ones
    if exclude_texts:
        available = [q for q in t_bank if q.get("question") not in exclude_texts]
    else:
        available = t_bank
        
    if not available:
        available = t_bank
        
    selected = random.choice(available)
    return copy.deepcopy(selected)


def generate_question_set(module: str, topic: str, difficulty: str, count: int = 5, company: str = None) -> list[dict[str, Any]]:
    from database.mcq_generator import get_mcq_questions
    import copy
    import uuid
    import random
    
    # Get the 120+ pool of questions for this module & difficulty
    pool = get_mcq_questions(module, topic, difficulty)
    
    # Slice the first count questions
    selected_pool = pool[:count]
    
    questions = []
    for index, q in enumerate(selected_pool):
        question = copy.deepcopy(q)
        question["id"] = str(uuid.uuid4())
        question["order"] = index + 1
        question["topic"] = topic or question.get("topic", "General")
        question["difficulty"] = difficulty
        
        # Randomize options order and adjust correct_index using Fisher-Yates
        options = question.get("options", [])
        correct_idx = int(question.get("correct_index", 0))
        
        if len(options) == 4:
            # Shuffle using random.shuffle (which uses Fisher-Yates under the hood)
            indexed_options = list(enumerate(options))
            random.shuffle(indexed_options)
            
            new_options = [opt for _, opt in indexed_options]
            new_correct_idx = next(i for i, (old_idx, _) in enumerate(indexed_options) if old_idx == correct_idx)
            
            question["options"] = new_options
            question["correct_index"] = new_correct_idx
            question["answer_index"] = new_correct_idx
            
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

    from database.coding_question_bank import CODING_QUESTION_BANK
    
    hr_pool = [
        "Tell me about a time you faced a difficult challenge at work.",
        "How do you handle working with a difficult team member?",
        "Describe a situation where you had to meet a tight deadline.",
        "What is your greatest professional achievement?",
        "Why do you want to work for this company?",
        "Where do you see yourself in five years?",
        "Tell me about a time you failed and what you learned from it.",
        "How do you stay updated with the latest technologies?",
        "Describe your ideal work environment.",
        "What are your greatest strengths and weaknesses?"
    ]
    
    dynamic_hr = random.sample(info["hr_questions"] + hr_pool, 3)
    
    difficulty_level = details["difficulty"].lower()
    coding_pool = CODING_QUESTION_BANK.get(difficulty_level, CODING_QUESTION_BANK["easy"])
    dynamic_coding_raw = random.sample(coding_pool, min(2, len(coding_pool)))
    dynamic_coding = [{"title": p["title"], "desc": p["problem_statement"]} for p in dynamic_coding_raw]

    return {
        "company": company,
        "focus_areas": details["focus"],
        "difficulty": details["difficulty"],
        "interview_patterns": info["rounds"],
        "hr_questions": dynamic_hr,
        "coding_problems": dynamic_coding,
        "modules": {
            "aptitude": generate_question_set("aptitude", random.choice(APPLIED_TOPICS["aptitude"]), details["difficulty"], count=3, company=company),
            "technical": generate_question_set("technical", random.choice(APPLIED_TOPICS["technical"]), details["difficulty"], count=3, company=company),
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
    from database.mongo_store import fetch_all_mongo
    
    apt_tests = fetch_all_mongo("aptitude_tests", {"user_id": user_id})
    cod_tests = fetch_all_mongo("coding_tests", {"user_id": user_id})
    int_tests = fetch_all_mongo("interviews", {"user_id": user_id})
    tech_tests = fetch_all_mongo("technical_tests", {"user_id": user_id})
    log_tests = fetch_all_mongo("logical_tests", {"user_id": user_id})
    verb_tests = fetch_all_mongo("verbal_tests", {"user_id": user_id})
    
    topic_scores = {}
    for tests in [apt_tests, tech_tests, log_tests, verb_tests]:
        for t in tests:
            if "topic" in t and "score" in t:
                topic_scores.setdefault(t["topic"], []).append(float(t["score"]))
                
    for t in cod_tests:
        if "language" in t and "score" in t:
            topic_scores.setdefault(t["language"], []).append(float(t["score"]))
            
    weak_topics = []
    strong_topics = []
    if topic_scores:
        avg_scores = {k: sum(v)/len(v) for k, v in topic_scores.items()}
        sorted_topics = sorted(avg_scores.items(), key=lambda x: x[1])
        weak_topics = [k for k, v in sorted_topics[:3] if v < 70]
        strong_topics = [k for k, v in sorted_topics[-3:] if v >= 70]
        
    metrics = get_dashboard_metrics(user_id)
    base = metrics["placement_readiness_score"]
    history_len = len(apt_tests) + len(cod_tests) + len(int_tests) + len(tech_tests) + len(log_tests) + len(verb_tests)
    
    return {
        "daily_progress": [max(base - 6, 0), max(base - 2, 0), base],
        "weekly_progress": [max(base - 12, 0), max(base - 7, 0), max(base - 3, 0), base],
        "monthly_progress": [max(base - 15, 0), max(base - 10, 0), max(base - 5, 0), base],
        "interview_trend": [max(metrics["interview_score"] - 10, 0), max(metrics["interview_score"] - 5, 0), metrics["interview_score"]],
        "weak_topics": weak_topics or ["Needs more data"],
        "strong_topics": strong_topics or ["Needs more data"],
        "total_tests_taken": history_len
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


def generate_mock_module(module_key: str, topic: str | None, difficulty: str, count: int = 20) -> dict[str, Any]:
    topic = topic or random.choice(APPLIED_TOPICS.get(module_key, [module_key.title()]))
    
    easy_count = int(count * 0.35)
    hard_count = int(count * 0.25)
    medium_count = count - easy_count - hard_count
    
    q_easy = generate_question_set(module_key, topic, "easy", count=easy_count)
    q_medium = generate_question_set(module_key, topic, "medium", count=medium_count)
    q_hard = generate_question_set(module_key, topic, "hard", count=hard_count)
    
    questions = q_easy + q_medium + q_hard
    random.shuffle(questions)
    
    for idx, q in enumerate(questions):
        q["order"] = idx + 1

    return {
        "module": module_key,
        "topic": topic,
        "difficulty": "Mixed",
        "questions": questions,
    }


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


user_last_coding_problem = {}

def get_random_coding_problem(user_id: str, difficulty: str) -> dict[str, Any]:
    from database.coding_question_bank import CODING_QUESTION_BANK
    import random
    import copy
    
    problems = CODING_QUESTION_BANK.get(difficulty.lower(), CODING_QUESTION_BANK["easy"])
    last_title = user_last_coding_problem.get(user_id)
    
    available = [p for p in problems if p["title"] != last_title]
    if not available:
        available = problems
        
    problem = copy.deepcopy(random.choice(available))
    user_last_coding_problem[user_id] = problem["title"]
    return problem