// api.js
const API_BASE_URL = 'http://127.0.0.1:8000';
let csrfToken = '';

// Hàm lấy CSRF Token từ backend
async function prepareCsrf() {
    const response = await fetch(`${API_BASE_URL}/api/csrf/`, {
        credentials: 'include' // BẮT BUỘC: để backend set cookie
    });
    const data = await response.json();
    csrfToken = data.csrf_token;
}

// Hàm gọi API dùng chung
async function apiRequest(path, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const headers = new Headers(options.headers || {});

    // Nếu không phải GET, BẮT BUỘC phải có CSRF Token
    if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
        if (!csrfToken) await prepareCsrf();
        headers.set('X-CSRFToken', csrfToken);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        method,
        headers,
        credentials: 'include' // BẮT BUỘC gửi kèm Session Cookie
    });
    
    // Xử lý khi backend trả về lỗi 500 (không parse được JSON)
    if (response.status === 500) {
        return { response, data: { message: "Lỗi hệ thống từ máy chủ!" } };
    }

    const data = await response.json();
    return { response, data };
}