(function () {
    if (window.__hirevisionRouterInitialized) {
        return;
    }

    function showRouterStartupError(message) {
        if (window.__hirevisionRouterStartFailed) {
            return;
        }

        window.__hirevisionRouterStartFailed = true;
        let errorEl = document.getElementById('routerError');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.id = 'routerError';
            errorEl.style.cssText = 'position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(2,6,23,0.95);color:#fff;z-index:99999;padding:24px;text-align:center;font-family:Inter, system-ui, sans-serif;';
            document.body.appendChild(errorEl);
        }

        errorEl.innerHTML = `
            <div style="max-width: 420px; background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 16px; padding: 24px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);">
                <h2 style="margin: 0 0 12px; font-size: 1.25rem;">Application failed to start</h2>
                <p style="margin: 0 0 16px; line-height: 1.5; color: #cbd5e1;">${message}</p>
                <button type="button" onclick="window.location.reload()" style="background: #2563eb; color: #fff; border: 0; border-radius: 999px; padding: 10px 16px; cursor: pointer;">Refresh page</button>
            </div>
        `;
    }

    function getRuntimeReady() {
        return Boolean(window.React && window.ReactDOM && window.ReactRouterDOM);
    }

    function getMissingRuntimeDependencies() {
        const missing = [];
        if (!window.React) missing.push('React');
        if (!window.ReactDOM) missing.push('ReactDOM');
        if (!window.ReactRouterDOM) missing.push('ReactRouterDOM');
        return missing;
    }

    function mountRouter() {
        if (window.__hirevisionRouterMounted) {
            return;
        }

        if (!getRuntimeReady()) {
            const missing = getMissingRuntimeDependencies();
            console.error('[ROUTER] React runtime missing', missing.join(', '));
            showRouterStartupError(`The application could not load its React runtime. Missing: ${missing.join(', ')}`);
            return;
        }

        const rootEl = document.getElementById('routerRoot');
        if (!rootEl) {
            return;
        }

        const React = window.React;
        const { BrowserRouter, Routes, Route, Navigate, useNavigate } = window.ReactRouterDOM;

        const protectedViewMap = {
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

        function AuthRoute({ mode }) {
            const navigate = useNavigate();

            React.useEffect(() => {
                if (window.state?.isAuthenticated) {
                    navigate('/dashboard', { replace: true });
                    return;
                }

                const authScreen = document.getElementById('authScreen');
                const appShell = document.querySelector('.app-shell');
                if (authScreen) authScreen.hidden = false;
                if (appShell) appShell.style.display = 'none';

                if (typeof window.openAuthScreen === 'function') {
                    window.openAuthScreen(mode);
                }
            }, [mode, navigate]);

            if (window.state?.authChecked && window.state.isAuthenticated) {
                return React.createElement(Navigate, { to: '/dashboard', replace: true });
            }

            return null;
        }

        function ProtectedRoute({ viewId }) {
            const navigate = useNavigate();

            React.useEffect(() => {
                if (!window.state?.authChecked) {
                    return;
                }

                if (!window.state.isAuthenticated) {
                    navigate('/login', { replace: true });
                    return;
                }

                const loadShell = async () => {
                    const authScreen = document.getElementById('authScreen');
                    const appShell = document.querySelector('.app-shell');
                    if (authScreen) authScreen.hidden = true;

                    if (!appShell && typeof window.mountDashboardShell === 'function') {
                        await window.mountDashboardShell();
                    }

                    const mountedShell = document.querySelector('.app-shell');
                    if (mountedShell) {
                        mountedShell.style.display = 'grid';
                    }

                    if (typeof window.showView === 'function') {
                        window.showView(viewId);
                    }

                    if (window.backendHealthy && !window.panelsLoaded) {
                        window.panelsLoaded = true;
                        if (typeof window.loadAllPanels === 'function') {
                            window.loadAllPanels();
                        }
                    }
                };

                loadShell().catch((error) => {
                    console.error('[ROUTER] Failed to load protected view:', error);
                });
            }, [navigate, viewId]);

            if (!window.state?.authChecked) {
                return null;
            }

            if (!window.state.isAuthenticated) {
                return React.createElement(Navigate, { to: '/login', replace: true });
            }

            return null;
        }

        function RouteBridge() {
            const navigate = useNavigate();
            const [, forceUpdate] = React.useReducer((value) => value + 1, 0);

            React.useEffect(() => {
                const handler = () => forceUpdate();
                window.addEventListener('auth-changed', handler);
                return () => window.removeEventListener('auth-changed', handler);
            }, []);

            React.useEffect(() => {
                const routeHandler = (event) => {
                    const path = event?.detail?.path;
                    if (path) {
                        navigate(path, { replace: Boolean(event.detail?.replace) });
                    }
                };

                window.addEventListener('hirevision-route-request', routeHandler);
                return () => window.removeEventListener('hirevision-route-request', routeHandler);
            }, [navigate]);

            React.useEffect(() => {
                if (!window.state?.authChecked) {
                    return;
                }

                const authScreen = document.getElementById('authScreen');
                const appShell = document.querySelector('.app-shell');
                const isAuthRoute = ['/login', '/register', '/forgot-password'].includes(window.location.pathname);

                if (!window.state.isAuthenticated) {
                    if (!isAuthRoute) {
                        navigate('/login', { replace: true });
                    }
                    if (authScreen) authScreen.hidden = false;
                    if (appShell) appShell.style.display = 'none';
                    return;
                }

                if (window.location.pathname === '/' || isAuthRoute) {
                    navigate('/dashboard', { replace: true });
                    return;
                }

                if (authScreen) authScreen.hidden = true;
                if (appShell) appShell.style.display = 'grid';
            }, [navigate, window.state?.authChecked, window.state?.isAuthenticated]);

            return React.createElement(Routes, null,
                React.createElement(Route, {
                    path: '/',
                    element: React.createElement(Navigate, { to: window.state?.isAuthenticated ? '/dashboard' : '/login', replace: true }),
                }),
                React.createElement(Route, {
                    path: '/login',
                    element: React.createElement(AuthRoute, { mode: 'login' }),
                }),
                React.createElement(Route, {
                    path: '/register',
                    element: React.createElement(AuthRoute, { mode: 'register' }),
                }),
                React.createElement(Route, {
                    path: '/forgot-password',
                    element: React.createElement(AuthRoute, { mode: 'forgot' }),
                }),
                React.createElement(Route, {
                    path: '/dashboard',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/dashboard'] }),
                }),
                React.createElement(Route, {
                    path: '/resume',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/resume'] }),
                }),
                React.createElement(Route, {
                    path: '/aptitude',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/aptitude'] }),
                }),
                React.createElement(Route, {
                    path: '/technical',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/technical'] }),
                }),
                React.createElement(Route, {
                    path: '/logical',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/logical'] }),
                }),
                React.createElement(Route, {
                    path: '/verbal',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/verbal'] }),
                }),
                React.createElement(Route, {
                    path: '/coding',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/coding'] }),
                }),
                React.createElement(Route, {
                    path: '/gd',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/gd'] }),
                }),
                React.createElement(Route, {
                    path: '/hr',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/hr'] }),
                }),
                React.createElement(Route, {
                    path: '/analytics',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/analytics'] }),
                }),
                React.createElement(Route, {
                    path: '/career-coach',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/career-coach'] }),
                }),
                React.createElement(Route, {
                    path: '/profile',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/profile'] }),
                }),
                React.createElement(Route, {
                    path: '/company-wise',
                    element: React.createElement(ProtectedRoute, { viewId: protectedViewMap['/company-wise'] }),
                }),
                React.createElement(Route, {
                    path: '*',
                    element: React.createElement(Navigate, { to: window.state?.isAuthenticated ? '/dashboard' : '/login', replace: true }),
                })
            );
        }

        const root = window.ReactDOM.createRoot(rootEl);
        root.render(
            React.createElement(BrowserRouter, null,
                React.createElement(RouteBridge)
            )
        );

        window.__hirevisionRouterMounted = true;
        window.__hirevisionRouterInitialized = true;
        window.routerReady = true;
        window.dispatchEvent(new Event('router-ready'));
    }

    window.HireVisionRouterNavigate = function (path, options = {}) {
        window.dispatchEvent(new CustomEvent('hirevision-route-request', {
            detail: {
                path,
                replace: Boolean(options.replace),
            },
        }));
    };

    function initializeRouter() {
        if (window.__hirevisionRouterInitialized || window.__hirevisionRouterStartFailed) {
            return;
        }
        mountRouter();
    }

    window.addEventListener('react-runtime-ready', initializeRouter, { once: true });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeRouter, { once: true });
    } else {
        initializeRouter();
    }

    window.addEventListener('load', initializeRouter, { once: true });
})();
