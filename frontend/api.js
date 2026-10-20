// Cầu nối dùng chung giữa giao diện và Django API.
const API_BASE_URL = 'http://127.0.0.1:8000';
let csrfToken = '';

async function prepareCsrf() {
    const response = await fetch(`${API_BASE_URL}/api/csrf/`, { credentials: 'include' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Không lấy được CSRF token.');
    csrfToken = data.csrf_token;
}

async function apiRequest(path, options = {}, retry = true) {
    const method = (options.method || 'GET').toUpperCase();
    const headers = new Headers(options.headers || {});
    if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
        if (!csrfToken) await prepareCsrf();
        headers.set('X-CSRFToken', csrfToken);
    }
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options, method, headers, credentials: 'include'
    });
    let data;
    try {
        data = await response.json();
    } catch {
        throw new Error('Máy chủ trả dữ liệu không hợp lệ. Hãy kiểm tra Backend.');
    }
    if (data.code === 'CSRF_FAILED' && retry) {
        await prepareCsrf();
        return apiRequest(path, options, false);
    }
    return { response, data };
}

async function getSession() {
    const { response, data } = await apiRequest('/api/session/');
    if (!response.ok && response.status !== 401) throw new Error(data.message || 'Không kiểm tra được phiên.');
    return response.status === 401 ? null : data;
}

function showMessage(text, isError = true) {
    const element = document.getElementById('message');
    element.textContent = text;
    element.className = isError ? 'message error' : 'message success';
    element.hidden = !text;
}
