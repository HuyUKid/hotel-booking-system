# API Contract - Xác thực nhân viên

### 1. Đăng nhập
- **Endpoint:** `POST /api/login/`
- **Body:** `{"username": "nv01", "password": "initial_password"}`
- **Response:**
  - `status`: "success" | "error"
  - `must_change_password`: true | false

### 2. Đổi mật khẩu
- **Endpoint:** `POST /api/change-password/`
- **Body:** `{"new_password": "NewSecretPassword@123"}`
- **Response:**
  - `status`: "success" | "error"