"""Ba bảng đơn giản: loại phòng, phiếu đặt và lịch sử xử lý."""
from django.conf import settings
from django.db import models


class RoomType(models.Model):
    name = models.CharField(max_length=80, unique=True)
    capacity = models.PositiveIntegerField(default=2)
    total_rooms = models.PositiveIntegerField(default=5)
    nightly_price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return self.name


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Mới tiếp nhận'
        WAITING = 'waiting', 'Danh sách chờ'
        AGREED = 'agreed', 'Đã thỏa thuận / lưu phiếu'
        CONFIRMED = 'confirmed', 'Đã khẳng định với khách'
        REJECTED = 'rejected', 'Khách không đồng ý'
        CANCELLED = 'cancelled', 'Đã hủy'

    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=250, blank=True)
    group_name = models.CharField(max_length=120, blank=True)
    source = models.CharField(max_length=80, default='Điện thoại')
    arrival_time = models.TimeField(default='14:00')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    nightly_price = models.DecimalField(max_digits=12, decimal_places=0)
    guaranteed = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=80, default='Tiền mặt')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    confirmation_channel = models.CharField(max_length=80, blank=True)
    reconfirmed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def code(self):
        return f'DP{self.pk:05d}'

    @property
    def total_price(self):
        return (self.check_out - self.check_in).days * self.quantity * self.nightly_price

    def __str__(self):
        return f'{self.code} - {self.customer_name}'


class BookingEvent(models.Model):
    booking = models.ForeignKey(Booking, related_name='events', on_delete=models.CASCADE)
    description = models.TextField()
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
