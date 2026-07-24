(function () {
    if (!window.React || !window.ReactDOM || !window.ReactRouterDOM) {
        console.error('React Router bridge could not start.');
        return;
    }

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

    function authRouteMode(pathname) {
        if (pathname === '/register') return 'register';
        if (pathname === '/forgot-password') return 'forgot';
        return 'login';
    }

    function AuthRoute({ mode }) {
        React.useEffect(() => {
            if (window.state && window.state.isAuthenticated) {
                if (window.HireVisionRouteNavigate) window.HireVisionRouteNavigate('/dashboard');
                return;
            }
            // Ensure auth screen is shown and app shell is hidden
            const authScreen = document.getElementById('authScreen');
            const appShell = document.querySelector('.app-shell');
            if (authScreen) authScreen.hidden = false;
            if (appShell) appShell.style.display = 'none';
            
            if (typeof window.openAuthScreen === 'function') window.openAuthScreen(mode);
        }, [mode]);

        if (window.state && window.state.authChecked && window.state.isAuthenticated) {
            return React.createElement(Navigate, { to: '/dashboard', replace: true });
        }

        return React.createElement('div', { style: { display: 'none' } });
    }

    function ProtectedRoute({ viewId }) {
        React.useEffect(() => {
            if (!window.state || !window.state.authChecked || !window.state.isAuthenticated) {
                return;
            }

            // First access to protected route - load dashboard shell if not already loaded
            const appShell = document.querySelector('.app-shell');
            if (!appShell) {
                // Dashboard shell not loaded yet - load it now
                if (typeof window.mountDashboardShell === 'function') {
                    window.mountDashboardShell().then(() => {
                        const authScreen = document.getElementById('authScreen');
                        const newAppShell = document.querySelector('.app-shell');
                        if (authScreen) authScreen.hidden = true;
                        if (newAppShell) newAppShell.style.display = 'grid';
                        
                        // Now show the view
                        if (typeof window.showView === 'function') {
                            window.showView(viewId);
                        }
                        
                        // Load panels if backend is healthy
                        if (window.backendHealthy && !window.panelsLoaded) {
                            window.panelsLoaded = true;
                            if (typeof window.loadAllPanels === 'function') {
                                window.loadAllPanels();
                            }
                        }
                    }).catch(err => {
                        console.error('Failed to load dashboard shell:', err);
                    });
                }
            } else {
                // Dashboard shell already loaded - just show it and update view
                const authScreen = document.getElementById('authScreen');
                if (authScreen) authScreen.hidden = true;
                appShell.style.display = 'grid';
                
                if (typeof window.showView === 'function') {
                    window.showView(viewId);
                }
            }
        }, [viewId]);

        if (window.state && !window.state.authChecked) {
            return React.createElement('div', { style: { display: 'none' } });
        }

        if (!window.state || !window.state.isAuthenticated) {
            return React.createElement(Navigate, { to: '/login', replace: true });
        }

        return React.createElement('div', { style: { display: 'none' } });
    }

    function RouteBridge() {
        const navigate = useNavigate();

        React.useEffect(() => {
            window.HireVisionRouteNavigate = (path) => navigate(path);
            return () => {
                if (window.HireVisionRouteNavigate) {
                    delete window.HireVisionRouteNavigate;
                }
            };
        }, [navigate]);

        React.useEffect(() => {
            if (window.state && !window.state.authChecked) return;
            if (!window.state || !window.state.isAuthenticated) {
                if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/forgot-password') {
                    navigate('/login', { replace: true });
                }
                // Show auth screen when not authenticated
                const authScreen = document.getElementById('authScreen');
                const appShell = document.querySelector('.app-shell');
                if (authScreen) authScreen.hidden = false;
                if (appShell) appShell.style.display = 'none';
                return;
            }

            const currentPath = window.location.pathname;
            if (currentPath === '/' || currentPath === '/login' || currentPath === '/register' || currentPath === '/forgot-password') {
                navigate('/dashboard', { replace: true });
            }
            // Show app shell when authenticated
            const authScreen = document.getElementById('authScreen');
            const appShell = document.querySelector('.app-shell');
            if (authScreen) authScreen.hidden = true;
            if (appShell) appShell.style.display = 'grid';
        }, [navigate]);

        return React.createElement(Routes, null,
            React.createElement(Route, {
                path: '/',
                element: React.createElement(Navigate, { to: window.state && window.state.isAuthenticated ? '/dashboard' : '/login', replace: true }),
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
                element: React.createElement(Navigate, { to: window.state && window.state.isAuthenticated ? '/dashboard' : '/login', replace: true }),
            })
        );
    }

    function mountRouter() {
        const rootEl = document.getElementById('routerRoot');
        if (!rootEl) return;
        const root = ReactDOM.createRoot(rootEl);
        root.render(
            React.createElement(BrowserRouter, null, React.createElement(RouteBridge))
        );
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mountRouter);
    } else {
        mountRouter();
    }
})();
