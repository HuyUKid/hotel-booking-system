"""HTTP/JSON: đọc request -> gọi service -> trả dữ liệu cho Frontend."""
import json
from datetime import date
from functools import wraps

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Booking, RoomType
from .services import BookingError, available_rooms, create_booking, parse_dates, process_booking


def handle_errors(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except BookingError as error:
            return JsonResponse({'status': 'error', 'code': error.code, 'message': error.message}, status=error.status)
    return wrapped


def json_body(request):
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        raise BookingError('Body phải là JSON hợp lệ.', 'INVALID_JSON')
    if not isinstance(data, dict):
        raise BookingError('Body phải là object JSON.', 'INVALID_JSON')
    return data


def booking_data(booking, detail=False):
    data = {
        'id': booking.pk, 'code': booking.code,
        'customer_name': booking.customer_name, 'phone': booking.phone,
        'email': booking.email, 'address': booking.address, 'group_name': booking.group_name,
        'source': booking.source, 'arrival_time': str(booking.arrival_time)[:5],
        'check_in': str(booking.check_in), 'check_out': str(booking.check_out),
        'guests': booking.guests, 'quantity': booking.quantity,
        'room_type_id': booking.room_type_id, 'room_type_name': booking.room_type.name,
        'nightly_price': str(booking.nightly_price), 'total_price': str(booking.total_price),
        'guaranteed': booking.guaranteed, 'payment_method': booking.payment_method,
        'notes': booking.notes, 'status': booking.status, 'status_label': booking.get_status_display(),
        'created_by': booking.created_by.username,
        'confirmation_channel': booking.confirmation_channel,
        'reconfirmed_at': booking.reconfirmed_at.isoformat() if booking.reconfirmed_at else None,
    }
    if detail:
        data['events'] = [
            {'description': event.description, 'actor': event.actor.username, 'at': event.created_at.isoformat()}
            for event in booking.events.select_related('actor').order_by('created_at', 'id')
        ]
    return data


@require_GET
def room_types(request):
    return JsonResponse({'status': 'success', 'items': list(RoomType.objects.order_by('id').values())})


@require_GET
@handle_errors
def availability(request):
    start, end = parse_dates(request.GET.get('check_in'), request.GET.get('check_out'))
    items = []
    for room_type in RoomType.objects.order_by('id'):
        items.append({
            'room_type_id': room_type.pk, 'name': room_type.name,
            'total_rooms': room_type.total_rooms,
            'available_rooms': available_rooms(room_type, start, end),
            'nightly_price': str(room_type.nightly_price),
        })
    return JsonResponse({'status': 'success', 'items': items})


@require_http_methods(['GET', 'POST'])
@handle_errors
def bookings(request):
    if request.method == 'POST':
        booking = create_booking(json_body(request), request.user)
        return JsonResponse({'status': 'success', 'booking': booking_data(booking, True)}, status=201)
    rows = Booking.objects.select_related('room_type', 'created_by').order_by('check_in', 'customer_name')
    if request.GET.get('q'):
        query = request.GET['q']
        rows = rows.filter(Q(customer_name__icontains=query) | Q(phone__icontains=query))
    if request.GET.get('status'):
        rows = rows.filter(status=request.GET['status'])
    return JsonResponse({'status': 'success', 'items': [booking_data(row) for row in rows]})


@require_GET
@handle_errors
def booking_detail(request, pk):
    booking = Booking.objects.select_related('room_type', 'created_by').filter(pk=pk).first()
    if booking is None:
        raise BookingError('Không tìm thấy phiếu.', 'NOT_FOUND', 404)
    return JsonResponse({'status': 'success', 'booking': booking_data(booking, True)})


@require_POST
@handle_errors
def booking_action(request, pk):
    booking = process_booking(pk, json_body(request), request.user)
    return JsonResponse({'status': 'success', 'booking': booking_data(booking, True)})


@require_GET
@handle_errors
def handover(request):
    try:
        day = date.fromisoformat(request.GET.get('date', date.today().isoformat()))
    except ValueError:
        raise BookingError('Ngày bàn giao không hợp lệ.')
    confirmed = Booking.objects.select_related('room_type', 'created_by').filter(status='confirmed')
    return JsonResponse({
        'status': 'success', 'date': str(day),
        'arrivals': [booking_data(b) for b in confirmed.filter(check_in=day)],
        'departures': [booking_data(b) for b in confirmed.filter(check_out=day)],
        'staying_rooms': sum(confirmed.filter(check_in__lte=day, check_out__gt=day).values_list('quantity', flat=True)),
        'waiting_count': Booking.objects.filter(status='waiting').count(),
    })
