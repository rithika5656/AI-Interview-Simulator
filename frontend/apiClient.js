(() => {
    const host = window.location.hostname || 'localhost';
    const protocol = window.location.protocol === 'file:' ? 'http:' : window.location.protocol;
    const isLocal = host === 'localhost' || host === '127.0.0.1';

    // ONLY use :5000 fallback on localhost. On production, leave empty so the app
    // shows the "Connect Backend" form and prompts the user for their Render URL.
    const localFallbackBase = isLocal ? `${protocol}//${host}:5000/api` : '';
    const localFallbackSocket = isLocal ? `${protocol}//${host}:5000` : '';

    const apiBaseUrl = window.HireVisionConfig?.apiBaseUrl
        || window.__HIREVISION_API_BASE__
        || localStorage.getItem('hirevisionApiBaseUrl')
        || localStorage.getItem('hirevisionCustomApiUrl')
        || localFallbackBase;

    const socketUrl = window.HireVisionConfig?.socketUrl
        || window.__HIREVISION_SOCKET_URL__
        || localStorage.getItem('hirevisionSocketUrl')
        || localStorage.getItem('hirevisionCustomSocketUrl')
        || localFallbackSocket;

    async function request(path, options = {}) {
        const url = `${apiBaseUrl}${path}`;
        const response = await fetch(url, {
            method: options.method || 'GET',
            headers: options.headers,
            body: options.body,
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
