const apiClient = window.HireVisionApiClient || {};
const customApiUrl = localStorage.getItem('hirevisionCustomApiUrl');
const customSocketUrl = localStorage.getItem('hirevisionCustomSocketUrl');

const API_URL = customApiUrl || apiClient.baseUrl || (window.HireVisionConfig?.apiBaseUrl) || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? `${window.location.protocol}//${window.location.hostname}:5000/api`
    : '');

const socket = window.io && window.location.protocol !== 'file:' && (customSocketUrl || apiClient.socketUrl || window.HireVisionConfig?.socketUrl || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? io(customSocketUrl || apiClient.socketUrl || (window.HireVisionConfig?.socketUrl) || `${window.location.protocol}//${window.location.hostname}:5000`)
    : null;

const state = {
    userId: localStorage.getItem('hirevisionUserId') || 'demo_student',
    currentInterviewId: null,
    questionCount: 0,
    mediaRecorder: null,
    audioChunks: [],
    stream: null,
    moduleSets: {},
    charts: {},
    resumeData: null,
    profileMode: localStorage.getItem('hirevisionProfileMode') || 'student',
    editor: null, // Monaco editor instance
    currentTechQuestion: '',
    currentTechTechnology: 'Python'
};

document.addEventListener('DOMContentLoaded', () => {
    bindNavigation();
    bindThemeToggle();
    bindModuleForms();
    bindLegacyInterview();
    bindTechnicalInterview();
    bindAuthEvents();
    bindProfileEdit();
    hydrateSelectors();
    restoreTheme();
    updateActiveUserProfileUI();
    showView('dashboardView');
    // Show "not connected" placeholders immediately
    showOfflinePlaceholders();
    // Check backend health - panels load only after successful connection
    checkBackendHealth();
    setTimeout(initMonacoEditor, 500); // Load Monaco Editor
});

function $(selector, root = document) {
    return root.querySelector(selector);
}

function $all(selector, root = document) {
    return Array.from(root.querySelectorAll(selector));
}

function showView(viewId) {
    $all('.view').forEach((view) => view.classList.remove('active'));
    const target = $(`#${viewId}`);
    if (target) target.classList.add('active');
    $all('[data-view]').forEach((button) => button.classList.toggle('active', button.dataset.view === viewId));
    
    // Trigger editor layout recalculation when Coding Assessment tab is clicked
    if (viewId === 'codingView' && state.editor) {
        setTimeout(() => state.editor.layout(), 100);
    }
}

function bindNavigation() {
    $all('[data-view]').forEach((button) => {
        button.addEventListener('click', () => showView(button.dataset.view));
    });
}

function bindThemeToggle() {
    const toggle = $('#themeToggle');
    if (!toggle) return;
    toggle.addEventListener('click', () => {
        const next = document.body.classList.contains('theme-light') ? 'dark' : 'light';
        applyTheme(next);
    });
}

function applyTheme(theme) {
    document.body.classList.toggle('theme-dark', theme === 'dark');
    document.body.classList.toggle('theme-light', theme === 'light');
    localStorage.setItem('hirevisionTheme', theme);
}

function restoreTheme() {
    applyTheme(localStorage.getItem('hirevisionTheme') || 'dark');
}

function bindModuleForms() {
    const resumeForm = $('#resumeForm');
    if (resumeForm) resumeForm.addEventListener('submit', handleResumeUpload);

    ['aptitude', 'logical', 'verbal', 'technical'].forEach((moduleKey) => {
        const generateBtn = $(`[data-generate-module="${moduleKey}"]`);
        const submitBtn = $(`[data-submit-module="${moduleKey}"]`);
        if (generateBtn) generateBtn.addEventListener('click', () => generateModule(moduleKey));
        if (submitBtn) submitBtn.addEventListener('click', () => submitModule(moduleKey));
    });

    const gdBtn = $('#gdSimulateBtn');
    if (gdBtn) gdBtn.addEventListener('click', simulateGD);

    const codingRunBtn = $('#codingRunBtn');
    if (codingRunBtn) codingRunBtn.addEventListener('click', runCoding);

    const codingReviewBtn = $('#codingReviewBtn');
    if (codingReviewBtn) codingReviewBtn.addEventListener('click', reviewCoding);

    const companySelect = $('#companySelect');
    if (companySelect) companySelect.addEventListener('change', () => loadCompanyTrack(companySelect.value));
}

function bindLegacyInterview() {
    const startBtn = $('#startLegacyInterviewBtn');
    const recordBtn = $('#recordBtn');
    const stopBtn = $('#stopBtn');
    const submitBtn = $('#submitBtn');
    const newBtn = $('#newInterviewBtn');
    const downloadBtn = $('#downloadReportBtn');

    if (startBtn) startBtn.addEventListener('click', startInterview);
    if (recordBtn) recordBtn.addEventListener('click', toggleRecording);
    if (stopBtn) stopBtn.addEventListener('click', stopRecording);
    if (submitBtn) submitBtn.addEventListener('click', submitResponse);
    if (newBtn) newBtn.addEventListener('click', startNewInterview);
    if (downloadBtn) downloadBtn.addEventListener('click', downloadReport);

    if (socket) {
        socket.on('transcription_update', (data) => {
            const transcription = $('#transcriptionText');
            if (transcription) transcription.textContent = data.text || '';
        });
    }
}

function bindTechnicalInterview() {
    const generateBtn = $('#technicalInterviewGenerate');
    if (generateBtn) generateBtn.addEventListener('click', generateTechnicalInterviewQuestion);
    
    const submitBtn = $('#techSubmitBtn');
    if (submitBtn) submitBtn.addEventListener('click', submitTechnicalAnswer);
}

function hydrateSelectors() {
    const topics = {
        aptitude: ['Quantitative Aptitude', 'Number System', 'Time & Work', 'Time & Distance', 'Probability', 'Permutation & Combination', 'Profit & Loss', 'Percentage', 'Ratio', 'Simplification'],
        logical: ['Blood Relation', 'Seating Arrangement', 'Coding Decoding', 'Puzzle', 'Syllogism', 'Direction Sense', 'Statement & Assumption'],
        verbal: ['Synonyms', 'Antonyms', 'Reading Comprehension', 'Grammar', 'Error Spotting', 'Sentence Correction'],
        technical: ['Java', 'Python', 'C++', 'DBMS', 'OOPS', 'Operating System', 'Computer Networks', 'SQL', 'HTML', 'CSS', 'JavaScript', 'React', 'AI/ML'],
    };

    Object.entries(topics).forEach(([moduleKey, list]) => {
        const select = $(`#${moduleKey}Topic`);
        if (select) select.innerHTML = list.map((item) => `<option value="${item}">${item}</option>`).join('');
    });

    const companySelect = $('#companySelect');
    if (companySelect) {
        companySelect.innerHTML = ['TCS', 'Infosys', 'Cognizant', 'Wipro', 'Zoho', 'Accenture', 'Capgemini', 'Amazon', 'Microsoft', 'Google']
            .map((company) => `<option value="${company}">${company}</option>`)
            .join('');
    }
}

async function apiGet(path) {
    if (!API_URL) throw new Error('Backend not connected. Enter your backend URL in the banner above.');
    if (window.HireVisionApiClient?.get) {
        return window.HireVisionApiClient.get(path);
    }
    const response = await fetch(`${API_URL}${path}`);
    const body = await safeJson(response);
    if (!response.ok) throw new Error(body.error || `Server error ${response.status}`);
    return body;
}

async function apiPost(path, payload, options = {}) {
    if (!API_URL) throw new Error('Backend not connected. Enter your backend URL in the banner above.');
    if (window.HireVisionApiClient?.post) {
        if (options.body instanceof FormData) {
            return window.HireVisionApiClient.post(path, options.body, { headers: options.headers });
        }
        return window.HireVisionApiClient.post(path, payload, { headers: options.headers });
    }
    const isFormData = payload instanceof FormData || options.body instanceof FormData;
    const response = await fetch(`${API_URL}${path}`, {
        method: 'POST',
        headers: options.headers || (isFormData ? undefined : { 'Content-Type': 'application/json' }),
        body: options.body || (isFormData ? payload : JSON.stringify(payload || {})),
    });
    const body = await safeJson(response);
    if (!response.ok) throw new Error(body.error || `Server error ${response.status}`);
    return body;
}

async function safeJson(response) {
    try {
        return await response.json();
    } catch {
        return {};
    }
}

function loadingCard(message) {
    return `<div class="state-card"><i class="fa-solid fa-circle-notch fa-spin"></i> &nbsp; ${message}</div>`;
}

function errorCard(title, message) {
    return `<div class="state-card error"><strong>${title}</strong><p>${message}</p></div>`;
}

function showOfflinePlaceholders() {
    const notConnectedHtml = `<div class="state-card" style="text-align:center; padding: 24px;">
        <i class="fa-solid fa-plug-circle-xmark" style="font-size:2rem; color:var(--muted); margin-bottom:10px;"></i>
        <p style="color:var(--muted); margin:0;">Waiting for backend connection...</p>
    </div>`;
    const panels = ['#dashboardMetrics', '#analyticsResult', '#coachResult', '#profileResult', '#companyTrackResult'];
    panels.forEach(sel => {
        const el = $(sel);
        if (el) el.innerHTML = notConnectedHtml;
    });
}

async function loadAllPanels() {
    await Promise.allSettled([loadDashboard(), loadAnalytics(), loadCoach(), loadProfile(), loadCompanyTrack($('#companySelect')?.value || 'TCS')]);
}

async function loadDashboard() {
    const panel = $('#dashboardMetrics');
    if (!panel) return;
    panel.innerHTML = loadingCard('Loading dashboard metrics...');
    try {
        const data = await apiGet(`/dashboard/overview?user_id=${state.userId}`);
        renderDashboard(data);
    } catch (error) {
        panel.innerHTML = errorCard('Dashboard failed', error.message);
    }
}

function renderDashboard(data) {
    const metrics = data.metrics || {};
    const cards = [
        ['Placement Readiness Score', metrics.placement_readiness_score || 0],
        ['Resume Score', metrics.resume_score || 0],
        ['Aptitude Progress', metrics.aptitude_progress || 0],
        ['Coding Progress', metrics.coding_progress || 0],
        ['Interview Score', metrics.interview_score || 0],
        ['GD Score', metrics.gd_score || 0],
        ['Technical Score', metrics.technical_score || 0],
        ['Logical Score', metrics.logical_score || 0],
        ['Verbal Score', metrics.verbal_score || 0],
    ].map(([label, value]) => `
        <article class="metric-card">
            <p>${label}</p>
            <strong>${Number(value).toFixed(1)}%</strong>
            <div class="progress-track"><span style="width:${Math.min(Number(value), 100)}%"></span></div>
        </article>
    `).join('');

    const metricsPanel = $('#dashboardMetrics');
    if (metricsPanel) metricsPanel.innerHTML = cards;

    const goalsPanel = $('#dailyGoals');
    if (goalsPanel) goalsPanel.innerHTML = (data.daily_goals || []).map((goal) => `<li>${goal}</li>`).join('');

    const activityPanel = $('#recentActivities');
    if (activityPanel) {
        activityPanel.innerHTML = (data.recent_activities || []).map((activity) => `
            <div class="activity-row"><span>${activity.type}</span><strong>${activity.title}</strong><small>${formatDate(activity.timestamp)}</small></div>
        `).join('') || '<p class="muted">No recent activity yet.</p>';
    }

    const upcomingPanel = $('#upcomingTests');
    if (upcomingPanel) {
        upcomingPanel.innerHTML = (data.upcoming_mock_tests || []).map((test) => `
            <div class="upcoming-row"><div><strong>${test.title}</strong><p>${test.module}</p></div><span>${test.time}</span></div>
        `).join('');
    }

    const coachPanel = $('#dashboardCoach');
    if (coachPanel && data.career_coach) {
        coachPanel.innerHTML = `
            <div class="analysis-card"><h4>Strengths</h4><p>${(data.career_coach.strengths || []).join(', ')}</p></div>
            <div class="analysis-card"><h4>Weaknesses</h4><p>${(data.career_coach.weaknesses || []).join(', ')}</p></div>
            <div class="analysis-card"><h4>Placement Readiness</h4><p>${Number(data.career_coach.placement_readiness || metrics.placement_readiness_score || 0).toFixed(1)}%</p></div>
        `;
    }

    renderDashboardCharts(metrics);
}

function renderDashboardCharts(metrics) {
    if (!window.Chart) return;
    destroyCharts(['readinessChart', 'accuracyChart']);

    const readiness = $('#readinessChart');
    if (readiness) {
        state.charts.readinessChart = new Chart(readiness, {
            type: 'doughnut',
            data: {
                labels: ['Ready', 'Remaining'],
                datasets: [{ data: [metrics.placement_readiness_score || 0, Math.max(100 - (metrics.placement_readiness_score || 0), 0)], backgroundColor: ['#4ade80', '#233042'], borderWidth: 0 }],
            },
            options: { plugins: { legend: { labels: { color: '#cbd5e1' } } } },
        });
    }

    const accuracy = $('#accuracyChart');
    if (accuracy) {
        state.charts.accuracyChart = new Chart(accuracy, {
            type: 'bar',
            data: {
                labels: ['Resume', 'Aptitude', 'Coding', 'Interview', 'GD', 'Technical', 'Logical', 'Verbal'],
                datasets: [{ label: 'Scores', data: [metrics.resume_score || 0, metrics.aptitude_progress || 0, metrics.coding_progress || 0, metrics.interview_score || 0, metrics.gd_score || 0, metrics.technical_score || 0, metrics.logical_score || 0, metrics.verbal_score || 0], backgroundColor: ['#60a5fa', '#38bdf8', '#4ade80', '#f59e0b', '#f472b6', '#8b5cf6', '#ec4899', '#06b6d4'] }],
            },
            options: chartOptions(),
        });
    }
}

function chartOptions() {
    return {
        responsive: true,
        plugins: { legend: { labels: { color: '#cbd5e1' } } },
        scales: {
            x: { ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(148,163,184,0.15)' } },
            y: { beginAtZero: true, max: 100, ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(148,163,184,0.15)' } },
        },
    };
}

async function handleResumeUpload(event) {
    event.preventDefault();
    const output = $('#resumeResult');
    const formData = new FormData();
    formData.append('user_id', state.userId);

    const fileInput = $('#resumeFile');
    const textInput = $('#resumeText');
    if (fileInput?.files?.length) {
        formData.append('resume', fileInput.files[0]);
    } else if (textInput?.value.trim()) {
        formData.append('resume_text', textInput.value.trim());
    } else {
        if (output) output.innerHTML = errorCard('Resume required', 'Upload a file or paste resume text.');
        return;
    }

    if (output) output.innerHTML = loadingCard('Analyzing resume...');
    try {
        const data = await apiPost('/resume/analyze', null, { body: formData });
        state.resumeData = data;
        if (output) {
            output.innerHTML = `
                <div class="analysis-card success">
                    <h3>ATS Score: ${Number(data.ats_score || 0).toFixed(1)}%</h3>
                    <p><strong>Skills:</strong> ${(data.skills || []).join(', ') || 'Not detected'}</p>
                    <p><strong>Projects:</strong> ${(data.projects || []).join(' | ') || 'Not detected'}</p>
                    <p><strong>Education:</strong> ${(data.education || []).join(', ') || 'Not detected'}</p>
                    <p><strong>Missing Keywords:</strong> ${(data.missing_keywords || []).join(', ') || 'None'}</p>
                    <ul>${(data.suggestions || []).map((suggestion) => `<li>${suggestion}</li>`).join('')}</ul>
                </div>
            `;
        }
        loadDashboard();
        loadProfile();
    } catch (error) {
        if (output) output.innerHTML = errorCard('Resume analysis error', error.message);
    }
}

async function generateModule(moduleKey) {
    const topic = $(`#${moduleKey}Topic`)?.value || moduleKey;
    const difficulty = $(`#${moduleKey}Difficulty`)?.value || 'medium';
    const container = $(`#${moduleKey}Questions`);
    const result = $(`#${moduleKey}Result`);

    if (container) container.innerHTML = loadingCard('Generating questions...');
    if (result) result.innerHTML = '';

    try {
        const data = await apiPost(`/${moduleKey}/generate`, { topic, difficulty, count: 5 });
        state.moduleSets[moduleKey] = data.questions || [];
        if (container) container.innerHTML = renderQuestionSet(moduleKey, data.questions || []);
    } catch (error) {
        if (container) container.innerHTML = errorCard('Question generation failed', error.message);
    }
}

function renderQuestionSet(moduleKey, questions) {
    return questions.map((question, index) => `
        <article class="question-card">
            <header><span>Question ${index + 1}</span><small>${question.difficulty || 'medium'}</small></header>
            <p>${question.question}</p>
            <div class="option-list">
                ${(question.options || []).map((option, optionIndex) => `
                    <label><input type="radio" name="${moduleKey}-answer-${index}" value="${optionIndex}"><span>${option}</span></label>
                `).join('')}
            </div>
            <details><summary>AI Explanation</summary><p>${question.explanation || 'Explanation will appear after submission.'}</p></details>
        </article>
    `).join('');
}

async function submitModule(moduleKey) {
    const questions = state.moduleSets[moduleKey] || [];
    const result = $(`#${moduleKey}Result`);
    const answers = questions.map((_, index) => {
        const checked = $(`input[name="${moduleKey}-answer-${index}"]:checked`);
        return checked ? Number(checked.value) : null;
    });

    if (!questions.length) {
        if (result) result.innerHTML = errorCard('No questions to submit', 'Generate a set first.');
        return;
    }

    if (result) result.innerHTML = loadingCard('Submitting answers...');
    try {
        const data = await apiPost(`/${moduleKey}/submit`, { user_id: state.userId, questions, answers, topic: questions[0]?.topic || 'General', difficulty: questions[0]?.difficulty || 'medium' });
        const reviewedQuestions = questions.map((question, index) => {
            const selectedIndex = answers[index];
            const correctIndex = Number.isInteger(question.correct_index) ? question.correct_index : (Number.isInteger(question.answer_index) ? question.answer_index : null);
            return {
                question: question.question,
                selectedAnswer: selectedIndex !== null && selectedIndex !== undefined ? question.options?.[selectedIndex] : 'Not answered',
                correctAnswer: correctIndex !== null ? question.options?.[correctIndex] : 'N/A',
                isCorrect: selectedIndex !== null && selectedIndex !== undefined && correctIndex !== null
                    ? Number(selectedIndex) === Number(correctIndex)
                    : false,
                explanation: data.items?.[index]?.explanation || question.explanation || '',
            };
        });
        if (result) {
            result.innerHTML = `
                <div class="analysis-card success">
                    <h3>Score: ${Number(data.score || 0).toFixed(1)}%</h3>
                    <p>Correct Answers: ${data.correct_count}/${data.total_count}</p>
                    ${reviewedQuestions.map((item) => `
                        <div class="analysis-card ${item.isCorrect ? 'success' : 'error'}">
                            <strong>${item.question}</strong>
                            <p><strong>Your answer:</strong> ${item.selectedAnswer}</p>
                            <p><strong>Correct answer:</strong> ${item.correctAnswer}</p>
                            <p>${item.explanation}</p>
                        </div>
                    `).join('')}
                </div>
            `;
            result.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        loadAnalytics();
        loadDashboard();
    } catch (error) {
        if (result) result.innerHTML = errorCard('Submission failed', error.message);
    }
}

async function reviewCoding() {
    const result = $('#codingResult');
    if (result) result.innerHTML = loadingCard('Submitting code for deep AI review...');
    try {
        const codeText = state.editor ? state.editor.getValue() : ($('#codingEditor')?.value || '');
        const data = await apiPost('/coding/review', {
            user_id: state.userId,
            language: $('#codingLanguage')?.value || 'Python',
            code: codeText,
            problem_statement: $('#codingProblem')?.value || '',
        });
        if (result) {
            result.innerHTML = `
                <div class="analysis-card success">
                    <h3>AI Code Review Report</h3>
                    <p><strong>Evaluation Score:</strong> ${Number(data.score || 0).toFixed(1)}%</p>
                    <p><strong>Complexity:</strong> ${data.complexity_analysis || 'N/A'}</p>
                    <p><strong>Est. Runtime:</strong> ${data.runtime || 'N/A'}</p>
                    <p><strong>AI Critique:</strong> ${data.ai_review}</p>
                    
                    <h4>Dry Run Test Cases</h4>
                    <ul>${(data.hidden_tests || []).map((test) => `
                        <li>
                            <strong>Input:</strong> ${test.input}<br>
                            <strong>Expected:</strong> ${test.expected} | <strong>Actual:</strong> ${test.actual || 'N/A'}<br>
                            <strong>Status:</strong> <span class="status-text ${test.status === 'passed' ? 'success' : 'error'}">${test.status.toUpperCase()}</span>
                        </li>
                    `).join('')}</ul>
                </div>
            `;
        }
        loadProfile();
        loadDashboard();
    } catch (error) {
        if (result) result.innerHTML = errorCard('Code review failed', error.message);
    }
}

async function simulateGD() {
    const result = $('#gdResult');
    if (result) result.innerHTML = loadingCard('Analyzing group discussion...');
    try {
        const data = await apiPost('/gd/simulate', {
            topic: $('#gdTopic')?.value || 'AI in education',
            transcript: $('#gdTranscript')?.value || '',
            user_id: state.userId,
        });
        if (result) {
            result.innerHTML = `
                <div class="analysis-card success">
                    <h3>GD Feedback</h3>
                    <div class="score-pill-grid">
                        <span>Communication ${data.scores.communication}</span>
                        <span>Confidence ${data.scores.confidence}</span>
                        <span>Vocabulary ${data.scores.vocabulary}</span>
                        <span>Grammar ${data.scores.grammar}</span>
                        <span>Relevance ${data.scores.relevance}</span>
                        <span>Fluency ${data.scores.fluency}</span>
                    </div>
                    <ul>${(data.feedback || []).map((item) => `<li>${item}</li>`).join('')}</ul>
                </div>
            `;
        }
    } catch (error) {
        if (result) result.innerHTML = errorCard('GD analysis failed', error.message);
    }
}

async function loadCompanyTrack(company) {
    const result = $('#companyTrackResult');
    if (!result) return;
    result.innerHTML = loadingCard(`Loading ${company} track...`);
    try {
        const data = await apiGet(`/company-track/${encodeURIComponent(company)}`);
        result.innerHTML = `
            <div class="analysis-card success">
                <h3>${data.company} Preparation Track</h3>
                <p><strong>Difficulty:</strong> ${data.difficulty}</p>
                <p><strong>Focus Areas:</strong> ${(data.focus_areas || []).join(', ')}</p>
                <p>${data.interview_focus}</p>

                <h4>Interview Process Rounds</h4>
                <ul class="bullet-list">
                    ${(data.interview_patterns || []).map(round => `<li>${round}</li>`).join('')}
                </ul>

                <div class="grid grid-2" style="margin-top: 15px;">
                    <div class="panel-subcard">
                        <h4>Aptitude Questions</h4>
                        ${(data.modules?.aptitude || []).map((q) => `<p>• ${q.question}</p>`).join('')}
                    </div>
                    <div class="panel-subcard">
                        <h4>Technical Core</h4>
                        ${(data.modules?.technical || []).map((q) => `<p>• ${q.question}</p>`).join('')}
                    </div>
                </div>

                <div class="grid grid-2" style="margin-top: 15px;">
                    <div class="panel-subcard">
                        <h4>Company Specific Coding</h4>
                        ${(data.coding_problems || []).map((p) => `<p><strong>${p.title}:</strong> ${p.desc}</p>`).join('')}
                    </div>
                    <div class="panel-subcard">
                        <h4>Sample HR Questions</h4>
                        ${(data.hr_questions || []).map((q) => `<p>• ${q}</p>`).join('')}
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        result.innerHTML = errorCard('Company track failed', error.message);
    }
}

async function loadAnalytics() {
    const result = $('#analyticsResult');
    if (!result) return;
    try {
        const data = await apiGet(`/analytics/summary?user_id=${state.userId}`);
        result.innerHTML = `
            <div class="grid grid-2">
                <div class="panel-subcard"><h4>Daily Progress</h4><p>${(data.daily_progress || []).join(' → ')}</p></div>
                <div class="panel-subcard"><h4>Weekly Progress</h4><p>${(data.weekly_progress || []).join(' → ')}</p></div>
                <div class="panel-subcard"><h4>Monthly Progress</h4><p>${(data.monthly_progress || []).join(' → ')}</p></div>
                <div class="panel-subcard"><h4>Interview Trend</h4><p>${(data.interview_trend || []).join(' → ')}</p></div>
            </div>
        `;
    } catch (error) {
        result.innerHTML = errorCard('Analytics failed', error.message);
    }
}

async function loadCoach() {
    const result = $('#coachResult');
    if (!result) return;
    try {
        const data = await apiGet(`/career-coach?user_id=${state.userId}`);
        result.innerHTML = `
            <div class="analysis-card success">
                <h3>AI Career Coach</h3>
                <p><strong>Placement Readiness:</strong> ${Number(data.placement_readiness || 0).toFixed(1)}%</p>
                <p><strong>Strengths:</strong> ${(data.strengths || []).join(', ')}</p>
                <p><strong>Weaknesses:</strong> ${(data.weaknesses || []).join(', ')}</p>
                <p><strong>Recommended Topics:</strong> ${(data.recommended_topics || []).join(', ')}</p>
                <ol>${(data.learning_plan || []).map((item) => `<li>${item}</li>`).join('')}</ol>
            </div>
        `;
    } catch (error) {
        result.innerHTML = errorCard('Career coach failed', error.message);
    }
}

async function loadProfile() {
    const result = $('#profileResult');
    if (!result) return;
    try {
        const data = await apiGet(`/profile/${state.userId}`);
        
        // Populate edit profile fields
        const profileName = $('#profileName');
        const profileEmail = $('#profileEmail');
        const profileTargetRole = $('#profileTargetRole');
        const profileSkills = $('#profileSkills');
        const profileAchievements = $('#profileAchievements');
        if (profileName) profileName.value = data.name || '';
        if (profileEmail) profileEmail.value = data.email || '';
        if (profileTargetRole) profileTargetRole.value = data.target_role || '';
        if (profileSkills) profileSkills.value = (data.skills || []).join(', ');
        if (profileAchievements) profileAchievements.value = (data.achievements || []).join(', ');

        result.innerHTML = `
            <div class="analysis-card success">
                <h3>Student Profile: ${data.name || 'Practice Student'}</h3>
                <p><strong>Email:</strong> ${data.email || 'N/A'}</p>
                <p><strong>Target Role:</strong> ${data.target_role || 'N/A'}</p>
                <p><strong>Skills:</strong> ${(data.skills || []).join(', ') || 'None added yet'}</p>
                <p><strong>Achievements:</strong> ${(data.achievements || []).join(', ') || 'None added yet'}</p>
                <p><strong>Placement Score:</strong> ${Number(data.placement_score || 0).toFixed(1)}%</p>
                <p><strong>Resume:</strong> ${data.resume?.filename || 'Not uploaded yet'}</p>
                <p><strong>Interview Practice Sessions:</strong> ${data.interview_history?.length || 0}</p>
                <p><strong>Coding Practice Submissions:</strong> ${data.coding_history?.length || 0}</p>
                <p><strong>Aptitude Tests:</strong> ${data.aptitude_history?.length || 0}</p>
                <p><strong>Logical Tests:</strong> ${data.logical_history?.length || 0}</p>
                <p><strong>Verbal Tests:</strong> ${data.verbal_history?.length || 0}</p>
                <p><strong>Technical MCQ Tests:</strong> ${data.technical_mcq_history?.length || 0}</p>
                <p><strong>GD History:</strong> ${data.gd_history?.length || 0}</p>
            </div>
            <div class="analysis-card">
                <h3>Student Progress Report</h3>
                <p>This profile tracks overall assessment history, placement readiness, and custom achievements to build a resume recommendation.</p>
            </div>
        `;
    } catch (error) {
        result.innerHTML = errorCard('Profile failed', error.message);
    }
}

function destroyCharts(ids) {
    ids.forEach((id) => {
        if (state.charts[id]) {
            state.charts[id].destroy();
            delete state.charts[id];
        }
    });
}

function formatDate(timestamp) {
    return timestamp ? new Date(timestamp).toLocaleString() : 'Recent';
}

function humanize(value) {
    return value.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase());
}

async function startInterview() {
    const jobRole = $('#jobRole')?.value || 'Software Engineer';
    const interviewName = $('#interviewName')?.value || 'Demo Student';

    state.currentInterviewId = `interview_${Date.now()}`;
    state.questionCount = 1;

    try {
        const data = await apiPost('/start-interview', {
            interview_id: state.currentInterviewId,
            job_role: jobRole,
            interview_name: interviewName,
            user_id: state.userId
        });
        $('#questionText').textContent = data.question;
        $('#questionNumber').textContent = state.questionCount;
        showView('legacyInterviewView');
        await startWebcam();
    } catch (error) {
        showToast(`Error starting interview: ${error.message}`, 'error');
    }
}

async function startWebcam() {
    try {
        state.stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 640 }, height: { ideal: 480 } }, audio: true });
        const video = $('#videoElement');
        if (video) video.srcObject = state.stream;

        const audioStream = new MediaStream(state.stream.getAudioTracks());
        state.mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
        state.mediaRecorder.ondataavailable = (event) => {
            if (!event.data || event.data.size === 0) return;
            state.audioChunks.push(event.data);
            if (!socket || socket.disconnected) return;

            const reader = new FileReader();
            reader.onload = () => {
                const base64 = String(reader.result).split(',')[1];
                socket.emit('audio_chunk', { interview_id: state.currentInterviewId, audio_chunk: base64, final: false });
            };
            reader.readAsDataURL(event.data);
        };

        const recordBtn = $('#recordBtn');
        const stopBtn = $('#stopBtn');
        if (recordBtn) recordBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
    } catch (error) {
        showToast('Camera and microphone enabled. Press Start to practice speaking.', 'info');
        // Fallback: Enable typing response if camera/microphone access throws error
        const recordBtn = $('#recordBtn');
        if (recordBtn) recordBtn.disabled = true;
        
        // Turn transcription box into editable textarea
        const transcription = $('#transcriptionText');
        if (transcription && transcription.tagName !== 'TEXTAREA') {
            const textarea = document.createElement('textarea');
            textarea.id = 'transcriptionText';
            textarea.className = 'editable-transcription';
            textarea.placeholder = 'Type your practicing answer here since camera/microphone is unavailable...';
            transcription.replaceWith(textarea);
        }
        
        const submitBtn = $('#submitBtn');
        if (submitBtn) submitBtn.disabled = false;
    }
}

function toggleRecording() {
    const recordBtn = $('#recordBtn');
    const stopBtn = $('#stopBtn');
    const indicator = $('#recordingIndicator');
    
    if (state.mediaRecorder && state.mediaRecorder.state === 'inactive') {
        state.mediaRecorder.start(500);
        if (recordBtn) recordBtn.disabled = true;
        if (stopBtn) stopBtn.disabled = false;
        if (indicator) indicator.style.display = 'block';
    }
    
    // Start local SpeechRecognition fallback
    startHrSpeech();
}

function stopRecording() {
    const recordBtn = $('#recordBtn');
    const stopBtn = $('#stopBtn');
    const submitBtn = $('#submitBtn');
    const indicator = $('#recordingIndicator');

    if (state.mediaRecorder && state.mediaRecorder.state === 'recording') {
        state.mediaRecorder.stop();
    }
    
    if (recordBtn) recordBtn.disabled = false;
    if (stopBtn) stopBtn.disabled = true;
    if (submitBtn) submitBtn.disabled = false;
    if (indicator) indicator.style.display = 'none';
    
    // Stop local SpeechRecognition
    stopHrSpeech();
}

async function submitResponse() {
    const transcription = $('#transcriptionText');
    const answerText = transcription ? (transcription.value || transcription.textContent || '') : '';
    
    if (!answerText.trim() && state.audioChunks.length === 0) {
        showToast('Please record or type your response first', 'warning');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('interview_id', state.currentInterviewId);
        
        if (state.audioChunks.length > 0) {
            const blob = new Blob(state.audioChunks, { type: 'audio/webm' });
            formData.append('audio', blob, 'response.webm');
        }
        
        formData.append('text', answerText);

        const data = await apiPost('/submit-response', formData);
        
        // Show immediate feedback
        const transcriptionTextElement = $('#transcriptionText');
        if (transcriptionTextElement) {
            if (transcriptionTextElement.tagName === 'TEXTAREA') {
                transcriptionTextElement.value = data.immediate_feedback.text;
            } else {
                transcriptionTextElement.textContent = data.immediate_feedback.text;
            }
        }
        
        $('#confidenceScore').textContent = data.immediate_feedback.sentiment.confidence.toFixed(2);
        $('#fillerCount').textContent = data.immediate_feedback.filler_words.length;
        $('#sentimentType').textContent = data.immediate_feedback.sentiment.sentiment_type;

        state.questionCount++;

        if (state.questionCount <= 5) {
            $('#questionNumber').textContent = state.questionCount;
            $('#questionText').textContent = data.next_question;
            
            // Clear transcription text for next question
            if (transcriptionTextElement) {
                if (transcriptionTextElement.tagName === 'TEXTAREA') {
                    transcriptionTextElement.value = '';
                } else {
                    transcriptionTextElement.textContent = '';
                }
            }
        } else {
            await endInterview();
        }

        state.audioChunks = [];
        const submitBtn = $('#submitBtn');
        if (submitBtn) submitBtn.disabled = true;
    } catch (error) {
        showToast(`Error submitting response: ${error.message}`, 'error');
    }
}

async function endInterview() {
    try {
        const data = await apiPost('/end-interview', { interview_id: state.currentInterviewId });
        displayResults(data.report);
        showView('legacyResultsView');
        
        // Stop stream if practicing
        if (state.stream) {
            state.stream.getTracks().forEach(track => track.stop());
            state.stream = null;
        }
    } catch (error) {
        showToast(`Error generating report: ${error.message}`, 'error');
    }
}

function displayResults(report) {
    $('#overallScore').textContent = `${report.summary.overall_score.toFixed(1)}/100`;
    $('#communicationScore').textContent = `${report.summary.communication_score.toFixed(1)}/100`;
    $('#technicalScore').textContent = `${report.summary.technical_score.toFixed(1)}/100`;
    $('#strengthsList').innerHTML = (report.detailed_feedback.strengths || []).map((item) => `<li>${item}</li>`).join('');
    $('#improvementsList').innerHTML = (report.detailed_feedback.areas_for_improvement || []).map((item) => `<li>${item}</li>`).join('');
    $('#recommendationsList').innerHTML = (report.recommendations || []).map((item) => `<li>${item}</li>`).join('');
    $('#responseDetails').innerHTML = (report.response_details || []).map((entry, index) => `
        <div class="response-detail">
            <h4>Response ${index + 1}</h4>
            <p><strong>Your Answer:</strong> ${entry.text}</p>
            <p><strong>Relevance Score:</strong> ${entry.analysis?.relevance_score || 'N/A'}/100</p>
            <p><strong>Sentiment:</strong> ${entry.sentiment?.sentiment_type || 'Neutral'}</p>
            <p><strong>Key Strengths:</strong> ${(entry.analysis?.key_strengths || []).join(', ') || 'N/A'}</p>
        </div>
    `).join('');
}

function startNewInterview() {
    $('#jobRole').value = 'Software Engineer';
    $('#interviewName').value = '';
    const transcription = $('#transcriptionText');
    if (transcription) {
        if (transcription.tagName === 'TEXTAREA') {
            transcription.value = '';
        } else {
            transcription.textContent = '';
        }
    }
    $('#recordBtn').disabled = false;
    $('#stopBtn').disabled = true;
    state.audioChunks = [];
    state.questionCount = 0;
    showView('dashboardView');
}

function downloadReport() {
    const report = {
        interviewId: state.currentInterviewId,
        overallScore: $('#overallScore').textContent,
        communicationScore: $('#communicationScore').textContent,
        technicalScore: $('#technicalScore').textContent,
        strengths: Array.from($('#strengthsList').querySelectorAll('li')).map((li) => li.textContent),
        improvements: Array.from($('#improvementsList').querySelectorAll('li')).map((li) => li.textContent),
        timestamp: new Date().toISOString(),
    };

    const link = document.createElement('a');
    link.href = `data:text/plain;charset=utf-8,${encodeURIComponent(JSON.stringify(report, null, 2))}`;
    link.download = `hirevision_report_${state.currentInterviewId || 'session'}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Interactive Technical Interview
async function generateTechnicalInterviewQuestion() {
    const result = $('#techResultDisplay');
    const questionBox = $('#techQuestionBox');
    if (result) result.innerHTML = loadingCard('Generating adaptive technical question...');
    if (questionBox) questionBox.style.display = 'none';

    try {
        const resumeSkills = ($('#technicalInterviewSkills')?.value || '').split(',').map((item) => item.trim()).filter(Boolean);
        const data = await apiPost('/technical-interview/question', {
            technology: $('#technicalInterviewTechnology')?.value || 'Python',
            resume_skills: resumeSkills,
            job_description: $('#technicalInterviewJobDescription')?.value || '',
        });
        
        state.currentTechQuestion = data.question;
        state.currentTechTechnology = data.technology;
        
        $('#techQuestionText').textContent = data.question;
        $('#techQuestionHint').textContent = data.follow_up_hint;
        
        if (questionBox) questionBox.style.display = 'block';
        if (result) result.innerHTML = '';
        
        // Reset answer field
        if ($('#techResponseText')) $('#techResponseText').value = '';
        initTechSpeech();
    } catch (error) {
        if (result) result.innerHTML = errorCard('Technical question failed', error.message);
    }
}

let techSpeechRecognition = null;
function initTechSpeech() {
    const recordBtn = $('#techRecordBtn');
    const stopBtn = $('#techStopBtn');
    const indicator = $('#techRecordingIndicator');
    const textarea = $('#techResponseText');
    
    if (!recordBtn) return;
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        recordBtn.style.display = 'none';
        stopBtn.style.display = 'none';
        return;
    }
    
    if (!techSpeechRecognition) {
        techSpeechRecognition = new SpeechRecognition();
        techSpeechRecognition.continuous = true;
        techSpeechRecognition.interimResults = true;
        techSpeechRecognition.lang = 'en-US';
        
        techSpeechRecognition.onstart = () => {
            if (indicator) indicator.style.display = 'inline-block';
            recordBtn.disabled = true;
            stopBtn.disabled = false;
        };
        
        techSpeechRecognition.onresult = (event) => {
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
            if (textarea && finalTranscript) {
                textarea.value += (textarea.value ? ' ' : '') + finalTranscript;
            }
        };
        
        techSpeechRecognition.onend = () => {
            if (indicator) indicator.style.display = 'none';
            recordBtn.disabled = false;
            stopBtn.disabled = true;
        };
        
        techSpeechRecognition.onerror = (event) => {
            showToast(`Speech recognition warning: ${event.error}`, 'warning');
        };
    }
    
    recordBtn.onclick = () => {
        try {
            techSpeechRecognition.start();
        } catch (e) {
            techSpeechRecognition.stop();
        }
    };
    
    stopBtn.onclick = () => {
        techSpeechRecognition.stop();
    };
}

async function submitTechnicalAnswer() {
    const result = $('#techResultDisplay');
    const responseText = $('#techResponseText')?.value || '';
    if (!responseText.trim()) {
        showToast('Please type or speak your answer before submitting', 'warning');
        return;
    }

    if (result) result.innerHTML = loadingCard('Submitting answer for AI evaluation...');
    try {
        const data = await apiPost('/technical-interview/submit', {
            user_id: state.userId,
            technology: state.currentTechTechnology || 'Python',
            question: state.currentTechQuestion || '',
            response: responseText
        });
        
        if (result) {
            result.innerHTML = `
                <div class="analysis-card success">
                    <h3>AI Technical Assessment Report</h3>
                    <p><strong>Clarity Score:</strong> ${Number(data.clarity_score || 0).toFixed(1)}/100</p>
                    <p><strong>Technical Depth Score:</strong> ${Number(data.depth_score || 0).toFixed(1)}/100</p>
                    <p><strong>Overall Score:</strong> ${Number(data.score || 0).toFixed(1)}/100</p>
                    <p><strong>AI Critique:</strong> ${data.feedback}</p>
                    <p><strong>Key Strengths:</strong> ${(data.key_strengths || []).join(', ')}</p>
                    <p><strong>Areas for Improvement:</strong> ${(data.improvement_areas || []).join(', ')}</p>
                </div>
            `;
            const questionBox = $('#techQuestionBox');
            if (questionBox) questionBox.style.display = 'none';
        }
        loadProfile();
        loadDashboard();
    } catch (error) {
        if (result) result.innerHTML = errorCard('Evaluation failed', error.message);
    }
}

// Local Speech Recognition (Web Speech API) for HR Interview
let hrSpeechRecognition = null;
function startHrSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const transcription = $('#transcriptionText');
    if (!transcription) return;

    if (!hrSpeechRecognition) {
        hrSpeechRecognition = new SpeechRecognition();
        hrSpeechRecognition.continuous = true;
        hrSpeechRecognition.interimResults = true;
        hrSpeechRecognition.lang = 'en-US';

        hrSpeechRecognition.onresult = (event) => {
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
            if (finalTranscript) {
                if (transcription.tagName === 'TEXTAREA') {
                    transcription.value += (transcription.value ? ' ' : '') + finalTranscript;
                } else {
                    transcription.textContent += (transcription.textContent ? ' ' : '') + finalTranscript;
                }
            }
        };

        hrSpeechRecognition.onerror = (e) => {
            console.log('HR Speech recognition error:', e.error);
        };
    }

    try {
        hrSpeechRecognition.start();
    } catch (e) {
        hrSpeechRecognition.stop();
    }
}

function stopHrSpeech() {
    if (hrSpeechRecognition) {
        hrSpeechRecognition.stop();
    }
}

// Monaco Editor Integration
function initMonacoEditor() {
    if (typeof require === 'undefined') return;
    require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' } });
    require(['vs/editor/editor.main'], function () {
        const container = document.getElementById('codingEditorContainer');
        if (!container) return;
        state.editor = monaco.editor.create(container, {
            value: 'def two_sum(nums, target):\n    return []',
            language: 'python',
            theme: 'vs-dark',
            automaticLayout: true,
            fontSize: 14,
            minimap: { enabled: false }
        });
        
        // Listen to language selector changes
        const codingLangSelect = $('#codingLanguage');
        if (codingLangSelect) {
            codingLangSelect.addEventListener('change', (e) => {
                if (!state.editor) return;
                const lang = e.target.value;
                const model = state.editor.getModel();
                let code = '';
                if (lang === 'Python') {
                    code = 'def two_sum(nums, target):\n    return []';
                } else if (lang === 'Java') {
                    code = 'class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        return new int[0];\n    }\n}';
                } else if (lang === 'C++') {
                    code = 'class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        return {};\n    }\n};';
                } else if (lang === 'JavaScript') {
                    code = 'function twoSum(nums, target) {\n    return [];\n}';
                }
                state.editor.setValue(code);
                const monacoLang = lang === 'C++' ? 'cpp' : lang.toLowerCase();
                monaco.editor.setModelLanguage(model, monacoLang);
            });
        }
    });
}

async function runCoding() {
    const result = $('#codingResult');
    if (result) result.innerHTML = loadingCard('Compiling and running sample test cases...');
    try {
        const codeText = state.editor ? state.editor.getValue() : '';
        const data = await apiPost('/coding/review', {
            user_id: state.userId,
            language: $('#codingLanguage')?.value || 'Python',
            code: codeText,
            problem_statement: $('#codingProblem')?.value || '',
        });
        if (result) {
            const passes = (data.hidden_tests || []).filter(t => t.status === 'passed').length;
            const total = (data.hidden_tests || []).length;
            result.innerHTML = `
                <div class="analysis-card success">
                    <h3>Run Outputs & Hidden Tests</h3>
                    <p><strong>Status:</strong> ${passes === total ? 'All Tests Passed' : 'Some Tests Failed'}</p>
                    <p><strong>Sample Cases:</strong> ${passes}/${total} passed</p>
                    <p><strong>Estimated Complexity:</strong> ${data.complexity_analysis || 'N/A'}</p>
                    <p><strong>Estimated Runtime:</strong> ${data.runtime || 'N/A'}</p>
                    
                    <h4>Execution Log</h4>
                    <ul>${(data.hidden_tests || []).map((test) => `
                        <li>
                            <strong>Case:</strong> ${test.input}<br>
                            <strong>Expected:</strong> ${test.expected} | <strong>Status:</strong> <span class="status-text ${test.status === 'passed' ? 'success' : 'error'}">${test.status.toUpperCase()}</span>
                        </li>
                    `).join('')}</ul>
                </div>
            `;
        }
    } catch (error) {
        if (result) result.innerHTML = errorCard('Run execution failed', error.message);
    }
}

// User Authentication Modal UI and Switch Profile
function bindAuthEvents() {
    const modal = $('#authModal');
    const switchBtn = $('#switchUserBtn');
    const closeBtn = $('#closeAuthBtn');
    const form = $('#authForm');
    
    if (switchBtn) {
        switchBtn.addEventListener('click', () => {
            $('#authName').value = localStorage.getItem('hirevisionUserName') || '';
            $('#authEmail').value = localStorage.getItem('hirevisionUserEmail') || '';
            $('#authRole').value = localStorage.getItem('hirevisionUserRole') || 'student';
            $('#authTargetRole').value = localStorage.getItem('hirevisionUserTargetRole') || 'Software Engineer';
            modal.classList.add('active');
        });
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = $('#authName').value.trim();
            const email = $('#authEmail').value.trim();
            const role = $('#authRole').value;
            const targetRole = $('#authTargetRole').value.trim();
            const userId = 'user_' + email.replace(/[^a-zA-Z0-9]/g, '_');
            
            try {
                // Save user on backend
                await apiPost('/profile/save', {
                    user_id: userId,
                    name,
                    email,
                    role,
                    target_role: targetRole,
                    skills: [],
                    achievements: []
                });
                
                // Save locally
                localStorage.setItem('hirevisionUserId', userId);
                localStorage.setItem('hirevisionUserName', name);
                localStorage.setItem('hirevisionUserEmail', email);
                localStorage.setItem('hirevisionUserRole', role);
                localStorage.setItem('hirevisionUserTargetRole', targetRole);
                
                state.userId = userId;
                updateActiveUserProfileUI();
                modal.classList.remove('active');
                showToast('Profile switched successfully!', 'success');
                
                // Reload dashboard/profile datasets
                loadAllPanels();
            } catch (error) {
                showToast(`Failed to register profile: ${error.message}`, 'error');
            }
        });
    }
}

function updateActiveUserProfileUI() {
    const name = localStorage.getItem('hirevisionUserName') || 'Demo Student';
    const role = localStorage.getItem('hirevisionUserRole') || 'student';
    if ($('#activeUserName')) $('#activeUserName').textContent = name;
    if ($('#activeUserRole')) $('#activeUserRole').textContent = role;
}

// Edit Profile Form Submit
function bindProfileEdit() {
    const form = $('#profileEditForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = $('#profileName').value.trim();
        const email = $('#profileEmail').value.trim();
        const targetRole = $('#profileTargetRole').value.trim();
        const skills = $('#profileSkills').value.split(',').map(s => s.trim()).filter(Boolean);
        const achievements = $('#profileAchievements').value.split(',').map(s => s.trim()).filter(Boolean);
        
        try {
            await apiPost('/profile/save', {
                user_id: state.userId,
                name,
                email,
                role: localStorage.getItem('hirevisionUserRole') || 'student',
                target_role: targetRole,
                skills,
                achievements
            });
            
            localStorage.setItem('hirevisionUserName', name);
            localStorage.setItem('hirevisionUserEmail', email);
            localStorage.setItem('hirevisionUserTargetRole', targetRole);
            
            updateActiveUserProfileUI();
            showToast('Student profile updated successfully!', 'success');
            loadProfile();
            loadDashboard();
        } catch (error) {
            showToast(`Profile update failed: ${error.message}`, 'error');
        }
    });
}

// Backend Health Check Wakeup Retry
let healthCheckInterval = null;
let connectionAttempts = 0;
let panelsLoaded = false;

function showBackendConnectForm(reason) {
    const badge = $('#backendStatus');
    const alert = $('#systemAlert');
    if (badge) {
        badge.className = 'backend-status status-offline';
        badge.querySelector('.status-text').textContent = 'Not Connected';
    }
    if (!alert) return;
    alert.hidden = false;
    const currentUrl = API_URL ? API_URL.replace(/\/api\/?$/, '') : '';
    alert.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:12px; width:100%">
            <div style="display:flex; align-items:flex-start; gap:15px;">
                <i class="fa-solid fa-triangle-exclamation" style="font-size:1.5rem; color:var(--warning); flex-shrink:0; margin-top:2px;"></i>
                <div>
                    <strong style="font-size:1rem;">Connect Your Backend</strong>
                    <p style="margin: 6px 0 0 0; font-size: 0.88rem; color: var(--muted);">${reason}</p>
                    <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--muted);">Deploy your backend to <a href="https://render.com" target="_blank" style="color:var(--primary)">Render.com</a> (free), then paste the URL below:</p>
                </div>
            </div>
            <div style="display:flex; gap:10px; width:100%; flex-wrap:wrap;">
                <input type="text" id="customBackendInput" value="${currentUrl}" placeholder="https://your-backend.onrender.com" 
                    style="flex:1; min-width:200px; padding:10px 14px; border-radius:8px; border:1px solid var(--line); background:var(--bg); color:var(--text); outline:none; font-size:0.95rem;">
                <button id="saveCustomBackendBtn" class="btn btn-primary" style="white-space:nowrap;">
                    <i class="fa-solid fa-plug"></i> Connect Backend
                </button>
            </div>
        </div>
    `;
    const saveBtn = $('#saveCustomBackendBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            let url = ($('#customBackendInput')?.value || '').trim();
            if (!url) { showToast('Please enter a valid URL', 'warning'); return; }
            url = url.replace(/\/+$/, '');
            const apiUrl = url.endsWith('/api') ? url : `${url}/api`;
            localStorage.setItem('hirevisionCustomApiUrl', apiUrl);
            localStorage.setItem('hirevisionCustomSocketUrl', url);
            showToast('Connecting to backend...', 'info');
            setTimeout(() => window.location.reload(), 800);
        });
    }
}

async function checkBackendHealth() {
    const badge = $('#backendStatus');
    const alert = $('#systemAlert');
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

    // Immediately show connection form if no URL configured on production
    if (!API_URL && !isLocal) {
        showBackendConnectForm('No backend URL was configured. The Vercel build did not receive the API_URL environment variable.');
        return;
    }

    if (connectionAttempts >= 5) {
        showBackendConnectForm(`Could not reach backend after 5 attempts. Current URL: ${API_URL.replace(/\/api\/?$/, '')}`);
        return;
    }

    try {
        const healthUrl = `${API_URL.replace(/\/api\/?$/, '')}/health`;
        const response = await fetch(healthUrl, { signal: AbortSignal.timeout(8000) });
        if (!response.ok) throw new Error(`Status ${response.status}`);

        // SUCCESS - Backend is online
        connectionAttempts = 0;
        if (badge) {
            badge.className = 'backend-status status-online';
            const isCustomUrl = !!localStorage.getItem('hirevisionCustomApiUrl');
            badge.querySelector('.status-text').innerHTML = isCustomUrl
                ? `Online <a href="#" id="resetBackendBtn" style="color:var(--primary);font-size:0.75rem;margin-left:6px;text-decoration:underline;">(Disconnect)</a>`
                : 'Online';
            const resetBtn = $('#resetBackendBtn');
            if (resetBtn) {
                resetBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    localStorage.removeItem('hirevisionCustomApiUrl');
                    localStorage.removeItem('hirevisionCustomSocketUrl');
                    setTimeout(() => window.location.reload(), 500);
                });
            }
        }
        if (alert) alert.hidden = true;
        clearInterval(healthCheckInterval);
        healthCheckInterval = null;

        // Load all panels now that backend is confirmed available
        if (!panelsLoaded) {
            panelsLoaded = true;
            loadAllPanels();
        }
    } catch (e) {
        connectionAttempts++;
        if (badge) {
            badge.className = 'backend-status status-connecting';
            badge.querySelector('.status-text').textContent = `Waking up... (${connectionAttempts}/5)`;
        }
        if (alert) {
            alert.hidden = false;
            alert.innerHTML = `
                <div style="display:flex; align-items:center; gap:15px; width:100%">
                    <i class="fa-solid fa-circle-notch fa-spin" style="font-size:1.4rem; color:var(--warning)"></i>
                    <div>
                        <strong>Backend is waking up (attempt ${connectionAttempts}/5)</strong>
                        <p style="margin:4px 0 0; font-size:0.85rem; color:var(--muted)">Free Render instances sleep when idle. This takes 30-60 seconds...</p>
                    </div>
                </div>
            `;
        }
        if (!healthCheckInterval) {
            healthCheckInterval = setInterval(checkBackendHealth, 5000);
        }
    }
}

function formatDate(timestamp) {
    return timestamp ? new Date(timestamp).toLocaleString() : 'Recent';
}

function humanize(value) {
    return value.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase());
}

window.startInterview = startInterview;
window.toggleRecording = toggleRecording;
window.stopRecording = stopRecording;
window.submitResponse = submitResponse;
window.endInterview = endInterview;
window.startNewInterview = startNewInterview;
window.downloadReport = downloadReport;

window.showToast = function(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-xmark';
    if (type === 'warning') iconClass = 'fa-triangle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <div class="toast-message">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        toast.addEventListener('animationend', () => {
            toast.remove();
        });
    }, 4000);
};
