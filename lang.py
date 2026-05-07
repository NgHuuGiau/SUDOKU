"""
Xử lý ngôn ngữ cho game.
"""
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.txt")

def doc_ngon_ngu():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return f.read().strip()
    return "vi"

def luu_ngon_ngu(lang):
    with open(SETTINGS_FILE, "w") as f:
        f.write(lang)

ngon_ngu_hien_tai = doc_ngon_ngu()

ban_dich = {
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
        "move": "WASD: Move",
        "input": "1-9: Input",
        "delete": "Backspace: Delete",
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
        "move": "WASD: Di chuyển",
        "input": "1-9: Nhập",
        "delete": "Backspace: Xóa",
    }
}

def _(khoa):
    return ban_dich[ngon_ngu_hien_tai][khoa]

def chuyen_ngon_ngu():
    global ngon_ngu_hien_tai
    ngon_ngu_hien_tai = "vi" if ngon_ngu_hien_tai == "en" else "en"
    luu_ngon_ngu(ngon_ngu_hien_tai)