// Luồng: thao tác trên trang -> gọi API -> hiển thị dữ liệu thật từ Backend.
const bookingForm = document.getElementById('bookingForm');
let roomTypes = [];
let selectedBooking = null;
let editingId = null;
const money = value => Number(value).toLocaleString('vi-VN') + ' đ';
// Luôn escape dữ liệu người dùng trước khi tạo HTML.
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

async function requestData(path, options = {}) {
    const { response, data } = await apiRequest(path, options);
    if (data.code === 'AUTHENTICATION_REQUIRED') location.replace('login.html');
    if (data.code === 'PASSWORD_CHANGE_REQUIRED') location.replace('change-password.html');
    if (!response.ok) throw new Error(data.message || 'Không thực hiện được thao tác.');
    return data;
}

function postData(path, data) {
    return requestData(path, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
    });
}

async function withLoading(button, task) {
    const oldText = button.textContent;
    button.disabled = true;
    button.textContent = 'Đang xử lý…';
    showMessage('');
    try { await task(); }
    catch (error) { showMessage(error.message || 'Không kết nối được Backend.'); }
    finally {
        button.disabled = false;
        if (button.textContent === 'Đang xử lý…') button.textContent = oldText;
    }
}

function showPage(id) {
    for (const name of ['createPage', 'listPage', 'handoverPage']) {
        document.getElementById(name).hidden = name !== id;
    }
}

function resetForm() {
    bookingForm.reset();
    editingId = null;
    document.getElementById('formTitle').textContent = 'B1. Tiếp nhận yêu cầu đặt phòng';
    document.getElementById('saveButton').textContent = 'Lưu yêu cầu';
    document.getElementById('availabilityResult').textContent = '';
    setBasePrice();
}

function setBasePrice() {
    const room = roomTypes.find(item => item.id === Number(bookingForm.elements.room_type_id.value));
    if (room) bookingForm.elements.nightly_price.value = room.nightly_price;
}

async function checkAvailability() {
    const query = new URLSearchParams({
        check_in: bookingForm.elements.check_in.value, check_out: bookingForm.elements.check_out.value
    });
    const data = await requestData('/api/booking/availability/?' + query);
    document.getElementById('availabilityResult').innerHTML = '<h3>B2. Số phòng có thể đáp ứng</h3>' +
        '<p class="muted">Kết quả hiện tại, được kiểm tra lại khi khẳng định. Khi sửa phiếu, bảng này vẫn tính cả phiếu cũ.</p>' +
        '<ul>' + data.items.map(room => `<li>${escapeHtml(room.name)}: còn <strong>${room.available_rooms}/${room.total_rooms}</strong> phòng · ${money(room.nightly_price)}/đêm</li>`).join('') + '</ul>';
}

function bookingTable(rows) {
    if (!rows.length) return '<p class="muted">Chưa có phiếu phù hợp.</p>';
    return `<table><thead><tr><th>Mã / khách</th><th>Kỳ lưu trú</th><th>Phòng</th><th>Trạng thái</th><th></th></tr></thead><tbody>${rows.map(row => `
        <tr><td>${escapeHtml(row.code)}<br>${escapeHtml(row.customer_name)}<br>${escapeHtml(row.phone)}</td>
        <td>${escapeHtml(row.check_in)} → ${escapeHtml(row.check_out)}</td>
        <td>${escapeHtml(row.room_type_name)} × ${row.quantity}</td><td>${escapeHtml(row.status_label)}</td>
        <td><button data-open="${row.id}">Mở phiếu</button></td></tr>`).join('')}</tbody></table>`;
}

async function loadBookings() {
    const query = new URLSearchParams(new FormData(document.getElementById('filters')));
    const data = await requestData('/api/booking/bookings/?' + query);
    document.getElementById('bookingList').innerHTML = bookingTable(data.items);
}

async function openBooking(id) {
    const data = await requestData(`/api/booking/bookings/${id}/`);
    selectedBooking = data.booking;
    renderDetail();
}

function renderDetail() {
    const b = selectedBooking;
    const ended = ['cancelled', 'rejected'].includes(b.status);
    const button = (action, label, css = '') => `<button data-action="${action}" class="${css}">${label}</button>`;
    let actions = '';
    if (['pending', 'waiting'].includes(b.status)) actions += button('agree', 'B3–B4. Khách đồng ý / lưu phiếu');
    if (['pending', 'agreed', 'waiting'].includes(b.status)) {
        actions += button('wait', 'Đưa vào danh sách chờ', 'secondary');
        actions += button('reject', 'Khách không đồng ý', 'secondary');
    }
    if (b.status === 'agreed') actions += button('confirm', 'B5. Đã liên hệ khẳng định với khách');
    if (b.status === 'confirmed') actions += button('reconfirm', 'B7. Khách khẳng định lại');
    if (!ended) {
        actions += button('edit', 'B7. Sửa thông tin', 'secondary');
        actions += button('cancel', 'Hủy phiếu', 'danger');
    }
    const detail = document.getElementById('bookingDetail');
    detail.hidden = false;
    detail.innerHTML = `<hr><h2>${escapeHtml(b.code)} · ${escapeHtml(b.status_label)}</h2>
        <div class="grid"><p><strong>Khách:</strong> ${escapeHtml(b.customer_name)}<br>
        Điện thoại: ${escapeHtml(b.phone)}<br>Email: ${escapeHtml(b.email)}<br>Địa chỉ: ${escapeHtml(b.address)}<br>Đoàn: ${escapeHtml(b.group_name)}</p>
        <p><strong>Lưu trú:</strong> ${escapeHtml(b.check_in)} → ${escapeHtml(b.check_out)} · ${escapeHtml(b.arrival_time)}<br>
        ${escapeHtml(b.room_type_name)} × ${b.quantity} phòng · ${b.guests} khách<br>
        ${money(b.nightly_price)}/phòng/đêm · Tổng: <strong>${money(b.total_price)}</strong><br>
        ${b.guaranteed ? 'Có đảm bảo' : 'Không đảm bảo'} · ${escapeHtml(b.payment_method)}</p></div>
        <p>Yêu cầu / dịch vụ: ${escapeHtml(b.notes) || 'Không có'}<br>Người tiếp nhận: ${escapeHtml(b.created_by)}<br>
        Kênh khẳng định: ${escapeHtml(b.confirmation_channel) || 'Chưa có'}</p>
        <p class="muted">B5 là ghi nhận nhân viên đã liên hệ; hệ thống demo không tự gửi email hay gọi điện.</p>
        <label>Kênh khẳng định<select id="confirmChannel"><option>Điện thoại</option><option>Email</option><option>Trực tiếp</option></select></label>
        <label>Ghi chú xử lý (khi hủy: ghi người yêu cầu và lý do)<textarea id="actionNote" maxlength="3000"></textarea></label>
        <div class="actions">${actions}<button id="printButton" class="secondary">In phiếu</button></div>
        <h3>Lịch sử lưu hồ sơ</h3><div class="history">${b.events.map(event => `<p>${escapeHtml(event.description)}<br><small>${escapeHtml(event.actor)} · ${escapeHtml(new Date(event.at).toLocaleString('vi-VN'))}</small></p>`).join('')}</div>`;
}

async function runAction(action) {
    if (action === 'edit') {
        editingId = selectedBooking.id;
        for (const element of bookingForm.elements) {
            if (element.name && selectedBooking[element.name] !== undefined) element.value = String(selectedBooking[element.name]);
        }
        document.getElementById('formTitle').textContent = 'B7. Sửa phiếu ' + selectedBooking.code;
        document.getElementById('saveButton').textContent = 'Lưu thay đổi';
        document.getElementById('availabilityResult').textContent = '';
        showPage('createPage');
        return;
    }
    if (action === 'cancel' && !window.confirm('Xác nhận hủy phiếu này?')) return;
    const data = await postData(`/api/booking/bookings/${selectedBooking.id}/actions/`, {
        action, channel: document.getElementById('confirmChannel').value,
        note: document.getElementById('actionNote').value
    });
    selectedBooking = data.booking;
    renderDetail();
    await loadBookings();
    showMessage('Đã cập nhật phiếu và lưu lịch sử.', false);
}

async function loadHandover() {
    const query = new URLSearchParams(new FormData(document.getElementById('handoverForm')));
    const data = await requestData('/api/booking/handover/?' + query);
    document.getElementById('handoverResult').innerHTML = `
        <p>Đang sử dụng dự kiến: <strong>${data.staying_rooms}</strong> phòng · Danh sách chờ: ${data.waiting_count} phiếu</p>
        <h3>Khách dự kiến đến</h3><div class="table-wrap">${bookingTable(data.arrivals)}</div>
        <h3>Khách dự kiến đi</h3><div class="table-wrap">${bookingTable(data.departures)}</div>`;
}

bookingForm.addEventListener('submit', event => {
    event.preventDefault();
    withLoading(document.getElementById('saveButton'), async () => {
        const fields = Object.fromEntries(new FormData(bookingForm));
        fields.guaranteed = fields.guaranteed === 'true';
        const data = editingId
            ? await postData(`/api/booking/bookings/${editingId}/actions/`, { ...fields, action: 'edit' })
            : await postData('/api/booking/bookings/', fields);
        selectedBooking = data.booking;
        resetForm();
        showPage('listPage');
        await loadBookings();
        renderDetail();
        showMessage('Đã lưu phiếu. Mở phần chi tiết để tiếp tục thỏa thuận và khẳng định.', false);
    });
});
document.getElementById('checkButton').onclick = event => withLoading(event.target, checkAvailability);
document.getElementById('resetButton').onclick = resetForm;
document.getElementById('roomType').onchange = setBasePrice;
document.getElementById('filters').onsubmit = event => {
    event.preventDefault(); withLoading(event.submitter, loadBookings);
};
document.getElementById('handoverForm').onsubmit = event => {
    event.preventDefault(); withLoading(event.submitter, loadHandover);
};
document.querySelector('nav').addEventListener('click', event => {
    const id = event.target.dataset.page;
    if (!id) return;
    withLoading(event.target, async () => {
        showPage(id);
        if (id === 'listPage') await loadBookings();
        if (id === 'handoverPage') await loadHandover();
    });
});
document.getElementById('app').addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button) return;
    if (button.dataset.open) withLoading(button, async () => {
        document.getElementById('bookingDetail').hidden = true;
        showPage('listPage'); await loadBookings(); await openBooking(button.dataset.open);
    });
    if (button.dataset.action) withLoading(button, () => runAction(button.dataset.action));
    if (button.id === 'printButton') window.print();
});
document.getElementById('logoutButton').onclick = event => withLoading(event.target, async () => {
    const { response, data } = await apiRequest('/api/logout/', { method: 'POST' });
    if (!response.ok && response.status !== 401) throw new Error(data.message);
    location.replace('login.html');
});

async function initializeApp() {
    try {
        const session = await getSession();
        if (!session) { location.replace('login.html'); return; }
        if (session.must_change_password) { location.replace('change-password.html'); return; }
        document.getElementById('employeeName').textContent = session.display_name;
        const data = await requestData('/api/booking/room-types/');
        roomTypes = data.items;
        if (!roomTypes.length) throw new Error('Chưa có loại phòng. Chạy lệnh manage.py seed_demo ở Backend rồi tải lại.');
        document.getElementById('roomType').innerHTML = roomTypes.map(room => `<option value="${room.id}">${escapeHtml(room.name)} · ${room.capacity} khách/phòng</option>`).join('');
        setBasePrice();
        const today = new Date();
        const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
        document.querySelector('#handoverForm input').value = localDate;
        document.getElementById('app').hidden = false;
        showMessage('');
    } catch (error) { showMessage(error.message || 'Không kết nối được Backend.'); }
}
initializeApp();
