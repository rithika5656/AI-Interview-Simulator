(() => {
    // Try to use VERCEL_URL or REACT_APP_API_URL or similar environment variables if available
    // For Vercel frontend, use NEXT_PUBLIC_ or REACT_APP_ variables
    const apiBaseUrl = window.__HIREVISION_API_BASE__
        || localStorage.getItem('hirevisionApiBaseUrl')
        || (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL)
        || (typeof process !== 'undefined' && process.env?.REACT_APP_API_URL)
        // Fallback - user must replace this with their deployed backend URL
        || 'https://hirevision-backend.onrender.com/api';

    const socketUrl = window.__HIREVISION_SOCKET_URL__
        || localStorage.getItem('hirevisionSocketUrl')
        || (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_SOCKET_URL)
        || (typeof process !== 'undefined' && process.env?.REACT_APP_SOCKET_URL)
        || 'https://hirevision-backend.onrender.com';

    async function request(path, options = {}) {
        const url = `${apiBaseUrl}${path}`;
        const response = await fetch(url, {
            method: options.method || 'GET',
            headers: options.headers,
            body: options.body,
            credentials: 'include',
        });

        let payload;
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            payload = await response.json();
        } else {
            payload = { message: await response.text() };
        }

        if (!response.ok) {
            throw new Error(payload.error || payload.message || 'Request failed');
        }

        return payload;
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

    window.HireVisionApiClient = {
        get,
        post,
        request,
        baseUrl: apiBaseUrl,
        socketUrl,
        setBaseUrl: (url) => {
            localStorage.setItem('hirevisionApiBaseUrl', url);
            window.location.reload();
        },
        setSocketUrl: (url) => {
            localStorage.setItem('hirevisionSocketUrl', url);
            window.location.reload();
        },
    };
})();
