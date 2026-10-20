from django.contrib import admin
from .models import Booking, BookingEvent, RoomType

admin.site.register(RoomType)
admin.site.register(Booking)
admin.site.register(BookingEvent)
