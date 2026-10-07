from django.urls import path
from .views import api_login, api_change_password

urlpatterns = [
    path('login/', api_login, name='api_login'),
    path('change-password/', api_change_password, name='api_change_password'),
]