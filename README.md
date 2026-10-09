# Sudoku Master

> Game Sudoku desktop viết bằng Python và Pygame · Phiên bản **2.0.0**

[![Python](https://img.shields.io/badge/Python-3.10--3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-1F6FEB)](https://www.pygame.org/)
[![Giấy phép MIT](https://img.shields.io/badge/Gi%E1%BA%A5y%20ph%C3%A9p-MIT-22C55E)](LICENSE)

Sudoku Master là dự án game chạy trực tiếp trên máy tính, hướng đến trải nghiệm chơi gọn gàng, dễ đọc và thuận tiện để khám phá mã nguồn. Ứng dụng có menu, bàn Sudoku, nhiều mức độ khó, lưu ván cục bộ, bảng xếp hạng và hai ngôn ngữ giao diện: **Tiếng Việt** và **English**.

Đây là ứng dụng desktop ngoại tuyến: dự án không có máy chủ, API web, cơ sở dữ liệu hay đồng bộ đám mây. Dữ liệu trò chơi được lưu dưới dạng JSON trên máy người chơi. Nhật ký thay đổi nằm trong [CHANGELOG.md](CHANGELOG.md).

## Ảnh giao diện

Các ảnh dưới đây là ảnh chụp từ giao diện hiện tại trong `assets/preview/`.

### Menu chính

<div align="center">
  <img src="./assets/preview/menu.png" alt="Menu chính của Sudoku Master" width="70%" />
</div>

### Bàn chơi

<div align="center">
  <img src="./assets/preview/game.png" alt="Bàn chơi Sudoku và bảng công cụ" width="70%" />
</div>

### Tạm dừng và chiến thắng

<div align="center">
  <img src="./assets/preview/stop.png" alt="Hộp thoại tạm dừng" width="48%" />
  <img src="./assets/preview/win.png" alt="Hộp thoại chiến thắng" width="48%" />
</div>

## Tính năng

- Tạo Sudoku ở các chế độ Dễ, Trung bình, Khó, Thử thách hằng ngày và Tùy chỉnh.
- Bảo đảm puzzle được tạo hoặc nhập có đúng một lời giải; chế độ tùy chỉnh có thể tạo ít ô trống hơn mục tiêu để giữ điều kiện này.
- Daily Challenge được xác định theo ngày UTC, nên mọi người chơi cùng một bảng trong cùng ngày UTC.
- Ghi chú thủ công, tự điền ghi chú khả dĩ, gợi ý, xóa ô, kiểm tra lỗi, hoàn tác và làm lại (tối đa 200 trạng thái).
- Chọn ô và thao tác bằng chuột hoặc bàn phím; có modal trợ giúp phím tắt.
- Tạm dừng, chơi lại, lưu và quay về menu; tự lưu ván đang chơi để tiếp tục sau khi mở lại ứng dụng.
- Lưu thời gian tốt nhất và TOP 10 theo từng chế độ trên máy hiện tại. Khi thời gian thắng đủ điều kiện vào TOP 10, game cho phép nhập tên người chơi.
- Bốn giao diện màu, hiệu ứng chuyển động nhẹ và âm thanh có thể bật/tắt.
- Hai ngôn ngữ giao diện: Tiếng Việt có dấu và English; lựa chọn ngôn ngữ và âm thanh được lưu cục bộ giữa các lần chạy.
- Nhập puzzle từ JSON đã xuất hoặc chuỗi gồm 81 chữ số; xuất puzzle vào clipboard. Mọi hộp thoại đều vẽ trong game, không cần Tcl/Tk.

## Điều khiển

| Thao tác | Phím |
| --- | --- |
| Di chuyển ô chọn | `W`, `A`, `S`, `D` hoặc phím mũi tên |
| Điền số | `1`–`9` |
| Xóa ô đang chọn | `Backspace`, `Delete` hoặc `Kp0` |
| Bật/tắt ghi chú | `Space` hoặc `N` |
| Hoàn tác | `Ctrl+Z` |
| Làm lại | `Ctrl+Y` hoặc `Ctrl+Shift+Z` |
| Tạm dừng / tiếp tục | `Esc` hoặc `P` |
| Mở / đóng trợ giúp | `F1` |
| Điều hướng menu | `Tab` / `Shift+Tab`, chọn bằng `Enter` hoặc `Space` |

Bạn cũng có thể dùng chuột để chọn ô và bấm các nút trên giao diện. Game làm nổi bật số trùng trong hàng, cột hoặc khối; tùy chọn **Kiểm tra lỗi** làm nổi bật thêm các số không khớp lời giải.

## Bố cục mã nguồn

```text
SUDOKU/
├── .github/
│   └── workflows/
│       └── ci.yml              # Kiểm thử, lint, kiểu dữ liệu, bảo mật, build và phát hành
├── assets/
│   ├── icons/                  # Icon ứng dụng
│   └── preview/                # Ảnh chụp giao diện dùng trong README
├── src/
│   └── sudoku/
│       ├── __init__.py
│       ├── config.py           # Chuỗi giao diện tiếng Việt và tiếng Anh
│       ├── error_handling.py   # Ghi log và decorator xử lý ngoại lệ
│       ├── game.py             # Trạng thái game, sự kiện và bộ điều khiển ứng dụng
│       ├── logic.py            # Sinh, giải, xác thực và nhập/xuất puzzle
│       ├── main.py             # Điểm vào ứng dụng và smoke test bản đóng gói
│       ├── persistence.py      # Lưu game, thống kê, kỷ lục và bảng xếp hạng
│       ├── sounds.py           # Tạo và phát âm thanh bằng Pygame
│       └── ui/
│           ├── __init__.py
│           ├── board.py        # Vẽ bàn Sudoku và hiệu ứng
│           ├── colors.py       # Bảng màu và quản lý giao diện
│           ├── drawing.py      # Các thành phần vẽ dùng chung
│           ├── fonts.py        # Tải font và font dự phòng theo hệ điều hành
│           ├── geometry.py     # Kích thước, vị trí và hitbox
│           ├── icons.py        # Icon vector và hiệu ứng hạt
│           ├── menu.py         # Menu chính
│           ├── modals.py       # Hộp thoại trợ giúp, tạm dừng, chiến thắng, xếp hạng
│           ├── screen.py       # Khởi tạo cửa sổ, DPI và icon ứng dụng
│           ├── sidebar.py      # Nút điều khiển và bàn phím số
│           └── view.py         # Ghép các thành phần thành màn hình chơi
├── tests/
│   ├── conftest.py
│   ├── test_sudoku.py
│   └── test_ui_smoke.py
├── build.bat                  # Script build trên Windows
├── build.spec                 # Cấu hình PyInstaller cho Windows, Linux và macOS
├── pyproject.toml             # Metadata package và cấu hình công cụ
├── requirements.txt           # Dependency tối thiểu để chạy game
├── .gitignore
├── .pre-commit-config.yaml
├── .secrets.baseline
├── CHANGELOG.md
├── LICENSE
└── README.md
```

### Luồng hoạt động

`main.py` khởi chạy `AppController` trong `game.py`. Bộ điều khiển chuyển giữa menu, ván chơi, trợ giúp và bảng xếp hạng. `GameState` gọi `logic.py` để sinh/xác thực bảng và `persistence.py` để lưu trạng thái; các màn hình được chia thành module trong `ui/`. Cấu hình ngôn ngữ nằm trong `config.py`, còn hiệu ứng âm thanh do `sounds.py` tạo trực tiếp, không cần file âm thanh ngoài.

## Yêu cầu và cài đặt

- Python **3.10–3.13**. CI kiểm tra cả bốn phiên bản này.
- Bàn chơi dùng canvas logic `1120 × 800`; trên màn hình nhỏ hơn, cửa sổ được thu nhỏ theo tỷ lệ để vừa màn hình và vẫn giữ đúng vị trí chuột.
- `pip` để cài dependency.

Cài dependency chạy game:

```bash
python -m pip install -r requirements.txt
```

Cài thêm công cụ phát triển và kiểm thử:

```bash
python -m pip install -e ".[dev]"
```

Chạy ứng dụng:

```bash
python -m sudoku.main
```

## Dữ liệu và quyền riêng tư

Dữ liệu runtime được lưu cục bộ trong thư mục riêng theo hệ điều hành:

| Hệ điều hành | Thư mục mặc định |
| --- | --- |
| Windows | `%LOCALAPPDATA%\SudokuMaster` |
| macOS | `~/Library/Application Support/SudokuMaster` |
| Linux | `$XDG_DATA_HOME/SudokuMaster`, hoặc `~/.local/share/SudokuMaster` nếu biến chưa đặt |

Trong đó có thể có ván đang chơi, kỷ lục, thống kê Daily Challenge, bảng xếp hạng và log. Ở lần chạy đầu, các file dữ liệu cũ trong thư mục dự án được sao chép sang vị trí runtime; dấu mốc di chuyển ngăn dữ liệu cũ bị khôi phục lại sau khi người chơi xóa ván. Biến môi trường `SUDOKU_DATA_DIR` ghi đè thư mục mặc định, hữu ích khi kiểm thử hoặc chạy bản portable. Game không gửi các dữ liệu này lên mạng.

Nếu thư mục mặc định không thể ghi, game thử lưu trong `~/.sudoku-master` thay vì dừng ngay khi khởi động.

## Kiểm tra chất lượng

Chạy các kiểm tra cục bộ sau để xác minh mã nguồn và giao diện:

```bash
python -m pytest -q
python -m pytest --cov=. --cov-report=term-missing
python -m ruff check .
python -m ruff format --check .
python -m mypy . --ignore-missing-imports
python -m compileall -q .
python -m sudoku.main --smoke-test
```

`--smoke-test` khởi tạo giao diện ở chế độ headless và render các màn hình cơ bản; dữ liệu thử nghiệm được ghi vào thư mục tạm. GitHub Actions chạy test có coverage, Ruff, mypy, quét `pip-audit`/secret, build Windows/Linux/macOS và smoke-test artifact.

Pipeline CI chạy test, Ruff, mypy, `pip-audit` và `detect-secrets` trên Linux. Build Windows, Linux và macOS tạo ứng dụng bằng PyInstaller rồi chạy smoke test. CI Summary tổng hợp kết quả; tag `v*` tạo GitHub Release với artifact cho cả ba hệ điều hành.

## Đóng gói

Cài PyInstaller rồi tạo bản thực thi cho hệ điều hành hiện tại:

```bash
python -m pip install -e ".[build]"
pyinstaller build.spec --clean
```

Trên Windows có thể dùng `build.bat`. Artifact nằm trong `dist/`; không đưa thư mục build hoặc file thực thi sinh ra vào Git. Mỗi hệ điều hành cần build riêng trên hệ điều hành tương ứng. Bản macOS được đóng gói thành `SudokuMaster-macos.zip` chứa ứng dụng `.app`.

## Giới hạn hiện tại

- Các mức Dễ, Trung bình và Khó hiện được phân loại theo số ô trống; game chưa đánh giá độ khó dựa trên kỹ thuật giải cần thiết.
- Đây là game desktop một người chơi, lưu dữ liệu cục bộ; chưa có tài khoản, multiplayer, đồng bộ online hoặc dịch vụ backend.
- Layout được thiết kế trên canvas `1120 × 800`; cửa sổ sẽ thu nhỏ trên màn hình thấp hơn nên chữ và nút cũng nhỏ theo.
- Màn hình thống kê tổng quan hiển thị kỷ lục, dữ liệu Daily Challenge, số ván bắt đầu/hoàn thành và số gợi ý đã dùng; chưa thống kê thời gian trung bình hoặc số lỗi.
- CI đã được cấu hình để build và smoke-test bản macOS; vẫn cần xác minh trải nghiệm cài đặt trên máy Mac thực tế trước khi phát hành rộng rãi.

## Giấy phép

Dự án được phát hành theo [giấy phép MIT](LICENSE).



