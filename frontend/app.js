const API_URL = (typeof process !== 'undefined' && process.env.API_URL) ? process.env.API_URL : (window.HireVisionConfig?.apiBaseUrl || window.__APP_CONFIG__?.API_URL || 'https://ai-interview-simulator-12.onrender.com/api');

const SOCKET_URL = (typeof process !== 'undefined' && process.env.SOCKET_URL) ? process.env.SOCKET_URL : (window.HireVisionConfig?.socketUrl || window.__APP_CONFIG__?.SOCKET_URL || 'https://ai-interview-simulator-12.onrender.com');
const socket = window.io ? io(SOCKET_URL, { secure: true, reconnection: true, transports: ['websocket', 'polling'] }) : null;

const AUTH_STORAGE_KEY = 'hirevisionAuthToken';
const AUTH_SESSION_KEY = 'hirevisionAuthTokenSession';

const state = {
    userId: null,
    authUser: null,
    isAuthenticated: false,
    authChecked: false,
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
    currentTechTechnology: 'Python',
    currentCodingProblem: null
};

window.state = state;
let dashboardShellMounted = false;
let dashboardShellLoadPromise = null;

document.addEventListener('DOMContentLoaded', () => {
    const routerRoot = document.getElementById('routerRoot');
    if (routerRoot) routerRoot.hidden = false;
    
    bindAuthEvents();
    restoreTheme();
    prepareShellForAuth();
    // Show "not connected" placeholders immediately
    showOfflinePlaceholders();
    // Check backend health - panels load only after successful connection
    checkBackendHealth();
    bootstrapAuth();
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
    
    // Auto start/stop webcam preview based on active view
    if (viewId === 'legacyInterviewView') {
        startWebcam('videoElement');
    } else if (viewId === 'technicalInterviewView') {
        startWebcam('techVideoElement');
    } else if (viewId === 'gdView') {
        startWebcam('gdVideoElement');
    } else {
        stopWebcam();
    }

    // Trigger editor layout recalculation when Coding Assessment tab is clicked
    if (viewId === 'codingView') {
        if (state.editor) {
            setTimeout(() => state.editor.layout(), 100);
        }
        if (!state.currentCodingProblem) {
            setTimeout(loadCodingProblem, 200);
        }
    }
    
    // Lazy load panels
    triggerPanelLoad(viewId);
}

const viewRouteMap = {
    dashboardView: '/dashboard',
    resumeView: '/resume',
    aptitudeView: '/aptitude',
    logicalView: '/logical',
    verbalView: '/verbal',
    technicalMcqView: '/technical',
    codingView: '/coding',
    gdView: '/gd',
    legacyInterviewView: '/hr',
    technicalInterviewView: '/hr',
    analyticsView: '/analytics',
    coachView: '/career-coach',
    profileView: '/profile',
    companyView: '/company-wise',
};

function getStoredAuthToken() {
    return sessionStorage.getItem(AUTH_SESSION_KEY) || localStorage.getItem(AUTH_STORAGE_KEY);
}

function storeAuthToken(token, rememberMe) {
    sessionStorage.removeItem(AUTH_SESSION_KEY);
    localStorage.removeItem(AUTH_STORAGE_KEY);
    if (!token) return;
    if (rememberMe) {
        localStorage.setItem(AUTH_STORAGE_KEY, token);
    } else {
        sessionStorage.setItem(AUTH_SESSION_KEY, token);
    }
}

function clearAuthSession() {
    sessionStorage.removeItem(AUTH_SESSION_KEY);
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem('hirevisionUserId');
    localStorage.removeItem('hirevisionUserName');
    localStorage.removeItem('hirevisionUserEmail');
    localStorage.removeItem('hirevisionUserRole');
    localStorage.removeItem('hirevisionUserTargetRole');
}

function prepareShellForAuth() {
    const authScreen = $('#authScreen');
    const appShell = $('.app-shell');
    if (authScreen) authScreen.hidden = false;
    if (appShell) appShell.style.display = 'none';
    document.body.classList.add('auth-locked');
    document.body.style.overflow = 'hidden';
}

async function showAuthenticatedShell() {
    await mountDashboardShell();
    const authScreen = $('#authScreen');
    const appShell = $('.app-shell');
    if (authScreen) authScreen.hidden = true;
    if (appShell) appShell.style.display = 'grid';
    document.body.classList.remove('auth-locked');
    document.body.style.overflow = '';
}

function unmountDashboardShell() {
    const appShell = $('.app-shell');
    if (appShell) {
        appShell.remove();
    }
    dashboardShellMounted = false;
    dashboardShellLoadPromise = null;
}

async function mountDashboardShell() {
    if (dashboardShellMounted) return;

    if (!dashboardShellLoadPromise) {
        dashboardShellLoadPromise = fetch('dashboard-shell.html')
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Failed to load dashboard shell (${response.status})`);
                }
                return response.text();
            })
            .then((markup) => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(markup, 'text/html');
                const shell = doc.querySelector('.app-shell');
                if (!shell) {
                    throw new Error('Dashboard shell markup missing');
                }
                document.body.appendChild(shell);
                dashboardShellMounted = true;

                bindNavigation();
                bindThemeToggle();
                bindModuleForms();
                bindLegacyInterview();
                bindTechnicalInterview();
                bindProfileEdit();
                hydrateSelectors();
                updateActiveUserProfileUI();

                if (typeof initMonacoEditor === 'function') {
                    setTimeout(initMonacoEditor, 200);
                }
            })
            .catch((error) => {
                dashboardShellLoadPromise = null;
                throw error;
            });
    }

    await dashboardShellLoadPromise;

}

function applyAuthenticatedUser(user) {
    console.log('[AUTH] applyAuthenticatedUser() called with user:', user);
    if (!user) {
        console.warn('[AUTH] No user provided to applyAuthenticatedUser');
        return;
    }
    state.authUser = user;
    state.isAuthenticated = true;
    state.authChecked = true;  // CRITICAL: Mark auth check as complete
    state.userId = user.id;
    localStorage.setItem('hirevisionUserId', user.id || '');
    localStorage.setItem('hirevisionUserName', user.full_name || user.name || 'Student');
    localStorage.setItem('hirevisionUserEmail', user.email || '');
    localStorage.setItem('hirevisionUserRole', user.role || 'student');
    localStorage.setItem('hirevisionUserTargetRole', user.target_role || 'Software Engineer');
    updateActiveUserProfileUI();
    const interviewName = $('#interviewName');
    const resumeName = $('#resumeName');
    if (interviewName) interviewName.value = user.full_name || user.name || '';
    if (resumeName) resumeName.value = user.full_name || user.name || '';
    
    console.log('[AUTH] Triggering router update...');
    // Trigger React Router to re-render and detect auth state change
    if (window.triggerRouterUpdate) {
        console.log('[AUTH] Calling window.triggerRouterUpdate()');
        window.triggerRouterUpdate();
    } else {
        console.error('[AUTH] ERROR: window.triggerRouterUpdate not available!');
    }
}

async function bootstrapAuth() {
    const token = getStoredAuthToken();
    console.log('[AUTH] bootstrapAuth() - Token from storage:', token ? 'YES' : 'NO');
    
    if (!token) {
        console.log('[AUTH] No token found, marking as not authenticated');
        state.isAuthenticated = false;
        state.authChecked = true;
        prepareShellForAuth();
        if (window.triggerRouterUpdate) {
            console.log('[AUTH] Triggering router update (no token)');
            window.triggerRouterUpdate();
        }
        return;
    }

    try {
        console.log('[AUTH] Token found, validating with /auth/me');
        const response = await apiGet('/auth/me');
        console.log('[AUTH] /auth/me response:', response);
        applyAuthenticatedUser(response.user);
        // applyAuthenticatedUser sets authChecked and triggers router update
        if (window.HireVisionRouteNavigate) {
            console.log('[AUTH] Navigating to /dashboard from bootstrap');
            window.HireVisionRouteNavigate('/dashboard');
        }
    } catch (error) {
        console.error('[AUTH] Error during bootstrap auth:', error);
        clearAuthSession();
        state.authUser = null;
        state.isAuthenticated = false;
        state.userId = null;
        state.authChecked = true;
        prepareShellForAuth();
        showToast('Session expired. Please sign in again.', 'warning');
        if (window.triggerRouterUpdate) {
            console.log('[AUTH] Triggering router update (error)');
            window.triggerRouterUpdate();
        }
        if (window.HireVisionRouteNavigate) {
            console.log('[AUTH] Navigating to /login (error)');
            window.HireVisionRouteNavigate('/login');
        }
    }
}

const loadedPanels = new Set();
function triggerPanelLoad(viewId, force = false) {
    if (!force && loadedPanels.has(viewId)) return;
    
    if (viewId === 'dashboardView') loadDashboard();
    else if (viewId === 'analyticsView') loadAnalytics();
    else if (viewId === 'profileView') loadProfile();
    else if (viewId === 'companyView') loadCompanyTrack($('#companySelect')?.value || 'TCS');
    else if (viewId === 'coachView') loadCoach();
    
    loadedPanels.add(viewId);
}

function bindNavigation() {
    $all('[data-view]').forEach((button) => {
        button.addEventListener('click', () => {
            const route = viewRouteMap[button.dataset.view];
            if (route && window.HireVisionRouteNavigate && state.isAuthenticated) {
                window.HireVisionRouteNavigate(route);
                return;
            }
            showView(button.dataset.view);
        });
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

    const gdGenerateBtn = $('#gdGenerateTopicBtn');
    if (gdGenerateBtn) gdGenerateBtn.addEventListener('click', generateGdTopic);

    initGdSpeech();

    const codingRunBtn = $('#codingRunBtn');
    if (codingRunBtn) codingRunBtn.addEventListener('click', runCoding);

    const codingReviewBtn = $('#codingReviewBtn');
    if (codingReviewBtn) codingReviewBtn.addEventListener('click', reviewCoding);

    const codingProblemBtn = $('#codingProblemBtn');
    if (codingProblemBtn) codingProblemBtn.addEventListener('click', loadCodingProblem);

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
        return window.HireVisionApiClient.get(path, { headers: getAuthHeaders() });
    }
    const response = await fetch(`${API_URL}${path}`, { headers: getAuthHeaders() });
    const body = await safeJson(response);
    if (!response.ok) throw new Error(body.error || `Server error ${response.status}`);
    return body;
}

async function apiPost(path, payload, options = {}) {
    if (!API_URL) throw new Error('Backend not connected. Enter your backend URL in the banner above.');
    if (window.HireVisionApiClient?.post) {
        if (options.body instanceof FormData) {
            return window.HireVisionApiClient.post(path, options.body, { headers: { ...getAuthHeaders(), ...(options.headers || {}) } });
        }
        return window.HireVisionApiClient.post(path, payload, { headers: { ...getAuthHeaders(), ...(options.headers || {}) } });
    }
    const isFormData = payload instanceof FormData || options.body instanceof FormData;
    const headers = { ...getAuthHeaders(), ...(options.headers || {}) };
    const response = await fetch(`${API_URL}${path}`, {
        method: 'POST',
        headers: isFormData ? headers : { 'Content-Type': 'application/json', ...headers },
        body: options.body || (isFormData ? payload : JSON.stringify(payload || {})),
    });
    const body = await safeJson(response);
    if (!response.ok) throw new Error(body.error || `Server error ${response.status}`);
    return body;
}

function getAuthHeaders() {
    const token = getStoredAuthToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
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
    if (!state.isAuthenticated) return;
    loadedPanels.clear();
    const activeView = $('.view.active');
    if (activeView) {
        triggerPanelLoad(activeView.id, true);
    } else {
        triggerPanelLoad('dashboardView', true);
    }
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
    if (goalsPanel) {
        goalsPanel.innerHTML = (data.daily_goals && data.daily_goals.length > 0)
            ? data.daily_goals.map((goal) => `<li>${goal}</li>`).join('')
            : '<p class="muted" style="padding: 10px 0;">No interview completed</p>';
    }

    const activityPanel = $('#recentActivities');
    if (activityPanel) {
        activityPanel.innerHTML = (data.recent_activities && data.recent_activities.length > 0)
            ? data.recent_activities.map((activity) => `
                <div class="activity-row"><span>${activity.type}</span><strong>${activity.title}</strong><small>${formatDate(activity.timestamp)}</small></div>
            `).join('')
            : '<p class="muted" style="padding: 10px 0;">No activity yet</p>';
    }

    const upcomingPanel = $('#upcomingTests');
    if (upcomingPanel) {
        upcomingPanel.innerHTML = (data.upcoming_mock_tests && data.upcoming_mock_tests.length > 0)
            ? data.upcoming_mock_tests.map((test) => `
                <div class="upcoming-row"><div><strong>${test.title}</strong><p>${test.module}</p></div><span>${test.time}</span></div>
            `).join('')
            : '<p class="muted" style="padding: 10px 0;">No coding submissions</p>';
    }

    const coachPanel = $('#dashboardCoach');
    if (coachPanel && data.career_coach) {
        const isNewUser = (data.career_coach.strengths || []).includes("No activity yet");
        if (isNewUser) {
            coachPanel.innerHTML = `
                <div class="analysis-card" style="grid-column: span 3; text-align: center; padding: 20px;">
                    <h4>AI Coach Feedback</h4>
                    <p class="muted">No analytics available</p>
                </div>
            `;
        } else {
            coachPanel.innerHTML = `
                <div class="analysis-card"><h4>Strengths</h4><p>${(data.career_coach.strengths || []).join(', ')}</p></div>
                <div class="analysis-card"><h4>Weaknesses</h4><p>${(data.career_coach.weaknesses || []).join(', ')}</p></div>
                <div class="analysis-card"><h4>Placement Readiness</h4><p>${Number(data.career_coach.placement_readiness || metrics.placement_readiness_score || 0).toFixed(1)}%</p></div>
            `;
        }
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
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 15px; background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px;">
                        <p style="margin: 4px 0;"><strong>Name:</strong> ${data.name || 'Not detected'}</p>
                        <p style="margin: 4px 0;"><strong>Email:</strong> ${data.email || 'Not detected'}</p>
                        <p style="margin: 4px 0;"><strong>Phone:</strong> ${data.phone || 'Not detected'}</p>
                        <p style="margin: 4px 0;"><strong>Languages:</strong> ${(data.languages || []).join(', ') || 'Not detected'}</p>
                    </div>
                    <p><strong>Skills:</strong> ${(data.skills || []).join(', ') || 'Not detected'}</p>
                    <p><strong>Education:</strong> ${(data.education || []).join(' | ') || 'Not detected'}</p>
                    <p><strong>Experience:</strong> ${(data.experience || []).join(' | ') || 'Not detected'}</p>
                    <p><strong>Projects:</strong> ${(data.projects || []).join(' | ') || 'Not detected'}</p>
                    <p><strong>Certifications:</strong> ${(data.certifications || []).join(', ') || 'Not detected'}</p>
                    <p><strong>Achievements:</strong> ${(data.achievements || []).join(', ') || 'Not detected'}</p>
                    <p><strong>Internships:</strong> ${(data.internships || []).join(', ') || 'Not detected'}</p>
                    <p><strong>Missing Keywords:</strong> ${(data.missing_keywords || []).join(', ') || 'None'}</p>
                    <h4 style="margin-top: 15px; margin-bottom: 8px;">Suggestions & Recommendations:</h4>
                    <ul style="margin: 0; padding-left: 20px;">${(data.suggestions || []).map((suggestion) => `<li>${suggestion}</li>`).join('')}</ul>
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
            problem_statement: state.currentCodingProblem?.title || 'Two Sum',
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
        stopWebcam();
    } catch (error) {
        if (result) result.innerHTML = errorCard('GD analysis failed', error.message);
        stopWebcam();
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
                        <h4>Company HR Questions</h4>
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
                <div class="panel-subcard"><h4>Strong Topics</h4><p>${(data.strong_topics || []).join(', ')}</p></div>
                <div class="panel-subcard"><h4>Weak Topics</h4><p>${(data.weak_topics || []).join(', ')}</p></div>
                <div class="panel-subcard"><h4>Total Tests Taken</h4><p>${data.total_tests_taken || 0}</p></div>
                <div class="panel-subcard"><h4>Performance Trend</h4><p>${(data.weekly_progress || []).map(n => Number(n).toFixed(1) + '%').join(' → ')}</p></div>
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
        const profileCollege = $('#profileCollege');
        const profileDepartment = $('#profileDepartment');
        const profileYear = $('#profileYear');
        const profilePhone = $('#profilePhone');
        const profileTargetRole = $('#profileTargetRole');
        const profileSkills = $('#profileSkills');
        const profileAchievements = $('#profileAchievements');
        if (profileName) profileName.value = data.name || '';
        if (profileEmail) profileEmail.value = data.email || '';
        if (profileCollege) profileCollege.value = data.college || '';
        if (profileDepartment) profileDepartment.value = data.department || '';
        if (profileYear) profileYear.value = data.year || '';
        if (profilePhone) profilePhone.value = data.phone || '';
        if (profileTargetRole) profileTargetRole.value = data.target_role || '';
        if (profileSkills) profileSkills.value = (data.skills || []).join(', ');
        if (profileAchievements) profileAchievements.value = (data.achievements || []).join(', ');

        result.innerHTML = `
            <div class="analysis-card success">
                <h3>Student Profile: ${data.name || 'Practice Student'}</h3>
                <p><strong>Email:</strong> ${data.email || 'N/A'}</p>
                <p><strong>College:</strong> ${data.college || 'N/A'}</p>
                <p><strong>Department:</strong> ${data.department || 'N/A'}</p>
                <p><strong>Year:</strong> ${data.year || 'N/A'}</p>
                <p><strong>Phone:</strong> ${data.phone || 'N/A'}</p>
                <p><strong>Target Role:</strong> ${data.target_role || 'N/A'}</p>
                <p><strong>Skills:</strong> ${(data.skills || []).join(', ') || 'None added yet'}</p>
                <p><strong>Achievements:</strong> ${(data.achievements || []).join(', ') || 'None added yet'}</p>
                <p><strong>Joined:</strong> ${data.created_at || 'N/A'}</p>
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
    const interviewName = $('#interviewName')?.value || state.authUser?.full_name || state.authUser?.name || 'HireVision User';

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
    } catch (error) {
        showToast(`Error starting interview: ${error.message}`, 'error');
    }
}

async function startWebcam(videoElementId = 'videoElement') {
    let requestedNewStream = false;
    try {
        if (!state.stream || state.stream.getTracks().some(t => t.readyState === 'ended')) {
            state.stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 640 }, height: { ideal: 480 } }, audio: true });
            requestedNewStream = true;
        }

        const video = $(`#${videoElementId}`);
        if (video) {
            video.srcObject = state.stream;
            try { await video.play(); } catch (e) { console.warn("Video playback blocked", e); }
        }

        if (videoElementId === 'videoElement' && (!state.mediaRecorder || requestedNewStream)) {
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
        }

        const recordBtn = videoElementId === 'videoElement' ? $('#recordBtn') : (videoElementId === 'techVideoElement' ? $('#techRecordBtn') : $('#gdRecordBtn'));
        const stopBtn = videoElementId === 'videoElement' ? $('#stopBtn') : (videoElementId === 'techVideoElement' ? $('#techStopBtn') : $('#gdStopBtn'));
        if (recordBtn) recordBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;

        if (requestedNewStream) {
            showToast('Camera and microphone enabled.', 'success');
        }
    } catch (error) {
        if (!state.stream) showToast('Camera/Microphone access denied. You can manually type your responses.', 'error');
        const recordBtn = videoElementId === 'videoElement' ? $('#recordBtn') : (videoElementId === 'techVideoElement' ? $('#techRecordBtn') : $('#gdRecordBtn'));
        if (recordBtn) recordBtn.disabled = false;
        
        if (videoElementId === 'videoElement') {
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
}

function stopWebcam() {
    if (state.stream) {
        state.stream.getTracks().forEach(track => track.stop());
        state.stream = null;
    }
    ['videoElement', 'techVideoElement', 'gdVideoElement'].forEach(id => {
        const video = $(`#${id}`);
        if (video) video.srcObject = null;
    });
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

let gdSpeechRecognition = null;
function initGdSpeech() {
    const recordBtn = $('#gdRecordBtn');
    const stopBtn = $('#gdStopBtn');
    const indicator = $('#gdRecordingIndicator');
    const textarea = $('#gdTranscript');
    
    if (!recordBtn) return;
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        recordBtn.style.display = 'none';
        stopBtn.style.display = 'none';
        return;
    }
    
    if (!gdSpeechRecognition) {
        gdSpeechRecognition = new SpeechRecognition();
        gdSpeechRecognition.continuous = true;
        gdSpeechRecognition.interimResults = true;
        gdSpeechRecognition.lang = 'en-US';
        
        gdSpeechRecognition.onstart = () => {
            if (indicator) indicator.style.display = 'inline-block';
            recordBtn.disabled = true;
            stopBtn.disabled = false;
        };
        
        gdSpeechRecognition.onresult = (event) => {
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
        
        gdSpeechRecognition.onend = () => {
            if (indicator) indicator.style.display = 'none';
            recordBtn.disabled = false;
            stopBtn.disabled = true;
        };
        
        gdSpeechRecognition.onerror = (event) => {
            showToast(`Speech recognition warning: ${event.error}`, 'warning');
        };
    }
    
    recordBtn.onclick = () => {
        try {
            gdSpeechRecognition.start();
        } catch (e) {
            gdSpeechRecognition.stop();
        }
    };
    
    stopBtn.onclick = () => {
        gdSpeechRecognition.stop();
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
        stopWebcam();
        loadProfile();
        loadDashboard();
    } catch (error) {
        if (result) result.innerHTML = errorCard('Evaluation failed', error.message);
        stopWebcam();
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
                if (state.currentCodingProblem && state.currentCodingProblem.starter_code && state.currentCodingProblem.starter_code[lang]) {
                    code = state.currentCodingProblem.starter_code[lang];
                } else {
                    if (lang === 'Python') {
                        code = 'def two_sum(nums, target):\n    return []';
                    } else if (lang === 'Java') {
                        code = 'class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        return new int[0];\n    }\n}';
                    } else if (lang === 'C++') {
                        code = 'class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        return {};\n    }\n};';
                    } else if (lang === 'JavaScript') {
                        code = 'function twoSum(nums, target) {\n    return [];\n}';
                    }
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
            problem_statement: state.currentCodingProblem?.title || 'Two Sum',
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

// Authentication and profile management
function bindAuthEvents() {
    const switchBtn = $('#switchUserBtn');
    const logoutBtn = $('#logoutBtn');
    const loginForm = $('#loginForm');
    const registerForm = $('#registerForm');
    const forgotForm = $('#forgotPasswordForm');
    const resetForm = $('#resetPasswordForm');
    const showRegisterBtn = $('#showRegisterBtn');
    const showLoginBtn = $('#showLoginBtn');
    const showForgotBtn = $('#showForgotBtn');
    const showResetBtn = $('#showResetBtn');
    const showForgotBtnInline = $('#showForgotBtnInline');
    const showRegisterBtnInline = $('#showRegisterBtnInline');
    const cancelAuthBtn = $('#backToLoginBtn');

    if (switchBtn) {
        switchBtn.addEventListener('click', () => {
            if (state.isAuthenticated) {
                logout();
            } else {
                openAuthScreen('login');
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    if (showRegisterBtn) showRegisterBtn.addEventListener('click', () => openAuthScreen('register'));
    if (showLoginBtn) showLoginBtn.addEventListener('click', () => openAuthScreen('login'));
    if (showForgotBtn) showForgotBtn.addEventListener('click', () => openAuthScreen('forgot'));
    if (showResetBtn) showResetBtn.addEventListener('click', () => openAuthScreen('reset'));
    if (showForgotBtnInline) showForgotBtnInline.addEventListener('click', () => openAuthScreen('forgot'));
    if (showRegisterBtnInline) showRegisterBtnInline.addEventListener('click', () => openAuthScreen('register'));
    if (cancelAuthBtn) cancelAuthBtn.addEventListener('click', () => openAuthScreen('login'));

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    if (forgotForm) {
        forgotForm.addEventListener('submit', handleForgotPassword);
    }
    if (resetForm) {
        resetForm.addEventListener('submit', handleResetPassword);
    }
}

function openAuthScreen(mode = 'login') {
    const authScreen = $('#authScreen');
    const appShell = $('.app-shell');
    if (authScreen) authScreen.hidden = false;
    if (appShell) appShell.style.display = 'none';

    $all('[data-auth-panel]').forEach((panel) => {
        panel.classList.toggle('active', panel.dataset.authPanel === mode);
    });
    $all('[data-auth-tab]').forEach((tab) => {
        tab.classList.toggle('active', tab.dataset.authTab === mode);
    });
}

function updateActiveUserProfileUI() {
    const name = state.authUser?.full_name || state.authUser?.name || localStorage.getItem('hirevisionUserName') || 'Sign in to continue';
    const role = state.authUser?.target_role || localStorage.getItem('hirevisionUserTargetRole') || 'student';
    if ($('#activeUserName')) $('#activeUserName').textContent = name;
    if ($('#activeUserRole')) $('#activeUserRole').textContent = role;
    if ($('#switchUserBtn')) {
        $('#switchUserBtn').title = state.isAuthenticated ? 'Logout' : 'Sign In';
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = $('#loginEmail')?.value.trim();
    const password = $('#loginPassword')?.value || '';
    const rememberMe = Boolean($('#loginRemember')?.checked);

    console.log('[AUTH] Login attempt:', { email, rememberMe });
    console.log('[AUTH] API_URL:', API_URL);
    console.log('[AUTH] Calling apiPost to /auth/login');

    try {
        const response = await apiPost('/auth/login', { email, password, remember_me: rememberMe });
        console.log('[AUTH] Login response received:', response);
        
        if (!response.token) {
            throw new Error('No token in response');
        }
        
        console.log('[AUTH] Storing token...');
        storeAuthToken(response.token, rememberMe || response.remember_me);
        
        console.log('[AUTH] Applying authenticated user...');
        applyAuthenticatedUser(response.user);
        
        console.log('[AUTH] State after login:', {
            isAuthenticated: window.state.isAuthenticated,
            authChecked: window.state.authChecked,
            userId: window.state.userId
        });
        
        showToast('Welcome back to HireVision.', 'success');
        
        console.log('[AUTH] window.HireVisionRouteNavigate:', typeof window.HireVisionRouteNavigate);
        console.log('[AUTH] window.triggerRouterUpdate:', typeof window.triggerRouterUpdate);
        
        if (window.HireVisionRouteNavigate) {
            console.log('[AUTH] Calling navigate("/dashboard")');
            window.HireVisionRouteNavigate('/dashboard');
        } else {
            console.error('[AUTH] ERROR: window.HireVisionRouteNavigate is not available!');
        }
    } catch (error) {
        console.error('[AUTH] Login error:', error);
        showToast(`Login failed: ${error.message}`, 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const payload = {
        full_name: $('#registerName')?.value.trim(),
        email: $('#registerEmail')?.value.trim(),
        password: $('#registerPassword')?.value || '',
        college: $('#registerCollege')?.value.trim(),
        department: $('#registerDepartment')?.value.trim(),
        year: $('#registerYear')?.value.trim(),
        phone: $('#registerPhone')?.value.trim(),
        target_role: $('#registerTargetRole')?.value.trim(),
        remember_me: Boolean($('#registerRemember')?.checked),
    };

    try {
        const response = await apiPost('/auth/register', payload);
        storeAuthToken(response.token, response.remember_me);
        applyAuthenticatedUser(response.user);
        // DO NOT call showAuthenticatedShell() here - let router.js handle it
        // Just navigate to dashboard, the ProtectedRoute will load the shell
        showToast('Account created successfully.', 'success');
        if (window.HireVisionRouteNavigate) {
            window.HireVisionRouteNavigate('/dashboard');
        }
    } catch (error) {
        showToast(`Registration failed: ${error.message}`, 'error');
    }
}

async function handleForgotPassword(event) {
    event.preventDefault();
    const email = $('#forgotEmail')?.value.trim();

    try {
        const response = await apiPost('/auth/forgot-password', { email });
        const resetToken = $('#resetToken');
        if (resetToken && response.reset_token) {
            resetToken.value = response.reset_token;
        }
        openAuthScreen('reset');
        if (window.HireVisionRouteNavigate) {
            window.HireVisionRouteNavigate('/forgot-password');
        }
        showToast('Reset token generated. Use it to set a new password.', 'success');
    } catch (error) {
        showToast(`Password reset request failed: ${error.message}`, 'error');
    }
}

async function handleResetPassword(event) {
    event.preventDefault();
    const email = $('#resetEmail')?.value.trim();
    const resetToken = $('#resetToken')?.value.trim();
    const password = $('#resetPassword')?.value || '';

    try {
        await apiPost('/auth/reset-password', { email, reset_token: resetToken, password });
        showToast('Password updated. Please sign in.', 'success');
        openAuthScreen('login');
        if (window.HireVisionRouteNavigate) {
            window.HireVisionRouteNavigate('/login');
        }
    } catch (error) {
        showToast(`Password reset failed: ${error.message}`, 'error');
    }
}

async function logout() {
    try {
        await apiPost('/auth/logout', {});
    } catch (error) {
        console.warn('Logout request failed:', error.message);
    }

    clearAuthSession();
    state.authUser = null;
    state.isAuthenticated = false;
    state.userId = null;
    state.authChecked = true;  // Mark as checked before redirecting
    updateActiveUserProfileUI();
    unmountDashboardShell();
    prepareShellForAuth();
    openAuthScreen('login');
    showToast('You have been logged out.', 'info');
    if (window.triggerRouterUpdate) window.triggerRouterUpdate();
    if (window.HireVisionRouteNavigate) {
        window.HireVisionRouteNavigate('/login');
    }
}

// Edit Profile Form Submit
function bindProfileEdit() {
    const form = $('#profileEditForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = $('#profileName').value.trim();
        const email = $('#profileEmail').value.trim();
        const college = $('#profileCollege').value.trim();
        const department = $('#profileDepartment').value.trim();
        const year = $('#profileYear').value.trim();
        const phone = $('#profilePhone').value.trim();
        const targetRole = $('#profileTargetRole').value.trim();
        const skills = $('#profileSkills').value.split(',').map(s => s.trim()).filter(Boolean);
        const achievements = $('#profileAchievements').value.split(',').map(s => s.trim()).filter(Boolean);

        try {
            await apiPost('/profile/save', {
                user_id: state.userId,
                full_name: name,
                name,
                email,
                college,
                department,
                year,
                phone,
                role: localStorage.getItem('hirevisionUserRole') || 'student',
                target_role: targetRole,
                skills,
                achievements
            });

            localStorage.setItem('hirevisionUserName', name);
            localStorage.setItem('hirevisionUserEmail', email);
            localStorage.setItem('hirevisionUserTargetRole', targetRole);

            if (state.authUser) {
                state.authUser = { ...state.authUser, full_name: name, name, email, college, department, year, phone, target_role: targetRole };
            }

            updateActiveUserProfileUI();
            showToast('Profile updated successfully!', 'success');
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
let backendHealthy = false;

function showBackendConnectForm(reason) {
    // Deliberately removed as per user request to remove "Connect Your Backend" banner.
    console.warn('Backend connection issue:', reason);
}

async function checkBackendHealth() {
    const badge = $('#backendStatus');
    const alert = $('#systemAlert');
    
    // Hide the badge completely to remove "Not Connected"
    if (badge) badge.style.display = 'none';
    if (alert) alert.style.display = 'none';

    try {
        const healthUrl = `${API_URL.replace(/\/api\/?$/, '')}/health`;
        const response = await fetch(healthUrl, { signal: AbortSignal.timeout(8000) });
        if (!response.ok) throw new Error(`Status ${response.status}`);

        // SUCCESS - Backend is online
        backendHealthy = true;
        connectionAttempts = 0;
        clearInterval(healthCheckInterval);
        healthCheckInterval = null;

        // Load all panels now that backend is confirmed available
        if (state.isAuthenticated && !panelsLoaded) {
            panelsLoaded = true;
            loadAllPanels();
        }
    } catch (e) {
        connectionAttempts++;
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


async function generateGdTopic() {
    const select = $('#gdTopic');
    const btn = $('#gdGenerateTopicBtn');
    if (!select || !btn) return;
    
    btn.disabled = true;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';
    
    try {
        const excludeTopics = Array.from(select.options).map(opt => opt.value);
        const data = await apiPost('/gd/generate-topic', { exclude_topics: excludeTopics });
        if (data && data.topic) {
            const newOpt = document.createElement('option');
            newOpt.value = data.topic;
            newOpt.textContent = data.topic;
            select.appendChild(newOpt);
            select.value = data.topic;
            showToast('AI Topic generated successfully!', 'success');
        }
    } catch (error) {
        showToast(`Failed to generate topic: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

window.startInterview = startInterview;
window.toggleRecording = toggleRecording;
window.stopRecording = stopRecording;
window.submitResponse = submitResponse;
window.endInterview = endInterview;
window.startNewInterview = startNewInterview;
window.downloadReport = downloadReport;
window.mountDashboardShell = mountDashboardShell;
window.showView = showView;
window.loadAllPanels = loadAllPanels;

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

async function loadCodingProblem() {
    const difficulty = $('#codingDifficulty')?.value || 'Easy';
    const titleEl = $('#codingProblemTitle');
    const descEl = $('#codingProblemDesc');
    const examplesEl = $('#codingProblemExamples');
    const constraintsEl = $('#codingProblemConstraints');
    const btn = $('#codingProblemBtn');
    
    if (btn) btn.disabled = true;
    if (titleEl) titleEl.textContent = 'Loading problem...';
    if (descEl) descEl.textContent = '';
    if (examplesEl) examplesEl.innerHTML = '';
    if (constraintsEl) constraintsEl.innerHTML = '';
    
    try {
        const problem = await apiGet(`/coding/problem?difficulty=${difficulty}&user_id=${state.userId}`);
        state.currentCodingProblem = problem;
        
        if (titleEl) titleEl.innerHTML = `${problem.title} <span class="badge ${difficulty.toLowerCase()}">${difficulty}</span>`;
        if (descEl) descEl.textContent = problem.problem_statement;
        
        if (examplesEl) {
            examplesEl.innerHTML = '<strong>Examples:</strong><br>' + (problem.examples || []).map(ex => `
                <div style="background: rgba(255,255,255,0.01); padding: 8px; border-radius: 6px; margin-top: 5px; border: 1px solid rgba(255,255,255,0.03);">
                    <strong>Input:</strong> <code>${ex.input}</code><br>
                    <strong>Output:</strong> <code>${ex.output}</code><br>
                    ${ex.explanation ? `<strong>Explanation:</strong> <small class="muted">${ex.explanation}</small>` : ''}
                </div>
            `).join('');
        }
        
        if (constraintsEl) {
            constraintsEl.innerHTML = '<strong>Constraints:</strong><ul style="margin: 4px 0 0 0; padding-left: 20px;">' + 
                (problem.constraints || []).map(c => `<li><code>${c}</code></li>`).join('') + '</ul>';
        }
        
        // Update starter code in Monaco editor
        if (state.editor) {
            const lang = $('#codingLanguage')?.value || 'Python';
            const code = problem.starter_code?.[lang] || '';
            state.editor.setValue(code);
        }
    } catch (error) {
        if (titleEl) titleEl.textContent = 'Failed to load problem';
        if (descEl) descEl.textContent = error.message;
    } finally {
        if (btn) btn.disabled = false;
    }
}
