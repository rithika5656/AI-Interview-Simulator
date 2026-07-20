"""
NLP Engine for generating interview questions and analyzing responses
Uses GPT-3.5/4 for intelligent follow-ups and content analysis
"""

import os

# Support both the older `openai` (0.x) and newer SDKs that expose `OpenAI`
try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _use_modern_client = True
except Exception:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    _client = openai
    _use_modern_client = False

def _extract_chat_content(resp):
    try:
        # modern client returns objects with attributes
        return resp.choices[0].message.content
    except Exception:
        # older client returns dict-like
        try:
            return resp['choices'][0]['message']['content']
        except Exception:
            return str(resp)

INTERVIEW_PROMPTS = {
    'Software Engineer': [
        "Tell me about your most challenging project and how you overcame the obstacles.",
        "Describe your experience with system design. Can you walk through a design decision?",
        "How do you approach code reviews and what do you look for?",
        "Tell me about a time you had to learn a new technology quickly.",
        "How do you balance technical debt with feature development?"
    ],
    'Data Scientist': [
        "Describe a machine learning project you've worked on from data collection to deployment.",
        "How do you approach feature engineering?",
        "Tell me about a time when your model performed poorly. How did you debug it?",
        "How do you handle imbalanced datasets?",
        "What metrics do you use to evaluate model performance?"
    ],
    'Product Manager': [
        "Walk me through your product development process.",
        "Tell me about a product you've built. What made it successful?",
        "How do you handle conflicting stakeholder priorities?",
        "Describe your approach to user research.",
        "How do you measure product success?"
    ]
}

def generate_questions(job_role, question_number=1, previous_response=None):
    """
    Generate interview questions based on job role
    Args:
        job_role: Position being interviewed for
        question_number: Question sequence number
        previous_response: Candidate's previous response for context
    Returns:
        Generated question
    """
    try:
        # Get predefined questions if available
        if job_role in INTERVIEW_PROMPTS:
            if question_number <= len(INTERVIEW_PROMPTS[job_role]):
                return INTERVIEW_PROMPTS[job_role][question_number - 1]
        
        # Use GPT for dynamic follow-up questions
        if previous_response:
            prompt = f"""Based on this interview response for a {job_role} position:
            
Response: {previous_response}

Generate a thoughtful follow-up question that digs deeper into their experience and competencies.
Keep it concise and professional."""
        else:
            prompt = f"""Generate a strong opening interview question for a {job_role} position.
The question should help assess technical skills, problem-solving ability, and communication.
Keep it concise and professional."""
        
        if _use_modern_client:
            response = _client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
        else:
            response = _client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )

        return _extract_chat_content(response)
    except Exception as e:
        print(f"Error generating question: {e}")
        return "Tell me about your professional background."

def analyze_response(response_text, job_role):
    """
    Analyze candidate response for relevance and quality
    Args:
        response_text: Candidate's response
        job_role: Position being interviewed for
    Returns:
        Analysis dictionary with scores and feedback
    """
    try:
        prompt = f"""Analyze this interview response for a {job_role} position.
        
Response: {response_text}

Provide analysis in JSON format with:
- relevance_score (0-100): How relevant is the answer to the position?
- clarity_score (0-100): How clear and well-articulated is the response?
- depth_score (0-100): Does it show sufficient depth and understanding?
- filler_words: List any filler words detected (um, uh, like, basically, etc.)
- key_strengths: List 2-3 key strengths demonstrated
- improvement_areas: List 1-2 areas for improvement

Return only valid JSON."""
        
        if _use_modern_client:
            response = _client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )
        else:
            response = _client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )

        import json
        analysis_text = _extract_chat_content(response)
        
        # Parse JSON response
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, return basic structure
            analysis = {
                "relevance_score": 70,
                "clarity_score": 75,
                "depth_score": 70,
                "filler_words": [],
                "key_strengths": ["Good communication"],
                "improvement_areas": ["Add more specific examples"]
            }
        
        return analysis
    except Exception as e:
        print(f"Error analyzing response: {e}")
        return {"relevance_score": 0, "error": str(e)}
