import copy
import ctypes
import math
import os
import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import font as tkfont
from tkinter import messagebox, ttk

import pygame

from config import (
    APP_TITLE,
    MENU_HEADING,
    MENU_TITLE,
    VERSION_TEXT,
    chuyen_ngon_ngu,
    game_text,
    menu_text,
)
from persistence import has_save_file, load_game_state

try:
    from logic import is_valid_placement
except ImportError:
    is_valid_placement = None


def enable_high_dpi() -> None:
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def get_sudoku_icon_path() -> str:
    return os.path.join(os.path.dirname(__file__), "Picture", "SUDOKU.ico")


# Kích thước màn hình
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 740

BOARD_SIZE = 558
CELL_SIZE = BOARD_SIZE // 9  # 62px

BOARD_X = 36
BOARD_Y = 100

SIDEBAR_X = BOARD_X + BOARD_SIZE + 28  # 622
SIDEBAR_Y = BOARD_Y
SIDEBAR_WIDTH = SCREEN_WIDTH - SIDEBAR_X - 36  # 302


@dataclass(frozen=True)
class GameFonts:
    cell: pygame.font.Font
    cell_bold: pygame.font.Font
    small: pygame.font.Font
    medium: pygame.font.Font
    large: pygame.font.Font
    title: pygame.font.Font
    note: pygame.font.Font
    tiny: pygame.font.Font
    badge: pygame.font.Font


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-10, 2)
        self.lifetime = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.22
        self.lifetime -= 0.02

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = max(0, min(255, int(self.lifetime * 255)))
            radius = max(2, int(4 * self.lifetime))
            glow_radius = radius * 3
            surface_size = glow_radius * 2
            particle_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            center = (glow_radius, glow_radius)
            pygame.draw.circle(particle_surface, (*self.color, alpha // 4), center, glow_radius)
            pygame.draw.circle(particle_surface, (*self.color, alpha), center, radius)
            screen.blit(particle_surface, (int(self.x) - glow_radius, int(self.y) - glow_radius))


def load_fonts() -> GameFonts:
    def get_font(size: int, is_bold: bool = False, is_italic: bool = False) -> pygame.font.Font:
        for font_name in ("segoe ui", "tahoma", "helvetica", "arial"):
            matched_font = pygame.font.match_font(font_name, bold=is_bold, italic=is_italic)
            if matched_font:
                return pygame.font.Font(matched_font, size)
        return pygame.font.SysFont("arial", size, bold=is_bold, italic=is_italic)

    return GameFonts(
        cell=get_font(38, is_bold=True),
        cell_bold=get_font(42, is_bold=True),
        small=get_font(16, is_bold=True),
        medium=get_font(24, is_bold=True),
        large=get_font(36, is_bold=True),
        title=get_font(24, is_bold=True),
        note=get_font(13, is_bold=True),
        tiny=get_font(13),
        badge=get_font(12, is_bold=True),
    )


def create_game_screen() -> pygame.Surface:
    enable_high_dpi()
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(APP_TITLE)
    try:
        icon_path = get_sudoku_icon_path()
        if os.path.exists(icon_path):
            pygame.display.set_icon(pygame.image.load(icon_path))
    except Exception:
        pass
    return screen


class Colors:
    BG_MAIN = (248, 250, 252)         # Slate-50 sạch sẽ, sang trọng
    BG_CARD = (255, 255, 255)         # Thẻ trắng thuần khiết
    BG_BOARD = (255, 255, 255)
    WHITE = (255, 255, 255)

    GRID_THIN = (226, 232, 240)       # Slate-200
    GRID_THICK = (51, 65, 85)         # Slate-700
    GRID_OUTER = (15, 23, 42)         # Slate-900
    CARD_BORDER = (226, 232, 240)
    SHADOW = (226, 232, 240)

    FIXED_TEXT = (15, 23, 42)         # Slate-900 (Đề bài đậm rõ)
    USER_TEXT = (37, 99, 235)         # Blue-600 (Người chơi)
    HINT_TEXT = (5, 150, 105)         # Emerald-600 (Gợi ý)
    ERROR_TEXT = (220, 38, 38)        # Red-600 (Lỗi)
    NOTE_TEXT = (100, 116, 139)       # Slate-500 (Ghi chú)

    SELECTED_BG = (238, 242, 255)     # Indigo-50
    SELECTED_BORDER = (79, 70, 229)   # Indigo-600
    CROSSHAIR = (241, 245, 249)       # Slate-100
    SAME_NUMBER = (254, 243, 199)     # Amber-100 (Vàng ấm dịu mắt)
    ERROR_BG = (254, 226, 226)        # Red-100

    BTN_PRIMARY = (79, 70, 229)       # Indigo-600
    BTN_PRIMARY_HOVER = (67, 56, 202) # Indigo-700
    BTN_SECONDARY = (241, 245, 249)   # Slate-100
    BTN_SECONDARY_HOVER = (226, 232, 240)
    BTN_SECONDARY_TEXT = (30, 41, 59)

    BTN_ACTIVE = (238, 242, 255)      # Indigo-50
    BTN_ACTIVE_BORDER = (79, 70, 229)
    BTN_ACTIVE_TEXT = (67, 56, 202)

    BTN_SUCCESS = (16, 185, 129)      # Emerald-500
    BTN_SUCCESS_HOVER = (5, 150, 105)
    BTN_WARNING = (245, 158, 11)      # Amber-500
    BTN_WARNING_HOVER = (217, 119, 6)
    BTN_DANGER = (239, 68, 68)        # Red-500
    BTN_DANGER_HOVER = (220, 38, 38)

    NUM_DONE_BG = (241, 245, 249)
    NUM_DONE_TEXT = (148, 163, 184)

    HEADER_BG = (255, 255, 255)
    TIMER_TEXT = (15, 23, 42)
    STATUS_TEXT = (71, 85, 105)
    GOLD = (234, 179, 8)


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


# ==============================================================================
# BỘ RENDER ICON SUPERSAMPLED (KHỬ RĂNG CƯA 4X - MỊN MÀNG CHUẨN ĐỒ HỌA CAO CẤP)
# ==============================================================================

class SmoothIcons:
    _cache = {}

    @classmethod
    def get(cls, name: str, size: int, color) -> pygame.Surface:
        key = (name, size, color)
        if key in cls._cache:
            return cls._cache[key]

        scale = 4
        canvas_size = size * scale
        surf = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
        cx, cy = canvas_size / 2, canvas_size / 2
        s = canvas_size

        if name == 'undo':
            r = s * 0.28
            rect = pygame.Rect(cx - r, cy - r + s * 0.04, r * 2, r * 2)
            pygame.draw.arc(surf, color, rect, 0.4, 3.2, int(s * 0.08))
            tip_x, tip_y = cx - r + s * 0.02, cy + s * 0.04
            pts = [(tip_x - s * 0.02, tip_y - s * 0.15), (tip_x - s * 0.15, tip_y + s * 0.03), (tip_x + s * 0.07, tip_y + s * 0.03)]
            pygame.draw.polygon(surf, color, pts)

        elif name == 'redo':
            r = s * 0.28
            rect = pygame.Rect(cx - r, cy - r + s * 0.04, r * 2, r * 2)
            pygame.draw.arc(surf, color, rect, -0.05, 2.75, int(s * 0.08))
            tip_x, tip_y = cx + r - s * 0.02, cy + s * 0.04
            pts = [(tip_x + s * 0.02, tip_y - s * 0.15), (tip_x + s * 0.15, tip_y + s * 0.03), (tip_x - s * 0.07, tip_y + s * 0.03)]
            pygame.draw.polygon(surf, color, pts)

        elif name == 'pencil':
            p_body = [
                (cx - s * 0.20, cy + s * 0.16),
                (cx + s * 0.16, cy - s * 0.20),
                (cx + s * 0.23, cy - s * 0.13),
                (cx - s * 0.13, cy + s * 0.23),
            ]
            pygame.draw.polygon(surf, color, p_body)
            p_tip = [
                (cx - s * 0.20, cy + s * 0.16),
                (cx - s * 0.13, cy + s * 0.23),
                (cx - s * 0.28, cy + s * 0.28),
            ]
            pygame.draw.polygon(surf, color, p_tip)

        elif name == 'hint':
            r = s * 0.20
            bulb_cy = cy - s * 0.06
            pygame.draw.circle(surf, color, (int(cx), int(bulb_cy)), int(r), width=int(s * 0.07))
            base_w = s * 0.20
            pygame.draw.line(surf, color, (cx - base_w / 2, cy + r - s * 0.04), (cx + base_w / 2, cy + r - s * 0.04), int(s * 0.07))
            pygame.draw.line(surf, color, (cx - base_w * 0.3, cy + r + s * 0.03), (cx + base_w * 0.3, cy + r + s * 0.03), int(s * 0.07))

        elif name == 'erase':
            half = s * 0.20
            pygame.draw.line(surf, color, (cx - half, cy - half), (cx + half, cy + half), int(s * 0.08))
            pygame.draw.line(surf, color, (cx + half, cy - half), (cx - half, cy + half), int(s * 0.08))

        elif name == 'sparkles':
            for offset_x, offset_y, star_r in [(0, -s * 0.08, s * 0.22), (s * 0.20, s * 0.14, s * 0.11), (-s * 0.20, s * 0.14, s * 0.11)]:
                scx, scy = cx + offset_x, cy + offset_y
                pts = [
                    (scx, scy - star_r), (scx + star_r * 0.25, scy - star_r * 0.25),
                    (scx + star_r, scy), (scx + star_r * 0.25, scy + star_r * 0.25),
                    (scx, scy + star_r), (scx - star_r * 0.25, scy + star_r * 0.25),
                    (scx - star_r, scy), (scx - star_r * 0.25, scy - star_r * 0.25),
                ]
                pygame.draw.polygon(surf, color, pts)

        elif name == 'clock':
            r = s * 0.32
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r), width=int(s * 0.08))
            pygame.draw.line(surf, color, (cx, cy), (cx, cy - r * 0.65), int(s * 0.08))
            pygame.draw.line(surf, color, (cx, cy), (cx + r * 0.6, cy), int(s * 0.08))
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(s * 0.06))

        elif name == 'pause':
            bar_w = s * 0.10
            bar_h = s * 0.44
            gap = s * 0.12
            r1 = pygame.Rect(cx - gap / 2 - bar_w, cy - bar_h / 2, bar_w, bar_h)
            r2 = pygame.Rect(cx + gap / 2, cy - bar_h / 2, bar_w, bar_h)
            pygame.draw.rect(surf, color, r1, border_radius=int(s * 0.04))
            pygame.draw.rect(surf, color, r2, border_radius=int(s * 0.04))

        elif name == 'play':
            half = s * 0.24
            pts = [(cx - half * 0.7, cy - half), (cx + half * 0.9, cy), (cx - half * 0.7, cy + half)]
            pygame.draw.polygon(surf, color, pts)

        elif name == 'restart':
            r = s * 0.28
            arc_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            pygame.draw.arc(surf, color, arc_rect, 0.6, 5.8, int(s * 0.08))
            tip_x, tip_y = cx + r - s * 0.02, cy - s * 0.02
            pts = [(tip_x + s * 0.09, tip_y - s * 0.09), (tip_x - s * 0.09, tip_y - s * 0.09), (tip_x, tip_y + s * 0.08)]
            pygame.draw.polygon(surf, color, pts)

        elif name == 'home':
            half = s * 0.26
            roof = [(cx, cy - half), (cx + half + s * 0.02, cy - s * 0.02), (cx - half - s * 0.02, cy - s * 0.02)]
            pygame.draw.polygon(surf, color, roof)
            body = pygame.Rect(cx - half + s * 0.06, cy - s * 0.02, (half - s * 0.06) * 2, half * 0.9)
            pygame.draw.rect(surf, color, body, width=int(s * 0.07), border_radius=int(s * 0.02))

        elif name == 'check':
            pts = [(cx - s * 0.24, cy), (cx - s * 0.06, cy + s * 0.20), (cx + s * 0.24, cy - s * 0.18)]
            pygame.draw.lines(surf, color, False, pts, width=int(s * 0.08))

        elif name == 'trophy':
            w, h = s * 0.5, s * 0.5
            cup_rect = pygame.Rect(cx - w * 0.35, cy - h * 0.45, w * 0.7, h * 0.5)
            pygame.draw.arc(surf, color, cup_rect, 3.14, 6.28, int(s * 0.07))
            pygame.draw.line(surf, color, (cup_rect.left, cup_rect.centery), (cup_rect.right, cup_rect.centery), int(s * 0.07))
            pygame.draw.line(surf, color, (cx, cy + h * 0.05), (cx, cy + h * 0.35), int(s * 0.07))
            pygame.draw.line(surf, color, (cx - w * 0.3, cy + h * 0.35), (cx + w * 0.3, cy + h * 0.35), int(s * 0.07))
            pygame.draw.arc(surf, color, pygame.Rect(cx - w * 0.5, cy - h * 0.45, w * 0.3, h * 0.3), 1.5, 4.5, int(s * 0.06))
            pygame.draw.arc(surf, color, pygame.Rect(cx + w * 0.2, cy - h * 0.45, w * 0.3, h * 0.3), -1.5, 1.5, int(s * 0.06))

        elif name == 'grid_logo':
            rect = pygame.Rect(cx - s * 0.36, cy - s * 0.36, s * 0.72, s * 0.72)
            pygame.draw.rect(surf, color, rect, width=int(s * 0.06), border_radius=int(s * 0.08))
            step = rect.width / 3
            pygame.draw.line(surf, color, (rect.left + step, rect.top), (rect.left + step, rect.bottom), int(s * 0.05))
            pygame.draw.line(surf, color, (rect.left + step * 2, rect.top), (rect.left + step * 2, rect.bottom), int(s * 0.05))
            pygame.draw.line(surf, color, (rect.left, rect.top + step), (rect.right, rect.top + step), int(s * 0.05))
            pygame.draw.line(surf, color, (rect.left, rect.top + step * 2), (rect.right, rect.top + step * 2), int(s * 0.05))

        elif name == 'star':
            pts = []
            radius = s * 0.36
            for i in range(10):
                r = radius if i % 2 == 0 else radius * 0.44
                angle = i * math.pi / 5 - math.pi / 2
                pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
            pygame.draw.polygon(surf, color, pts)

        smooth_result = pygame.transform.smoothscale(surf, (size, size))
        cls._cache[key] = smooth_result
        return smooth_result


# ==============================================================================
# HÀM BỐ CỤC & TÍNH TOÁN VỊ TRÍ
# ==============================================================================

def get_timer_rect() -> pygame.Rect:
    return pygame.Rect(SCREEN_WIDTH - 250, 22, 115, 46)


def get_cell_from_pos(x: int, y: int):
    if not (BOARD_X <= x < BOARD_X + BOARD_SIZE and BOARD_Y <= y < BOARD_Y + BOARD_SIZE):
        return None
    row = (y - BOARD_Y) * 9 // BOARD_SIZE
    col = (x - BOARD_X) * 9 // BOARD_SIZE
    return (row, col) if 0 <= row < 9 and 0 <= col < 9 else None


def get_sidebar_layout() -> dict:
    x = SIDEBAR_X
    w = SIDEBAR_WIDTH
    y = SIDEBAR_Y

    # 1. Nhóm Thao tác nhanh (4 nút: Hoàn tác, Làm lại, Ghi chú, Gợi ý)
    quick_btn_w = (w - 18) // 4
    quick_btn_h = 58
    quick_buttons = []
    for i in range(4):
        bx = x + i * (quick_btn_w + 6)
        quick_buttons.append(pygame.Rect(bx, y, quick_btn_w, quick_btn_h))

    y += quick_btn_h + 12

    # 2. Nhóm Công cụ (Xóa ô, Ghi chú tự động)
    tool_btn_w = (w - 10) // 2
    tool_btn_h = 42
    clear_rect = pygame.Rect(x, y, tool_btn_w, tool_btn_h)
    auto_notes_rect = pygame.Rect(x + tool_btn_w + 10, y, tool_btn_w, tool_btn_h)

    y += tool_btn_h + 18

    # 3. Bàn phím số 1-9 (3x3 grid)
    num_grid_y = y + 18
    num_btn_w = (w - 16) // 3
    num_btn_h = 58
    number_buttons = []
    for i in range(9):
        col = i % 3
        row = i // 3
        number_buttons.append(pygame.Rect(
            x + col * (num_btn_w + 8),
            num_grid_y + row * (num_btn_h + 8),
            num_btn_w,
            num_btn_h,
        ))

    y = num_grid_y + 3 * (num_btn_h + 8) + 14

    # 4. Nhóm Hành động cuối (Ván mới, Thoát về menu)
    action_btn_w = (w - 10) // 2
    action_btn_h = 46
    new_game_rect = pygame.Rect(x, y, action_btn_w, action_btn_h)
    menu_rect = pygame.Rect(x + action_btn_w + 10, y, action_btn_w, action_btn_h)

    return {
        "quick_undo": quick_buttons[0],
        "quick_redo": quick_buttons[1],
        "quick_notes": quick_buttons[2],
        "quick_hint": quick_buttons[3],
        "clear": clear_rect,
        "auto_notes": auto_notes_rect,
        "numbers": number_buttons,
        "new_game": new_game_rect,
        "menu": menu_rect,
        "undo": quick_buttons[0],
        "redo": quick_buttons[1],
    }


def draw_rounded_card(screen: pygame.Surface, rect: pygame.Rect, bg_color, border_color=None, border_width=1, radius=12, shadow=True):
    if shadow:
        shadow_rect = rect.move(0, 3)
        pygame.draw.rect(screen, Colors.SHADOW, shadow_rect, border_radius=radius)
    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(screen, border_color, rect, width=border_width, border_radius=radius)


def draw_modern_button(screen: pygame.Surface, rect: pygame.Rect, text: str, mouse_pos, font_to_use,
                       variant='secondary', is_active=False, subtext=None, sub_font=None, radius=10, icon_name=None, icon_size=20):
    is_hover = rect.collidepoint(mouse_pos)

    # Thiết lập màu sắc
    if is_active:
        bg_color = Colors.BTN_ACTIVE
        border_color = Colors.BTN_ACTIVE_BORDER
        text_color = Colors.BTN_ACTIVE_TEXT
        border_w = 2
    elif variant == 'primary':
        bg_color = Colors.BTN_PRIMARY_HOVER if is_hover else Colors.BTN_PRIMARY
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == 'success':
        bg_color = Colors.BTN_SUCCESS_HOVER if is_hover else Colors.BTN_SUCCESS
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == 'warning':
        bg_color = Colors.BTN_WARNING_HOVER if is_hover else Colors.BTN_WARNING
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == 'danger':
        bg_color = Colors.BTN_DANGER_HOVER if is_hover else Colors.BTN_DANGER
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == 'disabled':
        bg_color = Colors.NUM_DONE_BG
        border_color = Colors.CARD_BORDER
        text_color = Colors.NUM_DONE_TEXT
        border_w = 1
    else:  # secondary
        bg_color = Colors.BTN_SECONDARY_HOVER if is_hover else Colors.BTN_SECONDARY
        border_color = Colors.CARD_BORDER
        text_color = Colors.BTN_SECONDARY_TEXT
        border_w = 1

    # Đổ bóng
    if variant != 'disabled':
        shadow_rect = rect.move(0, 2 if not is_hover else 3)
        pygame.draw.rect(screen, Colors.SHADOW, shadow_rect, border_radius=radius)

    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    if border_color and border_w > 0:
        pygame.draw.rect(screen, border_color, rect, width=border_w, border_radius=radius)

    # Vẽ nội dung icon và text
    if icon_name and subtext and sub_font:
        # Nút card dọc (Quick action buttons): Icon ở trên, text ở dưới
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        icon_rect = icon_surf.get_rect(center=(rect.centerx, rect.top + 20))
        screen.blit(icon_surf, icon_rect)

        s_surf = sub_font.render(subtext, True, text_color)
        screen.blit(s_surf, s_surf.get_rect(center=(rect.centerx, rect.bottom - 13)))
        return rect

    elif icon_name and text:
        # Nút card ngang: Icon ở trái, text ở phải
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        t_surf = font_to_use.render(text, True, text_color)
        total_w = icon_size + 8 + t_surf.get_width()
        start_x = rect.centerx - total_w // 2

        icon_rect = icon_surf.get_rect(midleft=(start_x, rect.centery))
        screen.blit(icon_surf, icon_rect)
        screen.blit(t_surf, (icon_rect.right + 8, rect.centery - t_surf.get_height() // 2))
        return rect

    elif subtext and sub_font:
        # Nút số: Digit ở trên, subtext badge ở dưới
        t_surf = font_to_use.render(text, True, text_color)
        s_surf = sub_font.render(subtext, True, text_color)
        total_h = t_surf.get_height() + s_surf.get_height() + 2
        start_y = rect.centery - total_h // 2
        screen.blit(t_surf, t_surf.get_rect(center=(rect.centerx, start_y + t_surf.get_height() // 2)))
        screen.blit(s_surf, s_surf.get_rect(center=(rect.centerx, start_y + t_surf.get_height() + s_surf.get_height() // 2)))
        return rect

    elif text:
        t_surf = font_to_use.render(text, True, text_color)
        screen.blit(t_surf, t_surf.get_rect(center=rect.center))
        return rect

    elif icon_name:
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        screen.blit(icon_surf, icon_surf.get_rect(center=rect.center))
        return rect

    return rect


def draw_header(screen: pygame.Surface, fonts: GameFonts, state, mouse_pos, translate) -> dict:
    header_rect = pygame.Rect(BOARD_X, 18, SCREEN_WIDTH - BOARD_X * 2, 60)
    draw_rounded_card(screen, header_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=12)

    # 1. Logo 3x3 Grid & App Title
    logo_x = header_rect.left + 24
    logo_surf = SmoothIcons.get('grid_logo', 24, Colors.BTN_PRIMARY)
    screen.blit(logo_surf, logo_surf.get_rect(midleft=(logo_x, header_rect.centery)))

    title_text = fonts.title.render("SUDOKU", True, Colors.FIXED_TEXT)
    screen.blit(title_text, (logo_x + 32, header_rect.centery - title_text.get_height() // 2))

    # 2. Huy hiệu Độ khó có sao vàng mượt mà
    diff_key = state.difficulty
    diff_name = translate(diff_key)
    star_count = {"easy": 1, "medium": 2, "hard": 3}.get(diff_key, 1)

    diff_badge_rect = pygame.Rect(header_rect.left + 185, header_rect.centery - 18, 140, 36)
    pygame.draw.rect(screen, Colors.SELECTED_BG, diff_badge_rect, border_radius=18)
    pygame.draw.rect(screen, Colors.SELECTED_BORDER, diff_badge_rect, width=1, border_radius=18)

    # Vẽ các ngôi sao vàng mượt mà
    star_start_x = diff_badge_rect.left + 16
    for s_idx in range(star_count):
        star_surf = SmoothIcons.get('star', 13, Colors.GOLD)
        screen.blit(star_surf, star_surf.get_rect(center=(star_start_x + s_idx * 14, diff_badge_rect.centery)))

    diff_surf = fonts.small.render(diff_name, True, Colors.BTN_ACTIVE_TEXT)
    diff_text_x = star_start_x + star_count * 14 + 6
    screen.blit(diff_surf, (diff_text_x, diff_badge_rect.centery - diff_surf.get_height() // 2))

    # 3. Đồng hồ bấm giờ (Icon đồng hồ + Time text)
    elapsed = state.get_elapsed_time()
    mins, secs = divmod(max(0, elapsed), 60)
    time_str = f"{mins:02}:{secs:02}"
    timer_x = header_rect.right - 235

    clock_surf = SmoothIcons.get('clock', 20, Colors.TIMER_TEXT)
    screen.blit(clock_surf, clock_surf.get_rect(midleft=(timer_x + 6, header_rect.centery)))

    timer_surf = fonts.medium.render(time_str, True, Colors.TIMER_TEXT)
    screen.blit(timer_surf, (timer_x + 32, header_rect.centery - timer_surf.get_height() // 2))

    # 4. Nút Tạm dừng / Tiếp tục
    pause_btn_rect = pygame.Rect(header_rect.right - 110, header_rect.centery - 18, 95, 36)
    pause_label = translate("tiep_tuc") if state.paused else translate("tam_dung_btn")
    pause_variant = 'warning' if state.paused else 'secondary'
    pause_icon = 'play' if state.paused else 'pause'
    draw_modern_button(screen, pause_btn_rect, pause_label, mouse_pos, fonts.small,
                       variant=pause_variant, radius=8, icon_name=pause_icon, icon_size=16)

    return {"pause": pause_btn_rect}


def draw_board(screen: pygame.Surface, fonts: GameFonts, state, selected_cell=None):
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)
    draw_rounded_card(screen, board_rect, Colors.BG_BOARD, Colors.GRID_OUTER, border_width=2, radius=10)

    r_sel, c_sel = (selected_cell if selected_cell else state.selected)
    highlight_num = state.board[r_sel][c_sel] if state.selected else 0

    # 1. Vẽ các lớp highlight nền
    for r in range(9):
        for c in range(9):
            cell_rect = pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            # Crosshair
            if state.selected and not state.paused:
                if r == r_sel or c == c_sel or (r // 3 == r_sel // 3 and c // 3 == c_sel // 3):
                    pygame.draw.rect(screen, Colors.CROSSHAIR, cell_rect)

            # Cùng số với ô đang chọn
            if highlight_num != 0 and state.board[r][c] == highlight_num and not state.paused:
                pygame.draw.rect(screen, Colors.SAME_NUMBER, cell_rect)

            # Ô lỗi
            if state.board[r][c] != 0 and state.original[r][c] == 0:
                is_err = False
                if is_valid_placement and not is_valid_placement(state.board, r, c, state.board[r][c]):
                    is_err = True
                elif state.show_errors and state.board[r][c] != state.solution[r][c]:
                    is_err = True
                if is_err:
                    pygame.draw.rect(screen, Colors.ERROR_BG, cell_rect)

            # Ô đang chọn trực tiếp
            if (r, c) == (r_sel, c_sel) and not state.paused:
                pygame.draw.rect(screen, Colors.SELECTED_BG, cell_rect)

    # 2. Vẽ đường lưới
    for i in range(10):
        is_thick = (i % 3 == 0)
        line_color = Colors.GRID_THICK if is_thick else Colors.GRID_THIN
        line_width = 3 if is_thick else 1

        x = BOARD_X + i * CELL_SIZE
        y = BOARD_Y + i * CELL_SIZE
        pygame.draw.line(screen, line_color, (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), line_width)
        pygame.draw.line(screen, line_color, (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), line_width)

    # 3. Viền phát sáng cho ô đang chọn
    if state.selected and not state.paused:
        sel_rect = pygame.Rect(BOARD_X + c_sel * CELL_SIZE, BOARD_Y + r_sel * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, Colors.SELECTED_BORDER, sel_rect, width=3, border_radius=4)

    # 4. Vẽ số và ghi chú
    if not state.paused:
        for r in range(9):
            for c in range(9):
                cell_rect = pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                val = state.board[r][c]

                if val != 0:
                    is_fixed = (state.original[r][c] != 0)
                    if is_fixed:
                        color = Colors.FIXED_TEXT
                    elif is_valid_placement and not is_valid_placement(state.board, r, c, val):
                        color = Colors.ERROR_TEXT
                    elif state.show_errors and val != state.solution[r][c]:
                        color = Colors.ERROR_TEXT
                    else:
                        color = Colors.USER_TEXT

                    font_to_use = fonts.cell_bold if is_fixed else fonts.cell
                    num_surf = font_to_use.render(str(val), True, color)
                    screen.blit(num_surf, num_surf.get_rect(center=cell_rect.center))
                elif state.notes[r][c]:
                    sub_size = CELL_SIZE // 3
                    for note_digit in sorted(state.notes[r][c]):
                        nr = (note_digit - 1) // 3
                        nc = (note_digit - 1) % 3
                        note_center = (
                            cell_rect.left + nc * sub_size + sub_size // 2,
                            cell_rect.top + nr * sub_size + sub_size // 2,
                        )
                        note_surf = fonts.note.render(str(note_digit), True, Colors.NOTE_TEXT)
                        screen.blit(note_surf, note_surf.get_rect(center=note_center))


def get_remaining_counts(board) -> dict:
    counts = dict.fromkeys(range(1, 10), 0)
    for row in board:
        for val in row:
            if 1 <= val <= 9:
                counts[val] += 1
    return {num: max(0, 9 - counts[num]) for num in range(1, 10)}


def draw_controls(screen: pygame.Surface, fonts: GameFonts, mouse_pos, translate, state) -> dict:
    layout = get_sidebar_layout()
    rem_counts = get_remaining_counts(state.board)

    # 1. Tiêu đề nhóm Thao tác nhanh
    sec1_label = fonts.badge.render(translate("thao_tac_nhanh"), True, Colors.STATUS_TEXT)
    screen.blit(sec1_label, (SIDEBAR_X + 2, SIDEBAR_Y - 20))

    # Nút Hoàn tác & Làm lại
    draw_modern_button(screen, layout["quick_undo"], "", mouse_pos, fonts.medium,
                       variant='secondary', subtext=translate("hoan_tac"), sub_font=fonts.badge,
                       icon_name='undo', icon_size=20)
    draw_modern_button(screen, layout["quick_redo"], "", mouse_pos, fonts.medium,
                       variant='secondary', subtext=translate("lam_lai"), sub_font=fonts.badge,
                       icon_name='redo', icon_size=20)

    # Nút Ghi chú
    notes_active = state.notes_mode
    notes_subtext = f"{translate('ghi_chu')} {'ON' if notes_active else 'OFF'}"
    draw_modern_button(screen, layout["quick_notes"], "", mouse_pos, fonts.small,
                       variant='secondary', is_active=notes_active,
                       subtext=notes_subtext, sub_font=fonts.badge,
                       icon_name='pencil', icon_size=20)

    # Nút Gợi ý
    draw_modern_button(screen, layout["quick_hint"], "", mouse_pos, fonts.small,
                       variant='secondary', subtext=translate("goi_y"), sub_font=fonts.badge,
                       icon_name='hint', icon_size=20)

    # 2. Nhóm Công cụ (Xóa & Tự động ghi chú)
    draw_modern_button(screen, layout["clear"], translate('xoa_btn'), mouse_pos, fonts.small,
                       variant='danger', icon_name='erase', icon_size=16)
    draw_modern_button(screen, layout["auto_notes"], translate('ghi_chu_tu_dong'), mouse_pos, fonts.badge,
                       variant='secondary', icon_name='sparkles', icon_size=16)

    # 3. Tiêu đề nhóm Bàn phím số
    num_title_y = layout["clear"].bottom + 10
    sec2_label = fonts.badge.render(translate("ban_phim_so"), True, Colors.STATUS_TEXT)
    screen.blit(sec2_label, (SIDEBAR_X + 2, num_title_y))

    # Bàn phím số 1-9
    for i, num_rect in enumerate(layout["numbers"]):
        digit = i + 1
        rem = rem_counts[digit]
        is_done = (rem == 0)

        if is_done:
            sub_text = translate("con_lai_du")
            btn_variant = 'disabled'
        else:
            sub_text = translate("con_lai_fmt").replace("{n}", str(rem))
            btn_variant = 'secondary'

        draw_modern_button(screen, num_rect, str(digit), mouse_pos, fonts.medium,
                           variant=btn_variant, subtext=sub_text, sub_font=fonts.badge, radius=8)

        # Vẽ icon checkmark xanh mượt khi số đã hoàn thành
        if is_done:
            chk_surf = SmoothIcons.get('check', 12, Colors.BTN_SUCCESS)
            screen.blit(chk_surf, chk_surf.get_rect(center=(num_rect.right - 12, num_rect.top + 12)))

    # 4. Nhóm Hành động cuối (Ván mới & Về Menu)
    draw_modern_button(screen, layout["new_game"], translate('van_moi'), mouse_pos, fonts.small,
                       variant='warning', icon_name='restart', icon_size=16)
    draw_modern_button(screen, layout["menu"], translate('thoat_ve_menu'), mouse_pos, fonts.small,
                       variant='secondary', icon_name='home', icon_size=16)

    return layout


def draw_footer_helper(screen: pygame.Surface, fonts: GameFonts, translate) -> None:
    helper_rect = pygame.Rect(BOARD_X, SCREEN_HEIGHT - 44, SCREEN_WIDTH - BOARD_X * 2, 32)
    pygame.draw.rect(screen, Colors.BG_CARD, helper_rect, border_radius=8)
    pygame.draw.rect(screen, Colors.CARD_BORDER, helper_rect, width=1, border_radius=8)

    txt = f"{translate('move')}  |  {translate('input')}  |  {translate('notes_shortcut')}  |  {translate('delete')}"
    help_surf = fonts.tiny.render(txt, True, Colors.STATUS_TEXT)
    screen.blit(help_surf, help_surf.get_rect(center=helper_rect.center))


def draw_game_view(screen: pygame.Surface, fonts: GameFonts, state, mouse_pos, particles=None, translate=game_text) -> dict:
    overlay_rects = {
        "pause_resume": None,
        "pause_quit": None,
        "win_restart": None,
        "win_quit": None,
        "header_pause": None,
    }

    screen.fill(Colors.BG_MAIN)

    # 1. Header
    header_res = draw_header(screen, fonts, state, mouse_pos, translate)
    overlay_rects["header_pause"] = header_res["pause"]

    # 2. Bàn cờ
    draw_board(screen, fonts, state)

    # 3. Sidebar & Footer
    if not state.game_over and not state.paused:
        draw_controls(screen, fonts, mouse_pos, translate, state)
        draw_footer_helper(screen, fonts, translate)

    # 4. Màn hình Chiến thắng (Victory Modal)
    if state.game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 23, 42, 170))
        screen.blit(overlay, (0, 0))

        if particles:
            for p in particles:
                p.draw(screen)

        card_w, card_h = 460, 320
        modal_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h)
        draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

        # Cúp vàng mượt mà
        trophy_surf = SmoothIcons.get('trophy', 48, Colors.GOLD)
        screen.blit(trophy_surf, trophy_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 50)))

        win_title = fonts.large.render(translate('chien_thang'), True, Colors.GOLD)
        screen.blit(win_title, win_title.get_rect(center=(modal_rect.centerx, modal_rect.top + 95)))

        sub_msg = fonts.small.render(translate("chuc_mung_thang"), True, Colors.STATUS_TEXT)
        screen.blit(sub_msg, sub_msg.get_rect(center=(modal_rect.centerx, modal_rect.top + 130)))

        mins, secs = divmod(max(0, state.final_time), 60)
        time_info = f"{translate('thoi_gian_hoan_thanh')}: {mins:02}:{secs:02}"
        time_surf = fonts.medium.render(time_info, True, Colors.FIXED_TEXT)
        screen.blit(time_surf, time_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 165)))

        # Nút Chơi tiếp & Về Menu
        btn_w, btn_h = 180, 48
        btn_y = modal_rect.bottom - 75
        win_restart = pygame.Rect(modal_rect.centerx - btn_w - 12, btn_y, btn_w, btn_h)
        win_quit = pygame.Rect(modal_rect.centerx + 12, btn_y, btn_w, btn_h)

        draw_modern_button(screen, win_restart, translate('choi_tiep'), mouse_pos, fonts.small,
                           variant='primary', icon_name='restart', icon_size=18)
        draw_modern_button(screen, win_quit, translate('thoat_ve_menu'), mouse_pos, fonts.small,
                           variant='secondary', icon_name='home', icon_size=18)

        overlay_rects["win_restart"] = win_restart
        overlay_rects["win_quit"] = win_quit

    # 5. Màn hình Tạm dừng (Pause Modal)
    elif state.paused:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 23, 42, 180))
        screen.blit(overlay, (0, 0))

        card_w, card_h = 420, 260
        modal_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h)
        draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

        # Icon tạm dừng mượt mà
        pause_surf = SmoothIcons.get('pause', 36, Colors.FIXED_TEXT)
        screen.blit(pause_surf, pause_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 45)))

        pause_title = fonts.large.render(translate('tam_dung'), True, Colors.FIXED_TEXT)
        screen.blit(pause_title, pause_title.get_rect(center=(modal_rect.centerx, modal_rect.top + 90)))

        # Nút Tiếp tục & Thoát
        btn_w, btn_h = 165, 48
        btn_y = modal_rect.bottom - 80
        pause_resume = pygame.Rect(modal_rect.centerx - btn_w - 10, btn_y, btn_w, btn_h)
        pause_quit = pygame.Rect(modal_rect.centerx + 10, btn_y, btn_w, btn_h)

        draw_modern_button(screen, pause_resume, translate('tiep_tuc'), mouse_pos, fonts.small,
                           variant='primary', icon_name='play', icon_size=18)
        draw_modern_button(screen, pause_quit, translate('thoat_ve_menu'), mouse_pos, fonts.small,
                           variant='secondary', icon_name='home', icon_size=18)

        overlay_rects["pause_resume"] = pause_resume
        overlay_rects["pause_quit"] = pause_quit

    pygame.display.flip()
    return overlay_rects


# ==============================================================================
# GIAO DIỆN MENU KHỞI ĐỘNG (TKINTER MODERN MENU)
# ==============================================================================

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

        # 4. Resume Game Card (if save exists)
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

        # 6. Footer
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
        # Try to load saved state to get difficulty and time
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
        from datetime import date

        from logic import get_daily_challenge_info
        from persistence import get_daily_stats

        stats = get_daily_stats()
        get_daily_challenge_info(date.today())
        completed_today = stats["last_completed_date"] == date.today().isoformat()

        if completed_today:
            title = "[ ✓ ] " + menu_text("daily_challenge")
            desc = f"{menu_text('completed_today')}  {menu_text('streak_label').format(n=stats['streak'])}"
            accent = MENU_COLORS['secondary']  # Green for completed
            MENU_COLORS['secondary_hover']
        else:
            title = "[ ⚡ ] " + menu_text("daily_challenge")
            desc = f"{menu_text('daily_challenge_desc')}  {menu_text('streak_label').format(n=stats['streak'])}"
            accent = MENU_COLORS['primary']  # Blue for available
            MENU_COLORS['primary_hover']

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
            from logic import generate_daily_challenge
            board, solution, seed = generate_daily_challenge("medium")
            # Create a GameState with the daily challenge board
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
            state.start_time = 0  # Will be set when game starts
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

        # Update daily challenge card
        if hasattr(self, 'daily_card') and self.daily_card:
            from datetime import date

            from persistence import get_daily_stats
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
        chieu_cao = 620
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

