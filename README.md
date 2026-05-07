# 🧩 Modern Sudoku Game

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: Pygame](https://img.shields.io/badge/Framework-Pygame-green.svg)](https://www.pygame.org)

Một ứng dụng game Sudoku chuyên nghiệp được xây dựng bằng Python. Dự án tập trung vào giao diện người dùng tối giản, sắc nét và thuật toán xử lý logic tối ưu.

## ✨ Tính năng nổi bật

- **🎨 UI/UX Cao cấp**: Hệ thống màu sắc hài hòa, hỗ trợ cross-highlighting hàng/cột giúp tăng khả năng tập trung.
- **🧠 Thuật toán thông minh**:
  - **Generation**: Tạo bảng Sudoku ngẫu nhiên không trùng lặp.
  - **Solver**: Tích hợp thuật toán Backtracking để giải bảng trong chớp mắt.
- **⚡ Hiệu năng tối ưu**: Xử lý render mượt mà, không gây hiện tượng giật lag pixel.
- **🛠 Công cụ hỗ trợ**: Chế độ ghi chú (Notes), gợi ý (Hint), và kiểm tra lỗi sai thời gian thực.

## 📂 Cấu trúc dự án

```text
SUDOKU/
├── main.py          # Entry point của ứng dụng
├── ui.py            # Quản lý giao diện và hằng số hiển thị
├── logic.py         # Thuật toán sinh bảng và giải Sudoku
├── menu.py          # Xử lý giao diện Menu (Tkinter/Pygame)
├── game.py          # Vòng lặp chính của trò chơi
└── README.md        # Tài liệu hướng dẫn dự án
```

## 🚀 Hướng dẫn cài đặt & Chạy game

### 1. Yêu cầu hệ thống

- Python 3.8 trở lên.
- Thư viện Pygame.

### 2. Triển khai

Cài đặt các thư viện cần thiết:

```bash
pip install pygame
```

### 3. Chạy game

```bash
python main.py
```

## 🛠 Công nghệ sử dụng

- **Ngôn ngữ**: Python
- **Thư viện chính**: Pygame (Xử lý đồ họa)
- **Thuật toán**: Backtracking (Giải Sudoku)
