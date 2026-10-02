# Nhật ký thay đổi

## Chưa phát hành

### Bảo trì

- Lưu lựa chọn ngôn ngữ và âm thanh vào thiết lập cục bộ; hiện thông báo trong game khi không thể ghi ván lưu.
- Thêm điều hướng menu bằng Tab/Shift+Tab và Enter/Space kèm chỉ dẫn hiển thị; CI kiểm thử Python 3.13 và metadata giới hạn phạm vi 3.10–3.13.
- Bỏ vòng lặp Game.run không còn caller và tham số không dùng trong solver DLX.
- Bỏ kiểm tra Tcl/Tk khỏi smoke test, `build.spec` và CI vì game không còn dùng Tkinter.
- Tắt pytest cache provider và lọc warning của `pygame`/`pkg_resources` để output kiểm thử sạch (thư mục cache bị khóa ghi trên máy Windows dùng OneDrive).
- Bổ sung test cho các nhánh xử lý chuột/bàn phím, modal nhập text, luồng thắng và menu (coverage tổng 82%); render lại ảnh preview README theo đúng giao diện hiện tại.
- Chuyển thư mục dữ liệu tạm của test ra system temp để OneDrive không khóa file gây fail ngẫu nhiên.

- Cập nhật README đầy đủ về kiến trúc, luồng dữ liệu, cài đặt, lưu dữ liệu, kiểm thử, CI, đóng gói và giới hạn hiện tại; xác nhận giao diện hỗ trợ Tiếng Việt có dấu và English.
- Dùng snapshot bảng xếp hạng trong lúc mở modal thay vì đọc JSON ở từng khung hình; tái sử dụng bề mặt phủ mờ của các modal.
- Lọc hạt pháo hoa trong một lượt tuyến tính, tránh xóa từng phần tử giữa danh sách khi hiệu ứng kết thúc.
- Đóng cửa sổ Tcl/Tk trong mọi trường hợp sau hộp thoại nhập tên; chỉ chấp nhận ký tự bàn phím ASCII `1`–`9` để tránh lỗi chuyển đổi ký tự số Unicode đặc biệt.
- Bổ sung kiểm tra đồng bộ khóa dịch tiếng Anh/tiếng Việt cho menu và hồi quy lưu snapshot bảng xếp hạng.

- Tối ưu render bàn Sudoku bằng cache bề mặt, tái sử dụng hình chữ nhật và chỉ tính ô xung đột một lần mỗi khung hình.
- Chuẩn hóa định dạng toàn bộ mã Python bằng Ruff và bỏ tham số không sử dụng khi ghi nhận Daily Challenge.
- Bỏ getter thời gian tốt nhất chỉ chuyển tiếp và mức log chưa được sử dụng.
- Loại bỏ bộ đo hiệu năng và các lớp thực thi an toàn/circuit breaker chưa được game sử dụng.
- Bỏ API tương thích, bảng màu Tkinter cũ, kiểu dữ liệu và tài nguyên không được ứng dụng dùng.
- Dùng trực tiếp bộ nạp thống kê hằng ngày và xóa các alias bố cục trùng lặp.
- Bỏ ghi thống kê ván chưa có màn hình hiển thị; vẫn giữ nguyên dữ liệu cũ khi lưu theme.
- Chỉ nhúng icon ứng dụng vào bản build, không đóng gói ảnh README.

### Lối chơi và dữ liệu

- Đồng bộ Daily Challenge theo ngày UTC và dùng đúng bộ sinh puzzle hằng ngày khi bắt đầu hoặc chơi lại.
- Từ chối puzzle JSON có nhiều hơn một lời giải; giữ puzzle nhập vào trong nhóm độ khó tùy chỉnh.
- Lưu mục tiêu ô trống của chế độ tùy chỉnh để chơi lại và tiếp tục ván đúng thiết lập.
- Chỉ lưu tối đa 50 trạng thái undo gần nhất xuống đĩa (phiên chơi vẫn giữ đủ 200) để file save gọn nhẹ.
- Đánh dấu hoàn tất di chuyển dữ liệu cũ để không tự khôi phục file lưu sau khi người chơi xóa ván.
- Khởi tạo lại bộ đếm tự lưu theo phiên hiện tại khi tải game.
- Chỉ đọc save và thống kê khi vào menu/thành ván, không nạp lại JSON ở mỗi khung hình.

### Giao diện

- Layout mới hoàn toàn: menu 1 cột giữa (logo, resume, daily, 4 hàng độ khó, hàng nút tròn); màn chơi về layout sidebar dọc + footer quen thuộc trên nền theme mới, icon giữ màu theo token, thêm pill đếm lỗi sai live cạnh bàn phím số.
- Canh chữ theo số đo: tab Daily rộng theo nhãn, nút toggle dùng dot trạng thái thay chữ ON, toolbar cao 48px hết cạ icon/label, dãy số 2 dòng (số + còn lại).
- Nới huy hiệu độ khó header (220px + chữ badge) và nút Tạm dừng (132px) để "Thử thách hàng ngày"/"Tạm dừng" hết tràn.
- Sửa màn thắng: dùng đúng key dịch kỷ lục, dãn layout hết đè huy hiệu/nút.
- Modal tạm dừng: cảnh báo xuống 2 dòng hết tràn thẻ, nút rộng 126px, nút restart dùng chữ "Chơi lại" gọn.
- Tương phản toàn UI đạt chuẩn đọc: nút rực dùng chữ đậm `BTN_VIVID_TEXT`, đậm hóa số người chơi, ghi chú, nhãn active, chữ phụ và số đã xong (chỉ còn badge trang trí dưới chuẩn, luôn đi kèm nhãn đầy đủ).
- Chữ to rõ hơn: font badge 15→16px, số bàn phím lên medium, icon tools 18px; dãy số 2 dòng hết đè pill cũ.
- Footer thu hẹp đúng chiều rộng board, hết đè 2 nút đáy; vẽ lại icon bóng đèn (tia sáng), cúp (quai cầm), tẩy (2 tone) và nét icon đậm hơn.
- Lấp cột phải màn chơi bằng thẻ thông tin (độ khó, kỷ lục, streak) thay khoảng trống.- Hệ icon màu theo design token: 17 token `ICON_*` cho cả 4 theme (Undo tím, Notes xanh, Hint vàng, Erase coral, Timer cyan, Daily/Streak cam, Leaderboard/Victory vàng...), tile nền tint tự thích ứng Light/Dark; nút hỗ trợ màu icon riêng, Notes bật có glow.
- Sidebar có pill đếm lỗi sai live (icon khiên + số), bàn phím số và victory modal hiển thị kỷ lục + huy hiệu NEW BEST; viền ô đang chọn dày hơn.
- Lột xác toàn bộ giao diện sang phong cách kẹo ngọt phẳng: 4 theme mới (Nắng, Đêm, Bạc hà, Đào), nút phẳng bo tròn lớn, kiểm tra tương phản chữ/nền đạt chuẩn đọc.
- Thay cả ba hộp thoại Tcl/Tk (nhập ván, xuất ván, nhập tên kỷ lục) bằng modal nhập text và thông báo toast vẽ trong game; sao chép clipboard qua `pygame.scrap`, không còn cần Tcl/Tk.
- Sửa số ô trống hiển thị ở độ khó Khó và giải thích giới hạn của chế độ tùy chỉnh.
- Bổ sung tab tùy chỉnh, hiển thị đủ TOP 10 và bản dịch cho trạng thái bảng xếp hạng trống.
- Dùng bản dịch hiện hành cho bộ đếm số còn thiếu trên bàn phím.
- Dịch đúng tên độ khó trong header và các hộp thoại nhập/xuất puzzle.
- Cập nhật ảnh preview theo giao diện và số ô trống hiện tại.
- Đánh dấu màn hình thống kê tổng quan là tính năng chưa triển khai trong README.

## [2.0.0] - 2026-09-16

### Giao diện

- Làm mới menu, bảng Sudoku, sidebar, modal tạm dừng và màn hình chiến thắng.
- Tăng kích thước chữ và bảng chơi để dễ đọc hơn.
- Sắp xếp nút thao tác thành các nhóm rõ ràng, tránh tràn chữ.
- Thay icon xuất/nhập ván bằng biểu tượng upload/download vector.
- Thêm cơ chế tự co nhãn chữ theo kích thước nút.

### Lõi ứng dụng

- Tách logic Sudoku, persistence, âm thanh và renderer UI thành các module riêng.
- Cải thiện lưu JSON an toàn bằng ghi file tạm và thay thế nguyên tử.
- Kiểm tra dữ liệu puzzle nhập vào và bảo đảm lời giải hợp lệ.
- Dùng bộ sinh ngẫu nhiên cục bộ để không ảnh hưởng trạng thái random toàn cục.

### Dữ liệu và bảo trì

- Lưu dữ liệu runtime trong thư mục riêng của người dùng.
- Tự động di chuyển dữ liệu cũ từ thư mục dự án khi chạy lần đầu.
- Loại bỏ module không được sử dụng và các file build/cache khỏi repository.
- Đồng bộ dependency giữa `requirements.txt`, `pyproject.toml` và CI.

### Kiểm thử và đóng gói

- Bổ sung test render UI chạy headless.
- Bổ sung kiểm tra các control trong sidebar không bị chồng lấn hoặc vượt màn hình.
- CI chạy test, Ruff, mypy và build đa nền tảng.
- Build Windows `.exe` thành công bằng PyInstaller.
