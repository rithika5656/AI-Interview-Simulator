
const apiClient = window.HireVisionApiClient || {};
const API_URL = apiClient.baseUrl || `${window.location.protocol}//${window.location.hostname}:5000/api`;
const socket = window.io && window.location.protocol !== 'file:'
    ? io(apiClient.socketUrl || `${window.location.protocol}//${window.location.hostname}:5000`)
    : null;

const state = {
    currentInterviewId: null,
    questionCount: 0,
    mediaRecorder: null,
    audioChunks: [],
    stream: null,
    moduleSets: {},
    charts: {},
    resumeData: null,
    profileMode: localStorage.getItem('hirevisionProfileMode') || 'student',
};

document.addEventListener('DOMContentLoaded', () => {
    bindNavigation();
    bindThemeToggle();
    bindProfileModeToggle();
    bindModuleForms();
    bindLegacyInterview();
    bindTechnicalInterview();
    hydrateSelectors();
    restoreTheme();
    syncProfileMode();
    showView('dashboardView');
    checkBackendStatus();
    loadAllPanels();
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

function bindProfileModeToggle() {
    const studentBtn = $('#studentModeBtn');
    const adminBtn = $('#adminModeBtn');

    if (studentBtn) {
        studentBtn.addEventListener('click', () => setProfileMode('student'));
    }

    if (adminBtn) {
        adminBtn.addEventListener('click', () => setProfileMode('admin'));
    }
}

function setProfileMode(mode) {
    state.profileMode = mode === 'admin' ? 'admin' : 'student';
    localStorage.setItem('hirevisionProfileMode', state.profileMode);
    syncProfileMode();
    loadProfile();
    loadAdmin();
    updateStatusLabel();
}

function syncProfileMode() {
    document.body.dataset.profileMode = state.profileMode;
    $all('[data-profile-mode]').forEach((button) => {
        button.classList.toggle('active', button.dataset.profileMode === state.profileMode);
    });
    $all('[data-role="admin"]').forEach((element) => {
        element.classList.toggle('hidden-role', state.profileMode !== 'admin');
    });
    $all('[data-role="student"]').forEach((element) => {
        element.classList.toggle('hidden-role', state.profileMode !== 'student');
    });
    const adminView = $('#adminView');
    if (adminView) adminView.classList.toggle('hidden-role', state.profileMode !== 'admin');
    const activeView = $('.view.active');
    if (activeView && activeView.classList.contains('hidden-role')) {
        showView('dashboardView');
    }
    updateStatusLabel();
}

function updateStatusLabel() {
    const status = $('.status-pill');
    if (status) {
        status.textContent = state.profileMode === 'admin' ? 'Admin Profile' : 'Student Profile';
    }
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

    const codingBtn = $('#codingReviewBtn');
    if (codingBtn) codingBtn.addEventListener('click', reviewCoding);

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
    if (window.HireVisionApiClient?.get) {
        return window.HireVisionApiClient.get(path);
    }

    const response = await fetch(`${API_URL}${path}`);
    const body = await safeJson(response);
    if (!response.ok) throw new Error(body.error || 'Request failed');
    return body;
}

async function apiPost(path, payload, options = {}) {
    if (window.HireVisionApiClient?.post) {
        if (options.body instanceof FormData) {
            return window.HireVisionApiClient.post(path, options.body, { headers: options.headers });
        }
        return window.HireVisionApiClient.post(path, payload, { headers: options.headers });
    }

    const response = await fetch(`${API_URL}${path}`, {
        method: 'POST',
        headers: options.headers || { 'Content-Type': 'application/json' },
        body: options.body || JSON.stringify(payload || {}),
    });
    const body = await safeJson(response);
    if (!response.ok) throw new Error(body.error || 'Request failed');
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
    return `<div class="state-card">${message}</div>`;
}

function errorCard(title, message) {
    return `<div class="state-card error"><strong>${title}</strong><p>${message}</p></div>`;
}

async function loadAllPanels() {
    await Promise.allSettled([loadDashboard(), loadAnalytics(), loadCoach(), loadAdmin(), loadProfile(), loadCompanyTrack($('#companySelect')?.value || 'TCS')]);
}

async function checkBackendStatus() {
    const alertBox = $('#systemAlert');
    if (!alertBox || !window.HireVisionApiClient?.healthCheck) return;

    const result = await window.HireVisionApiClient.healthCheck();
    if (result.ok) {
        alertBox.hidden = true;
        alertBox.textContent = '';
        return;
    }

    const message = result.error?.message || result.payload?.error || 'Backend API is unreachable.';
    alertBox.textContent = `Demo mode active: ${message}`;
    alertBox.hidden = false;
}

async function loadDashboard() {
    const panel = $('#dashboardMetrics');
    if (!panel) return;
    panel.innerHTML = loadingCard('Loading dashboard metrics...');
    try {
        const data = await apiGet('/dashboard/overview?user_id=demo_student');
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
                labels: ['Resume', 'Aptitude', 'Coding', 'Interview', 'GD'],
                datasets: [{ label: 'Scores', data: [metrics.resume_score || 0, metrics.aptitude_progress || 0, metrics.coding_progress || 0, metrics.interview_score || 0, metrics.gd_score || 0], backgroundColor: ['#60a5fa', '#38bdf8', '#4ade80', '#f59e0b', '#f472b6'] }],
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
    formData.append('user_id', 'demo_student');

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
        const data = await apiPost(`/${moduleKey}/submit`, { questions, answers });
        const reviewedQuestions = questions.map((question, index) => {
            const selectedIndex = answers[index];
            const correctIndex = Number.isInteger(question.correct_index) ? question.correct_index : null;
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
    if (result) result.innerHTML = loadingCard('Reviewing code...');
    try {
        const data = await apiPost('/coding/review', {
            language: $('#codingLanguage')?.value || 'Python',
            code: $('#codingEditor')?.value || '',
            problem_statement: $('#codingProblem')?.value || '',
        });
        if (result) {
            result.innerHTML = `
                <div class="analysis-card success">
                    <h3>Code Review</h3>
                    <p><strong>Score:</strong> ${Number(data.score || 0).toFixed(1)}%</p>
                    <p><strong>Runtime:</strong> ${data.runtime}</p>
                    <p><strong>Complexity:</strong> ${data.complexity_analysis}</p>
                    <p><strong>AI Review:</strong> ${data.ai_review}</p>
                    <ul>${(data.hidden_tests || []).map((test) => `<li>${test.input} - ${test.status}</li>`).join('')}</ul>
                </div>
            `;
        }
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
            user_id: 'demo_student',
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
                <div class="grid grid-2">
                    <div class="panel-subcard"><h4>Aptitude</h4>${(data.modules?.aptitude || []).map((q) => `<p>${q.question}</p>`).join('')}</div>
                    <div class="panel-subcard"><h4>Technical</h4>${(data.modules?.technical || []).map((q) => `<p>${q.question}</p>`).join('')}</div>
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
        const data = await apiGet('/analytics/summary?user_id=demo_student');
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
        const data = await apiGet('/career-coach?user_id=demo_student');
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

async function loadAdmin() {
    const result = $('#adminResult');
    if (!result || state.profileMode !== 'admin') return;
    try {
        const data = await apiGet('/admin/overview');
        result.innerHTML = `
            <div class="analysis-card success">
                <h3>Admin Overview</h3>
                <div class="admin-grid">${Object.entries(data.totals || {}).map(([key, value]) => `<div class="admin-tile"><span>${humanize(key)}</span><strong>${value}</strong></div>`).join('')}</div>
                <p><strong>Weak Areas:</strong> ${(data.weak_areas || []).join(', ')}</p>
            </div>
            <div class="analysis-card">
                <h3>Faculty Controls</h3>
                <p>Monitor student scores, weak areas, interview attempts, leaderboard position, and module completion from one place.</p>
            </div>
        `;
    } catch (error) {
        result.innerHTML = errorCard('Admin overview failed', error.message);
    }
}

async function loadProfile() {
    const result = $('#profileResult');
    if (!result) return;
    try {
        if (state.profileMode === 'admin') {
            const data = await apiGet('/admin/overview');
            result.innerHTML = `
                <div class="analysis-card success">
                    <h3>Admin Profile</h3>
                    <p><strong>Total Users:</strong> ${data.totals?.users || 0}</p>
                    <p><strong>Interviews:</strong> ${data.totals?.interviews || 0}</p>
                    <p><strong>Coding Tests:</strong> ${data.totals?.coding_tests || 0}</p>
                    <p><strong>Aptitude Tests:</strong> ${data.totals?.aptitude_tests || 0}</p>
                    <p><strong>GD Sessions:</strong> ${data.totals?.gd_sessions || 0}</p>
                    <p><strong>Weak Areas:</strong> ${(data.weak_areas || []).join(', ')}</p>
                </div>
                <div class="analysis-card">
                    <h3>Admin Summary</h3>
                    <p>Track student performance, reports, weak topics, and interview attempts from the faculty dashboard.</p>
                </div>
            `;
            return;
        }

        const data = await apiGet('/profile/demo_student');
        result.innerHTML = `
            <div class="analysis-card success">
                <h3>Student Profile</h3>
                <p><strong>Placement Score:</strong> ${Number(data.placement_score || 0).toFixed(1)}%</p>
                <p><strong>Resume:</strong> ${data.resume?.filename || 'Not uploaded yet'}</p>
                <p><strong>Interview History:</strong> ${data.interview_history?.length || 0}</p>
                <p><strong>Coding History:</strong> ${data.coding_history?.length || 0}</p>
                <p><strong>Aptitude History:</strong> ${data.aptitude_history?.length || 0}</p>
                <p><strong>GD History:</strong> ${data.gd_history?.length || 0}</p>
            </div>
            <div class="analysis-card">
                <h3>Student Progress</h3>
                <p>This profile is focused on exam readiness, practice history, and placement score.</p>
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
        });
        $('#questionText').textContent = data.question;
        $('#questionNumber').textContent = state.questionCount;
        showView('legacyInterviewView');
        await startWebcam();
    } catch (error) {
        showToast(`Error starting interview: ${error.message}`);
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
            if (!socket) return;

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
        showToast('Please allow access to camera and microphone');
    }
}

function toggleRecording() {
    if (!state.mediaRecorder) return;

    if (state.mediaRecorder.state === 'inactive') {
        state.mediaRecorder.start(500);
        const recordBtn = $('#recordBtn');
        const stopBtn = $('#stopBtn');
        const indicator = $('#recordingIndicator');
        if (recordBtn) recordBtn.disabled = true;
        if (stopBtn) stopBtn.disabled = false;
        if (indicator) indicator.style.display = 'block';
    }
}

function stopRecording() {
    if (!state.mediaRecorder || state.mediaRecorder.state !== 'recording') return;

    state.mediaRecorder.stop();
    const recordBtn = $('#recordBtn');
    const stopBtn = $('#stopBtn');
    const submitBtn = $('#submitBtn');
    const indicator = $('#recordingIndicator');
    if (recordBtn) recordBtn.disabled = false;
    if (stopBtn) stopBtn.disabled = true;
    if (submitBtn) submitBtn.disabled = false;
    if (indicator) indicator.style.display = 'none';
}

async function submitResponse() {
    if (state.audioChunks.length === 0) {
        showToast('Please record your response first');
        return;
    }

    try {
        const blob = new Blob(state.audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('interview_id', state.currentInterviewId);
        formData.append('audio', blob, 'response.webm');
        formData.append('text', $('#transcriptionText')?.textContent || '');

        const data = await apiPost('/submit-response', formData);
        $('#transcriptionText').textContent = data.immediate_feedback.text;
        $('#confidenceScore').textContent = data.immediate_feedback.sentiment.confidence.toFixed(2);
        $('#fillerCount').textContent = data.immediate_feedback.filler_words.length;
        $('#sentimentType').textContent = data.immediate_feedback.sentiment.sentiment_type;

        state.questionCount++;

        if (state.questionCount <= 5) {
            $('#questionNumber').textContent = state.questionCount;
            $('#questionText').textContent = data.next_question;
        } else {
            await endInterview();
        }

        state.audioChunks = [];
        const submitBtn = $('#submitBtn');
        if (submitBtn) submitBtn.disabled = true;
    } catch (error) {
        showToast(`Error submitting response: ${error.message}`);
    }
}

async function endInterview() {
    try {
        const data = await apiPost('/end-interview', { interview_id: state.currentInterviewId });
        displayResults(data.report);
        showView('legacyResultsView');
    } catch (error) {
        showToast(`Error generating report: ${error.message}`);
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
    $('#transcriptionText').textContent = '';
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

async function generateTechnicalInterviewQuestion() {
    const result = $('#technicalInterviewResult');
    if (result) result.innerHTML = loadingCard('Generating adaptive question...');

    try {
        const resumeSkills = ($('#technicalInterviewSkills')?.value || '').split(',').map((item) => item.trim()).filter(Boolean);
        const data = await apiPost('/technical-interview/question', {
            technology: $('#technicalInterviewTechnology')?.value || 'Python',
            resume_skills: resumeSkills,
            job_description: $('#technicalInterviewJobDescription')?.value || '',
        });
        if (result) {
            result.innerHTML = `
                <div class="analysis-card success">
                    <h3>${data.technology} Interview Question</h3>
                    <p>${data.question}</p>
                    <p><strong>Hint:</strong> ${data.follow_up_hint}</p>
                </div>
            `;
        }
    } catch (error) {
        if (result) result.innerHTML = errorCard('Technical interview failed', error.message);
    }
}

function humanize(value) {
    return value.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase());
}

function formatDate(timestamp) {
    return timestamp ? new Date(timestamp).toLocaleString() : 'Recent';
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
