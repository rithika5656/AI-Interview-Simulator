(function () {
    if (window.__hirevisionRouterInitialized) {
        return;
    }

    function mountRouter() {
        const rootEl = document.getElementById('routerRoot');
        if (!rootEl) {
            return;
        }

        const React = window.React;
        const ReactDOM = window.ReactDOM;
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
                if (authScreen) {
                    authScreen.hidden = false;
                }
                if (appShell) {
                    appShell.style.display = 'none';
                }

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
                    if (authScreen) {
                        authScreen.hidden = true;
                    }

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

        function AppRouter() {
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
                    if (authScreen) {
                        authScreen.hidden = false;
                    }
                    if (appShell) {
                        appShell.style.display = 'none';
                    }
                    return;
                }

                if (window.location.pathname === '/' || isAuthRoute) {
                    navigate('/dashboard', { replace: true });
                    return;
                }

                if (authScreen) {
                    authScreen.hidden = true;
                }
                if (appShell) {
                    appShell.style.display = 'grid';
                }
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

        const root = ReactDOM.createRoot(rootEl);
        root.render(
            React.createElement(BrowserRouter, null,
                React.createElement(AppRouter)
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

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mountRouter, { once: true });
    } else {
        mountRouter();
    }
})();
