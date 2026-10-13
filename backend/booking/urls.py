from django.urls import path

from . import views


urlpatterns = [
    path('api/csrf/', views.api_csrf, name='api_csrf'),
    path('api/session/', views.api_session, name='api_session'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/change-password/', views.api_change_password, name='api_change_password'),
]
