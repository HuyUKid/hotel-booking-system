"""Kiểm thử trình duyệt tùy chọn, dùng SQLite tạm; không sửa database của người dùng.

Chạy bằng Python trong backend/venv sau khi cài playwright.
Hai cổng 8000 và 5501 cần đang trống.
"""
import os
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


def check():
    import django
    from django.conf import settings
    from django.core.management import call_command
    from django.core.wsgi import get_wsgi_application
    from playwright.sync_api import sync_playwright, expect

    with tempfile.TemporaryDirectory(prefix='hotel-demo-') as folder:
        settings.DATABASES['default']['NAME'] = str(Path(folder) / 'test.sqlite3')
        settings.ALLOWED_HOSTS = ['127.0.0.1']
        django.setup()
        call_command('migrate', verbosity=0)
        call_command('seed_demo', verbosity=0)
        api_server = make_server('127.0.0.1', 8000, get_wsgi_application())
        try:
            web_server = ThreadingHTTPServer(('127.0.0.1', 5501), partial(
                SimpleHTTPRequestHandler, directory=str(ROOT / 'frontend'),
            ))
        except Exception:
            api_server.server_close()
            raise
        for server in (api_server, web_server):
            threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as playwright:
                # Dùng Chromium đã có nếu máy chưa tải phiên bản do Playwright hiện tại yêu cầu.
                cached = sorted((Path(os.environ.get('LOCALAPPDATA', '')) / 'ms-playwright').glob(
                    'chromium-*/chrome-win64/chrome.exe'
                ))
                browser = playwright.chromium.launch(
                    executable_path=str(cached[-1]) if cached else None, headless=True,
                )
                try:
                    page = browser.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.goto('http://127.0.0.1:5501/login.html')
                    page.locator('[name=username]').fill('demo')
                    page.locator('[name=password]').fill('wrong')
                    page.get_by_role('button', name='Đăng nhập', exact=True).click()
                    expect(page.locator('#message')).to_contain_text('không đúng')
                    page.locator('[name=password]').fill('demo123')
                    page.get_by_role('button', name='Đăng nhập', exact=True).click()
                    page.wait_for_url('**/change-password.html')
                    page.locator('[name=new_password]').fill('new123')
                    page.locator('[name=confirm_password]').fill('new123')
                    page.get_by_role('button', name='Lưu mật khẩu').click()
                    page.wait_for_url('**/index.html')
                    expect(page.locator('#app')).to_be_visible()
                    page.locator('[name=customer_name]').fill('Khách kiểm thử')
                    page.locator('[name=phone]').fill('0901234567')
                    page.locator('[name=check_in]').fill('2026-11-01')
                    page.locator('[name=check_out]').fill('2026-11-03')
                    page.locator('[name=quantity]').fill('2')
                    page.locator('[name=guests]').fill('3')
                    page.locator('#checkButton').click()
                    expect(page.locator('#availabilityResult')).to_contain_text('5/5')
                    page.locator('#saveButton').click()
                    expect(page.locator('#bookingDetail')).to_be_visible()
                    page.locator('[data-action=agree]').click()
                    expect(page.locator('[data-action=confirm]')).to_be_visible()
                    page.locator('[data-action=confirm]').click()
                    expect(page.locator('#bookingDetail h2')).to_contain_text('Đã khẳng định')
                    page.locator('[data-action=reconfirm]').click()
                    expect(page.locator('.history')).to_contain_text('Ghi nhận khách khẳng định lại')
                    page.locator('[data-action=edit]').click()
                    expect(page.locator('#createPage')).to_be_visible()
                    page.locator('[name=quantity]').fill('1')
                    page.locator('[name=guests]').fill('2')
                    page.locator('#saveButton').click()
                    expect(page.locator('#bookingDetail')).to_contain_text('× 1 phòng')
                    page.locator('[data-page=handoverPage]').click()
                    page.locator('#handoverForm input').fill('2026-11-01')
                    page.get_by_role('button', name='Xem bàn giao', exact=True).click()
                    expect(page.locator('#handoverResult')).to_contain_text('Khách kiểm thử')
                    page.locator('#handoverResult [data-open]').click()
                    expect(page.locator('#bookingDetail')).to_be_visible()
                    page.locator('#actionNote').fill('Khách kiểm thử yêu cầu hủy vì đổi lịch')
                    page.once('dialog', lambda dialog: dialog.accept())
                    page.locator('[data-action=cancel]').click()
                    expect(page.locator('#bookingDetail h2')).to_contain_text('Đã hủy')
                    page.set_viewport_size({'width': 390, 'height': 844})
                    page.locator('[data-page=createPage]').click()
                    overflow = page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
                    assert not overflow, 'Trang form bị tràn ngang trên điện thoại'
                    page.locator('#logoutButton').click()
                    page.wait_for_url('**/login.html')
                    page.goto('http://127.0.0.1:5501/index.html')
                    page.wait_for_url('**/login.html')
                    assert not errors, errors
                    print('PASS: login, password change, availability, create, agree, confirm, edit, cancel, handover, mobile, logout')
                finally:
                    browser.close()
        finally:
            for server in (api_server, web_server):
                server.shutdown()
                server.server_close()
            from django.db import connections
            connections.close_all()


if __name__ == '__main__':
    check()
