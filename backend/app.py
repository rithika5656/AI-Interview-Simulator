"""
AI Interview Simulator Backend
Real-time speech analysis and AI-powered interview questions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import os
from dotenv import load_dotenv
from utils.speech_processor import process_audio
from utils.nlp_engine import generate_questions, analyze_response
from utils.sentiment_analyzer import analyze_sentiment
from utils.feedback_generator import generate_report

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store interview sessions
interview_sessions = {}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    """Initialize a new interview session"""
    data = request.json
    interview_id = data.get('interview_id')
    job_role = data.get('job_role', 'Software Engineer')
    
    interview_sessions[interview_id] = {
        'job_role': job_role,
        'responses': [],
        'analysis': [],
        'started_at': None
    }
    
    # Generate initial question
    initial_question = generate_questions(job_role, question_number=1)
    
    return jsonify({
        "interview_id": interview_id,
        "question": initial_question,
        "message": "Interview started"
    }), 200

@app.route('/api/submit-response', methods=['POST'])
def submit_response():
    """Process user response and generate feedback"""
    data = request.json
    interview_id = data.get('interview_id')
    audio_file = request.files.get('audio')
    user_text = data.get('text', '')
    
    if not interview_id or interview_id not in interview_sessions:
        return jsonify({"error": "Invalid interview ID"}), 400
    
    # Process audio if provided
    if audio_file:
        user_text = process_audio(audio_file)
    
    # Analyze sentiment
    sentiment = analyze_sentiment(user_text)
    
    # Analyze response quality
    analysis = analyze_response(user_text, interview_sessions[interview_id]['job_role'])
    
    # Store response
    interview_sessions[interview_id]['responses'].append({
        'text': user_text,
        'sentiment': sentiment,
        'analysis': analysis
    })
    
    interview_sessions[interview_id]['analysis'].append({
        'sentiment_score': sentiment['score'],
        'confidence': sentiment['confidence'],
        'filler_words': analysis.get('filler_words', []),
        'content_relevance': analysis.get('relevance_score', 0)
    })
    
    # Generate follow-up question
    response_number = len(interview_sessions[interview_id]['responses'])
    if response_number < 5:
        next_question = generate_questions(
            interview_sessions[interview_id]['job_role'],
            question_number=response_number + 1,
            previous_response=user_text
        )
        follow_up = next_question
    else:
        follow_up = "Thank you for completing the interview! We'll now generate your report."
    
    return jsonify({
        "interview_id": interview_id,
        "immediate_feedback": {
            "sentiment": sentiment,
            "filler_words": analysis.get('filler_words', []),
            "relevance_score": analysis.get('relevance_score', 0)
        },
        "next_question": follow_up
    }), 200

@app.route('/api/end-interview', methods=['POST'])
def end_interview():
    """Generate final report and end interview"""
    data = request.json
    interview_id = data.get('interview_id')
    
    if not interview_id or interview_id not in interview_sessions:
        return jsonify({"error": "Invalid interview ID"}), 400
    
    session = interview_sessions[interview_id]
    report = generate_report(session)
    
    return jsonify({
        "interview_id": interview_id,
        "report": report,
        "message": "Interview completed"
    }), 200

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('response', {'data': 'Connected to AI Interview Simulator'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """Handle real-time audio chunks for live transcription"""
    interview_id = data.get('interview_id')
    audio_chunk = data.get('audio_chunk')
    
    if interview_id and audio_chunk:
        # Process audio chunk
        text = process_audio(audio_chunk)
        emit('transcription_update', {
            'text': text,
            'interview_id': interview_id
        }, broadcast=False)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
