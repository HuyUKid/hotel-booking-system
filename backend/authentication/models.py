from django.contrib.auth.models import User
from django.db import models


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    must_change_password = models.BooleanField(default=True)

    class Meta:
        # Giữ nguyên bảng cũ khi chuyển model từ app booking sang authentication.
        db_table = 'booking_employeeprofile'

    def __str__(self):
        return self.user.username
