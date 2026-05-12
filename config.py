"""Cau hinh chung cho game.
Chua bien ngon ngu hien tai va ham chuyen doi ngon ngu.
"""

ngon_ngu_hien_tai = "vi"

APP_TITLE = "Sudoku"
MENU_TITLE = "Sudoku Cổ Điển"
MENU_HEADING = "SUDOKU"
VERSION_TEXT = "v1.0.0"

GAME_DICT = {
    "en": {
        "move": "WASD: Move",
        "input": "1-9: Input",
        "delete": "Backspace: Delete",
        "chien_thang": "Victory!",
        "nhan_phim_bat_ky": "Press any key to return to Menu",
        "tam_dung": "PAUSED",
        "tiep_tuc": "RESUME",
        "van_moi": "New Game",
        "goi_y": "Hint",
        "kiem_tra": "Check",
        "tam_dung_btn": "Pause",
        "ghi_chu": "Notes",
        "nhap_so": "Input",
        "ghi_chu_tu_dong": "Auto Notes",
        "hoan_tac": "Undo",
        "lam_lai": "Redo",
        "xoa_btn": "Clear",
        "thoat": "Quit",
        "choi_tiep": "Play Again",
        "thoat_ve_menu": "Back to Menu",
    },
    "vi": {
        "move": "WASD: Di chuyển",
        "input": "1-9: Nhập",
        "delete": "Backspace: Xóa",
        "chien_thang": "Chiến Thắng!",
        "nhan_phim_bat_ky": "Nhấn phím bất kỳ để quay lại Menu",
        "tam_dung": "ĐANG TẠM DỪNG",
        "tiep_tuc": "TIẾP TỤC",
        "van_moi": "Ván mới",
        "goi_y": "Gợi ý",
        "kiem_tra": "Kiểm tra",
        "tam_dung_btn": "Tạm dừng",
        "ghi_chu": "Ghi chú",
        "nhap_so": "Nhập số",
        "ghi_chu_tu_dong": "Ghi chú tự động",
        "hoan_tac": "Hoàn tác",
        "lam_lai": "Làm lại",
        "xoa_btn": "Xóa",
        "thoat": "Thoát",
        "choi_tiep": "Chơi tiếp",
        "thoat_ve_menu": "Về Menu",
    },
}

MENU_DICT = {
    "en": {
        "thu_thach": "Challenge your intelligence!",
        "chon_do_kho": "Select Difficulty",
        "de": "Easy",
        "trung_binh": "Medium",
        "kho": "Hard",
        "chuc_vui_ve": "Have fun playing!",
        "chien_thang": "Victory!",
        "chuc_mung": "Congratulations! You solved the Sudoku.\nDo you want to play another game?",
        "ngon_ngu": "Language",
    },
    "vi": {
        "thu_thach": "Thử thách trí tuệ của bạn!",
        "chon_do_kho": "Chọn Độ Khó",
        "de": "Chơi Dễ",
        "trung_binh": "Chơi Trung bình",
        "kho": "Chơi Khó",
        "chuc_vui_ve": "Chúc bạn chơi game vui vẻ!",
        "chien_thang": "Chiến Thắng!",
        "chuc_mung": "Chúc mừng! Bạn đã giải xong Sudoku.\nBạn có muốn chơi tiếp ván mới không?",
        "ngon_ngu": "Ngôn ngữ",
    },
}


def chuyen_ngon_ngu():
    global ngon_ngu_hien_tai
    ngon_ngu_hien_tai = "vi" if ngon_ngu_hien_tai == "en" else "en"


def game_text(key: str) -> str:
    return GAME_DICT[ngon_ngu_hien_tai][key]


def menu_text(key: str) -> str:
    return MENU_DICT[ngon_ngu_hien_tai][key]
