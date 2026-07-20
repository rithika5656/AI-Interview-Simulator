# HireVision - AI-based Placement Preparation System

A comprehensive AI-powered platform for placement preparation, including resume analysis, aptitude tests, coding challenges, group discussion practice, and AI interviews.

## 🎯 Features

### Core Modules
- **Dashboard** - Placement readiness score, performance charts, recent activity, goals, AI coach snapshot
- **Resume Analyzer** - PDF upload, text extraction, ATS score, missing skills, grammar suggestions
- **Aptitude** - Question generation, timed tests, instant evaluation, score saving
- **Logical Reasoning** - Reasoning questions, explanations, progress tracking
- **Verbal Ability** - Vocabulary, grammar, reading comprehension, evaluation
- **Technical MCQ** - Topic-based questions (Java, Python, DBMS, OS, etc.), difficulty levels, scoring
- **Coding Assessment** - Code editor, test case evaluation, complexity analysis
- **Group Discussion** - AI topic generation, communication scoring, feedback
- **HR Interview** - AI interviewer, voice input, feedback, weakness analysis
- **Technical Interview** - Adaptive technical questions, AI evaluation
- **Company Wise Preparation** - Company-specific questions (TCS, Infosys, Wipro, Amazon, Google, Microsoft, etc.)
- **Analytics** - Performance charts, strong/weak areas, progress over time
- **AI Career Coach** - Resume advice, skill roadmap, learning recommendations
- **Student Profile** - User info, scores, progress, history

### Technical Features
- Student-only mode (no Admin features)
- Dark theme support
- Fully functional backend APIs
- SQLite database for persistence
- CORS configuration for deployment
- Real-time interview support via Socket.io

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask with Flask-SocketIO
- **Database**: SQLite
- **AI/ML**: OpenAI (optional), TextBlob, NLTK
- **Deployment**: Render / Railway
- **Other**: Flask-CORS, python-dotenv, PyPDF2, python-docx

### Frontend
- **UI**: HTML5, CSS3 (custom dark theme)
- **JavaScript**: Vanilla JS
- **Charts**: Chart.js
- **Real-time**: Socket.io client
- **Deployment**: Vercel

## 📋 Project Structure
```
AI-Interview-Simulator/
├── backend/
│   ├── app.py                       # Main Flask application
│   ├── requirements.txt             # Python dependencies
│   ├── render.yaml                  # Render deployment config
│   ├── .env.example                 # Environment variables template
│   ├── ai/                          # AI-related logic
│   │   └── hirevision_ai.py
│   ├── database/                    # SQLite database
│   │   └── sqlite_store.py
│   ├── routes/                      # API routes
│   │   └── placement_routes.py
│   ├── services/                    # Business logic
│   │   └── placement_service.py
│   └── utils/                       # Utility modules
│       ├── speech_processor.py
│       ├── nlp_engine.py
│       ├── sentiment_analyzer.py
│       └── feedback_generator.py
├── frontend/
│   ├── index.html                   # Main UI
│   ├── styles.css                   # Styling
│   ├── app.js                       # Client-side logic
│   └── apiClient.js                 # API client
├── scripts/
│   └── test_submit.py
├── package.json
├── vercel.json
└── README.md
```

## 🚀 Deployment Guide

### 1. Deploy Backend on Render

1. **Fork/Clone this repository**
2. **Create a new Web Service** on [Render](https://render.com/)
3. **Configure the service**:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 app:app`
   - **Root Directory**: `backend`
4. **Add Environment Variables** (optional):
   - `FRONTEND_ORIGINS`: Set to your Vercel frontend URL (e.g., `https://hirevision.vercel.app`)
   - `OPENAI_API_KEY` (optional): Your OpenAI API key for enhanced AI features
5. **Deploy the service**
6. **Copy the deployed backend URL** (e.g., `https://hirevision-backend.onrender.com`)

### 2. Configure Frontend for Deployed Backend

Update the fallback URL in `frontend/apiClient.js` (lines 8-9) to your deployed backend:
```javascript
// Frontend: frontend/apiClient.js
// ...
|| 'https://your-deployed-backend.onrender.com/api'; // Replace this!
// ...
|| 'https://your-deployed-backend.onrender.com';     // And this!
```

### 3. Deploy Frontend on Vercel

1. **Connect your repository** to Vercel
2. **Configure the project**:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Other (or Vite if you prefer)
3. **Add Environment Variables** (optional):
   - `NEXT_PUBLIC_API_URL` or `REACT_APP_API_URL`: Your deployed backend URL + `/api`
4. **Deploy!**

### 4. Verify Deployment

1. **Test the backend health check**: Visit `https://your-deployed-backend.onrender.com/health`
2. **Open your deployed Vercel frontend**
3. **Try all modules** (Dashboard, Resume, Aptitude, etc.)!

## 🖥️ Local Development

### Prerequisites
- Python 3.8 or higher
- Node.js (optional, for frontend dev server)

### Backend Setup (Local)

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create a virtual environment**:
```bash
python -m venv venv
# Activate:
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Copy environment variables template**:
```bash
cp .env.example .env
# Edit .env to add any optional variables (like OPENAI_API_KEY)
```

5. **Run the backend**:
```bash
python app.py
```

Backend is now running at `http://localhost:5000`

### Frontend Setup (Local)

1. **Navigate to frontend directory**:
```bash
cd ../frontend
```

2. **Start a simple HTTP server**:
```bash
# Python:
python -m http.server 8000
# Or Node.js:
npx http-server
```

3. **Open in browser**: Visit `http://localhost:8000`

## 🔑 Environment Variables (Backend)

Create a `.env` file in `/backend`:

```env
# Optional: OpenAI API key for enhanced AI features
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Google Cloud project ID (for speech-to-text)
GOOGLE_CLOUD_PROJECT_ID=your_project_id_here

# Optional: Frontend URL(s) for CORS (defaults to *)
FRONTEND_ORIGINS=https://your-vercel-frontend.vercel.app

# Optional: Host and port (defaults to 0.0.0.0 and 5000)
HOST=0.0.0.0
PORT=5000
```

## 📊 API Endpoints

Check out the backend routes in `/backend/routes/placement_routes.py` and `/backend/app.py` for the full list of API endpoints.

## 🤝 Contributing

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details.

---

**Created with ❤️ for placement preparation**
