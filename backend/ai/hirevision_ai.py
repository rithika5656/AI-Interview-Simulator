"""Shared AI helpers for HireVision.

These helpers reuse the existing OpenAI-compatible setup in the project while
providing consistent JSON-shaped outputs for the new placement modules.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

try:
    from openai import OpenAI

    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _use_modern_client = True
except Exception:
    import openai

    openai.api_key = os.getenv("OPENAI_API_KEY")
    _client = openai
    _use_modern_client = False


def _extract_content(response: Any) -> str:
    try:
        return response.choices[0].message.content
    except Exception:
        try:
            return response["choices"][0]["message"]["content"]
        except Exception:
            return str(response)


def _call_json_prompt(prompt: str, fallback: dict[str, Any], max_tokens: int = 500) -> dict[str, Any]:
    try:
        if _use_modern_client:
            response = _client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=max_tokens,
            )
        else:
            response = _client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=max_tokens,
            )
        content = _extract_content(response)
        return json.loads(content)
    except Exception:
        return fallback


def generate_structured_mcq(module: str, topic: str, difficulty: str) -> dict[str, Any]:
    fallback = _fallback_mcq(module, topic, difficulty)
    prompt = f"""
Generate one {module} multiple-choice question for the topic '{topic}' at '{difficulty}' difficulty.
Return JSON with keys: question, options (array of 4 strings), answer_index (0-3), correct_index (0-3), explanation, difficulty, topic.
Make the question clear, practical, and suitable for placement preparation.
"""
    result = _call_json_prompt(prompt, fallback, max_tokens=450)
    if "correct_index" not in result and "answer_index" in result:
        result["correct_index"] = result["answer_index"]
    return result


def generate_resume_analysis(resume_text: str) -> dict[str, Any]:
    fallback = _fallback_resume_analysis(resume_text)
    prompt = f"""
Analyze this resume text for a placement preparation system.
Return JSON with keys: skills (array), projects (array), education (array), certifications (array), ats_score (number 0-100), missing_keywords (array), suggestions (array).
Resume text:
{resume_text[:6000]}
"""
    return _call_json_prompt(prompt, fallback, max_tokens=700)


def generate_gd_feedback(topic: str, transcript: str) -> dict[str, Any]:
    fallback = {
        "communication": 72,
        "confidence": 68,
        "vocabulary": 70,
        "grammar": 71,
        "relevance": 69,
        "fluency": 70,
        "feedback": [f"Continue framing points around {topic}.", "Use a brief opening and a sharper conclusion."],
    }
    prompt = f"""
Evaluate a group discussion response for topic '{topic}'.
Return JSON with keys: communication, confidence, vocabulary, grammar, relevance, fluency, feedback (array of strings).
Transcript:
{transcript[:6000]}
"""
    return _call_json_prompt(prompt, fallback, max_tokens=450)


def generate_career_coach_snapshot(scores: dict[str, float]) -> dict[str, Any]:
    fallback = {
        "strengths": ["Consistent practice", "Balanced preparation"],
        "weaknesses": ["Increase coding accuracy", "Revise aptitude basics"],
        "learning_plan": ["Practice 2 coding problems daily", "Take one timed aptitude set", "Record one mock interview response"],
        "recommended_topics": ["Arrays", "Time and Work", "System Design Basics"],
        "placement_readiness": scores.get("placement_readiness_score", 70),
    }
    prompt = f"""
Act as an AI career coach for placement preparation.
Use these scores: {json.dumps(scores)}
Return JSON with keys: strengths (array), weaknesses (array), learning_plan (array), recommended_topics (array), placement_readiness (number).
"""
    return _call_json_prompt(prompt, fallback, max_tokens=500)


def generate_follow_up_question(domain: str, previous_response: str | None = None) -> str:
    context = previous_response or "fresh opening question"
    prompt = f"""
Create one concise follow-up interview question for a {domain} interview.
Use this context: {context}
Return plain text only.
"""
    try:
        if _use_modern_client:
            response = _client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=120,
            )
        else:
            response = _client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=120,
            )
        return _extract_content(response).strip()
    except Exception:
        return f"Tell me more about your experience related to {domain}."


def _fallback_mcq(module: str, topic: str, difficulty: str) -> dict[str, Any]:
    templates = {
        "aptitude": {
            "Percentage": {
                "question": "What is 15% of 240?",
                "options": ["24", "30", "36", "42"],
                "answer_index": 2,
                "correct_index": 2,
                "explanation": "15% of 240 is 36.",
            },
            "Ratio": {
                "question": "If the ratio of boys to girls is 3:5 and there are 40 students, how many girls are there?",
                "options": ["15", "20", "25", "30"],
                "answer_index": 2,
                "correct_index": 2,
                "explanation": "Total parts are 8, so each part is 5 and girls are 5 × 5 = 25.",
            },
        },
        "technical": {
            "SQL": {
                "question": "Which SQL clause is used to filter aggregated results?",
                "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
                "answer_index": 1,
                "correct_index": 1,
                "explanation": "HAVING filters groups after aggregation.",
            },
            "OOPS": {
                "question": "Which OOP concept allows one interface to represent multiple forms?",
                "options": ["Encapsulation", "Abstraction", "Polymorphism", "Inheritance"],
                "answer_index": 2,
                "correct_index": 2,
                "explanation": "Polymorphism lets the same interface behave differently based on context.",
            },
        },
    }

    module_templates = templates.get(module.lower(), {})
    topic_template = module_templates.get(topic)
    if topic_template:
        return {
            **topic_template,
            "topic": topic,
            "difficulty": difficulty,
        }

    return {
        "question": f"Sample {module} question on {topic}.",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "answer_index": 0,
        "correct_index": 0,
        "explanation": f"This is a fallback explanation for {topic}.",
        "topic": topic,
        "difficulty": difficulty,
    }


def _fallback_resume_analysis(resume_text: str) -> dict[str, Any]:
    lower = resume_text.lower()
    skills = [skill for skill in ["python", "java", "sql", "react", "flask", "machine learning", "c++", "javascript"] if skill in lower]
    if not skills:
        skills = ["Communication", "Problem Solving"]
    missing_keywords = [keyword for keyword in ["data structures", "system design", "docker", "testing", "cloud"] if keyword not in lower]
    return {
        "skills": list(dict.fromkeys(skill.title() for skill in skills)),
        "projects": [line.strip() for line in re.split(r"[\n.;]", resume_text) if len(line.split()) > 4][:4],
        "education": ["Degree information detected"],
        "certifications": ["No certifications explicitly detected"],
        "ats_score": min(92, 58 + len(skills) * 6),
        "missing_keywords": missing_keywords[:5],
        "suggestions": ["Add impact metrics to project bullets", "Include ATS-friendly keywords from the target role"],
    }
