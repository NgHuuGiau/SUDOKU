# Sudoku

> Phiên bản hiện tại: **2.0.0** — giao diện Pygame hiện đại, kiểm thử tự động và lưu dữ liệu theo người dùng.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-1F6FEB)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/Gi%E1%BA%A5y%20ph%C3%A9p-MIT-22C55E)](LICENSE)

Đây là dự án game Sudoku desktop được xây dựng bằng Python và `pygame`, tập trung vào trải nghiệm chơi trực quan, bố cục rõ ràng và thao tác ổn định bằng cả chuột lẫn bàn phím.

Thay vì chỉ là một bảng Sudoku đơn giản, dự án được tổ chức như một ứng dụng hoàn chỉnh với menu mở đầu, nhiều mức độ khó, đồng hồ thời gian, ghi chú, gợi ý, hoàn tác, làm lại, tạm dừng và màn hình chiến thắng riêng.

## Tổng quan dự án

Dự án này phù hợp cho 3 mục đích:

- chơi Sudoku với giao diện đẹp và dễ dùng
- học cách tổ chức một project Python có giao diện bằng `pygame`
- dùng làm đồ án, project cá nhân hoặc dự án trưng bày trên GitHub

Mã nguồn được tách thành các phần riêng cho logic sinh bảng, kiểm tra hợp lệ, vòng lặp game, giao diện hiển thị, lưu dữ liệu và cấu hình ngôn ngữ. Nhờ vậy, dự án dễ đọc, dễ mở rộng và dễ chỉnh sửa hơn.

Xem chi tiết các thay đổi trong [CHANGELOG.md](CHANGELOG.md).

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

- Tạo bảng Sudoku ngẫu nhiên theo các chế độ: `easy`, `medium`, `hard`, `daily`, `custom`
- Kiểm tra tính hợp lệ của số được nhập
- Gợi ý số đúng cho ô đang chọn
- Tự động điền ghi chú khả dĩ
- Kiểm tra thắng khi bảng hiện tại trùng với lời giải
- **Lưu/Tải ván chơi tự động** (lưu sau thao tác với giới hạn tần suất ghi đĩa, tiếp tục ván dở khi mở lại game)
- **Kỷ lục thời gian tốt nhất** theo từng độ khó (lưu cục bộ, hiển thị khi chiến thắng)

### Điều khiển

- Chuột: chọn ô và bấm các nút chức năng
- `W`, `A`, `S`, `D` hoặc phím mũi tên: di chuyển ô chọn
- `1` đến `9`: nhập số
- `Backspace` hoặc `Delete`: xóa ô
- `Esc`: tạm dừng / tiếp tục
- `Ctrl+Z`: Hoàn tác, `Ctrl+Shift+Z` / `Ctrl+Y`: Làm lại (lưu tối đa 200 trạng thái)
- `Space` / `N`: Bật/tắt chế độ ghi chú

### Cấu trúc mã nguồn

- `main.py`: điểm khởi đầu để chạy ứng dụng
- `game.py`: quản lý vòng lặp game, trạng thái và sự kiện
- `logic.py`: xử lý sinh bảng Sudoku và kiểm tra logic
- `ui/`: các thành phần giao diện Pygame, bố cục và tương tác
- `config.py`: quản lý text hiển thị và ngôn ngữ
- `persistence.py`: lưu ván chơi, thống kê, kỷ lục và thử thách hằng ngày
- `sounds.py`: tạo và phát hiệu ứng âm thanh nhẹ bằng Pygame

## Cấu trúc thư mục

```text
SUDOKU/
|-- main.py
|-- game.py
|-- logic.py
|-- ui/
|   |-- board.py
|   |-- colors.py
|   |-- drawing.py
|   |-- fonts.py
|   |-- geometry.py
|   |-- icons.py
|   |-- menu.py
|   |-- modals.py
|   |-- screen.py
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
- Tcl/Tk (cần cho hộp thoại nhập/xuất puzzle; Linux cài thêm gói `python3-tk`)

### Cài thư viện

```bash
pip install -r requirements.txt
```

Lệnh trên chỉ cài dependency chạy game. Để chạy test, lint, type-check và đóng gói:

```bash
pip install -e ".[dev]"
```

### Dữ liệu người dùng

Ván chơi, thống kê, kỷ lục và bảng xếp hạng được lưu trong thư mục dữ liệu riêng của người dùng,
không ghi vào thư mục mã nguồn:

- Windows: `%LOCALAPPDATA%\SudokuMaster`
- macOS: `~/Library/Application Support/SudokuMaster`
- Linux: `$XDG_DATA_HOME/SudokuMaster` hoặc `~/.local/share/SudokuMaster`

Dữ liệu cũ trong thư mục dự án sẽ được sao chép tự động sang vị trí mới khi game chạy lần đầu.
Biến môi trường `SUDOKU_DATA_DIR` có thể dùng để chỉ định thư mục riêng khi test hoặc debug.

### Chạy game

```bash
python main.py
```

### Kiểm tra chất lượng

GitHub Actions chạy test, lint, type-check và quét lỗ hổng dependency trên Python `3.10`, `3.11` và `3.12`; build và smoke-test ứng dụng trên Windows/Linux cho pull request và push lên `main`/`master`. CI có job tổng kết kết quả. Release chỉ được tạo khi push tag phiên bản dạng `v*` (ví dụ `v2.1.0`).

```bash
python -m pytest -q
python -m ruff check .
python -m mypy . --ignore-missing-imports
python -m compileall -q .
python main.py --smoke-test
```

### Đóng gói

```bash
pip install -e ".[build]"
pyinstaller build.spec --clean
```

Trên Windows, có thể chạy nhanh bằng `build.bat`. File thực thi được tạo trong `dist/` và
không nên commit vào repository.

## Vì sao repo này phù hợp để đưa lên GitHub

- Có giao diện thật và ảnh minh họa rõ ràng
- Có phân tách module tương đối sạch
- Có thể dùng làm project học tập, đồ án hoặc sản phẩm portfolio
- Có test logic, test render UI và pipeline CI kiểm tra tự động

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
