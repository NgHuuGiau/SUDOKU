import tkinter as tk
from tkinter import ttk, messagebox
from game import start_game
from lang import _, chuyen_ngon_ngu

COLORS = {
    'bg': '#667eea',
    'frame': '#764ba2',
    'card': '#ffffff',
    'primary': '#4facfe',
    'primary_dark': '#00f2fe',
    'accent': '#f093fb',
    'text_dark': '#2d3748',
    'text_light': '#ffffff',
    'hover': '#f6d365',
    'shadow': '#rgba(0,0,0,0.1)',
}

class MenuSudoku:
    """Main menu class for selecting difficulty and language."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 Sudoku Cổ Điển")
        self.root.configure(bg=COLORS['bg'])
        self.root.resizable(False, False)

        try:
            icon_path = os.path.join(os.path.dirname(__file__), "Picture/SUDOKU.ico")
            self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self._cai_dat_kieu()
        self._tao_cac_widget()
        self._canh_giua_cua_so()

    def _cai_dat_kieu(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Easy.TButton',
                        font=('Segoe UI Emoji', 13, 'bold'),
                        background='#48bb78',
                        foreground=COLORS['text_light'],
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='#48bb78',
                        padding=10)
        style.map('Easy.TButton',
                  background=[('active', '#38a169')])

        style.configure('Medium.TButton',
                        font=('Segoe UI Emoji', 13, 'bold'),
                        background='#ed8936',
                        foreground=COLORS['text_light'],
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='#ed8936',
                        padding=10)
        style.map('Medium.TButton',
                  background=[('active', '#dd6b20')])

        style.configure('Hard.TButton',
                        font=('Segoe UI Emoji', 13, 'bold'),
                        background='#f56565',
                        foreground=COLORS['text_light'],
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='#f56565',
                        padding=10)
        style.map('Hard.TButton',
                  background=[('active', '#e53e3e')])

    def _tao_cac_widget(self):
        main_frame = tk.Frame(self.root, bg=COLORS['bg'])
        main_frame.pack(expand=True, fill=tk.BOTH)

        top_bar = tk.Frame(main_frame, bg='#4facfe', height=6)
        top_bar.pack(fill=tk.X)

        card = tk.Frame(main_frame, bg=COLORS['card'], padx=40, pady=15)
        card.pack(expand=True, fill=tk.BOTH, padx=30, pady=(10, 20))

        shadow = tk.Frame(main_frame, bg='#a0aec0', height=2)
        shadow.pack(fill=tk.X, side=tk.BOTTOM)

        title_label = tk.Label(
            card,
            text="🔢 SUDOKU 🔢",
            font=('Segoe UI Emoji', 36, 'bold'),
            bg=COLORS['card'],
            fg='#2d3748'
        )
        title_label.pack(pady=(0, 10))

        self.phu_de = tk.Label(
            card,
            text=_("thu_thach"),
            font=('Segoe UI Emoji', 13, 'italic'),
            bg=COLORS['card'],
            fg='#718096'
        )
        self.phu_de.pack(pady=(0, 15))

        dai_phan_cach = tk.Frame(card, height=2, bg='#e2e8f0')
        dai_phan_cach.pack(fill=tk.X, pady=(0, 25))

        self.nhan_chon_do_kho = tk.Label(
            card,
            text=_("chon_do_kho"),
            font=('Segoe UI Emoji', 18, 'bold'),
            bg=COLORS['card'],
            fg='#2d3748'
        )
        self.nhan_chon_do_kho.pack(pady=(0, 20))

        chieu_rong_nut = 18

        self.nut_de = ttk.Button(
            card,
            text=_('de'),
            command=lambda: self._bat_dau_tro_choi("easy"),
            style='Easy.TButton',
            width=chieu_rong_nut,
            takefocus=False
        )
        self.nut_de.pack(pady=5)

        self.nut_trung_binh = ttk.Button(
            card,
            text=_('trung_binh'),
            command=lambda: self._bat_dau_tro_choi("medium"),
            style='Medium.TButton',
            width=chieu_rong_nut,
            takefocus=False
        )
        self.nut_trung_binh.pack(pady=5)

        self.nut_kho = ttk.Button(
            card,
            text=_('kho'),
            command=lambda: self._bat_dau_tro_choi("hard"),
            style='Hard.TButton',
            width=chieu_rong_nut,
            takefocus=False
        )
        self.nut_kho.pack(pady=5)

        self.nut_ngon_ngu = ttk.Button(
            card,
            text=_('ngon_ngu'),
            command=self._chuyen_ngon_ngu,
            style='Medium.TButton',
            width=chieu_rong_nut,
            takefocus=False
        )
        self.nut_ngon_ngu.pack(pady=5)

        khung_chan_trang = tk.Frame(card, bg=COLORS['card'])
        khung_chan_trang.pack(pady=(15, 0))

        self.chan_trang = tk.Label(
            khung_chan_trang,
            text=_("chuc_vui_ve"),
            font=('Segoe UI Emoji', 10, 'italic'),
            bg=COLORS['card'],
            fg='#a0aec0'
        )
        self.chan_trang.pack()

        phien_ban = tk.Label(
            khung_chan_trang,
            text="v1.0.0",
            font=('Segoe UI Emoji', 8),
            bg=COLORS['card'],
            fg='#cbd5e0'
        )
        phien_ban.pack()

    def _chuyen_ngon_ngu(self):
        chuyen_ngon_ngu()
        self._cap_nhat_van_ban()

    def _cap_nhat_van_ban(self):
        self.phu_de.config(text=_("thu_thach"))
        self.nhan_chon_do_kho.config(text=_("chon_do_kho"))
        self.nut_de.config(text=_('de'))
        self.nut_trung_binh.config(text=_('trung_binh'))
        self.nut_kho.config(text=_('kho'))
        self.chan_trang.config(text=_("chuc_vui_ve"))
        self.nut_ngon_ngu.config(text=_('ngon_ngu'))

    def _canh_giua_cua_so(self):
        self.root.update_idletasks()
        chieu_rong = 550
        chieu_cao = 650
        x = (self.root.winfo_screenwidth() // 2) - (chieu_rong // 2)
        y = (self.root.winfo_screenheight() // 2) - (chieu_cao // 2)
        self.root.geometry(f'{chieu_rong}x{chieu_cao}+{x}+{y}')

    def _bat_dau_tro_choi(self, do_kho):
        self.root.withdraw()
        thang = start_game(self.root, do_kho)
        self.root.deiconify()
        if thang:
            if not messagebox.askyesno(_("chien_thang"), _("chuc_mung")):
                self.root.destroy()

    def chay(self):
        self.root.mainloop()

def tao_nut_bat_dau():
    """Khởi tạo và chạy menu chính."""
    menu = MenuSudoku()
    menu.chay()