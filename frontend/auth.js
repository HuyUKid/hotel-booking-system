// Hai form xác thực dùng chung cách kiểm tra phiên và gửi dữ liệu.
const form = document.querySelector('form');
const isLogin = form.id === 'loginForm';

async function initializeAuth() {
    try {
        const session = await getSession();
        if (isLogin && session) {
            location.replace(session.must_change_password ? 'change-password.html' : 'index.html');
        } else if (!isLogin && !session) {
            location.replace('login.html');
        } else if (!isLogin && !session.must_change_password) {
            location.replace('index.html');
        } else {
            form.hidden = false;
            showMessage('');
        }
    } catch (error) {
        showMessage('Không kết nối được Backend. Hãy chạy Backend và tải lại trang.');
    }
}

form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('button');
    const data = Object.fromEntries(new FormData(form));
    if (!isLogin && data.new_password !== data.confirm_password) {
        showMessage('Hai mật khẩu phải giống nhau.');
        return;
    }
    button.disabled = true;
    button.textContent = 'Đang xử lý…';
    try {
        const result = await apiRequest(isLogin ? '/api/login/' : '/api/change-password/', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (!result.response.ok) {
            if (result.data.code === 'AUTHENTICATION_REQUIRED') location.replace('login.html');
            throw new Error(result.data.message);
        }
        location.replace(isLogin && result.data.must_change_password ? 'change-password.html' : 'index.html');
    } catch (error) {
        showMessage(error.message || 'Không gửi được dữ liệu.');
    } finally {
        button.disabled = false;
        button.textContent = isLogin ? 'Đăng nhập' : 'Lưu mật khẩu';
    }
});

document.getElementById('exitButton')?.addEventListener('click', async event => {
    event.target.disabled = true;
    try {
        const { response } = await apiRequest('/api/logout/', { method: 'POST' });
        if (!response.ok && response.status !== 401) throw new Error('Chưa đăng xuất được.');
        location.replace('login.html');
    } catch (error) { showMessage(error.message); }
    finally { event.target.disabled = false; }
});
initializeAuth();
