import json

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import EmployeeProfile


def _must_change_password(user):
    return EmployeeProfile.objects.filter(user=user, must_change_password=True).exists()


def _unauthorized():
    return JsonResponse(
        {'status': 'error', 'message': 'Phiên đăng nhập không hợp lệ hoặc đã hết hạn.'},
        status=401,
    )


def _json_body(request):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse(
            {'status': 'error', 'message': 'Dữ liệu gửi lên không hợp lệ.'},
            status=400,
        )


@require_GET
@ensure_csrf_cookie
def api_csrf(request):
    return JsonResponse({'status': 'success', 'csrf_token': get_token(request)})


@require_GET
def api_session(request):
    if not request.user.is_authenticated:
        return _unauthorized()
    return JsonResponse({
        'status': 'success',
        'username': request.user.get_full_name() or request.user.username,
        'must_change_password': _must_change_password(request.user),
    })


@require_POST
def api_login(request):
    data, error_response = _json_body(request)
    if error_response:
        return error_response

    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))
    if not username or not password:
        return JsonResponse(
            {'status': 'error', 'message': 'Vui lòng nhập tên đăng nhập và mật khẩu.'},
            status=400,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse(
            {'status': 'error', 'message': 'Tên đăng nhập hoặc mật khẩu không đúng.'},
            status=401,
        )

    login(request, user)
    return JsonResponse({
        'status': 'success',
        'username': user.get_full_name() or user.username,
        'must_change_password': _must_change_password(user),
    })


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
    if new_password != confirm_password:
        return JsonResponse(
            {'status': 'error', 'message': 'Mật khẩu xác nhận không khớp.'},
            status=400,
        )

    try:
        validate_password(new_password, request.user)
    except ValidationError as exc:
        return JsonResponse(
            {'status': 'error', 'message': ' '.join(exc.messages)},
            status=400,
        )

    request.user.set_password(new_password)
    request.user.save(update_fields=['password'])
    EmployeeProfile.objects.filter(user=request.user).update(must_change_password=False)
    update_session_auth_hash(request, request.user)
    return JsonResponse({'status': 'success'})
