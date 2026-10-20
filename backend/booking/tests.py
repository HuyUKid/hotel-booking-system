"""Kiểm thử luồng nghiệp vụ qua API, bao gồm cookie và CSRF thật."""
import json
from datetime import date

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase

from .models import Booking, RoomType
from .services import available_rooms


class BookingFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='staff', password='initial')
        self.user.employeeprofile.must_change_password = False
        self.user.employeeprofile.save()
        self.client.force_login(self.user)
        self.room = RoomType.objects.create(name='Tiêu chuẩn', capacity=2, total_rooms=2, nightly_price=500000)
        self.fields = {
            'customer_name': 'Nguyễn An', 'phone': '0901234567',
            'room_type_id': self.room.pk, 'quantity': 2, 'guests': 3,
            'check_in': '2026-11-01', 'check_out': '2026-11-03',
            'nightly_price': '500000', 'guaranteed': False,
        }

    def post(self, url, fields):
        return self.client.post(url, json.dumps(fields), content_type='application/json')

    def create(self, **overrides):
        response = self.post('/api/booking/bookings/', {**self.fields, **overrides})
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()['booking']

    def action(self, booking, action, **extra):
        return self.post(f"/api/booking/bookings/{booking['id']}/actions/", {'action': action, **extra})

    def confirm(self, booking):
        self.assertEqual(self.action(booking, 'agree').status_code, 200)
        response = self.action(booking, 'confirm', channel='Điện thoại')
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()['booking']

    def free(self):
        return available_rooms(self.room, date(2026, 11, 1), date(2026, 11, 3))

    def test_eight_step_flow_wait_edit_confirm_reconfirm_cancel_and_handover(self):
        booking = self.create()
        self.assertEqual(self.free(), 2)  # Yêu cầu mới chưa giữ phòng.
        self.assertEqual(self.action(booking, 'wait').status_code, 200)
        booking = self.confirm(booking)
        self.assertEqual(booking['total_price'], '2000000')
        self.assertEqual(self.free(), 0)
        self.assertEqual(self.action(booking, 'reconfirm', note='Khách An gọi lại').status_code, 200)
        response = self.action(booking, 'edit', **{**self.fields, 'quantity': 1, 'guests': 2})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['booking']['reconfirmed_at'])
        self.assertEqual(self.free(), 1)
        handover = self.client.get('/api/booking/handover/?date=2026-11-01').json()
        self.assertEqual(len(handover['arrivals']), 1)
        self.assertEqual(handover['staying_rooms'], 1)
        self.assertEqual(self.action(booking, 'cancel').status_code, 400)
        response = self.action(booking, 'cancel', note='Khách An yêu cầu hủy do đổi lịch')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.free(), 2)
        self.assertGreaterEqual(len(response.json()['booking']['events']), 7)
        self.assertEqual(self.action(booking, 'confirm', channel='Email').status_code, 409)

    def test_confirmation_checks_inventory_again_and_does_not_double_confirm(self):
        first, second = self.create(), self.create()
        self.confirm(first)
        self.assertEqual(self.action(first, 'confirm', channel='Email').status_code, 409)
        self.action(second, 'agree')
        response = self.action(second, 'confirm', channel='Email')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['code'], 'NO_AVAILABILITY')
        self.assertEqual(Booking.objects.get(pk=second['id']).status, 'agreed')

    def test_edit_keeps_old_booking_when_new_stay_is_full(self):
        first = self.create()
        second = self.create(check_in='2026-11-03', check_out='2026-11-05')
        self.confirm(first)
        self.confirm(second)
        response = self.action(second, 'edit', **self.fields)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(str(Booking.objects.get(pk=second['id']).check_in), '2026-11-03')

    def test_inventory_counts_peak_per_night_and_allows_back_to_back_stays(self):
        self.confirm(self.create(quantity=1, guests=1, check_out='2026-11-02'))
        self.confirm(self.create(quantity=1, guests=1, check_in='2026-11-02'))
        self.assertEqual(self.free(), 1)  # Hai đơn ở hai đêm khác nhau, không cộng thành 2 phòng.

    def test_invalid_body_dates_capacity_and_price(self):
        self.assertEqual(self.post('/api/booking/bookings/', []).status_code, 400)
        for fields in [
            {'check_out': '2026-11-01'}, {'quantity': -1}, {'guests': 100},
            {'nightly_price': 'NaN'}, {'nightly_price': '-1'}, {'guaranteed': 'yes'},
            {'email': 'invalid'}, {'room_type_id': 999},
        ]:
            response = self.post('/api/booking/bookings/', {**self.fields, **fields})
            self.assertEqual(response.status_code, 400, response.content)
        self.assertFalse(Booking.objects.exists())

    def test_real_booking_endpoints_require_completed_password_change(self):
        anonymous = Client()
        self.assertEqual(anonymous.get('/api/booking/room-types/').status_code, 401)
        self.user.employeeprofile.must_change_password = True
        self.user.employeeprofile.save()
        self.assertEqual(self.client.get('/api/booking/room-types/').status_code, 403)

    def test_csrf_login_password_change_and_booking_flow(self):
        client = Client(enforce_csrf_checks=True)
        token = client.get('/api/csrf/').json()['csrf_token']
        login = client.post('/api/login/', json.dumps({'username': 'staff', 'password': 'initial'}),
                            content_type='application/json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(login.status_code, 200)
        # Django xoay CSRF khi login, Frontend phải lấy token mới.
        token = client.get('/api/csrf/').json()['csrf_token']
        response = client.post('/api/booking/bookings/', json.dumps(self.fields),
                               content_type='application/json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(client.post('/api/booking/bookings/', json.dumps(self.fields),
                                    content_type='application/json').status_code, 403)

    def test_seed_demo_is_repeatable_and_does_not_reset_password(self):
        call_command('seed_demo', verbosity=0)
        demo = User.objects.get(username='demo')
        self.assertTrue(demo.employeeprofile.must_change_password)
        demo.set_password('changed')
        demo.save()
        call_command('seed_demo', verbosity=0)
        demo.refresh_from_db()
        self.assertTrue(demo.check_password('changed'))
