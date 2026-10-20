"""Quy tắc nghiệp vụ đặt tại đây để view và giao diện không phải tự tính."""
from datetime import date, time, timedelta
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Booking, BookingEvent, RoomType


class BookingError(Exception):
    def __init__(self, message, code='INVALID_DATA', status=400):
        self.message, self.code, self.status = message, code, status


def parse_dates(check_in, check_out):
    try:
        start, end = date.fromisoformat(check_in), date.fromisoformat(check_out)
    except (ValueError, TypeError):
        raise BookingError('Ngày phải có định dạng YYYY-MM-DD.')
    if not 0 < (end - start).days <= 365:
        raise BookingError('Ngày đi phải sau ngày đến, tối đa 365 đêm.')
    return start, end


def available_rooms(room_type, start, end, exclude_id=None):
    # Ngày đi không chiếm phòng. Phải xét từng đêm, không cộng tất cả đơn giao nhau.
    bookings = Booking.objects.filter(
        room_type=room_type, status=Booking.Status.CONFIRMED,
        check_in__lt=end, check_out__gt=start,
    ).exclude(pk=exclude_id)
    stays = list(bookings.values('check_in', 'check_out', 'quantity'))
    peak = 0
    day = start
    while day < end:
        used = sum(b['quantity'] for b in stays if b['check_in'] <= day < b['check_out'])
        peak = max(peak, used)
        day += timedelta(days=1)
    return max(0, room_type.total_rooms - peak)


def booking_fields(data):
    """Kiểm tra cả khi tạo mới và khi sửa; không tin dữ liệu từ trình duyệt."""
    fields = {}
    limits = {'customer_name': 120, 'phone': 30, 'email': 254, 'address': 250,
              'group_name': 120, 'source': 80, 'payment_method': 80, 'notes': 3000}
    for name, limit in limits.items():
        value = data.get(name, '')
        if not isinstance(value, str) or len(value.strip()) > limit:
            raise BookingError(f'Trường {name} không hợp lệ hoặc quá dài.')
        fields[name] = value.strip()
    if not fields['customer_name'] or not fields['phone']:
        raise BookingError('Cần tên khách/người đăng ký và số điện thoại.')
    if fields['email']:
        try:
            validate_email(fields['email'])
        except ValidationError:
            raise BookingError('Email không hợp lệ.')
    fields['check_in'], fields['check_out'] = parse_dates(data.get('check_in'), data.get('check_out'))
    try:
        for name in ('guests', 'quantity', 'room_type_id'):
            value = data.get(name)
            if isinstance(value, bool) or not str(value).isdigit() or int(value) < 1:
                raise ValueError
            fields[name] = int(value)
        fields['arrival_time'] = time.fromisoformat(data.get('arrival_time', '14:00'))
        price = Decimal(str(data.get('nightly_price', '')))
        if not price.is_finite() or price < 0 or price > 999999999999 or price != price.to_integral_value():
            raise ValueError
        fields['nightly_price'] = price
    except (ValueError, TypeError, InvalidOperation):
        raise BookingError('Số khách, số phòng, giờ đến hoặc giá phòng không hợp lệ.')
    room_type = RoomType.objects.filter(pk=fields.pop('room_type_id')).first()
    if room_type is None:
        raise BookingError('Loại phòng không tồn tại.')
    if fields['guests'] > room_type.capacity * fields['quantity']:
        raise BookingError('Số khách vượt sức chứa của số phòng đã chọn.')
    if not isinstance(data.get('guaranteed', False), bool):
        raise BookingError('guaranteed phải là true hoặc false.')
    fields['guaranteed'] = data.get('guaranteed', False)
    fields['room_type'] = room_type
    return fields


def log_event(booking, user, description):
    BookingEvent.objects.create(booking=booking, actor=user, description=description)


@transaction.atomic
def create_booking(data, user):
    booking = Booking.objects.create(**booking_fields(data), created_by=user)
    log_event(booking, user, 'B1: Tiếp nhận yêu cầu; dữ liệu đã được lưu để theo dõi.')
    return booking


@transaction.atomic
def process_booking(pk, data, user):
    # Demo ít loại phòng: lấy khóa ghi SQLite trước khi đọc phiếu/tồn phòng.
    # Khi dùng PostgreSQL thực tế có thể thay bằng select_for_update cho loại phòng.
    RoomType.objects.update(total_rooms=F('total_rooms'))
    room_id = Booking.objects.filter(pk=pk).values_list('room_type_id', flat=True).first()
    if room_id is None:
        raise BookingError('Không tìm thấy phiếu.', 'NOT_FOUND', 404)
    booking = Booking.objects.select_related('room_type').get(pk=pk)
    action = data.get('action')
    note = data.get('note', '')
    if not isinstance(note, str) or len(note) > 3000:
        raise BookingError('Ghi chú không hợp lệ.')
    if booking.status in (Booking.Status.CANCELLED, Booking.Status.REJECTED):
        raise BookingError('Phiếu đã kết thúc, không thể sửa.', 'INVALID_STATE', 409)

    if action == 'edit':
        fields = booking_fields(data)
        if booking.status == Booking.Status.CONFIRMED:
            free = available_rooms(fields['room_type'], fields['check_in'], fields['check_out'], pk)
            if fields['quantity'] > free:
                raise BookingError('Không đủ phòng cho thay đổi. Phiếu cũ được giữ nguyên.', 'NO_AVAILABILITY', 409)
        changes = []
        for name, value in fields.items():
            old_value = getattr(booking, name)
            if old_value != value:
                changes.append(f'{name}: {old_value} → {value}')
            setattr(booking, name, value)
        booking.reconfirmed_at = None
        message = 'B7: Sửa thông tin; cần liên hệ khách xác nhận lại. ' + '; '.join(changes) + '. ' + note
    elif action == 'agree' and booking.status in ('pending', 'waiting'):
        booking.status = Booking.Status.AGREED
        message = 'B3–B4: Khách đồng ý phương án; lưu phiếu đặt. ' + note
    elif action in ('wait', 'reject') and booking.status in ('pending', 'waiting', 'agreed'):
        booking.status = Booking.Status.WAITING if action == 'wait' else Booking.Status.REJECTED
        message = ('B3: Đưa vào danh sách chờ. ' if action == 'wait' else 'B3: Khách từ chối phương án. ') + note
    elif action == 'confirm' and booking.status == Booking.Status.AGREED:
        channel = data.get('channel', '')
        if channel not in ('Điện thoại', 'Email', 'Trực tiếp'):
            raise BookingError('Chọn kênh đã liên hệ khẳng định với khách.')
        if booking.quantity > available_rooms(booking.room_type, booking.check_in, booking.check_out, pk):
            raise BookingError('Phòng vừa hết. Hãy thỏa thuận lại hoặc đưa vào danh sách chờ.', 'NO_AVAILABILITY', 409)
        booking.status = Booking.Status.CONFIRMED
        booking.confirmation_channel = channel
        message = f'B5: Nhân viên ghi nhận đã khẳng định với khách qua {channel}. ' + note
    elif action == 'reconfirm' and booking.status == Booking.Status.CONFIRMED:
        booking.reconfirmed_at = timezone.now()
        message = 'B7: Ghi nhận khách khẳng định lại đặt phòng. ' + note
    elif action == 'cancel':
        if not note.strip():
            raise BookingError('Nhập người yêu cầu và lý do hủy trong ghi chú.')
        booking.status = Booking.Status.CANCELLED
        message = 'B7: Hủy phiếu, giải phóng phòng. ' + note
    else:
        raise BookingError('Thao tác không hợp lệ với trạng thái phiếu.', 'INVALID_STATE', 409)
    booking.save()
    log_event(booking, user, message)
    return booking
