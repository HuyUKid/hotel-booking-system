from django.urls import path
from . import views


urlpatterns = [
    path('room-types/', views.room_types),
    path('availability/', views.availability),
    path('bookings/', views.bookings),
    path('bookings/<int:pk>/', views.booking_detail),
    path('bookings/<int:pk>/actions/', views.booking_action),
    path('handover/', views.handover),
]
