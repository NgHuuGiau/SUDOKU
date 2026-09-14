# Sudoku

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-1F6FEB)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/Gi%E1%BA%A5y%20ph%C3%A9p-MIT-22C55E)](LICENSE)

Đây là dự án game Sudoku được xây dựng bằng Python và `pygame`, tập trung vào trải nghiệm chơi trực quan, bố cục rõ ràng và các tính năng hỗ trợ đủ tốt để người chơi có thể giải đố thoải mái ngay trên giao diện desktop.

Thay vì chỉ là một bảng Sudoku đơn giản, dự án được tổ chức như một ứng dụng hoàn chỉnh với menu mở đầu, nhiều mức độ khó, đồng hồ thời gian, ghi chú, gợi ý, hoàn tác, làm lại, tạm dừng và màn hình chiến thắng riêng.

## Tổng quan dự án

Dự án này phù hợp cho 3 mục đích:

- chơi Sudoku với giao diện đẹp và dễ dùng
- học cách tổ chức một project Python có giao diện bằng `pygame`
- dùng làm đồ án, project cá nhân hoặc dự án trưng bày trên GitHub

Mã nguồn được tách thành các phần riêng cho logic sinh bảng, kiểm tra hợp lệ, vòng lặp game, giao diện hiển thị và cấu hình ngôn ngữ. Nhờ vậy, dự án dễ đọc, dễ mở rộng và dễ chỉnh sửa hơn.

## Xem trước giao diện

Ảnh preview dưới đây được chụp trực tiếp từ giao diện hiện tại, sau khi tái thiết kế lại menu, bàn chơi, modal và hệ thống icon.

### Menu chính

<div align="center">
  <img src="./assets/preview/menu.png" alt="Menu" width="60%" />
</div>

Menu mới dùng các thẻ độ khó rõ ràng, thanh điều khiển gọn, icon đồng nhất và hỗ trợ đổi ngôn ngữ, theme, âm thanh.

### Bàn chơi

<div align="center">
  <img src="./assets/preview/game.png" alt="Màn hình chơi" width="60%" />
</div>

Màn hình chơi chia thành bảng `9x9` lớn ở bên trái và sidebar thao tác ở bên phải. Số, trạng thái ô, timer, keypad và các nút hoàn tác được bố trí theo nhóm để dễ quét bằng mắt.

### Tạm dừng

<div align="center">
  <img src="./assets/preview/stop.png" alt="Tạm dừng" width="60%" />
</div>

Modal tạm dừng phủ nền mờ, giữ lại ngữ cảnh bàn chơi và đặt các thao tác tiếp tục, khởi động lại, lưu & thoát trong một cụm nút dễ nhận biết.

### Chiến thắng

<div align="center">
  <img src="./assets/preview/win.png" alt="Chiến thắng" width="60%" />
</div>

Màn hình chiến thắng dùng modal nổi bật với thời gian hoàn thành, icon trophy và hai lựa chọn chơi lại hoặc về menu.

## Điểm nổi bật

- Giao diện desktop rõ ràng, dễ nhìn
- Có menu chọn độ khó riêng trước khi chơi
- Hỗ trợ `ghi chú`, `gợi ý`, `kiểm tra`, `hoàn tác`, `làm lại`
- Điều khiển bằng cả chuột lẫn bàn phím
- Có trạng thái `tạm dừng` và `chiến thắng` riêng
- Có hỗ trợ nội dung tiếng Việt và tiếng Anh

## Tính năng chính

### Lối chơi

- Tạo bảng Sudoku ngẫu nhiên theo 3 mức độ khó: `easy`, `medium`, `hard`
- Kiểm tra tính hợp lệ của số được nhập
- Gợi ý số đúng cho ô đang chọn
- Tự động điền ghi chú khả dĩ
- Kiểm tra thắng khi bảng hiện tại trùng với lời giải
- **Lưu/Tải ván chơi tự động** (tự động lưu sau mỗi thao tác, tiếp tục được ván dở khi mở lại game)
- **Kỷ lục thời gian tốt nhất** theo từng độ khó (lưu cục bộ, hiển thị khi chiến thắng)

### Điều khiển

- Chuột: chọn ô và bấm các nút chức năng
- `W`, `A`, `S`, `D` hoặc phím mũi tên: di chuyển ô chọn
- `1` đến `9`: nhập số
- `Backspace` hoặc `Delete`: xóa ô
- `Esc`: tạm dừng / tiếp tục
- `Ctrl+Z`: Hoàn tác, `Ctrl+Shift+Z` / `Ctrl+Y`: Làm lại
- `Space` / `N`: Bật/tắt chế độ ghi chú

### Cấu trúc mã nguồn

- `main.py`: điểm khởi đầu để chạy ứng dụng
- `game.py`: quản lý vòng lặp game, trạng thái và sự kiện
- `logic.py`: xử lý sinh bảng Sudoku và kiểm tra logic
- `ui/`: các thành phần giao diện Pygame, bố cục và tương tác
- `config.py`: quản lý text hiển thị và ngôn ngữ

## Cấu trúc thư mục

```text
SUDOKU/
|-- main.py
|-- game.py
|-- logic.py
|-- ui/
|   |-- board.py
|   |-- menu.py
|   |-- sidebar.py
|   `-- view.py
|-- config.py
|-- menu.py
|-- requirements.txt
|-- tests/
|   |-- conftest.py
|   |-- test_sudoku.py
|   `-- test_ui_smoke.py
|-- assets/
|   `-- preview/
|       |-- menu.png
|       |-- game.png
|       |-- stop.png
|       |-- win.png
|       `-- SUDOKU.ico
|-- build.spec
|-- build.bat
`-- README.md
```

## Cài đặt nhanh

### Yêu cầu

- Python `3.10+`
- `pip`

### Cài thư viện

```bash
pip install -r requirements.txt
```

Khi phát triển hoặc đóng gói, cài thêm nhóm công cụ tương ứng từ `pyproject.toml`:

```bash
pip install -e ".[dev]"
```

### Dữ liệu người dùng

Ván chơi, thống kê và bảng xếp hạng được lưu trong thư mục dữ liệu riêng của người dùng,
không ghi vào thư mục mã nguồn. Trên Windows, vị trí mặc định là
`%LOCALAPPDATA%\SudokuMaster`. Dữ liệu cũ trong thư mục dự án sẽ được di chuyển tự động
khi game chạy lần đầu.

### Chạy game

```bash
python main.py
```

## Vì sao repo này phù hợp để đưa lên GitHub

- Có giao diện thật và ảnh minh họa rõ ràng
- Có phân tách module tương đối sạch
- Có thể dùng làm project học tập, đồ án hoặc sản phẩm portfolio
- Có sẵn nền tảng để phát triển thêm như lưu ván chơi, xếp hạng thời gian hoặc đóng gói thành file chạy độc lập

## Hướng phát triển tiếp

- [x] Tối ưu thuật toán sinh bảng để đảm bảo lời giải duy nhất tốt hơn
- [x] Lưu và tải lại trạng thái ván chơi
- [x] Ghi nhận thời gian chơi tốt nhất
- [x] Đóng gói thành bản `.exe` cho Windows
- [ ] Bổ sung ảnh GIF hoặc video demo thực tế
- [x] Có hiệu ứng âm thanh khi nhập số, thắng và dùng gợi ý
- [x] Có chế độ Daily Challenge (bảng mới mỗi ngày)
- [x] Có thống kê cơ bản, tỷ lệ thắng và thời gian trung bình

## Giấy phép

Dự án được phát hành theo [giấy phép MIT](LICENSE).
