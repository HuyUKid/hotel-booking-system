from django.urls import path

from . import views


urlpatterns = [
    path('csrf/', views.api_csrf, name='api_csrf'),
    path('session/', views.api_session, name='api_session'),
    path('login/', views.api_login, name='api_login'),
    path('logout/', views.api_logout, name='api_logout'),
    path('change-password/', views.api_change_password, name='api_change_password'),
]
