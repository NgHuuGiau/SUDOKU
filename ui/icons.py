"""Smooth supersampled icons for Sudoku UI."""

import math
import random

import pygame

_MODERN_ICON_NAMES = {
    "undo", "redo", "pencil", "hint", "erase", "sparkles", "clock", "pause", "play",
    "restart", "home", "check", "trophy", "grid_logo", "star", "save", "upload", "download",
    "palette", "sound", "sound_mute", "help", "close", "cross", "arrow_right", "flame", "crown",
    "calendar", "slider", "shield", "stats", "globe", "plus", "minus",
}


def _draw_modern_icon(
    name: str,
    surf: pygame.Surface,
    cx: float,
    cy: float,
    size: float,
    color: tuple[int, int, int],
) -> bool:
    """Draw the new filled geometric icon set over the legacy fallback set."""
    if name not in _MODERN_ICON_NAMES:
        return False

    soft_color = (*color, 30)
    pygame.draw.circle(surf, soft_color, (int(cx), int(cy)), max(2, int(size * 0.43)))
    width = max(2, int(size * 0.075))

    def line(points: list[tuple[float, float]], stroke_width: int = width) -> None:
        int_points = [(int(x), int(y)) for x, y in points]
        pygame.draw.lines(surf, color, False, int_points, stroke_width)
        radius = max(1, stroke_width // 2)
        for point in (int_points[0], int_points[-1]):
            pygame.draw.circle(surf, color, point, radius)

    def star(center_x: float, center_y: float, radius: float, points: int = 4) -> None:
        vertices = []
        for index in range(points * 2):
            current_radius = radius if index % 2 == 0 else radius * 0.34
            angle = index * math.pi / points - math.pi / 2
            vertices.append(
                (center_x + current_radius * math.cos(angle), center_y + current_radius * math.sin(angle))
            )
        pygame.draw.polygon(surf, color, vertices)

    if name in {"undo", "redo"}:
        radius = size * 0.25
        rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
        start, end = (0.45, 3.35) if name == "undo" else (-0.20, 2.70)
        pygame.draw.arc(surf, color, rect, start, end, width)
        direction = -1 if name == "undo" else 1
        tip_x = cx + direction * size * 0.28
        line([(tip_x, cy - size * 0.11), (tip_x - direction * size * 0.13, cy), (tip_x, cy + size * 0.11)])
    elif name == "pencil":
        pygame.draw.polygon(
            surf,
            color,
            [(cx - size * 0.24, cy + size * 0.18), (cx + size * 0.16, cy - size * 0.22),
             (cx + size * 0.27, cy - size * 0.11), (cx - size * 0.14, cy + size * 0.28)],
        )
        pygame.draw.polygon(surf, color, [(cx - size * 0.24, cy + size * 0.18),
                                           (cx - size * 0.14, cy + size * 0.28),
                                           (cx - size * 0.30, cy + size * 0.33)])
    elif name == "hint":
        pygame.draw.circle(surf, color, (int(cx), int(cy - size * 0.08)), int(size * 0.19))
        line([(cx - size * 0.13, cy + size * 0.14), (cx + size * 0.13, cy + size * 0.14)])
        line([(cx - size * 0.09, cy + size * 0.23), (cx + size * 0.09, cy + size * 0.23)])
    elif name == "erase":
        pygame.draw.polygon(surf, color, [(cx - size * 0.25, cy + size * 0.10),
                                           (cx - size * 0.02, cy - size * 0.24),
                                           (cx + size * 0.26, cy - size * 0.02),
                                           (cx + size * 0.03, cy + size * 0.32)])
        line([(cx - size * 0.08, cy + size * 0.21), (cx + size * 0.20, cy + size * 0.21)], max(1, width - 1))
    elif name == "sparkles":
        star(cx, cy - size * 0.10, size * 0.24)
        star(cx + size * 0.23, cy + size * 0.17, size * 0.12)
        star(cx - size * 0.23, cy + size * 0.20, size * 0.09)
    elif name == "clock":
        radius = size * 0.29
        pygame.draw.circle(surf, color, (int(cx), int(cy)), int(radius), width=width)
        line([(cx, cy), (cx, cy - radius * 0.55)], max(1, width - 1))
        line([(cx, cy), (cx + radius * 0.48, cy + radius * 0.12)], max(1, width - 1))
    elif name == "pause":
        bar_width = max(2, int(size * 0.12))
        bar_height = int(size * 0.44)
        for offset in (-size * 0.11, size * 0.11):
            pygame.draw.rect(surf, color, pygame.Rect(int(cx + offset - bar_width / 2), int(cy - bar_height / 2),
                                                        bar_width, bar_height), border_radius=max(1, width // 2))
    elif name == "play":
        pygame.draw.polygon(surf, color, [(cx - size * 0.14, cy - size * 0.24),
                                           (cx + size * 0.25, cy), (cx - size * 0.14, cy + size * 0.24)])
    elif name == "restart":
        radius = size * 0.27
        pygame.draw.arc(surf, color, pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2), 0.55, 5.55, width)
        line([(cx + size * 0.22, cy - size * 0.19), (cx + size * 0.30, cy - size * 0.03),
              (cx + size * 0.12, cy - size * 0.02)], max(1, width - 1))
    elif name == "home":
        pygame.draw.polygon(surf, color, [(cx, cy - size * 0.28), (cx + size * 0.30, cy - size * 0.02),
                                           (cx + size * 0.24, cy - size * 0.02), (cx + size * 0.24, cy + size * 0.27),
                                           (cx - size * 0.24, cy + size * 0.27), (cx - size * 0.24, cy - size * 0.02),
                                           (cx - size * 0.30, cy - size * 0.02)])
        pygame.draw.rect(surf, soft_color, pygame.Rect(int(cx - size * 0.06), int(cy + size * 0.06),
                                                        int(size * 0.12), int(size * 0.21)))
    elif name == "check":
        line([(cx - size * 0.24, cy), (cx - size * 0.06, cy + size * 0.18),
              (cx + size * 0.26, cy - size * 0.20)], max(2, int(size * 0.10)))
    elif name == "trophy":
        pygame.draw.polygon(surf, color, [(cx - size * 0.18, cy - size * 0.20),
                                           (cx + size * 0.18, cy - size * 0.20), (cx + size * 0.13, cy + size * 0.08),
                                           (cx, cy + size * 0.18), (cx - size * 0.13, cy + size * 0.08)])
        line([(cx, cy + size * 0.18), (cx, cy + size * 0.29)], max(1, width - 1))
        line([(cx - size * 0.18, cy + size * 0.31), (cx + size * 0.18, cy + size * 0.31)], max(1, width - 1))
    elif name == "grid_logo":
        rect = pygame.Rect(int(cx - size * 0.34), int(cy - size * 0.34), int(size * 0.68), int(size * 0.68))
        pygame.draw.rect(surf, color, rect, width=width, border_radius=max(2, int(size * 0.10)))
        step = rect.width / 3
        for multiplier in (1, 2):
            pygame.draw.line(surf, color, (rect.left + step * multiplier, rect.top + width),
                             (rect.left + step * multiplier, rect.bottom - width), max(1, width - 1))
            pygame.draw.line(surf, color, (rect.left + width, rect.top + step * multiplier),
                             (rect.right - width, rect.top + step * multiplier), max(1, width - 1))
    elif name == "star":
        star(cx, cy, size * 0.32, points=5)
    elif name == "save":
        rect = pygame.Rect(int(cx - size * 0.29), int(cy - size * 0.30), int(size * 0.58), int(size * 0.60))
        pygame.draw.rect(surf, color, rect, width=width, border_radius=max(2, int(size * 0.08)))
        pygame.draw.rect(surf, color, pygame.Rect(int(cx - size * 0.16), int(cy - size * 0.25), int(size * 0.32), int(size * 0.13)))
        pygame.draw.rect(surf, color, pygame.Rect(int(cx - size * 0.17), int(cy + size * 0.07), int(size * 0.34), int(size * 0.15)), width=max(1, width - 1))
    elif name in {"upload", "download"}:
        line([(cx - size * 0.26, cy + size * 0.24), (cx + size * 0.26, cy + size * 0.24)], max(1, width - 1))
        line([(cx - size * 0.20, cy + size * 0.15), (cx - size * 0.20, cy + size * 0.24)], max(1, width - 1))
        line([(cx + size * 0.20, cy + size * 0.15), (cx + size * 0.20, cy + size * 0.24)], max(1, width - 1))
        direction = -1 if name == "upload" else 1
        line([(cx, cy + direction * size * 0.16), (cx, cy - direction * size * 0.18)], max(1, width - 1))
        line([(cx, cy - direction * size * 0.18), (cx - size * 0.12, cy - direction * size * 0.05),
              (cx, cy - direction * size * 0.18), (cx + size * 0.12, cy - direction * size * 0.05)], max(1, width - 1))
    elif name == "palette":
        pygame.draw.circle(surf, color, (int(cx), int(cy)), int(size * 0.29), width=width)
        pygame.draw.circle(surf, color, (int(cx - size * 0.10), int(cy - size * 0.10)), max(1, int(size * 0.045)))
        pygame.draw.circle(surf, color, (int(cx + size * 0.07), int(cy - size * 0.18)), max(1, int(size * 0.045)))
        pygame.draw.circle(surf, color, (int(cx + size * 0.18), int(cy - size * 0.02)), max(1, int(size * 0.045)))
    elif name in {"sound", "sound_mute"}:
        pygame.draw.polygon(surf, color, [(cx - size * 0.28, cy - size * 0.11), (cx - size * 0.10, cy - size * 0.11),
                                           (cx + size * 0.08, cy - size * 0.27), (cx + size * 0.08, cy + size * 0.27),
                                           (cx - size * 0.10, cy + size * 0.11), (cx - size * 0.28, cy + size * 0.11)])
        if name == "sound":
            pygame.draw.arc(surf, color, pygame.Rect(int(cx - size * 0.02), int(cy - size * 0.22), int(size * 0.34), int(size * 0.44)), -1.0, 1.0, max(1, width - 1))
        else:
            line([(cx + size * 0.15, cy - size * 0.13), (cx + size * 0.30, cy + size * 0.13)], max(1, width - 1))
            line([(cx + size * 0.30, cy - size * 0.13), (cx + size * 0.15, cy + size * 0.13)], max(1, width - 1))
    elif name in {"help", "close", "cross"}:
        if name == "help":
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(size * 0.31), width=width)
            line([(cx - size * 0.09, cy - size * 0.10), (cx, cy - size * 0.18),
                  (cx + size * 0.11, cy - size * 0.09), (cx, cy + size * 0.05), (cx, cy + size * 0.12)], max(1, width - 1))
            pygame.draw.circle(surf, color, (int(cx), int(cy + size * 0.22)), max(1, int(size * 0.04)))
        else:
            line([(cx - size * 0.22, cy - size * 0.22), (cx + size * 0.22, cy + size * 0.22)], max(2, int(size * 0.10)))
            line([(cx + size * 0.22, cy - size * 0.22), (cx - size * 0.22, cy + size * 0.22)], max(2, int(size * 0.10)))
    elif name == "arrow_right":
        line([(cx - size * 0.20, cy), (cx + size * 0.18, cy), (cx, cy - size * 0.17)], max(1, width - 1))
        line([(cx + size * 0.18, cy), (cx, cy + size * 0.17)], max(1, width - 1))
    elif name == "flame":
        pygame.draw.polygon(surf, color, [(cx, cy - size * 0.34), (cx + size * 0.10, cy - size * 0.10),
                                           (cx + size * 0.23, cy), (cx + size * 0.18, cy + size * 0.22),
                                           (cx, cy + size * 0.32), (cx - size * 0.18, cy + size * 0.22),
                                           (cx - size * 0.23, cy), (cx - size * 0.10, cy - size * 0.10)])
        pygame.draw.polygon(surf, soft_color, [(cx, cy + size * 0.21), (cx - size * 0.07, cy + size * 0.05),
                                                (cx, cy - size * 0.04), (cx + size * 0.07, cy + size * 0.05)])
    elif name == "crown":
        pygame.draw.polygon(surf, color, [(cx - size * 0.30, cy + size * 0.18), (cx - size * 0.34, cy - size * 0.16),
                                           (cx - size * 0.12, cy), (cx, cy - size * 0.25),
                                           (cx + size * 0.12, cy), (cx + size * 0.34, cy - size * 0.16),
                                           (cx + size * 0.30, cy + size * 0.18)])
        pygame.draw.rect(surf, color, pygame.Rect(int(cx - size * 0.30), int(cy + size * 0.15), int(size * 0.60), int(size * 0.10)), border_radius=max(1, width // 2))
    elif name == "calendar":
        rect = pygame.Rect(int(cx - size * 0.29), int(cy - size * 0.24), int(size * 0.58), int(size * 0.52))
        pygame.draw.rect(surf, color, rect, width=width, border_radius=max(2, int(size * 0.07)))
        pygame.draw.line(surf, color, (rect.left + width, rect.top + int(size * 0.14)), (rect.right - width, rect.top + int(size * 0.14)), width)
        for offset_x in (-size * 0.14, size * 0.14):
            pygame.draw.circle(surf, color, (int(cx + offset_x), int(cy + size * 0.12)), max(1, int(size * 0.04)))
    elif name == "slider":
        pygame.draw.rect(surf, color, pygame.Rect(int(cx - size * 0.30), int(cy - width / 2), int(size * 0.60), width), border_radius=max(1, width // 2))
        pygame.draw.circle(surf, color, (int(cx + size * 0.06), int(cy)), int(size * 0.13))
    elif name == "shield":
        line([(cx - size * 0.25, cy - size * 0.26), (cx + size * 0.25, cy - size * 0.26),
              (cx + size * 0.25, cy + size * 0.04), (cx, cy + size * 0.32),
              (cx - size * 0.25, cy + size * 0.04), (cx - size * 0.25, cy - size * 0.26)], max(1, width - 1))
        line([(cx - size * 0.12, cy), (cx - size * 0.02, cy + size * 0.10), (cx + size * 0.14, cy - size * 0.10)], max(1, width - 1))
    elif name == "stats":
        for offset_x, height in ((-size * 0.22, 0.24), (0, 0.38), (size * 0.22, 0.31)):
            pygame.draw.rect(surf, color, pygame.Rect(int(cx + offset_x - size * 0.06), int(cy + size * 0.22 - size * height), int(size * 0.12), int(size * height)), border_radius=max(1, width // 2))
    elif name == "globe":
        radius = size * 0.30
        pygame.draw.circle(surf, color, (int(cx), int(cy)), int(radius), width=width)
        pygame.draw.line(surf, color, (int(cx - radius), int(cy)), (int(cx + radius), int(cy)), max(1, width - 1))
        pygame.draw.ellipse(surf, color, pygame.Rect(int(cx - radius * 0.45), int(cy - radius), int(radius * 0.90), int(radius * 2)), width=max(1, width - 1))
    elif name in {"plus", "minus"}:
        line([(cx - size * 0.22, cy), (cx + size * 0.22, cy)], max(2, int(size * 0.10)))
        if name == "plus":
            line([(cx, cy - size * 0.22), (cx, cy + size * 0.22)], max(2, int(size * 0.10)))
    return True


class SmoothIcons:
    _cache: dict[tuple[str, int, tuple[int, int, int]], pygame.Surface] = {}

    @classmethod
    def get(cls, name: str, size: int, color: tuple[int, int, int]) -> pygame.Surface:
        key = (name, size, color)
        if key in cls._cache:
            return cls._cache[key]

        scale = 4
        canvas_size = size * scale
        surf = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
        cx, cy = canvas_size / 2, canvas_size / 2
        s = canvas_size

        if _draw_modern_icon(name, surf, cx, cy, s, color):
            smooth_result = pygame.transform.smoothscale(surf, (size, size))
            cls._cache[key] = smooth_result
            return smooth_result

        stroke_width = max(2, int(s * 0.065))

        def stroke(points: list[tuple[float, float]], width: int = stroke_width) -> None:
            """Draw a rounded vector stroke for clean small-size icons."""
            int_points = [(int(x), int(y)) for x, y in points]
            pygame.draw.lines(surf, color, False, int_points, width)
            radius = max(1, width // 2)
            for point in (int_points[0], int_points[-1]):
                pygame.draw.circle(surf, color, point, radius)

        if name == "undo":
            r = s * 0.28
            rect = pygame.Rect(cx - r, cy - r + s * 0.04, r * 2, r * 2)
            pygame.draw.arc(surf, color, rect, 0.4, 3.2, int(s * 0.08))
            tip_x, tip_y = cx - r + s * 0.02, cy + s * 0.04
            pts = [
                (tip_x - s * 0.02, tip_y - s * 0.15),
                (tip_x - s * 0.15, tip_y + s * 0.03),
                (tip_x + s * 0.07, tip_y + s * 0.03),
            ]
            pygame.draw.polygon(surf, color, pts)

        elif name == "redo":
            r = s * 0.28
            rect = pygame.Rect(cx - r, cy - r + s * 0.04, r * 2, r * 2)
            pygame.draw.arc(surf, color, rect, -0.05, 2.75, int(s * 0.08))
            tip_x, tip_y = cx + r - s * 0.02, cy + s * 0.04
            pts = [
                (tip_x + s * 0.02, tip_y - s * 0.15),
                (tip_x + s * 0.15, tip_y + s * 0.03),
                (tip_x - s * 0.07, tip_y + s * 0.03),
            ]
            pygame.draw.polygon(surf, color, pts)

        elif name == "pencil":
            stroke([(cx - s * 0.23, cy + s * 0.22), (cx + s * 0.20, cy - s * 0.21)])
            stroke([(cx - s * 0.28, cy + s * 0.28), (cx - s * 0.23, cy + s * 0.22)])
            pygame.draw.line(
                surf,
                color,
                (cx + s * 0.12, cy - s * 0.28),
                (cx + s * 0.28, cy - s * 0.12),
                stroke_width,
            )

        elif name == "hint":
            r = s * 0.20
            bulb_cy = cy - s * 0.06
            pygame.draw.circle(surf, color, (int(cx), int(bulb_cy)), int(r), width=int(s * 0.07))
            base_w = s * 0.20
            pygame.draw.line(
                surf,
                color,
                (cx - base_w / 2, cy + r - s * 0.04),
                (cx + base_w / 2, cy + r - s * 0.04),
                int(s * 0.07),
            )
            pygame.draw.line(
                surf,
                color,
                (cx - base_w * 0.3, cy + r + s * 0.03),
                (cx + base_w * 0.3, cy + r + s * 0.03),
                int(s * 0.07),
            )

        elif name == "erase":
            stroke([(cx - s * 0.23, cy + s * 0.18), (cx - s * 0.06, cy + s * 0.30)])
            stroke([(cx - s * 0.06, cy + s * 0.30), (cx + s * 0.25, cy - s * 0.12)])
            stroke([(cx - s * 0.18, cy + s * 0.04), (cx + s * 0.13, cy + s * 0.16)])

        elif name == "sparkles":
            for offset_x, offset_y, star_r in [
                (0, -s * 0.08, s * 0.22),
                (s * 0.20, s * 0.14, s * 0.11),
                (-s * 0.20, s * 0.14, s * 0.11),
            ]:
                scx, scy = cx + offset_x, cy + offset_y
                pts = [
                    (scx, scy - star_r),
                    (scx + star_r * 0.25, scy - star_r * 0.25),
                    (scx + star_r, scy),
                    (scx + star_r * 0.25, scy + star_r * 0.25),
                    (scx, scy + star_r),
                    (scx - star_r * 0.25, scy + star_r * 0.25),
                    (scx - star_r, scy),
                    (scx - star_r * 0.25, scy - star_r * 0.25),
                ]
                pygame.draw.polygon(surf, color, pts)

        elif name == "clock":
            r = s * 0.32
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r), width=int(s * 0.08))
            pygame.draw.line(surf, color, (cx, cy), (cx, cy - r * 0.65), int(s * 0.08))
            pygame.draw.line(surf, color, (cx, cy), (cx + r * 0.6, cy), int(s * 0.08))
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(s * 0.06))

        elif name == "pause":
            bar_w = s * 0.10
            bar_h = s * 0.44
            gap = s * 0.12
            r1 = pygame.Rect(cx - gap / 2 - bar_w, cy - bar_h / 2, bar_w, bar_h)
            r2 = pygame.Rect(cx + gap / 2, cy - bar_h / 2, bar_w, bar_h)
            pygame.draw.rect(surf, color, r1, border_radius=int(s * 0.04))
            pygame.draw.rect(surf, color, r2, border_radius=int(s * 0.04))

        elif name == "play":
            half = s * 0.25
            stroke(
                [
                    (cx - half * 0.65, cy - half),
                    (cx + half * 0.85, cy),
                    (cx - half * 0.65, cy + half),
                    (cx - half * 0.65, cy - half),
                ]
            )

        elif name == "restart":
            r = s * 0.28
            arc_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            pygame.draw.arc(surf, color, arc_rect, 0.6, 5.8, int(s * 0.08))
            tip_x, tip_y = cx + r - s * 0.02, cy - s * 0.02
            pts = [
                (tip_x + s * 0.09, tip_y - s * 0.09),
                (tip_x - s * 0.09, tip_y - s * 0.09),
                (tip_x, tip_y + s * 0.08),
            ]
            pygame.draw.polygon(surf, color, pts)

        elif name == "home":
            half = s * 0.26
            roof = [
                (cx, cy - half),
                (cx + half + s * 0.02, cy - s * 0.02),
                (cx - half - s * 0.02, cy - s * 0.02),
            ]
            pygame.draw.polygon(surf, color, roof)
            body = pygame.Rect(
                cx - half + s * 0.06, cy - s * 0.02, (half - s * 0.06) * 2, half * 0.9
            )
            pygame.draw.rect(surf, color, body, width=int(s * 0.07), border_radius=int(s * 0.02))

        elif name == "check":
            stroke(
                [
                    (cx - s * 0.25, cy),
                    (cx - s * 0.06, cy + s * 0.18),
                    (cx + s * 0.26, cy - s * 0.20),
                ],
                max(2, int(s * 0.075)),
            )

        elif name == "trophy":
            w, h = s * 0.5, s * 0.5
            cup_rect = pygame.Rect(cx - w * 0.35, cy - h * 0.45, w * 0.7, h * 0.5)
            pygame.draw.arc(surf, color, cup_rect, 3.14, 6.28, int(s * 0.07))
            pygame.draw.line(
                surf,
                color,
                (cup_rect.left, cup_rect.centery),
                (cup_rect.right, cup_rect.centery),
                int(s * 0.07),
            )
            pygame.draw.line(surf, color, (cx, cy + h * 0.05), (cx, cy + h * 0.35), int(s * 0.07))
            pygame.draw.line(
                surf,
                color,
                (cx - w * 0.3, cy + h * 0.35),
                (cx + w * 0.3, cy + h * 0.35),
                int(s * 0.07),
            )
            pygame.draw.arc(
                surf,
                color,
                pygame.Rect(cx - w * 0.5, cy - h * 0.45, w * 0.3, h * 0.3),
                1.5,
                4.5,
                int(s * 0.06),
            )
            pygame.draw.arc(
                surf,
                color,
                pygame.Rect(cx + w * 0.2, cy - h * 0.45, w * 0.3, h * 0.3),
                -1.5,
                1.5,
                int(s * 0.06),
            )

        elif name == "grid_logo":
            rect = pygame.Rect(cx - s * 0.36, cy - s * 0.36, s * 0.72, s * 0.72)
            pygame.draw.rect(surf, color, rect, width=int(s * 0.06), border_radius=int(s * 0.08))
            step = rect.width / 3
            pygame.draw.line(
                surf,
                color,
                (rect.left + step, rect.top),
                (rect.left + step, rect.bottom),
                int(s * 0.05),
            )
            pygame.draw.line(
                surf,
                color,
                (rect.left + step * 2, rect.top),
                (rect.left + step * 2, rect.bottom),
                int(s * 0.05),
            )
            pygame.draw.line(
                surf,
                color,
                (rect.left, rect.top + step),
                (rect.right, rect.top + step),
                int(s * 0.05),
            )
            pygame.draw.line(
                surf,
                color,
                (rect.left, rect.top + step * 2),
                (rect.right, rect.top + step * 2),
                int(s * 0.05),
            )

        elif name == "star":
            pts = []
            radius = s * 0.36
            for i in range(10):
                r = radius if i % 2 == 0 else radius * 0.44
                angle = i * math.pi / 5 - math.pi / 2
                pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
            pygame.draw.polygon(surf, color, pts)

        elif name == "save":
            # Clear floppy-disk outline that remains recognizable at 16px.
            rect = pygame.Rect(cx - s * 0.32, cy - s * 0.32, s * 0.64, s * 0.64)
            pygame.draw.rect(surf, color, rect, width=max(1, int(s * 0.07)), border_radius=int(s * 0.06))
            pygame.draw.line(
                surf,
                color,
                (cx - s * 0.20, cy - s * 0.30),
                (cx + s * 0.20, cy - s * 0.30),
                max(1, int(s * 0.07)),
            )
            pygame.draw.rect(
                surf,
                color,
                pygame.Rect(cx - s * 0.18, cy + s * 0.06, s * 0.36, s * 0.18),
                width=max(1, int(s * 0.06)),
            )

        elif name in ("upload", "download"):
            # File transfer icon: tray plus an unambiguous arrow direction.
            tray = pygame.Rect(cx - s * 0.30, cy + s * 0.10, s * 0.60, s * 0.22)
            pygame.draw.line(
                surf, color, tray.topleft, tray.topright, max(1, int(s * 0.07))
            )
            pygame.draw.line(
                surf, color, tray.topright, tray.bottomright, max(1, int(s * 0.07))
            )
            pygame.draw.line(
                surf, color, tray.bottomleft, tray.bottomright, max(1, int(s * 0.07))
            )
            arrow_y = cy + s * 0.02 if name == "download" else cy - s * 0.08
            arrow_tip_y = cy + s * 0.08 if name == "download" else cy - s * 0.18
            pygame.draw.line(
                surf,
                color,
                (cx, arrow_tip_y),
                (cx, arrow_y),
                max(1, int(s * 0.08)),
            )
            direction = 1 if name == "download" else -1
            pygame.draw.line(
                surf,
                color,
                (cx, arrow_y),
                (cx - s * 0.14, arrow_y - direction * s * 0.14),
                max(1, int(s * 0.08)),
            )
            pygame.draw.line(
                surf,
                color,
                (cx, arrow_y),
                (cx + s * 0.14, arrow_y - direction * s * 0.14),
                max(1, int(s * 0.08)),
            )

        elif name == "palette":
            # Artist palette
            r = s * 0.32
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r), width=int(s * 0.07))
            # Thumb hole
            pygame.draw.circle(
                surf,
                color,
                (int(cx + r * 0.35), int(cy + r * 0.35)),
                int(s * 0.07),
                width=int(s * 0.04),
            )
            # 3 paint dots
            pygame.draw.circle(surf, color, (int(cx - r * 0.4), int(cy - r * 0.2)), int(s * 0.05))
            pygame.draw.circle(surf, color, (int(cx), int(cy - r * 0.5)), int(s * 0.05))
            pygame.draw.circle(surf, color, (int(cx + r * 0.4), int(cy - r * 0.2)), int(s * 0.05))

        elif name == "sound":
            # Speaker box
            pts = [
                (cx - s * 0.28, cy - s * 0.12),
                (cx - s * 0.12, cy - s * 0.12),
                (cx + s * 0.08, cy - s * 0.30),
                (cx + s * 0.08, cy + s * 0.30),
                (cx - s * 0.12, cy + s * 0.12),
                (cx - s * 0.28, cy + s * 0.12),
            ]
            pygame.draw.polygon(surf, color, pts)
            # Sound waves
            arc_r1 = pygame.Rect(cx - s * 0.06, cy - s * 0.16, s * 0.32, s * 0.32)
            pygame.draw.arc(surf, color, arc_r1, -1.0, 1.0, int(s * 0.06))
            arc_r2 = pygame.Rect(cx - s * 0.06, cy - s * 0.28, s * 0.48, s * 0.56)
            pygame.draw.arc(surf, color, arc_r2, -1.0, 1.0, int(s * 0.06))

        elif name == "sound_mute":
            # Speaker box
            pts = [
                (cx - s * 0.30, cy - s * 0.12),
                (cx - s * 0.14, cy - s * 0.12),
                (cx + s * 0.06, cy - s * 0.30),
                (cx + s * 0.06, cy + s * 0.30),
                (cx - s * 0.14, cy + s * 0.12),
                (cx - s * 0.30, cy + s * 0.12),
            ]
            pygame.draw.polygon(surf, color, pts)
            # X mark
            x_cx = cx + s * 0.24
            half = s * 0.12
            pygame.draw.line(
                surf, color, (x_cx - half, cy - half), (x_cx + half, cy + half), int(s * 0.06)
            )
            pygame.draw.line(
                surf, color, (x_cx + half, cy - half), (x_cx - half, cy + half), int(s * 0.06)
            )

        elif name == "help":
            # Question mark
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(s * 0.36), width=int(s * 0.06))
            # Arc for question mark
            top_arc = pygame.Rect(cx - s * 0.14, cy - s * 0.24, s * 0.28, s * 0.24)
            pygame.draw.arc(surf, color, top_arc, 0.0, 3.14, int(s * 0.06))
            pygame.draw.line(
                surf, color, (cx + s * 0.14, cy - s * 0.12), (cx, cy + s * 0.04), int(s * 0.06)
            )
            pygame.draw.line(surf, color, (cx, cy + s * 0.04), (cx, cy + s * 0.10), int(s * 0.06))
            pygame.draw.circle(surf, color, (int(cx), int(cy + s * 0.20)), int(s * 0.04))

        elif name in ("close", "cross"):
            half = s * 0.22
            pygame.draw.line(
                surf, color, (cx - half, cy - half), (cx + half, cy + half), int(s * 0.08)
            )
            pygame.draw.line(
                surf, color, (cx + half, cy - half), (cx - half, cy + half), int(s * 0.08)
            )

        elif name == "arrow_right":
            # Crisp modern chevron
            half = s * 0.20
            pts = [
                (cx - half * 0.6, cy - half),
                (cx + half * 0.6, cy),
                (cx - half * 0.6, cy + half),
            ]
            pygame.draw.lines(surf, color, False, pts, width=int(s * 0.09))

        elif name == "flame":
            flame_pts = [
                (cx, cy - s * 0.34),
                (cx + s * 0.08, cy - s * 0.10),
                (cx + s * 0.22, cy - s * 0.01),
                (cx + s * 0.20, cy + s * 0.20),
                (cx, cy + s * 0.32),
                (cx - s * 0.20, cy + s * 0.20),
                (cx - s * 0.22, cy - s * 0.01),
                (cx - s * 0.08, cy - s * 0.10),
                (cx, cy - s * 0.34),
            ]
            stroke(flame_pts)
            stroke([(cx, cy + s * 0.20), (cx - s * 0.07, cy + s * 0.08), (cx, cy - s * 0.05)])

        elif name == "crown":
            pts = [
                (cx - s * 0.30, cy + s * 0.20),
                (cx - s * 0.34, cy - s * 0.16),
                (cx - s * 0.12, cy + s * 0.02),
                (cx, cy - s * 0.24),
                (cx + s * 0.12, cy + s * 0.02),
                (cx + s * 0.34, cy - s * 0.16),
                (cx + s * 0.30, cy + s * 0.20),
                (cx - s * 0.30, cy + s * 0.20),
            ]
            stroke(pts)
            stroke([(cx - s * 0.30, cy + s * 0.20), (cx + s * 0.30, cy + s * 0.20)])

        elif name == "calendar":
            # Calendar
            cal_w, cal_h = s * 0.60, s * 0.54
            top = cy - cal_h / 2 + s * 0.04
            pygame.draw.rect(
                surf,
                color,
                pygame.Rect(cx - cal_w / 2, top, cal_w, cal_h),
                width=int(s * 0.06),
                border_radius=int(s * 0.06),
            )
            # Header line
            pygame.draw.line(
                surf,
                color,
                (cx - cal_w / 2, top + s * 0.16),
                (cx + cal_w / 2, top + s * 0.16),
                int(s * 0.05),
            )
            # Binder rings
            pygame.draw.line(
                surf,
                color,
                (cx - s * 0.16, top - s * 0.08),
                (cx - s * 0.16, top + s * 0.04),
                int(s * 0.06),
            )
            pygame.draw.line(
                surf,
                color,
                (cx + s * 0.16, top - s * 0.08),
                (cx + s * 0.16, top + s * 0.04),
                int(s * 0.06),
            )
            # Dots for dates
            for r_i in (0.26, 0.38):
                for c_i in (-0.16, 0.0, 0.16):
                    pygame.draw.circle(
                        surf, color, (int(cx + s * c_i), int(top + s * r_i)), int(s * 0.035)
                    )

        elif name == "slider":
            stroke([(cx - s * 0.30, cy), (cx + s * 0.30, cy)])
            pygame.draw.circle(surf, color, (int(cx + s * 0.05), int(cy)), int(s * 0.12))

        elif name == "shield":
            pts = [
                (cx - s * 0.28, cy - s * 0.28),
                (cx + s * 0.28, cy - s * 0.28),
                (cx + s * 0.28, cy + s * 0.04),
                (cx, cy + s * 0.36),
                (cx - s * 0.28, cy + s * 0.04),
            ]
            pygame.draw.polygon(surf, color, pts, width=int(s * 0.06))
            chk = [
                (cx - s * 0.14, cy),
                (cx - s * 0.02, cy + s * 0.12),
                (cx + s * 0.14, cy - s * 0.08),
            ]
            pygame.draw.lines(surf, color, False, chk, width=int(s * 0.06))

        elif name == "stats":
            # Bar chart
            w = s * 0.12
            pygame.draw.rect(
                surf,
                color,
                pygame.Rect(cx - s * 0.26, cy + s * 0.02, w, s * 0.26),
                border_radius=int(s * 0.02),
            )
            pygame.draw.rect(
                surf,
                color,
                pygame.Rect(cx - w / 2, cy - s * 0.24, w, s * 0.52),
                border_radius=int(s * 0.02),
            )
            pygame.draw.rect(
                surf,
                color,
                pygame.Rect(cx + s * 0.14, cy - s * 0.10, w, s * 0.38),
                border_radius=int(s * 0.02),
            )

        elif name == "globe":
            r = s * 0.32
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r), width=int(s * 0.06))
            pygame.draw.line(surf, color, (cx - r, cy), (cx + r, cy), int(s * 0.05))
            pygame.draw.ellipse(
                surf, color, pygame.Rect(cx - r * 0.5, cy - r, r, r * 2), width=int(s * 0.05)
            )

        elif name == "plus":
            half = s * 0.22
            pygame.draw.line(surf, color, (cx - half, cy), (cx + half, cy), int(s * 0.07))
            pygame.draw.line(surf, color, (cx, cy - half), (cx, cy + half), int(s * 0.07))

        elif name == "minus":
            half = s * 0.22
            pygame.draw.line(surf, color, (cx - half, cy), (cx + half, cy), int(s * 0.07))

        smooth_result = pygame.transform.smoothscale(surf, (size, size))
        cls._cache[key] = smooth_result
        return smooth_result


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
