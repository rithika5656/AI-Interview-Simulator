"""
Feedback report generator
Generates comprehensive feedback report with scores and recommendations
"""

def generate_report(session):
    """
    Generate comprehensive interview feedback report
    Args:
        session: Interview session data
    Returns:
        Detailed feedback report
    """
    responses = session.get('responses', [])
    analysis = session.get('analysis', [])
    
    if not responses:
        return {"error": "No responses recorded"}
    
    # Calculate aggregate scores
    avg_sentiment = sum(a['sentiment_score'] for a in analysis) / len(analysis) if analysis else 0
    avg_relevance = sum(r.get('analysis', {}).get('relevance_score', 0) for r in responses) / len(responses) if responses else 0
    total_fillers = sum(len(r.get('analysis', {}).get('filler_words', [])) for r in responses)
    
    # Generate scores
    communication_score = calculate_communication_score(analysis)
    technical_score = calculate_technical_score(responses)
    overall_score = (communication_score + technical_score) / 2
    
    report = {
        "summary": {
            "overall_score": round(overall_score, 1),
            "communication_score": round(communication_score, 1),
            "technical_score": round(technical_score, 1),
            "total_responses": len(responses),
            "average_sentiment": round(avg_sentiment, 2),
            "total_filler_words": total_fillers
        },
        "detailed_feedback": {
            "strengths": extract_strengths(responses),
            "areas_for_improvement": extract_improvements(responses),
            "communication_feedback": {
                "clarity": "Good" if communication_score > 70 else "Needs improvement",
                "confidence": "High" if avg_sentiment > 0.3 else "Moderate" if avg_sentiment > -0.2 else "Low",
                "filler_words": f"Detected {total_fillers} instances - consider reducing"
            },
            "technical_feedback": {
                "relevance": f"Average relevance score: {round(avg_relevance, 1)}/100",
                "depth": "Good" if technical_score > 70 else "Could be deeper",
                "problem_solving": "Demonstrated" if any(r.get('analysis', {}).get('depth_score', 0) > 70 for r in responses) else "Limited"
            }
        },
        "recommendations": generate_recommendations(communication_score, technical_score),
        "response_details": [
            {
                "number": i + 1,
                "text": r.get('text', ''),
                "sentiment": r.get('sentiment', {}),
                "analysis": r.get('analysis', {})
            }
            for i, r in enumerate(responses)
        ]
    }
    
    return report

def calculate_communication_score(analysis):
    """Calculate communication effectiveness score"""
    if not analysis:
        return 0
    
    scores = []
    for a in analysis:
        sentiment_score = (a.get('sentiment_score', 0) + 1) / 2 * 100
        confidence_score = a.get('confidence', 0) * 100
        filler_penalty = max(0, 100 - len(a.get('filler_words', [])) * 5)
        
        avg = (sentiment_score + confidence_score + filler_penalty) / 3
        scores.append(avg)
    
    return sum(scores) / len(scores) if scores else 0

def calculate_technical_score(responses):
    """Calculate technical knowledge and relevance score"""
    if not responses:
        return 0
    
    scores = []
    for r in responses:
        analysis = r.get('analysis', {})
        relevance = analysis.get('relevance_score', 50)
        clarity = analysis.get('clarity_score', 50)
        depth = analysis.get('depth_score', 50)
        
        avg = (relevance + clarity + depth) / 3
        scores.append(avg)
    
    return sum(scores) / len(scores) if scores else 0

def extract_strengths(responses):
    """Extract and summarize key strengths"""
    strengths = []
    for r in responses:
        analysis = r.get('analysis', {})
        key_strengths = analysis.get('key_strengths', [])
        if key_strengths:
            strengths.extend(key_strengths)
    
    # Remove duplicates and limit to top 5
    unique_strengths = list(set(strengths))[:5]
    return unique_strengths if unique_strengths else ["Clear communication", "Structured thinking"]

def extract_improvements(responses):
    """Extract and summarize areas for improvement"""
    improvements = []
    for r in responses:
        analysis = r.get('analysis', {})
        improvement_areas = analysis.get('improvement_areas', [])
        if improvement_areas:
            improvements.extend(improvement_areas)
    
    # Remove duplicates and limit to top 5
    unique_improvements = list(set(improvements))[:5]
    return unique_improvements if unique_improvements else ["Provide more specific examples", "Structure answers with STAR method"]

def generate_recommendations(communication_score, technical_score):
    """Generate actionable recommendations based on scores"""
    recommendations = []
    
    if communication_score < 60:
        recommendations.append("Practice speaking more clearly and confidently. Consider recording yourself answering mock questions.")
    
    if technical_score < 60:
        recommendations.append("Deepen your technical knowledge. Study core concepts and practice explaining them in simple terms.")
    
    if communication_score < 70 or technical_score < 70:
        recommendations.append("Use the STAR method (Situation, Task, Action, Result) to structure your answers.")
    
    recommendations.append("Review the feedback above and practice addressing the identified areas.")
    recommendations.append("Take multiple mock interviews to build confidence and refine your responses.")
    
    return recommendations
