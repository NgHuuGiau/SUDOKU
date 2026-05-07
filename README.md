# 🎮 Trò Chơi Sudoku Hiện Đại

Một trò chơi Sudoku đẹp mắt, hiện đại được xây dựng bằng Python, Pygame và Tkinter. Thử thách trí tuệ của bạn với giao diện đẹp, âm thanh sống động và tính năng đầy đủ!

## ✨ Tính Năng Nổi Bật

- **🎨 Giao Diện Hiện Đại**: Menu gradient đẹp mắt với Tkinter, bảng chơi mượt mà với Pygame
- **🎯 Chế Độ Khó**: Dễ, Trung bình, Khó - phù hợp mọi trình độ
- **🖱️ Chơi Tương Tác**: Điều khiển bằng chuột và bàn phím
- **💡 Gợi Ý & Ghi Chú**: Hệ thống gợi ý thông minh và ghi chú số có thể
- **↩️ Hoàn Tác/Làm Lại**: Chức năng undo/redo đầy đủ
- **⏱️ Đồng Hồ Thời Gian**: Đếm thời gian thực với khả năng tạm dừng
- **🌍 Đa Ngôn Ngữ**: Hỗ trợ tiếng Anh và tiếng Việt
- **🎆 Kỷ Niệm Chiến Thắng**: Hiệu ứng pháo hoa rực rỡ khi thắng

## 🚀 Bắt Đầu Nhanh

### Yêu Cầu Hệ Thống
- Python 3.8 hoặc cao hơn
- Trình quản lý gói pip

### Cài Đặt

1. **Tải mã nguồn**
   ```bash
   git clone <địa-chỉ-repo-của-bạn>
   cd sudoku
   ```

2. **Cài đặt thư viện phụ thuộc**
   ```bash
   pip install -r requirements.txt
   ```

3. **Chạy trò chơi**
   ```bash
   python main.py
   ```

## 🎯 Cách Chơi

### Điều Khiển
- **Chuột**: Nhấp vào ô và nút
- **WASD/Phím mũi tên**: Di chuyển con trỏ
- **1-9**: Nhập số
- **Backspace/Delete**: Xóa ô
- **Space**: Chuyển chế độ ghi chú

### Tính Năng
- **💡 Gợi Ý**: Nhận một số đúng (có giới hạn)
- **📝 Ghi Chú**: Đánh dấu số có thể trong ô
- **🔍 Kiểm Tra**: Làm nổi bật số sai
- **⏸️ Tạm Dừng**: Dừng/tiếp tục trò chơi
- **↩️ Hoàn Tác**: Quay lại bước trước

## 📁 Cấu Trúc Dự Án

```
sudoku/
├── main.py          # Điểm vào chính của chương trình
├── menu.py          # Giao diện menu Tkinter
├── game.py          # Logic trò chơi Pygame
├── ui.py            # Hằng số và hàm vẽ giao diện
├── logic.py         # Tạo và kiểm tra bảng Sudoku
├── lang.py          # Bản dịch ngôn ngữ
├── requirements.txt # Thư viện Python cần thiết
├── .gitignore       # Quy tắc bỏ qua Git
├── Picture/         # Tài nguyên biểu tượng (tùy chọn)
├── sounds/          # Hiệu ứng âm thanh (tùy chọn)
├── README.md        # Tài liệu này
├── LICENSE          # Giấy phép MIT
└── DEVELOPMENT.md   # Hướng dẫn phát triển
```

## 🎨 Tùy Chỉnh

### Màu Sắc
Chỉnh sửa class `Colors` trong `ui.py` để thay đổi chủ đề.

### Ngôn Ngữ
Thêm ngôn ngữ mới trong dict `ban_dich` của `lang.py`.

### Độ Khó
Sửa số ô trống trong hàm `generate_sudoku()` của `logic.py`.

## 🛠️ Phát Triển

### Thiết Lập Môi Trường Phát Triển
```bash
pip install -e ".[dev]"
```

### Kiểm Tra Chất Lượng Code
- Định dạng: `black .`
- Kiểm tra lỗi: `flake8`
- Kiểm tra kiểu: `mypy`

## 📝 Giấy Phép

Giấy phép MIT - xem file LICENSE để biết chi tiết.

## 🤝 Đóng Góp

1. Fork kho lưu trữ
2. Tạo nhánh tính năng
3. Commit thay đổi
4. Push lên nhánh
5. Tạo Pull Request

## 🙏 Lời Cảm Ơn

- Xây dựng với Pygame và Tkinter
- Lấy cảm hứng từ các trò chơi Sudoku cổ điển

---

**Chúc bạn chơi vui! 🎉**

*Tìm hiểu thêm trong [DEVELOPMENT.md](DEVELOPMENT.md)*