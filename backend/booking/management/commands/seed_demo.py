from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from booking.models import RoomType


class Command(BaseCommand):
    help = 'Tạo phòng và tài khoản demo; không ghi đè mật khẩu hoặc dữ liệu đã có.'

    def handle(self, *args, **options):
        for name, capacity, total, price in [('Tiêu chuẩn', 2, 5, 500000), ('Gia đình', 4, 3, 800000)]:
            RoomType.objects.get_or_create(name=name, defaults={
                'capacity': capacity, 'total_rooms': total, 'nightly_price': price,
            })
        user, created = User.objects.get_or_create(username='demo')
        if created:
            user.set_password('demo123')
            user.first_name = 'Nhân viên demo'
            user.save()
            self.stdout.write('Đã tạo demo / demo123. Lần đầu đăng nhập phải đổi mật khẩu.')
        else:
            self.stdout.write('Tài khoản demo đã tồn tại; giữ nguyên mật khẩu và profile.')
        self.stdout.write(self.style.SUCCESS('Danh mục phòng demo sẵn sàng.'))
