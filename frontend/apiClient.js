(() => {
    const defaultHost = window.location.hostname || 'localhost';
    const defaultProtocol = window.location.protocol === 'file:' ? 'http:' : window.location.protocol;
    const defaultBaseUrl = `${defaultProtocol}//${defaultHost}:5000/api`;
    const defaultSocketUrl = `${defaultProtocol}//${defaultHost}:5000`;

    const apiBaseUrl = window.__HIREVISION_API_BASE__
        || localStorage.getItem('hirevisionApiBaseUrl')
        || defaultBaseUrl;

    const socketUrl = window.__HIREVISION_SOCKET_URL__
        || localStorage.getItem('hirevisionSocketUrl')
        || defaultSocketUrl;

    const offlineState = {
        interview: null,
        questionsAsked: 0,
    };

    function nowIso() {
        return new Date().toISOString();
    }

    function topicQuestions(moduleKey, topic, count = 5) {
        const normalizedKey = String(moduleKey || '').toLowerCase();
        const banks = {
            aptitude: [
                { question: 'If a price increases from 200 to 230, what is the percentage increase?', options: ['10%', '12.5%', '15%', '20%'], correct_index: 2, explanation: 'Increase = 30, and 30/200 = 15%.' },
                { question: 'A train covers 180 km in 3 hours. What is its average speed?', options: ['50 km/h', '55 km/h', '60 km/h', '65 km/h'], correct_index: 2, explanation: 'Average speed = distance / time = 180 / 3 = 60 km/h.' },
                { question: 'What is 25% of 240?', options: ['40', '50', '60', '70'], correct_index: 2, explanation: '25% of 240 = 60.' },
                { question: 'If 6 workers finish a job in 12 days, how many days will 8 workers take?', options: ['6', '8', '9', '10'], correct_index: 2, explanation: '72 worker-days / 8 workers = 9 days.' },
            ],
            logical: [
                { question: 'Find the odd one out.', options: ['Triangle', 'Square', 'Circle', 'Cube'], correct_index: 3, explanation: 'Cube is a 3D solid; the others are 2D shapes.' },
                { question: "If A is B's brother and B is C's mother, what is A to C?", options: ['Father', 'Uncle', 'Brother', 'Cousin'], correct_index: 1, explanation: 'A is C’s maternal uncle.' },
                { question: 'Choose the next term: 2, 4, 8, 16, ?', options: ['18', '24', '32', '34'], correct_index: 2, explanation: 'The pattern doubles each time.' },
                { question: 'In a code, CAT is written as DBU. How is DOG written?', options: ['EPH', 'EPI', 'DPH', 'FQI'], correct_index: 0, explanation: 'Each letter shifts by +1.' },
            ],
            verbal: [
                { question: "Choose the synonym of 'abundant'.", options: ['Scarce', 'Plentiful', 'Tiny', 'Weak'], correct_index: 1, explanation: 'Abundant means plentiful.' },
                { question: "Choose the antonym of 'brisk'.", options: ['Quick', 'Lively', 'Slow', 'Sharp'], correct_index: 2, explanation: 'Brisk means quick; the opposite is slow.' },
                { question: 'Select the grammatically correct sentence.', options: ['She do not like tea.', 'She does not like tea.', 'She did not likes tea.', 'She not like tea.'], correct_index: 1, explanation: 'Does not is correct for third-person singular.' },
                { question: 'Fill in the blank: He is responsible ___ the project.', options: ['for', 'to', 'with', 'at'], correct_index: 0, explanation: 'The correct phrase is responsible for.' },
            ],
            technical: [
                { question: 'Which data structure is best for O(1) average lookup?', options: ['Array', 'Stack', 'HashMap', 'Queue'], correct_index: 2, explanation: 'Hash maps provide average constant-time lookup.' },
                { question: 'Which HTTP method is typically used to update an existing resource?', options: ['GET', 'POST', 'PUT', 'TRACE'], correct_index: 2, explanation: 'PUT is commonly used for updates.' },
                { question: 'In SQL, which clause filters grouped results?', options: ['WHERE', 'HAVING', 'ORDER BY', 'LIMIT'], correct_index: 1, explanation: 'HAVING filters after aggregation.' },
                { question: 'Which concept allows a class to use another class\'s behavior?', options: ['Encapsulation', 'Inheritance', 'Polymorphism', 'Abstraction'], correct_index: 1, explanation: 'Inheritance shares and extends behavior.' },
            ],
            default: [
                { question: `Explain ${topic} and where you would use it in a production system.`, options: ['Option A', 'Option B', 'Option C', 'Option D'], correct_index: 1, explanation: `Demo explanation for ${topic}.` },
            ],
        };

        const bank = banks[normalizedKey] || banks.default;
        return Array.from({ length: count }, (_, index) => {
            const template = bank[index % bank.length];
            return {
                question: template.question,
                options: template.options,
                correct_index: template.correct_index,
                explanation: template.explanation,
                difficulty: index % 3 === 0 ? 'easy' : index % 3 === 1 ? 'medium' : 'hard',
            };
        });
    }

    function mockDashboard() {
        return {
            metrics: {
                placement_readiness_score: 78,
                resume_score: 82,
                aptitude_progress: 71,
                coding_progress: 69,
                interview_score: 74,
                gd_score: 76,
            },
            daily_goals: [
                'Revise three aptitude topics',
                'Solve two coding questions',
                'Practice one HR interview response',
            ],
            recent_activities: [
                { type: 'Resume', title: 'ATS analysis completed', timestamp: nowIso() },
                { type: 'Coding', title: 'Two Sum reviewed', timestamp: nowIso() },
                { type: 'GD', title: 'AI in education simulated', timestamp: nowIso() },
            ],
            upcoming_mock_tests: [
                { title: 'Aptitude Practice Set', module: 'Aptitude', time: 'Today 6:00 PM' },
                { title: 'Technical Mock Interview', module: 'Interview', time: 'Tomorrow 11:00 AM' },
            ],
            career_coach: {
                strengths: ['Communication', 'Core programming', 'Resume structure'],
                weaknesses: ['System design depth', 'Advanced SQL', 'Mock interview pacing'],
                placement_readiness: 78,
            },
        };
    }

    function mockProfile() {
        return {
            placement_score: 78,
            resume: { filename: 'demo_resume.txt' },
            interview_history: [{ id: 'demo_hr_interview' }],
            coding_history: [{ id: 'demo_code_1' }],
            aptitude_history: [{ id: 'demo_aptitude_1' }],
            gd_history: [{ id: 'demo_gd_1' }],
        };
    }

    function mockAdminOverview() {
        return {
            totals: {
                users: 42,
                interviews: 18,
                coding_tests: 24,
                aptitude_tests: 31,
                gd_sessions: 14,
                reports: 12,
            },
            weak_areas: ['System Design', 'SQL Joins', 'Data Structures'],
        };
    }

    function mockAnalytics() {
        return {
            daily_progress: [62, 66, 70, 74, 78],
            weekly_progress: [55, 61, 67, 72, 78],
            monthly_progress: [48, 58, 66, 73, 78],
            interview_trend: [60, 64, 68, 71, 74],
        };
    }

    function mockCoach() {
        return {
            placement_readiness: 78,
            strengths: ['Resume quality', 'Problem solving', 'Communication'],
            weaknesses: ['Confidence under pressure', 'System design'],
            recommended_topics: ['SQL', 'Data Structures', 'Mock HR Interviews'],
            learning_plan: [
                'Revise weak topics for 30 minutes daily',
                'Complete one coding problem each day',
                'Record and review interview answers',
            ],
        };
    }

    function mockCompanyTrack(company) {
        return {
            company,
            difficulty: 'medium',
            focus_areas: ['Aptitude', 'Coding', 'HR', 'Domain knowledge'],
            interview_focus: `Prepare for ${company} with a balanced mix of core concepts and aptitude practice.`,
            modules: {
                aptitude: topicQuestions('aptitude', 'aptitude', 2),
                technical: topicQuestions('technical', 'technical interview', 2),
            },
        };
    }

    function mockResumeAnalysis() {
        return {
            ats_score: 82,
            skills: ['Python', 'Java', 'SQL', 'React', 'Flask'],
            projects: ['Placement portal', 'Resume analyzer', 'Interview simulator'],
            education: ['B.Tech CSE - 2026'],
            missing_keywords: ['Docker', 'System Design', 'Testing'],
            suggestions: ['Add measurable impact to project bullets', 'Mention internships and leadership'],
        };
    }

    function mockModuleSubmission(questions = [], answers = []) {
        const normalizedQuestions = questions.length ? questions : topicQuestions('practice', 'practice', 5);
        const totalCount = normalizedQuestions.length;
        const answerList = Array.isArray(answers) ? answers : [];
        const hasAnswerList = answerList.length > 0;
        const correctCount = hasAnswerList
            ? normalizedQuestions.reduce((count, question, index) => count + (Number(answerList[index]) === Number(question.correct_index) ? 1 : 0), 0)
            : Math.max(3, Math.floor(totalCount * 0.7));
        return {
            score: Math.round((correctCount / totalCount) * 100),
            correct_count: correctCount,
            total_count: totalCount,
            items: normalizedQuestions.map((question, index) => ({
                question: question.question,
                explanation: question.explanation,
                is_correct: hasAnswerList ? Number(answerList[index]) === Number(question.correct_index) : index < correctCount,
            })),
        };
    }

    function mockCodingReview() {
        return {
            score: 74,
            runtime: 'O(n)',
            complexity_analysis: 'Linear time with a hash-map based approach.',
            ai_review: 'Good baseline solution. Add edge-case handling and clarify naming.',
            hidden_tests: [
                { input: '[2, 7, 11, 15]', status: 'passed' },
                { input: '[3, 3]', status: 'passed' },
                { input: '[1, 8, 12]', status: 'needs optimization' },
            ],
        };
    }

    function mockGDFeedback() {
        return {
            scores: {
                communication: 78,
                confidence: 74,
                vocabulary: 76,
                grammar: 81,
                relevance: 79,
                fluency: 77,
            },
            feedback: [
                'Use one example to support each point.',
                'Keep the response structure tight and balanced.',
                'Speak slightly slower for emphasis.',
            ],
        };
    }

    function mockTechnicalQuestion() {
        return {
            question: 'How would you optimize a service that processes large volumes of interview responses?',
            explanation: 'Focus on batching, queueing, caching, and asynchronous processing.',
            follow_up: 'What observability would you add to detect latency spikes?',
        };
    }

    function mockStartInterview(payload) {
        offlineState.interview = {
            interview_id: payload?.interview_id || `offline_${Date.now()}`,
            job_role: payload?.job_role || 'Software Engineer',
            interview_name: payload?.interview_name || 'Demo Student',
        };
        offlineState.questionsAsked = 1;

        return {
            interview_id: offlineState.interview.interview_id,
            question: `Tell me about yourself as a ${offlineState.interview.job_role}.`,
            message: 'Interview started in demo mode',
        };
    }

    function mockSubmitResponse() {
        offlineState.questionsAsked += 1;
        return {
            immediate_feedback: {
                text: 'Clear response with good structure. Add one more concrete example.',
                sentiment: { confidence: 0.81, sentiment_type: 'Positive' },
                filler_words: ['um', 'like'],
            },
            next_question: `Follow-up question ${Math.min(offlineState.questionsAsked, 5)}: describe a challenge you solved.`,
        };
    }

    function mockEndInterview() {
        return {
            report: {
                summary: {
                    overall_score: 78,
                    communication_score: 80,
                    technical_score: 74,
                },
                detailed_feedback: {
                    strengths: ['Clear communication', 'Relevant examples', 'Good technical foundation'],
                    areas_for_improvement: ['Use stronger closing statements', 'Expand on outcomes'],
                },
                recommendations: ['Practice STAR answers', 'Review project impact', 'Do one mock interview daily'],
                response_details: [
                    {
                        text: 'Demo response content.',
                        analysis: { relevance_score: 78, key_strengths: ['Structure', 'Clarity'] },
                        sentiment: { sentiment_type: 'Positive' },
                    },
                ],
            },
        };
    }

    function mockGenerateModule(path, body) {
        const moduleKey = path.split('/').filter(Boolean)[0] || 'module';
        const topic = body?.topic || moduleKey;
        return { questions: topicQuestions(moduleKey, topic, body?.count || 5) };
    }

    function offlineFallback(path, options = {}) {
        const cleanPath = path.split('?')[0];
        const body = options.body && typeof options.body === 'string'
            ? JSON.parse(options.body)
            : options.body instanceof FormData
                ? Object.fromEntries(options.body.entries())
                : options.body || {};

        if (cleanPath === '/dashboard/overview') return mockDashboard();
        if (cleanPath === '/profile/demo_student') return mockProfile();
        if (cleanPath === '/admin/overview') return mockAdminOverview();
        if (cleanPath === '/analytics/summary') return mockAnalytics();
        if (cleanPath === '/career-coach') return mockCoach();
        if (cleanPath.startsWith('/company-track/')) return mockCompanyTrack(decodeURIComponent(cleanPath.split('/').pop() || 'TCS'));
        if (cleanPath === '/resume/analyze') return mockResumeAnalysis();
        if (cleanPath.endsWith('/generate')) return mockGenerateModule(cleanPath, body);
        if (cleanPath.endsWith('/submit') && cleanPath !== '/submit-response') return mockModuleSubmission(body?.questions || [], body?.answers || []);
        if (cleanPath === '/coding/review') return mockCodingReview();
        if (cleanPath === '/gd/simulate') return mockGDFeedback();
        if (cleanPath === '/technical-interview/question') return mockTechnicalQuestion();
        if (cleanPath === '/start-interview') return mockStartInterview(body);
        if (cleanPath === '/submit-response') return mockSubmitResponse();
        if (cleanPath === '/end-interview') return mockEndInterview();

        throw new Error('Backend unavailable and no offline mock exists for this endpoint.');
    }

    function timeoutSignal(timeoutMs) {
        if (!window.AbortController) {
            return { signal: undefined, cleanup: () => {} };
        }

        const controller = new AbortController();
        const timer = window.setTimeout(() => controller.abort(), timeoutMs);
        return {
            signal: controller.signal,
            cleanup: () => window.clearTimeout(timer),
        };
    }

    function normalizeError(error) {
        if (error?.name === 'AbortError') {
            return new Error('Request timed out. Backend server may be slow or unavailable.');
        }

        if (error instanceof TypeError) {
            return new Error('Network connection failed. Backend server is not running or cannot be reached.');
        }

        return error instanceof Error ? error : new Error('Unexpected API failure.');
    }

    function mapHttpError(status, payload) {
        if (status === 401 || status === 403) {
            return new Error(payload?.error || 'Authentication expired. Please sign in again.');
        }

        if (status === 404) {
            return new Error(payload?.error || 'API endpoint not found.');
        }

        if (status >= 500) {
            return new Error(payload?.error || 'Internal server error.');
        }

        return new Error(payload?.error || 'Request failed.');
    }

    async function parseResponse(response) {
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            return response.json();
        }

        return { message: await response.text() };
    }

    async function request(path, options = {}) {
        const timeoutMs = options.timeoutMs || 15000;
        const { signal, cleanup } = timeoutSignal(timeoutMs);
        const url = `${apiBaseUrl}${path}`;

        try {
            const response = await fetch(url, {
                method: options.method || 'GET',
                headers: options.headers,
                body: options.body,
                signal,
                credentials: 'include',
            });

            const payload = await parseResponse(response);
            if (!response.ok) {
                throw mapHttpError(response.status, payload);
            }

            return payload;
        } catch (error) {
            const normalized = normalizeError(error);
            if (normalized.message.includes('Network connection failed') || normalized.message.includes('timed out')) {
                return offlineFallback(path, options);
            }

            throw normalized;
        } finally {
            cleanup();
        }
    }

    async function get(path, options = {}) {
        return request(path, { ...options, method: 'GET' });
    }

    async function post(path, body, options = {}) {
        const isFormData = body instanceof FormData;
        const headers = isFormData ? options.headers : { 'Content-Type': 'application/json', ...(options.headers || {}) };
        const payload = isFormData ? body : JSON.stringify(body || {});
        return request(path, { ...options, method: 'POST', body: payload, headers });
    }

    async function healthCheck() {
        const { signal, cleanup } = timeoutSignal(8000);
        try {
            const response = await fetch(`${apiBaseUrl.replace(/\/api$/, '')}/health`, {
                method: 'GET',
                signal,
                credentials: 'include',
            });
            const payload = await parseResponse(response);
            return response.ok ? { ok: true, payload } : { ok: false, payload };
        } catch (error) {
            return { ok: false, error: normalizeError(error) };
        } finally {
            cleanup();
        }
    }

    function setBaseUrl(url) {
        localStorage.setItem('hirevisionApiBaseUrl', url);
    }

    function setSocketUrl(url) {
        localStorage.setItem('hirevisionSocketUrl', url);
    }

    window.HireVisionApiClient = {
        get,
        post,
        request,
        healthCheck,
        baseUrl: apiBaseUrl,
        socketUrl,
        isOffline: false,
        setBaseUrl,
        setSocketUrl,
    };
})();