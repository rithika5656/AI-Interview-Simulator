(function () {
    if (window.__hirevisionRouterInitialized) {
        return;
    }

    const routeViewMap = {
        '/dashboard': 'dashboardView',
        '/resume': 'resumeView',
        '/aptitude': 'aptitudeView',
        '/logical': 'logicalView',
        '/verbal': 'verbalView',
        '/technical': 'technicalMcqView',
        '/coding': 'codingView',
        '/gd': 'gdView',
        '/hr': 'legacyInterviewView',
        '/analytics': 'analyticsView',
        '/career-coach': 'coachView',
        '/profile': 'profileView',
        '/company-wise': 'companyView',
    };

    const publicRoutes = new Set(['/login', '/register', '/forgot-password']);

    function normalizePath(path) {
        if (!path) {
            return '/';
        }

        if (/^https?:\/\//i.test(path)) {
            try {
                return new URL(path, window.location.origin).pathname;
            } catch (error) {
                return '/';
            }
        }

        if (!path.startsWith('/')) {
            return `/${path}`;
        }

        return path;
    }

    function setDocumentTitle(path) {
        const titleMap = {
            '/login': 'HireVision · Login',
            '/register': 'HireVision · Register',
            '/forgot-password': 'HireVision · Reset Password',
            '/dashboard': 'HireVision · Dashboard',
        };

        if (titleMap[path]) {
            document.title = titleMap[path];
        }
    }

    function showAuthRoute(path) {
        const normalized = normalizePath(path);
        const routeKey = normalized === '/register' ? 'register' : normalized === '/forgot-password' ? 'forgot' : 'login';

        if (typeof window.prepareShellForAuth === 'function') {
            window.prepareShellForAuth();
        } else {
            const authScreen = document.getElementById('authScreen');
            const appShell = document.querySelector('.app-shell');
            if (authScreen) authScreen.hidden = false;
            if (appShell) appShell.style.display = 'none';
        }

        if (typeof window.openAuthScreen === 'function') {
            window.openAuthScreen(routeKey);
        } else {
            document.querySelectorAll('[data-auth-panel]').forEach((panel) => {
                panel.classList.toggle('active', panel.dataset.authPanel === routeKey);
            });
            document.querySelectorAll('[data-auth-tab]').forEach((tab) => {
                tab.classList.toggle('active', tab.dataset.authTab === routeKey);
            });
        }

        setDocumentTitle(normalized);
    }

    async function showProtectedRoute(path) {
        const targetView = routeViewMap[normalizePath(path)] || 'dashboardView';

        try {
            if (typeof window.showAuthenticatedShell === 'function') {
                await window.showAuthenticatedShell();
            } else {
                if (typeof window.mountDashboardShell === 'function') {
                    await window.mountDashboardShell();
                }
                const authScreen = document.getElementById('authScreen');
                const appShell = document.querySelector('.app-shell');
                if (authScreen) authScreen.hidden = true;
                if (appShell) appShell.style.display = 'grid';
            }

            if (typeof window.showView === 'function') {
                window.showView(targetView);
            }
        } catch (error) {
            console.error('[ROUTER] Protected route failed:', error);
        }

        setDocumentTitle('/dashboard');
    }

    function applyRoute(path) {
        const normalized = normalizePath(path);
        const isAuthenticated = Boolean(window.state?.isAuthenticated);
        const shouldShowAuth = !isAuthenticated || normalized === '/' || publicRoutes.has(normalized);

        if (shouldShowAuth) {
            if (normalized === '/' && isAuthenticated) {
                const targetPath = '/dashboard';
                history.replaceState(null, '', targetPath);
                showProtectedRoute(targetPath);
                return;
            }

            if (!isAuthenticated && normalized !== '/dashboard' && !routeViewMap[normalized]) {
                showAuthRoute(normalized === '/' ? '/login' : normalized);
                return;
            }

            if (!isAuthenticated) {
                showAuthRoute(normalized === '/' ? '/login' : normalized);
                return;
            }

            showAuthRoute('/login');
            return;
        }

        showProtectedRoute(normalized);
    }

    function initializeRouter() {
        const rootEl = document.getElementById('routerRoot');
        if (rootEl) {
            rootEl.hidden = false;
        }

        window.addEventListener('auth-changed', () => {
            applyRoute(window.location.pathname);
        });

        window.addEventListener('popstate', () => {
            applyRoute(window.location.pathname);
        });

        window.addEventListener('hirevision-route-request', (event) => {
            const path = event?.detail?.path;
            if (path) {
                window.HireVisionRouterNavigate(path, { replace: true });
            }
        });

        window.HireVisionRouterNavigate = function (path, options = {}) {
            const normalized = normalizePath(path);
            if (options.replace) {
                history.replaceState(null, '', normalized);
            } else {
                history.pushState(null, '', normalized);
            }
            applyRoute(normalized);
        };

        window.__hirevisionRouterMounted = true;
        window.__hirevisionRouterInitialized = true;
        window.routerReady = true;
        window.dispatchEvent(new Event('router-ready'));
        applyRoute(window.location.pathname);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeRouter, { once: true });
    } else {
        initializeRouter();
    }
})();
