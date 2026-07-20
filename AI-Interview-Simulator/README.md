# AI Interview Simulator

Practice interviews with AI interviewer featuring real-time speech analysis and response evaluation.

## 🎯 Features

- **Real-time Speech Recognition**: Transcribe audio using OpenAI Whisper
- **AI-Powered Questions**: Generate contextual follow-up questions with GPT-3.5/4
- **Sentiment Analysis**: Analyze emotional tone and confidence levels
- **Filler Word Detection**: Identify "um", "uh", "like" and similar filler words
- **Content Relevance Analysis**: Evaluate how well responses match job requirements
- **Real-time Video**: WebRTC-based video capture
- **Live Feedback**: Instant feedback during responses
- **Comprehensive Reports**: Detailed feedback report with scores and recommendations

## 🛠 Tech Stack

### Backend
- **Framework**: Flask with Flask-SocketIO
- **Speech**: OpenAI Whisper API
- **NLP**: OpenAI GPT-3.5/4
- **Analysis**: TextBlob for sentiment analysis
- **Real-time**: Socket.io for live updates

### Frontend
- **HTML5/CSS3**: Responsive design
- **JavaScript**: Vanilla JS with Socket.io client
- **WebRTC**: Video capture and streaming
- **MediaRecorder API**: Audio recording

## 📋 Project Structure

```
AI Interview Simulator/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment variables template
│   └── utils/
│       ├── speech_processor.py    # Audio to text conversion
│       ├── nlp_engine.py          # Question generation & analysis
│       ├── sentiment_analyzer.py  # Sentiment & confidence analysis
│       └── feedback_generator.py  # Report generation
├── frontend/
│   ├── index.html             # Main UI
│   ├── styles.css             # Styling
│   └── app.js                 # Client-side logic
├── README.md
└── .gitignore
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js (optional, for frontend development)
- OpenAI API key
- Modern web browser with WebRTC support

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/rithika5656/AI-Interview-Simulator.git
cd AI-Interview-Simulator/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. **Run the backend**
```bash
python app.py
```

The backend will start at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Start a local server** (required for WebRTC functionality)
```bash
# Using Python 3
python -m http.server 8000

# Or using Node.js/npm
npx http-server
```

3. **Access the application**
Open `http://localhost:8000` in your browser

## 📖 Usage

1. **Select Job Role**: Choose from Software Engineer, Data Scientist, or Product Manager
2. **Enter Your Name**: Provide your name for the interview session
3. **Start Interview**: Click "Start Interview" to begin
4. **Allow Permissions**: Grant camera and microphone access
5. **Record Responses**: Click "Start Recording" and answer the question
6. **Submit Response**: Click "Submit Response" to get feedback and next question
7. **Complete 5 Questions**: Answer all 5 questions to generate final report
8. **Review Feedback**: Analyze your performance scores, strengths, and recommendations
9. **Download Report**: Export your interview report as JSON

## 🔑 Environment Variables

Create a `.env` file in the backend directory:

```
OPENAI_API_KEY=your_api_key_here
GOOGLE_CLOUD_PROJECT_ID=your_project_id
FLASK_ENV=development
PORT=5000
```

## 📊 Feedback Metrics

### Scores (0-100)
- **Overall Score**: Combined communication and technical performance
- **Communication Score**: Based on clarity, confidence, and professionalism
- **Technical Score**: Based on relevance, depth, and quality of answers

### Real-time Analysis
- **Confidence Level**: Assessed from sentiment, response length, and speaking patterns
- **Filler Words**: Detected instances of "um", "uh", "like", etc.
- **Sentiment**: Positive, neutral, or negative tone detection

### Report Includes
- Detailed scores with visual cards
- Key strengths demonstrated
- Areas for improvement
- Actionable recommendations
- Individual response analysis
- Communication and technical feedback

## 🔌 API Endpoints

### `POST /api/start-interview`
Initialize a new interview session

**Request:**
```json
{
  "interview_id": "interview_123",
  "job_role": "Software Engineer"
}
```

### `POST /api/submit-response`
Process user response and provide feedback

**Request:**
```json
{
  "interview_id": "interview_123",
  "text": "user response text",
  "audio": <audio_file>
}
```

### `POST /api/end-interview`
Generate final report

**Request:**
```json
{
  "interview_id": "interview_123"
}
```

### WebSocket Events
- `connect`: Establish connection
- `audio_chunk`: Send audio for real-time processing
- `transcription_update`: Receive live transcription

## 🎓 Example Interview Questions

### Software Engineer
- Tell me about your most challenging project and how you overcame the obstacles
- Describe your experience with system design
- How do you approach code reviews?

### Data Scientist
- Describe a machine learning project from start to finish
- How do you handle feature engineering?
- Tell me about a time your model performed poorly

### Product Manager
- Walk me through your product development process
- Tell me about a product you've built
- How do you handle conflicting stakeholder priorities?

## 🐛 Troubleshooting

**Issue**: "Permission denied" for camera/microphone
- **Solution**: Check browser permissions and try in HTTPS or localhost

**Issue**: Audio processing errors
- **Solution**: Ensure OpenAI API key is valid and has quota remaining

**Issue**: Questions not generating
- **Solution**: Check API connection and model availability

**Issue**: CORS errors
- **Solution**: Ensure backend is running and CORS is properly configured

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

For issues, questions, or suggestions, please open an GitHub issue or contact the maintainers.

## 🎉 Future Enhancements

- [ ] Multiple language support
- [ ] Custom job role creation
- [ ] Interview history and tracking
- [ ] Comparison with industry benchmarks
- [ ] Advanced video analytics (eye contact, posture)
- [ ] Integration with LinkedIn
- [ ] Mobile app (React Native)
- [ ] Interview templates and preparation guides

---

**Created with ❤️ for interview preparation**
