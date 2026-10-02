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
??? .github/workflows/ci.yml  # Ki?m th?, lint, type-check, qu�t b?o m?t, build v� release
??? assets/
?   ??? icons/                 # Icon ?ng d?ng
?   ??? preview/               # ?nh ch?p giao di?n trong README
??? src/
?   ??? sudoku/               # G�i m? ngu?n ch�nh
?       ??? __init__.py
?       ??? config.py         # Chu?i giao di?n ti?ng Vi?t / ti?ng Anh
?       ??? error_handling.py # Ghi log v� decorator ghi nh?n l?i
?       ??? game.py           # Tr?ng th�i Sudoku, s? ki?n v� b? �i?u khi?n ?ng d?ng
?       ??? logic.py          # Sinh, gi?i, x�c th?c v� nh?p/xu?t puzzle
?       ??? main.py           # �i?m v�o ?ng d?ng v� smoke test b?n ��ng g�i
?       ??? persistence.py    # L�u game, th?ng k�, k? l?c v� b?ng x?p h?ng JSON
?       ??? sounds.py         # T?o v� ph�t �m thanh b?ng Pygame
?       ??? ui/               # Giao di?n Pygame
?           ??? __init__.py
?           ??? board.py      # Render b�n Sudoku v� animation
?           ??? colors.py     # B?ng m�u v� qu?n l? theme
?           ??? drawing.py    # N�t, th? v� th�nh ph?n v? d�ng chung
?           ??? fonts.py      # Font v� fallback theo h? �i?u h�nh
?           ??? geometry.py   # K�ch th�?c, v? tr� v� hitbox
?           ??? icons.py      # Icon vector v� h?t hi?u ?ng
?           ??? menu.py       # Menu ch�nh
?           ??? modals.py     # Modal tr? gi�p, t?m d?ng, chi?n th?ng, x?p h?ng
?           ??? screen.py     # Kh?i t?o c?a s?, DPI v� icon
?           ??? sidebar.py    # C�c n�t v� b�n ph�m s?
?           ??? view.py       # Gh�p c�c th�nh ph?n th�nh m�n h?nh ch�i
??? tests/                    # Unit, persistence, integration v� UI smoke tests
??? build.bat / build.spec    # ��ng g�i ?ng d?ng b?ng PyInstaller
??? pyproject.toml            # Metadata, dependency v� c?u h?nh c�ng c?
??? requirements.txt          # Dependency t?i thi?u �? ch?y game
??? .gitignore                # Lo?i tr? cache, d? li?u c� nh�n v� artifact build
??? .pre-commit-config.yaml   # Ki?m tra tr�?c khi commit
??? .secrets.baseline         # Baseline detect-secrets
??? CHANGELOG.md              # L?ch s? thay �?i
??? LICENSE                   # Gi?y ph�p MIT
??? README.md                 # T�i li?u d? �n
```

### Luồng hoạt động

`main.py` khởi chạy `AppController` trong `game.py`. Bộ điều khiển chuyển giữa menu, ván chơi, trợ giúp và bảng xếp hạng. `GameState` gọi `logic.py` để sinh/xác thực bảng và `persistence.py` để lưu trạng thái; các màn hình được chia thành module trong `ui/`. Cấu hình ngôn ngữ nằm trong `config.py`, còn hiệu ứng âm thanh do `sounds.py` tạo trực tiếp, không cần file âm thanh ngoài.

## Yêu cầu và cài đặt

- Python **3.10–3.13**. CI kiểm tra cả bốn phiên bản này.
- Cửa sổ game có kích thước cố định `1120 × 800`; nên dùng màn hình có độ phân giải tối thiểu bằng kích thước này.
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

`--smoke-test` khởi tạo giao diện ở chế độ headless và render các màn hình cơ bản; dữ liệu thử nghiệm được ghi vào thư mục tạm. GitHub Actions chạy test có coverage, Ruff, mypy, quét `pip-audit`/secret, build Windows/Linux và smoke-test các file thực thi.

Pipeline CI chạy test, Ruff, mypy, `pip-audit` và `detect-secrets` trên Linux. Build Windows và Linux tạo ứng dụng bằng PyInstaller rồi chạy smoke test cho file thực thi. CI Summary tổng hợp kết quả; tag `v*` tạo GitHub Release với artifact Windows và Linux. Build macOS chưa nằm trong CI và chưa được xác minh.

## Đóng gói

Cài PyInstaller rồi tạo bản thực thi cho hệ điều hành hiện tại:

```bash
python -m pip install -e ".[build]"
pyinstaller build.spec --clean
```

Trên Windows có thể dùng `build.bat`. Artifact nằm trong `dist/`; không đưa thư mục build hoặc file thực thi sinh ra vào Git. Mỗi hệ điều hành cần build riêng trên hệ điều hành tương ứng.

## Giới hạn hiện tại

- Đây là game desktop một người chơi, lưu dữ liệu cục bộ; chưa có tài khoản, multiplayer, đồng bộ online hoặc dịch vụ backend.
- Kích thước cửa sổ hiện cố định; layout được thiết kế cho `1120 × 800`.
- Màn hình thống kê tổng quan chưa được triển khai; hiện có bảng TOP 10 và các số liệu Daily Challenge.
- Pipeline phát hành tự động hiện cung cấp artifact Windows và Linux, chưa có bản macOS.

## Giấy phép

Dự án được phát hành theo [giấy phép MIT](LICENSE).



