import json

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import EmployeeProfile


def _error(code, message, status):
    return JsonResponse(
        {'status': 'error', 'code': code, 'message': message},
        status=status,
    )


def _must_change_password(user):
    return EmployeeProfile.objects.filter(user=user, must_change_password=True).exists()


def _unauthorized():
    return _error(
        'AUTHENTICATION_REQUIRED',
        'Phiên đăng nhập không hợp lệ hoặc đã hết hạn.',
        401,
    )


def _json_body(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, _error('INVALID_JSON', 'Dữ liệu gửi lên không hợp lệ.', 400)

    if not isinstance(data, dict):
        return None, _error('INVALID_JSON', 'Dữ liệu gửi lên phải là object JSON.', 400)
    return data, None


def _user_data(user):
    return {
        'username': user.username,
        'display_name': user.get_full_name() or user.username,
        'must_change_password': _must_change_password(user),
    }


def csrf_failure(request, reason=''):
    return _error(
        'CSRF_FAILED',
        'CSRF token không hợp lệ hoặc đã hết hạn.',
        403,
    )


@require_GET
@ensure_csrf_cookie
def api_csrf(request):
    return JsonResponse({'status': 'success', 'csrf_token': get_token(request)})


@require_GET
def api_session(request):
    if not request.user.is_authenticated:
        return _unauthorized()
    return JsonResponse({'status': 'success', **_user_data(request.user)})


@require_POST
def api_login(request):
    data, error_response = _json_body(request)
    if error_response:
        return error_response

    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))
    if not username or not password:
        return _error(
            'REQUIRED_FIELDS',
            'Vui lòng nhập tên đăng nhập và mật khẩu.',
            400,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return _error(
            'INVALID_CREDENTIALS',
            'Tên đăng nhập hoặc mật khẩu không đúng.',
            401,
        )

    login(request, user)
    return JsonResponse({'status': 'success', **_user_data(user)})


@require_POST
def api_logout(request):
    if not request.user.is_authenticated:
        return _unauthorized()
    logout(request)
    return JsonResponse({'status': 'success', 'message': 'Đã đăng xuất'})


@require_POST
def api_change_password(request):
    if not request.user.is_authenticated:
        return _unauthorized()

    data, error_response = _json_body(request)
    if error_response:
        return error_response

    new_password = str(data.get('new_password', ''))
    confirm_password = str(data.get('confirm_password', ''))
    if not new_password:
        return _error(
            'PASSWORD_REQUIRED',
            'Mật khẩu mới không được để trống.',
            400,
        )
    if new_password != confirm_password:
        return _error(
            'PASSWORD_MISMATCH',
            'Mật khẩu xác nhận không khớp.',
            400,
        )

    request.user.set_password(new_password)
    request.user.save(update_fields=['password'])
    EmployeeProfile.objects.filter(user=request.user).update(must_change_password=False)
    update_session_auth_hash(request, request.user)
    return JsonResponse({'status': 'success'})
