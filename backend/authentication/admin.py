from django.contrib import admin

from .models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'must_change_password')
    list_filter = ('must_change_password',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
