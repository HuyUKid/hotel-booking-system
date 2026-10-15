from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EmployeeProfile


@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, raw=False, **kwargs):
    """Mỗi tài khoản mới luôn có hồ sơ xác định luồng đổi mật khẩu lần đầu."""
    if not created or raw:
        return

    EmployeeProfile.objects.get_or_create(
        user=instance,
        defaults={'must_change_password': not instance.is_superuser},
    )
