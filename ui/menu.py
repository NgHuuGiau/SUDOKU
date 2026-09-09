"""Tkinter-based menu for Sudoku."""
import os
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from config import (
    APP_TITLE, MENU_HEADING, MENU_TITLE, VERSION_TEXT,
    chuyen_ngon_ngu, menu_text
)
from ui.screen import get_sudoku_icon_path, enable_high_dpi
from persistence import has_save_file, load_game_state, get_daily_stats
from logic import get_daily_challenge_info, generate_daily_challenge
from datetime import date
import copy


MENU_COLORS = {
    'bg': '#f8fafc',
    'hero': '#1e293b',
    'card': '#ffffff',
    'primary': '#4f46e5',
    'primary_hover': '#4338ca',
    'secondary': '#10b981',
    'secondary_hover': '#059669',
    'warning': '#f59e0b',
    'warning_hover': '#d97706',
    'danger': '#ef4444',
    'danger_hover': '#dc2626',
    'text_dark': '#0f172a',
    'text_muted': '#64748b',
    'text_light': '#ffffff',
    'border': '#e2e8f0',
    'badge_bg': '#eef2ff',
    'badge_fg': '#4338ca',
}


class MenuSudoku:
    def __init__(self, start_game_func):
        self.start_game_func = start_game_func
        self.root = tk.Tk()
        self.root.title(MENU_TITLE)
        self.root.configure(bg=MENU_COLORS['bg'])
        self.root.resizable(False, False)
        self._tao_font_menu()
        try:
            icon_path = get_sudoku_icon_path()
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
        self._cai_dat_kieu()
        self._tao_cac_widget()
        self._canh_giua_cua_so()

    def _tao_font_menu(self):
        self.menu_fonts = {
            "default": tkfont.Font(root=self.root, family="Segoe UI", size=10),
            "title": tkfont.Font(root=self.root, family="Segoe UI", size=26, weight="bold"),
            "badge": tkfont.Font(root=self.root, family="Segoe UI", size=9, weight="bold"),
            "subtitle": tkfont.Font(root=self.root, family="Segoe UI", size=11),
            "section": tkfont.Font(root=self.root, family="Segoe UI", size=13, weight="bold"),
            "card_title": tkfont.Font(root=self.root, family="Segoe UI", size=12, weight="bold"),
            "card_desc": tkfont.Font(root=self.root, family="Segoe UI", size=9),
            "footer": tkfont.Font(root=self.root, family="Segoe UI", size=9),
            "lang_btn": tkfont.Font(root=self.root, family="Segoe UI", size=10, weight="bold"),
        }
        self.root.option_add("*Font", self.menu_fonts["default"])

    def _cai_dat_kieu(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=self.menu_fonts["default"], background=MENU_COLORS['bg'])

    def _tao_cac_widget(self):
        self.main_frame = tk.Frame(self.root, bg=MENU_COLORS['bg'], padx=32, pady=24)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # 1. Top Bar
        top_bar = tk.Frame(self.main_frame, bg=MENU_COLORS['bg'])
        top_bar.pack(fill=tk.X, pady=(0, 10))

        self.app_badge = tk.Label(
            top_bar, text=f"[ {menu_text('app_badge')} ]",
            font=self.menu_fonts["badge"], bg=MENU_COLORS['badge_bg'],
            fg=MENU_COLORS['badge_fg'], padx=10, pady=4
        )
        self.app_badge.pack(side=tk.LEFT)

        self.btn_lang = tk.Button(
            top_bar, text=menu_text('ngon_ngu_btn'),
            font=self.menu_fonts["lang_btn"], bg=MENU_COLORS['card'],
            fg=MENU_COLORS['primary'], activebackground=MENU_COLORS['badge_bg'],
            relief=tk.FLAT, bd=1, highlightthickness=1, highlightbackground=MENU_COLORS['border'],
            cursor="hand2", padx=12, pady=3, command=self._chuyen_ngon_ngu
        )
        self.btn_lang.pack(side=tk.RIGHT)

        # 2. Hero Card
        hero_card = tk.Frame(self.main_frame, bg=MENU_COLORS['card'], padx=24, pady=18,
                             highlightbackground=MENU_COLORS['border'], highlightthickness=1)
        hero_card.pack(fill=tk.X, pady=(0, 16))

        title_lbl = tk.Label(
            hero_card, text=MENU_HEADING,
            font=self.menu_fonts["title"], bg=MENU_COLORS['card'],
            fg=MENU_COLORS['hero']
        )
        title_lbl.pack(pady=(0, 4))

        self.subtitle_lbl = tk.Label(
            hero_card, text=menu_text("thu_thach"),
            font=self.menu_fonts["subtitle"], bg=MENU_COLORS['card'],
            fg=MENU_COLORS['text_muted']
        )
        self.subtitle_lbl.pack()

        # 3. Section Title
        self.sec_title = tk.Label(
            self.main_frame, text=menu_text("chon_do_kho"),
            font=self.menu_fonts["section"], bg=MENU_COLORS['bg'],
            fg=MENU_COLORS['text_dark']
        )
        self.sec_title.pack(anchor=tk.W, pady=(4, 10))

        # 4. Resume Game Card
        self.resume_card = None
        if has_save_file():
            self.resume_card = self._tao_the_tiep_tuc()

        # 5. Daily Challenge Card
        self.daily_card = self._tao_the_daily_challenge()

        # 6. Difficulty Cards
        self.card_de = self._tao_the_do_kho(
            "easy", "[ 1 ] " + menu_text("de"), menu_text("de_desc"),
            MENU_COLORS['secondary'], MENU_COLORS['secondary_hover']
        )
        self.card_tb = self._tao_the_do_kho(
            "medium", "[ 2 ] " + menu_text("trung_binh"), menu_text("trung_binh_desc"),
            MENU_COLORS['warning'], MENU_COLORS['warning_hover']
        )
        self.card_kho = self._tao_the_do_kho(
            "hard", "[ 3 ] " + menu_text("kho"), menu_text("kho_desc"),
            MENU_COLORS['danger'], MENU_COLORS['danger_hover']
        )

        # 7. Footer
        footer_frame = tk.Frame(self.main_frame, bg=MENU_COLORS['bg'])
        footer_frame.pack(fill=tk.X, pady=(16, 0))

        self.footer_lbl = tk.Label(
            footer_frame, text=menu_text("chuc_vui_ve"),
            font=self.menu_fonts["footer"], bg=MENU_COLORS['bg'],
            fg=MENU_COLORS['text_muted']
        )
        self.footer_lbl.pack()

        ver_lbl = tk.Label(
            footer_frame, text=VERSION_TEXT,
            font=self.menu_fonts["footer"], bg=MENU_COLORS['bg'],
            fg='#94a3b8'
        )
        ver_lbl.pack()

    def _tao_the_do_kho(self, difficulty, title, desc, accent_color, hover_color):
        card = tk.Frame(self.main_frame, bg=MENU_COLORS['card'], padx=16, pady=12,
                        highlightbackground=MENU_COLORS['border'], highlightthickness=1,
                        cursor="hand2")
        card.pack(fill=tk.X, pady=4)

        accent_bar = tk.Frame(card, bg=accent_color, width=4)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        info_frame = tk.Frame(card, bg=MENU_COLORS['card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        t_lbl = tk.Label(info_frame, text=title, font=self.menu_fonts["card_title"],
                         bg=MENU_COLORS['card'], fg=MENU_COLORS['text_dark'], anchor=tk.W)
        t_lbl.pack(fill=tk.X)

        d_lbl = tk.Label(info_frame, text=desc, font=self.menu_fonts["card_desc"],
                         bg=MENU_COLORS['card'], fg=MENU_COLORS['text_muted'], anchor=tk.W)
        d_lbl.pack(fill=tk.X)

        arrow_lbl = tk.Label(card, text="->", font=self.menu_fonts["card_title"],
                             bg=MENU_COLORS['card'], fg=accent_color)
        arrow_lbl.pack(side=tk.RIGHT, padx=6)

        def on_click(event=None):
            self._bat_dau_tro_choi(difficulty)

        def on_enter(event=None):
            card.config(highlightbackground=accent_color)

        def on_leave(event=None):
            card.config(highlightbackground=MENU_COLORS['border'])

        for widget in (card, info_frame, t_lbl, d_lbl, arrow_lbl):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return {"card": card, "title_lbl": t_lbl, "desc_lbl": d_lbl, "difficulty": difficulty}

    def _tao_the_tiep_tuc(self):
        saved = load_game_state()
        if saved:
            diff_key = saved.difficulty
            diff_name = {"easy": menu_text("de"), "medium": menu_text("trung_binh"), "hard": menu_text("kho")}.get(diff_key, diff_key)
            elapsed = saved.get_elapsed_time()
            mins, secs = divmod(max(0, elapsed), 60)
            time_str = f"{mins:02}:{secs:02}"
            desc = menu_text("tiep_tuc_van_desc").format(diff=diff_name, time=time_str)
        else:
            diff_key = "medium"
            diff_name = menu_text("trung_binh")
            desc = menu_text("tiep_tuc_van_desc").format(diff=diff_name, time="--:--")

        card = tk.Frame(self.main_frame, bg=MENU_COLORS['card'], padx=16, pady=12,
                        highlightbackground=MENU_COLORS['primary'], highlightthickness=2,
                        cursor="hand2")
        card.pack(fill=tk.X, pady=(0, 8))

        accent_bar = tk.Frame(card, bg=MENU_COLORS['primary'], width=4)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        info_frame = tk.Frame(card, bg=MENU_COLORS['card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        t_lbl = tk.Label(info_frame, text="[ >> ] " + menu_text("tiep_tuc_van"),
                         font=self.menu_fonts["card_title"], bg=MENU_COLORS['card'],
                         fg=MENU_COLORS['primary'], anchor=tk.W)
        t_lbl.pack(fill=tk.X)

        d_lbl = tk.Label(info_frame, text=desc, font=self.menu_fonts["card_desc"],
                         bg=MENU_COLORS['card'], fg=MENU_COLORS['text_muted'], anchor=tk.W)
        d_lbl.pack(fill=tk.X)

        arrow_lbl = tk.Label(card, text="->", font=self.menu_fonts["card_title"],
                             bg=MENU_COLORS['card'], fg=MENU_COLORS['primary'])
        arrow_lbl.pack(side=tk.RIGHT, padx=6)

        def on_click(event=None):
            loaded = load_game_state()
            self._bat_dau_tro_choi(loaded.difficulty if loaded else "medium", loaded)

        def on_enter(event=None):
            card.config(highlightbackground=MENU_COLORS['primary'])

        def on_leave(event=None):
            card.config(highlightbackground=MENU_COLORS['primary'])

        for widget in (card, info_frame, t_lbl, d_lbl, arrow_lbl):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return {"card": card, "title_lbl": t_lbl, "desc_lbl": d_lbl}

    def _tao_the_daily_challenge(self):
        stats = get_daily_stats()
        info = get_daily_challenge_info(date.today())
        completed_today = stats["last_completed_date"] == date.today().isoformat()

        if completed_today:
            title = "[ ✓ ] " + menu_text("daily_challenge")
            desc = f"{menu_text('completed_today')}  {menu_text('streak_label').format(n=stats['streak'])}"
            accent = MENU_COLORS['secondary']
        else:
            title = "[ ⚡ ] " + menu_text("daily_challenge")
            desc = f"{menu_text('daily_challenge_desc')}  {menu_text('streak_label').format(n=stats['streak'])}"
            accent = MENU_COLORS['primary']

        card = tk.Frame(self.main_frame, bg=MENU_COLORS['card'], padx=16, pady=12,
                        highlightbackground=accent, highlightthickness=2,
                        cursor="hand2")
        card.pack(fill=tk.X, pady=(0, 8))

        accent_bar = tk.Frame(card, bg=accent, width=4)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        info_frame = tk.Frame(card, bg=MENU_COLORS['card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        t_lbl = tk.Label(info_frame, text=title,
                         font=self.menu_fonts["card_title"], bg=MENU_COLORS['card'],
                         fg=accent, anchor=tk.W)
        t_lbl.pack(fill=tk.X)

        d_lbl = tk.Label(info_frame, text=desc, font=self.menu_fonts["card_desc"],
                         bg=MENU_COLORS['card'], fg=MENU_COLORS['text_muted'], anchor=tk.W)
        d_lbl.pack(fill=tk.X)

        arrow_lbl = tk.Label(card, text="->", font=self.menu_fonts["card_title"],
                             bg=MENU_COLORS['card'], fg=accent)
        arrow_lbl.pack(side=tk.RIGHT, padx=6)

        def on_click(event=None):
            if completed_today:
                messagebox.showinfo(menu_text("daily_challenge"), menu_text("come_back_tomorrow"))
                return
            board, solution, seed = generate_daily_challenge("medium")
            from game import GameState
            state = GameState.__new__(GameState)
            state.difficulty = "daily"
            state.board = board
            state.solution = solution
            state.original = [row[:] for row in board]
            state.selected = [0, 0]
            state.notes = [[set() for _ in range(9)] for _ in range(9)]
            state.notes_mode = False
            state.game_over = False
            state.paused = False
            state.show_errors = False
            state.start_time = 0
            state.paused_time = 0
            state.last_pause_start = 0
            state.last_active_time = 0
            state.final_time = 0
            state.undo_stack = [(copy.deepcopy(board), copy.deepcopy(state.notes))]
            state.redo_stack = []
            self._bat_dau_tro_choi("daily", state)

        def on_enter(event=None):
            card.config(highlightbackground=accent)

        def on_leave(event=None):
            card.config(highlightbackground=accent)

        for widget in (card, info_frame, t_lbl, d_lbl, arrow_lbl):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return {"card": card, "title_lbl": t_lbl, "desc_lbl": d_lbl, "completed": completed_today}

    def _chuyen_ngon_ngu(self):
        chuyen_ngon_ngu()
        self._cap_nhat_van_ban()

    def _cap_nhat_van_ban(self):
        self.app_badge.config(text=f"[ {menu_text('app_badge')} ]")
        self.btn_lang.config(text=menu_text('ngon_ngu_btn'))
        self.subtitle_lbl.config(text=menu_text("thu_thach"))
        self.sec_title.config(text=menu_text("chon_do_kho"))

        self.card_de["title_lbl"].config(text="[ 1 ] " + menu_text("de"))
        self.card_de["desc_lbl"].config(text=menu_text("de_desc"))

        self.card_tb["title_lbl"].config(text="[ 2 ] " + menu_text("trung_binh"))
        self.card_tb["desc_lbl"].config(text=menu_text("trung_binh_desc"))

        self.card_kho["title_lbl"].config(text="[ 3 ] " + menu_text("kho"))
        self.card_kho["desc_lbl"].config(text=menu_text("kho_desc"))

        if self.resume_card:
            saved = load_game_state()
            if saved:
                diff_key = saved.difficulty
                diff_name = {"easy": menu_text("de"), "medium": menu_text("trung_binh"), "hard": menu_text("kho")}.get(diff_key, diff_key)
                elapsed = saved.get_elapsed_time()
                mins, secs = divmod(max(0, elapsed), 60)
                time_str = f"{mins:02}:{secs:02}"
                self.resume_card["desc_lbl"].config(text=menu_text("tiep_tuc_van_desc").format(diff=diff_name, time=time_str))

        if self.daily_card:
            stats = get_daily_stats()
            completed_today = stats["last_completed_date"] == date.today().isoformat()
            if completed_today:
                self.daily_card["title_lbl"].config(text="[ ✓ ] " + menu_text("daily_challenge"), fg=MENU_COLORS['secondary'])
                self.daily_card["desc_lbl"].config(text=f"{menu_text('completed_today')}  {menu_text('streak_label').format(n=stats['streak'])}")
            else:
                self.daily_card["title_lbl"].config(text="[ ⚡ ] " + menu_text("daily_challenge"), fg=MENU_COLORS['primary'])
                self.daily_card["desc_lbl"].config(text=f"{menu_text('daily_challenge_desc')}  {menu_text('streak_label').format(n=stats['streak'])}")

        self.footer_lbl.config(text=menu_text("chuc_vui_ve"))

    def _canh_giua_cua_so(self):
        self.root.update_idletasks()
        chieu_rong = 520
        chieu_cao = 660  # Increased for daily challenge card
        x = (self.root.winfo_screenwidth() // 2) - (chieu_rong // 2)
        y = (self.root.winfo_screenheight() // 2) - (chieu_cao // 2)
        self.root.geometry(f'{chieu_rong}x{chieu_cao}+{x}+{y}')

    def _bat_dau_tro_choi(self, do_kho, loaded_state=None):
        self.root.withdraw()
        thang = self.start_game_func(self.root, do_kho, loaded_state)
        self.root.deiconify()
        if thang:
            if not messagebox.askyesno(menu_text("chien_thang"), menu_text("chuc_mung")):
                self.root.destroy()

    def chay(self):
        self.root.mainloop()


def tao_nut_bat_dau(start_game_func=None):
    enable_high_dpi()
    if start_game_func is None:
        from game import start_game
        start_game_func = start_game
    menu = MenuSudoku(start_game_func)
    menu.chay()