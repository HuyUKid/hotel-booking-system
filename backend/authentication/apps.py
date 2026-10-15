from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    verbose_name = 'Xác thực nhân viên'

    def ready(self):
        # Đăng ký signal tạo hồ sơ ngay khi Django khởi động ứng dụng.
        from . import signals  # noqa: F401
