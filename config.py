"""Cau hinh chung cho game.
Chua bien ngon ngu hien tai va ham chuyen doi ngon ngu.
"""

ngon_ngu_hien_tai = "vi"

APP_TITLE = "Sudoku Master"
MENU_TITLE = "Sudoku Master - Giao diện Cổ điển & Hiện đại"
MENU_HEADING = "SUDOKU"
VERSION_TEXT = "v2.0.0 • Modern Edition"

GAME_DICT = {
    "en": {
        "move": "Move: WASD / Arrows",
        "input": "Input: 1-9",
        "delete": "Delete: Backspace",
        "notes_shortcut": "Notes: Space",
        "chien_thang": "Victory!",
        "nhan_phim_bat_ky": "Press any key to return to Menu",
        "tam_dung": "GAME PAUSED",
        "tiep_tuc": "Resume",
        "van_moi": "New Game",
        "goi_y": "Hint",
        "kiem_tra": "Check",
        "tam_dung_btn": "Pause",
        "ghi_chu": "Notes",
        "nhap_so": "Input",
        "ghi_chu_tu_dong": "Auto Notes",
        "hoan_tac": "Undo",
        "lam_lai": "Redo",
        "xoa_btn": "Erase",
        "thoat": "Quit",
        "choi_tiep": "Play Again",
        "thoat_ve_menu": "Menu",
        "do_kho": "Difficulty",
        "de": "Easy",
        "trung_binh": "Medium",
        "kho": "Hard",
        "thoi_gian": "Time",
        "thao_tac_nhanh": "QUICK ACTIONS",
        "ban_phim_so": "NUMBER PAD",
        "con_lai": "left",
        "da_du": "done",
        "con_lai_fmt": "{n} left",
        "con_lai_du": "Done",
        "chuc_mung_thang": "Puzzle Solved!",
        "thoi_gian_hoan_thanh": "Completion Time",
        "ky_luc_moi": "NEW BEST!",
        "daily_challenge": "Daily Challenge",
        "daily_challenge_desc": "Same puzzle for everyone today",
        "streak": "Streak",
        "completed_today": "Completed today!",
        "come_back_tomorrow": "Come back tomorrow for a new challenge",
    },
    "vi": {
        "move": "Di chuyển: WASD / Mũi tên",
        "input": "Điền số: 1-9",
        "delete": "Xóa ô: Backspace",
        "notes_shortcut": "Ghi chú: Phím Space",
        "chien_thang": "Chiến Thắng!",
        "nhan_phim_bat_ky": "Nhấn phím bất kỳ để quay lại Menu",
        "tam_dung": "ĐANG TẠM DỪNG",
        "tiep_tuc": "Tiếp tục",
        "van_moi": "Ván mới",
        "goi_y": "Gợi ý",
        "kiem_tra": "Kiểm tra",
        "tam_dung_btn": "Tạm dừng",
        "ghi_chu": "Ghi chú",
        "nhap_so": "Nhập số",
        "ghi_chu_tu_dong": "Ghi chú tự động",
        "hoan_tac": "Hoàn tác",
        "lam_lai": "Làm lại",
        "xoa_btn": "Xóa ô",
        "thoat": "Thoát",
        "choi_tiep": "Chơi lại",
        "thoat_ve_menu": "Về Menu",
        "do_kho": "Độ khó",
        "de": "Dễ",
        "trung_binh": "Trung bình",
        "kho": "Khó",
        "thoi_gian": "Thời gian",
        "thao_tac_nhanh": "THAO TÁC NHANH",
        "ban_phim_so": "BÀN PHÍM SỐ",
        "con_lai": "còn",
        "da_du": "xong",
        "con_lai_fmt": "còn {n}",
        "con_lai_du": "Đã đủ",
        "chuc_mung_thang": "Xuất sắc! Bạn đã giải xong!",
        "thoi_gian_hoan_thanh": "Thời gian hoàn thành",
        "ky_luc_moi": "KỶ LỤC MỚI!",
        "daily_challenge": "Thử Thách Hàng Ngày",
        "daily_challenge_desc": "Cùng một bảng cho mọi người hôm nay",
        "streak": "Chuỗi ngày",
        "completed_today": "Đã hoàn thành hôm nay!",
        "come_back_tomorrow": "Quay lại ngày mai để nhận thử thách mới",
    },
}

MENU_DICT = {
    "en": {
        "app_badge": "LOGIC PUZZLE",
        "thu_thach": "Challenge your intelligence and focus!",
        "chon_do_kho": "Select Difficulty",
        "de": "Easy",
        "de_desc": "38 empty cells - Perfect for beginners",
        "trung_binh": "Medium",
        "trung_binh_desc": "48 empty cells - Balanced and fun",
        "kho": "Hard",
        "kho_desc": "56 empty cells - True brain workout",
        "chuc_vui_ve": "Enjoy the game!",
        "chien_thang": "Victory!",
        "chuc_mung": "Congratulations! You solved the Sudoku.\nDo you want to play another game?",
        "ngon_ngu": "Language: English",
        "ngon_ngu_btn": "EN / VI",
        "ky_luc_label": "Best",
        "tiep_tuc_van": "Resume Game",
        "tiep_tuc_van_desc": "Continue your previous game ({diff} - {time})",
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
        "daily_challenge": "Daily Challenge",
        "daily_challenge_desc": "Same puzzle for everyone today",
        "streak_label": "Streak: {n} days",
    },
    "vi": {
        "app_badge": "TRÒ CHƠI TRÍ TUỆ",
        "thu_thach": "Thử thách tư duy logic và sự tập trung của bạn!",
        "chon_do_kho": "Chọn Mức Độ Chơi",
        "de": "Dễ",
        "de_desc": "38 ô trống - Dành cho người mới bắt đầu",
        "trung_binh": "Trung bình",
        "trung_binh_desc": "48 ô trống - Cân bằng và thú vị",
        "kho": "Khó",
        "kho_desc": "56 ô trống - Thử thách cao cấp",
        "chuc_vui_ve": "Chúc bạn có những phút giây giải trí tuyệt vời!",
        "chien_thang": "Chiến Thắng!",
        "chuc_mung": "Chúc mừng! Bạn đã giải thành công bảng Sudoku.\nBạn có muốn chơi tiếp ván mới không?",
        "ngon_ngu": "Ngôn ngữ: Tiếng Việt",
        "ngon_ngu_btn": "VI / EN",
        "ky_luc_label": "Kỷ lục",
        "tiep_tuc_van": "Tiếp Tục Ván Chơi",
        "tiep_tuc_van_desc": "Tiếp tục ván đấu đang chơi dở ({diff} - {time})",
        "easy": "Dễ",
        "medium": "Trung bình",
        "hard": "Khó",
        "daily_challenge": "Thử Thách Hàng Ngày",
        "daily_challenge_desc": "Cùng một bảng cho mọi người hôm nay",
        "streak_label": "Chuỗi ngày: {n} ngày",
    },
}


def chuyen_ngon_ngu():
    global ngon_ngu_hien_tai
    ngon_ngu_hien_tai = "vi" if ngon_ngu_hien_tai == "en" else "en"


def game_text(key: str) -> str:
    return GAME_DICT[ngon_ngu_hien_tai].get(key, key)


def menu_text(key: str) -> str:
    return MENU_DICT[ngon_ngu_hien_tai].get(key, key)
