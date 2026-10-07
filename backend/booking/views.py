import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import EmployeeProfile

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không được hỗ trợ'}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            profile, _ = EmployeeProfile.objects.get_or_create(user=user)

            return JsonResponse({
                'status': 'success',
                'username': user.username,
                'must_change_password': profile.must_change_password
            }, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Sai tên đăng nhập hoặc mật khẩu'}, status=401)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def api_change_password(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không được hỗ trợ'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Chưa đăng nhập'}, status=401)

    try:
        data = json.loads(request.body)
        new_password = data.get('new_password')

        if not new_password:
            return JsonResponse({'status': 'error', 'message': 'Mật khẩu mới không được để trống'}, status=400)

        # Kiểm tra độ an toàn mật khẩu
        try:
            validate_password(new_password, request.user)
        except ValidationError as err:
            return JsonResponse({'status': 'error', 'message': list(err.messages)}, status=400)

        # Đặt mật khẩu mới và gỡ cờ bắt buộc đổi
        request.user.set_password(new_password)
        request.user.save()

        profile, _ = EmployeeProfile.objects.get_or_create(user=request.user)
        profile.must_change_password = False
        profile.save()

        return JsonResponse({'status': 'success', 'message': 'Đổi mật khẩu thành công'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
