# Nhật ký thay đổi

## Chưa phát hành

### Bảo trì

- Lưu lựa chọn ngôn ngữ và âm thanh vào thiết lập cục bộ; hiện thông báo trong game khi không thể ghi ván lưu.
- Thêm điều hướng menu bằng Tab/Shift+Tab và Enter/Space kèm chỉ dẫn hiển thị; CI kiểm thử Python 3.13 và metadata giới hạn phạm vi 3.10–3.13.
- Bỏ vòng lặp Game.run không còn caller và tham số không dùng trong solver DLX.

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
- Đánh dấu hoàn tất di chuyển dữ liệu cũ để không tự khôi phục file lưu sau khi người chơi xóa ván.
- Khởi tạo lại bộ đếm tự lưu theo phiên hiện tại khi tải game.
- Chỉ đọc save và thống kê khi vào menu/thành ván, không nạp lại JSON ở mỗi khung hình.

### Giao diện

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
