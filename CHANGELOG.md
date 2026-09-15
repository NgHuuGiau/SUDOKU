# Nhật ký thay đổi

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
