"""
AI Interview Simulator Backend
Real-time speech analysis and AI-powered interview questions
[Deployment Verified: Vercel & Render Integration complete]
"""

# Python 3.12+ removed `pkgutil.get_loader`, but Flask (and Werkzeug) expect it.
# Add a small compatibility shim before importing Flask so imports work on
# newer Python versions.
import pkgutil
import importlib.util
import sys

if not hasattr(pkgutil, 'get_loader'):
    def _get_loader(name):
        # Some callers may pass '__main__' or other names that don't have
        # an import spec when running a script directly. Handle these cases
        # gracefully by returning None instead of raising.
        try:
            if name == '__main__':
                return None
            spec = importlib.util.find_spec(name)
            if spec is None:
                return None
            return getattr(spec, 'loader', None)
        except Exception:
            return None
    pkgutil.get_loader = _get_loader

from flask import Flask, request, jsonify
import time
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import os
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
from utils.speech_processor import process_audio
from utils.nlp_engine import generate_questions, analyze_response
from utils.sentiment_analyzer import analyze_sentiment
from utils.feedback_generator import generate_report
from database.mongo_store import init_db
from routes.placement_routes import placement_bp
from routes.auth_routes import auth_bp
from utils.auth_utils import auth_identity, require_auth

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
origins_env = os.getenv("FRONTEND_ORIGINS", "https://ai-interview-simulator-xi-three.vercel.app")
frontend_origins = [o.strip() for o in origins_env.split(",") if o.strip()] if origins_env != "*" else "*"
CORS(
    app,
    resources={r"/api/*": {"origins": frontend_origins}, r"/health": {"origins": frontend_origins}},
    supports_credentials=True,
)
socketio = SocketIO(app, cors_allowed_origins=frontend_origins, async_mode="threading")
app.register_blueprint(placement_bp)
app.register_blueprint(auth_bp)

init_db()

# Store interview sessions
interview_sessions = {}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify({
        "success": False,
        "error": error.description,
    })
    response.status_code = error.code or 500
    return response


@app.errorhandler(Exception)
def handle_unexpected_exception(error):
    app.logger.exception(error)
    return jsonify({
        "success": False,
        "error": str(error),
    }), 500

@app.route('/api/start-interview', methods=['POST'])
@require_auth
def start_interview():
    """Initialize a new interview session"""
    data = request.json
    interview_id = data.get('interview_id')
    job_role = data.get('job_role', 'Software Engineer')
    user_id = auth_identity() or data.get('user_id')
    
    interview_sessions[interview_id] = {
        'user_id': user_id,
        'job_role': job_role,
        'responses': [],
        'analysis': [],
        'started_at': None,
        # live_buffer: accumulate bytes for live transcription
        'live_buffer': bytearray(),
        'last_transcribe': 0,
        'questions': []
    }
    
    # Generate initial question
    initial_question = generate_questions(job_role, question_number=1, exclude_questions=[])
    interview_sessions[interview_id]['questions'].append(initial_question)
    
    return jsonify({
        "interview_id": interview_id,
        "question": initial_question,
        "message": "Interview started"
    }), 200

@app.route('/api/submit-response', methods=['POST'])
@require_auth
def submit_response():
    """Process user response and generate feedback"""
    try:
        # Support both JSON and multipart/form-data (FormData from frontend)
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            interview_id = request.form.get('interview_id')
            user_text = request.form.get('text', '')
        else:
            data = request.get_json(silent=True) or {}
            interview_id = data.get('interview_id')
            user_text = data.get('text', '')

        audio_file = request.files.get('audio') if request.files else None

        if not interview_id or interview_id not in interview_sessions:
            return jsonify({"error": "Invalid interview ID"}), 400
    except Exception as e:
        return jsonify({"error": f"Invalid request format: {e}"}), 400
    
    # Process audio if provided
    if audio_file:
        try:
            user_text = process_audio(audio_file)
        except Exception as e:
            print(f"Error processing audio in submit_response: {e}")
            return jsonify({"error": "Error processing audio"}), 500
    
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
        asked_questions = interview_sessions[interview_id].setdefault('questions', [])
        next_question = generate_questions(
            interview_sessions[interview_id]['job_role'],
            question_number=response_number + 1,
            previous_response=user_text,
            exclude_questions=asked_questions
        )
        asked_questions.append(next_question)
        follow_up = next_question
    else:
        follow_up = "Thank you for completing the interview! We'll now generate your report."
    
    return jsonify({
        "interview_id": interview_id,
        "immediate_feedback": {
            "text": user_text,
            "sentiment": sentiment,
            "filler_words": analysis.get('filler_words', []),
            "relevance_score": analysis.get('relevance_score', 0)
        },
        "next_question": follow_up
    }), 200

@app.route('/api/end-interview', methods=['POST'])
@require_auth
def end_interview():
    """Generate final report and end interview"""
    import json
    data = request.json
    interview_id = data.get('interview_id')
    
    if not interview_id or interview_id not in interview_sessions:
        return jsonify({"error": "Invalid interview ID"}), 400
    
    session = interview_sessions[interview_id]
    report = generate_report(session)
    
    # Save report to mongodb database
    try:
        from database.mongo_store import save_record
        from datetime import datetime
        now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        
        save_record("interviews", {
            "id": interview_id,
            "user_id": session.get('user_id'),
            "interview_type": "hr",
            "domain": session.get('job_role', 'Software Engineer'),
            "company": "General Practice",
            "questions_json": json.dumps([r.get('text') for r in session.get('responses', [])]), # Fallback text
            "responses_json": json.dumps([r.get('text') for r in session.get('responses', [])]),
            "scores_json": json.dumps({
                "overall": report.get('summary', {}).get('overall_score', 75),
                "communication": report.get('summary', {}).get('communication_score', 75),
                "technical": report.get('summary', {}).get('technical_score', 75)
            }),
            "transcript_json": json.dumps(report.get('response_details', [])),
            "created_at": now,
            "updated_at": now
        })
    except Exception as e:
        print(f"Error saving interview record: {e}")
        
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
    final = data.get('final', False)
    # audio_chunk is expected as a base64 string from the frontend
    if interview_id and audio_chunk:
        try:
            import base64
            # If we receive a data URL or plain base64, normalize it
            if isinstance(audio_chunk, str) and audio_chunk.startswith('data:'):
                audio_chunk = audio_chunk.split(',')[1]

            if isinstance(audio_chunk, str):
                audio_bytes = base64.b64decode(audio_chunk)
            else:
                audio_bytes = audio_chunk
            # Append to session buffer
            session = interview_sessions.get(interview_id)
            if session is None:
                # create a lightweight session if missing
                interview_sessions[interview_id] = {
                    'job_role': '', 'responses': [], 'analysis': [],
                    'started_at': None, 'live_buffer': bytearray(), 'last_transcribe': 0
                }
                session = interview_sessions[interview_id]

            buf = session.setdefault('live_buffer', bytearray())
            buf.extend(audio_bytes)

            now = time.time()
            last = session.get('last_transcribe', 0)

            # Transcribe when final chunk received or every ~2 seconds
            if final or (now - last) >= 2.0:
                try:
                    text = process_audio(bytes(buf))
                except Exception as e:
                    print(f"Live transcription error for {interview_id}: {e}")
                    text = ''

                emit('transcription_update', {
                    'text': text,
                    'interview_id': interview_id,
                    'final': bool(final)
                }, broadcast=False)

                session['last_transcribe'] = now
                # Clear buffer after transcribing final or periodically (keep small)
                session['live_buffer'] = bytearray()
        except Exception as e:
            print(f"Error handling audio_chunk: {e}")

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/config.js')
def serve_config():
    # Dynamically generate config.js so it points to the same origin (/api)
    config_js = "window.HireVisionConfig = { apiBaseUrl: '/api', socketUrl: '' };"
    return config_js, 200, {'Content-Type': 'application/javascript'}

# Fallback route for frontend client-side routing if any
@app.route('/<path:path>')
def serve_static_fallback(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    return app.send_static_file('index.html')

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    socketio.run(app, debug=True, host=host, port=port, allow_unsafe_werkzeug=True)
