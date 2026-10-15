from django.http import JsonResponse

from .models import EmployeeProfile


class BookingAuthenticationMiddleware:
    """Bảo vệ toàn bộ API nghiệp vụ đặt phòng bằng session và trạng thái mật khẩu."""

    booking_prefix = '/api/booking/'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path_info.startswith(self.booking_prefix):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    'status': 'error',
                    'code': 'AUTHENTICATION_REQUIRED',
                    'message': 'Bạn phải đăng nhập để sử dụng chức năng này.',
                },
                status=401,
            )

        if EmployeeProfile.objects.filter(
            user=request.user,
            must_change_password=True,
        ).exists():
            return JsonResponse(
                {
                    'status': 'error',
                    'code': 'PASSWORD_CHANGE_REQUIRED',
                    'message': 'Bạn phải đổi mật khẩu trước khi tiếp tục.',
                },
                status=403,
            )

        return self.get_response(request)
