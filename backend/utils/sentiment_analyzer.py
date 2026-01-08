"""
Sentiment analysis module
Analyzes emotional tone, confidence, and professionalism of responses
"""

from textblob import TextBlob
import re

def analyze_sentiment(text):
    """
    Analyze sentiment of candidate response
    Args:
        text: Response text
    Returns:
        Sentiment analysis with score and confidence
    """
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Detect professionalism markers
        professional_words = ['strategic', 'leverage', 'synergy', 'implement', 'optimize', 'analyze']
        professionalism_score = sum(1 for word in professional_words if word.lower() in text.lower()) / 10
        
        # Detect filler words
        filler_patterns = [
            r'\bum\b', r'\buh\b', r'\blike\b', r'\byou know\b',
            r'\bbasically\b', r'\bactually\b', r'\bkind of\b', r'\bsort of\b'
        ]
        filler_count = sum(len(re.findall(pattern, text.lower())) for pattern in filler_patterns)
        
        # Calculate confidence score based on various factors
        confidence = calculate_confidence(text, polarity, filler_count)
        
        return {
            "score": round(polarity, 3),
            "confidence": round(confidence, 3),
            "subjectivity": round(subjectivity, 3),
            "professionalism": round(min(professionalism_score, 1.0), 3),
            "filler_word_count": filler_count,
            "sentiment_type": get_sentiment_type(polarity),
            "summary": f"The candidate's response shows a {'positive' if polarity > 0 else 'neutral' if polarity == 0 else 'negative'} tone with {'high' if confidence > 0.7 else 'moderate' if confidence > 0.4 else 'low'} confidence."
        }
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return {"score": 0, "confidence": 0, "error": str(e)}

def calculate_confidence(text, polarity, filler_count):
    """
    Calculate confidence score based on multiple factors
    """
    # Longer, more detailed responses indicate confidence
    length_score = min(len(text.split()) / 100, 1.0)
    
    # Positive polarity indicates confidence
    polarity_score = (polarity + 1) / 2
    
    # Fewer filler words indicate confidence
    filler_score = max(1 - (filler_count / 10), 0)
    
    # Check for hedging language
    hedges = ['might', 'maybe', 'possibly', 'probably', 'seems', 'appears']
    hedge_count = sum(1 for hedge in hedges if hedge in text.lower())
    hedge_score = max(1 - (hedge_count / 5), 0)
    
    confidence = (length_score + polarity_score + filler_score + hedge_score) / 4
    return confidence

def get_sentiment_type(polarity):
    """Classify sentiment as positive, neutral, or negative"""
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def detect_filler_words(text):
    """Extract and count filler words"""
    filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'kind of', 'sort of']
    detected = []
    for filler in filler_words:
        if re.search(rf'\b{filler}\b', text.lower()):
            count = len(re.findall(rf'\b{filler}\b', text.lower()))
            detected.append({"word": filler, "count": count})
    return detected
