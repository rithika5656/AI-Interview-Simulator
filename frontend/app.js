const API_URL = 'http://localhost:5000/api';
const socket = io('http://localhost:5000');

let mediaRecorder;
let audioChunks = [];
let currentInterviewId;
let questionCount = 0;
let isRecording = false;

// Socket events
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('transcription_update', (data) => {
    document.getElementById('transcriptionText').textContent = data.text;
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

// Screen management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

// Start interview
async function startInterview() {
    const jobRole = document.getElementById('jobRole').value;
    const interviewName = document.getElementById('interviewName').value;

    if (!interviewName.trim()) {
        alert('Please enter your name');
        return;
    }

    currentInterviewId = `interview_${Date.now()}`;
    questionCount = 1;

    try {
        const response = await fetch(`${API_URL}/start-interview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                interview_id: currentInterviewId,
                job_role: jobRole
            })
        });

        const data = await response.json();
        document.getElementById('questionText').textContent = data.question;
        document.getElementById('questionNumber').textContent = questionCount;

        showScreen('interviewScreen');
        startWebcam();
    } catch (error) {
        console.error('Error starting interview:', error);
        alert('Error starting interview. Please try again.');
    }
}

// Webcam setup
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 } },
            audio: true
        });

        const videoElement = document.getElementById('videoElement');
        videoElement.srcObject = stream;

        // Use an audio-only recorder for live transcription (avoid sending video chunks)
        const audioStream = new MediaStream(stream.getAudioTracks());
        mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });

        mediaRecorder.ondataavailable = (event) => {
            if (!event.data || event.data.size === 0) return;
            audioChunks.push(event.data);

            // Send chunk to server as base64 for live transcription
            const reader = new FileReader();
            reader.onload = () => {
                try {
                    const dataUrl = reader.result; // data:audio/webm;base64,...
                    const base64 = dataUrl.split(',')[1];
                    socket.emit('audio_chunk', {
                        interview_id: currentInterviewId,
                        audio_chunk: base64,
                        final: false
                    });
                } catch (e) {
                    console.error('Failed to send audio chunk', e);
                }
            };
            reader.readAsDataURL(event.data);
        };
    } catch (error) {
        console.error('Error accessing webcam:', error);
        alert('Please allow access to camera and microphone');
    }
}

// Recording controls
function toggleRecording() {
    if (!isRecording) {
        audioChunks = [];
        mediaRecorder.start();
        isRecording = true;
        document.getElementById('recordBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('submitBtn').disabled = true;
        document.body.classList.add('is-recording');
        const indicator = document.getElementById('recordingIndicator');
        if (indicator) indicator.style.display = 'inline-block';
    }
}

function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    document.getElementById('recordBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('submitBtn').disabled = false;
    document.body.classList.remove('is-recording');
    const indicator = document.getElementById('recordingIndicator');
    if (indicator) indicator.style.display = 'none';
    // Send final chunk to server for a final transcription pass
    if (audioChunks.length > 0) {
        const finalBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.onload = () => {
            try {
                const dataUrl = reader.result;
                const base64 = dataUrl.split(',')[1];
                socket.emit('audio_chunk', {
                    interview_id: currentInterviewId,
                    audio_chunk: base64,
                    final: true
                });
            } catch (e) {
                console.error('Failed to send final audio chunk', e);
            }
        };
        reader.readAsDataURL(finalBlob);
    }
}

// Submit response
async function submitResponse() {
    if (audioChunks.length === 0) {
        alert('Please record your response first');
        return;
    }

    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('interview_id', currentInterviewId);
    formData.append('audio', audioBlob, 'response.webm');

    try {
        document.getElementById('submitBtn').disabled = true;
        const response = await fetch(`${API_URL}/submit-response`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errText = 'Error processing response. Please try again.';
            try {
                const errJson = await response.json();
                errText = errJson.error || errText;
            } catch (e) {}
            alert(errText);
            document.getElementById('submitBtn').disabled = false;
            return;
        }

        const data = await response.json();

        // Update transcription
        const transText = data.immediate_feedback?.text || data.immediate_feedback?.transcript || 'Processing...';
        document.getElementById('transcriptionText').textContent = transText;

        // Update feedback
        document.getElementById('confidenceScore').textContent = 
            ((data.immediate_feedback.sentiment?.confidence ?? 0) * 100).toFixed(0) + '%';
        document.getElementById('fillerCount').textContent = 
            data.immediate_feedback.filler_words?.length || 0;
        document.getElementById('sentimentType').textContent = 
            data.immediate_feedback.sentiment?.sentiment_type || 'Neutral';

        questionCount++;
        if (questionCount <= 5) {
            setTimeout(() => {
                document.getElementById('questionNumber').textContent = questionCount;
                document.getElementById('questionText').textContent = data.next_question;
                document.getElementById('transcriptionText').textContent = '';
                document.getElementById('recordBtn').disabled = false;
                document.getElementById('submitBtn').disabled = false;
                audioChunks = [];
            }, 1500);
        } else {
            endInterview();
        }
    } catch (error) {
        console.error('Error submitting response:', error);
        alert('Error processing response. Please try again.');
        document.getElementById('submitBtn').disabled = false;
    }
}

// End interview and show results
async function endInterview() {
    try {
        const response = await fetch(`${API_URL}/end-interview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ interview_id: currentInterviewId })
        });

        const data = await response.json();
        displayResults(data.report);
        showScreen('resultsScreen');
    } catch (error) {
        console.error('Error ending interview:', error);
        alert('Error generating report. Please try again.');
    }
}

// Display results
function displayResults(report) {
    // Scores
    document.getElementById('overallScore').textContent = 
        report.summary.overall_score.toFixed(1) + '/100';
    document.getElementById('communicationScore').textContent = 
        report.summary.communication_score.toFixed(1) + '/100';
    document.getElementById('technicalScore').textContent = 
        report.summary.technical_score.toFixed(1) + '/100';

    // Strengths
    const strengthsList = document.getElementById('strengthsList');
    strengthsList.innerHTML = report.detailed_feedback.strengths
        .map(s => `<li>${s}</li>`)
        .join('');

    // Improvements
    const improvementsList = document.getElementById('improvementsList');
    improvementsList.innerHTML = report.detailed_feedback.areas_for_improvement
        .map(i => `<li>${i}</li>`)
        .join('');

    // Recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = report.recommendations
        .map(r => `<li>${r}</li>`)
        .join('');

    // Response details
    const responseDetails = document.getElementById('responseDetails');
    responseDetails.innerHTML = report.response_details
        .map((r, idx) => `
            <div class="response-detail">
                <h4>Response ${idx + 1}</h4>
                <p><strong>Your Answer:</strong> ${r.text}</p>
                <p><strong>Relevance Score:</strong> ${r.analysis.relevance_score || 'N/A'}/100</p>
                <p><strong>Sentiment:</strong> ${r.sentiment.sentiment_type || 'Neutral'}</p>
                <p><strong>Key Strengths:</strong> ${(r.analysis.key_strengths || []).join(', ') || 'N/A'}</p>
            </div>
        `)
        .join('');
}

// Start new interview
function startNewInterview() {
    document.getElementById('jobRole').value = 'Software Engineer';
    document.getElementById('interviewName').value = '';
    document.getElementById('transcriptionText').textContent = '';
    document.getElementById('recordBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    audioChunks = [];
    questionCount = 0;
    showScreen('setupScreen');
}

// Download report
function downloadReport() {
    const report = {
        interviewId: currentInterviewId,
        overallScore: document.getElementById('overallScore').textContent,
        communicationScore: document.getElementById('communicationScore').textContent,
        technicalScore: document.getElementById('technicalScore').textContent,
        strengths: Array.from(document.querySelectorAll('#strengthsList li')).map(li => li.textContent),
        improvements: Array.from(document.querySelectorAll('#improvementsList li')).map(li => li.textContent),
        timestamp: new Date().toISOString()
    };

    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(report, null, 2)));
    element.setAttribute('download', `interview_report_${currentInterviewId}.json`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Interview Simulator loaded');
    showScreen('setupScreen');
});
