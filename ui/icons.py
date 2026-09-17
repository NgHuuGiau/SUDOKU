"""Smooth supersampled icons for Sudoku UI."""

import math
import random
from functools import lru_cache

import pygame

_MODERN_ICON_NAMES = {
    "undo",
    "redo",
    "pencil",
    "hint",
    "erase",
    "sparkles",
    "clock",
    "pause",
    "play",
    "restart",
    "home",
    "check",
    "trophy",
    "grid_logo",
    "star",
    "save",
    "upload",
    "download",
    "palette",
    "sound",
    "sound_mute",
    "help",
    "close",
    "cross",
    "arrow_right",
    "flame",
    "crown",
    "calendar",
    "slider",
    "shield",
    "stats",
    "globe",
    "plus",
    "minus",
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
                (
                    center_x + current_radius * math.cos(angle),
                    center_y + current_radius * math.sin(angle),
                )
            )
        pygame.draw.polygon(surf, color, vertices)

    if name in {"undo", "redo"}:
        radius = size * 0.25
        rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
        start, end = (0.45, 3.35) if name == "undo" else (-0.20, 2.70)
        pygame.draw.arc(surf, color, rect, start, end, width)
        direction = -1 if name == "undo" else 1
        tip_x = cx + direction * size * 0.28
        line(
            [
                (tip_x, cy - size * 0.11),
                (tip_x - direction * size * 0.13, cy),
                (tip_x, cy + size * 0.11),
            ]
        )
    elif name == "pencil":
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx - size * 0.24, cy + size * 0.18),
                (cx + size * 0.16, cy - size * 0.22),
                (cx + size * 0.27, cy - size * 0.11),
                (cx - size * 0.14, cy + size * 0.28),
            ],
        )
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx - size * 0.24, cy + size * 0.18),
                (cx - size * 0.14, cy + size * 0.28),
                (cx - size * 0.30, cy + size * 0.33),
            ],
        )
    elif name == "hint":
        pygame.draw.circle(surf, color, (int(cx), int(cy - size * 0.08)), int(size * 0.19))
        line([(cx - size * 0.13, cy + size * 0.14), (cx + size * 0.13, cy + size * 0.14)])
        line([(cx - size * 0.09, cy + size * 0.23), (cx + size * 0.09, cy + size * 0.23)])
    elif name == "erase":
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx - size * 0.25, cy + size * 0.10),
                (cx - size * 0.02, cy - size * 0.24),
                (cx + size * 0.26, cy - size * 0.02),
                (cx + size * 0.03, cy + size * 0.32),
            ],
        )
        line(
            [(cx - size * 0.08, cy + size * 0.21), (cx + size * 0.20, cy + size * 0.21)],
            max(1, width - 1),
        )
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
            pygame.draw.rect(
                surf,
                color,
                pygame.Rect(
                    int(cx + offset - bar_width / 2),
                    int(cy - bar_height / 2),
                    bar_width,
                    bar_height,
                ),
                border_radius=max(1, width // 2),
            )
    elif name == "play":
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx - size * 0.14, cy - size * 0.24),
                (cx + size * 0.25, cy),
                (cx - size * 0.14, cy + size * 0.24),
            ],
        )
    elif name == "restart":
        radius = size * 0.27
        pygame.draw.arc(
            surf,
            color,
            pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2),
            0.55,
            5.55,
            width,
        )
        line(
            [
                (cx + size * 0.22, cy - size * 0.19),
                (cx + size * 0.30, cy - size * 0.03),
                (cx + size * 0.12, cy - size * 0.02),
            ],
            max(1, width - 1),
        )
    elif name == "home":
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx, cy - size * 0.28),
                (cx + size * 0.30, cy - size * 0.02),
                (cx + size * 0.24, cy - size * 0.02),
                (cx + size * 0.24, cy + size * 0.27),
                (cx - size * 0.24, cy + size * 0.27),
                (cx - size * 0.24, cy - size * 0.02),
                (cx - size * 0.30, cy - size * 0.02),
            ],
        )
        pygame.draw.rect(
            surf,
            soft_color,
            pygame.Rect(
                int(cx - size * 0.06), int(cy + size * 0.06), int(size * 0.12), int(size * 0.21)
            ),
        )
    elif name == "check":
        line(
            [
                (cx - size * 0.24, cy),
                (cx - size * 0.06, cy + size * 0.18),
                (cx + size * 0.26, cy - size * 0.20),
            ],
            max(2, int(size * 0.10)),
        )
    elif name == "trophy":
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx - size * 0.18, cy - size * 0.20),
                (cx + size * 0.18, cy - size * 0.20),
                (cx + size * 0.13, cy + size * 0.08),
                (cx, cy + size * 0.18),
                (cx - size * 0.13, cy + size * 0.08),
            ],
        )
        line([(cx, cy + size * 0.18), (cx, cy + size * 0.29)], max(1, width - 1))
        line(
            [(cx - size * 0.18, cy + size * 0.31), (cx + size * 0.18, cy + size * 0.31)],
            max(1, width - 1),
        )
    elif name == "grid_logo":
        rect = pygame.Rect(
            int(cx - size * 0.34), int(cy - size * 0.34), int(size * 0.68), int(size * 0.68)
        )
        pygame.draw.rect(surf, color, rect, width=width, border_radius=max(2, int(size * 0.10)))
        step = rect.width / 3
        for multiplier in (1, 2):
            pygame.draw.line(
                surf,
                color,
                (rect.left + step * multiplier, rect.top + width),
                (rect.left + step * multiplier, rect.bottom - width),
                max(1, width - 1),
            )
            pygame.draw.line(
                surf,
                color,
                (rect.left + width, rect.top + step * multiplier),
                (rect.right - width, rect.top + step * multiplier),
                max(1, width - 1),
            )
    elif name == "star":
        star(cx, cy, size * 0.32, points=5)
    elif name == "save":
        rect = pygame.Rect(
            int(cx - size * 0.29), int(cy - size * 0.30), int(size * 0.58), int(size * 0.60)
        )
        pygame.draw.rect(surf, color, rect, width=width, border_radius=max(2, int(size * 0.08)))
        pygame.draw.rect(
            surf,
            color,
            pygame.Rect(
                int(cx - size * 0.16), int(cy - size * 0.25), int(size * 0.32), int(size * 0.13)
            ),
        )
        pygame.draw.rect(
            surf,
            color,
            pygame.Rect(
                int(cx - size * 0.17), int(cy + size * 0.07), int(size * 0.34), int(size * 0.15)
            ),
            width=max(1, width - 1),
        )
    elif name in {"upload", "download"}:
        line(
            [(cx - size * 0.26, cy + size * 0.24), (cx + size * 0.26, cy + size * 0.24)],
            max(1, width - 1),
        )
        line(
            [(cx - size * 0.20, cy + size * 0.15), (cx - size * 0.20, cy + size * 0.24)],
            max(1, width - 1),
        )
        line(
            [(cx + size * 0.20, cy + size * 0.15), (cx + size * 0.20, cy + size * 0.24)],
            max(1, width - 1),
        )
        direction = -1 if name == "upload" else 1
        line(
            [(cx, cy + direction * size * 0.16), (cx, cy - direction * size * 0.18)],
            max(1, width - 1),
        )
        line(
            [
                (cx, cy - direction * size * 0.18),
                (cx - size * 0.12, cy - direction * size * 0.05),
                (cx, cy - direction * size * 0.18),
                (cx + size * 0.12, cy - direction * size * 0.05),
            ],
            max(1, width - 1),
        )
    elif name == "palette":
        pygame.draw.circle(surf, color, (int(cx), int(cy)), int(size * 0.29), width=width)
        pygame.draw.circle(
            surf, color, (int(cx - size * 0.10), int(cy - size * 0.10)), max(1, int(size * 0.045))
        )
        pygame.draw.circle(
            surf, color, (int(cx + size * 0.07), int(cy - size * 0.18)), max(1, int(size * 0.045))
        )
        pygame.draw.circle(
            surf, color, (int(cx + size * 0.18), int(cy - size * 0.02)), max(1, int(size * 0.045))
        )
    elif name in {"sound", "sound_mute"}:
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx - size * 0.28, cy - size * 0.11),
                (cx - size * 0.10, cy - size * 0.11),
                (cx + size * 0.08, cy - size * 0.27),
                (cx + size * 0.08, cy + size * 0.27),
                (cx - size * 0.10, cy + size * 0.11),
                (cx - size * 0.28, cy + size * 0.11),
            ],
        )
        if name == "sound":
            pygame.draw.arc(
                surf,
                color,
                pygame.Rect(
                    int(cx - size * 0.02), int(cy - size * 0.22), int(size * 0.34), int(size * 0.44)
                ),
                -1.0,
                1.0,
                max(1, width - 1),
            )
        else:
            line(
                [(cx + size * 0.15, cy - size * 0.13), (cx + size * 0.30, cy + size * 0.13)],
                max(1, width - 1),
            )
            line(
                [(cx + size * 0.30, cy - size * 0.13), (cx + size * 0.15, cy + size * 0.13)],
                max(1, width - 1),
            )
    elif name in {"help", "close", "cross"}:
        if name == "help":
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(size * 0.31), width=width)
            line(
                [
                    (cx - size * 0.09, cy - size * 0.10),
                    (cx, cy - size * 0.18),
                    (cx + size * 0.11, cy - size * 0.09),
                    (cx, cy + size * 0.05),
                    (cx, cy + size * 0.12),
                ],
                max(1, width - 1),
            )
            pygame.draw.circle(
                surf, color, (int(cx), int(cy + size * 0.22)), max(1, int(size * 0.04))
            )
        else:
            line(
                [(cx - size * 0.22, cy - size * 0.22), (cx + size * 0.22, cy + size * 0.22)],
                max(2, int(size * 0.10)),
            )
            line(
                [(cx + size * 0.22, cy - size * 0.22), (cx - size * 0.22, cy + size * 0.22)],
                max(2, int(size * 0.10)),
            )
    elif name == "arrow_right":
        line(
            [(cx - size * 0.20, cy), (cx + size * 0.18, cy), (cx, cy - size * 0.17)],
            max(1, width - 1),
        )
        line([(cx + size * 0.18, cy), (cx, cy + size * 0.17)], max(1, width - 1))
    elif name == "flame":
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx, cy - size * 0.34),
                (cx + size * 0.10, cy - size * 0.10),
                (cx + size * 0.23, cy),
                (cx + size * 0.18, cy + size * 0.22),
                (cx, cy + size * 0.32),
                (cx - size * 0.18, cy + size * 0.22),
                (cx - size * 0.23, cy),
                (cx - size * 0.10, cy - size * 0.10),
            ],
        )
        pygame.draw.polygon(
            surf,
            soft_color,
            [
                (cx, cy + size * 0.21),
                (cx - size * 0.07, cy + size * 0.05),
                (cx, cy - size * 0.04),
                (cx + size * 0.07, cy + size * 0.05),
            ],
        )
    elif name == "crown":
        pygame.draw.polygon(
            surf,
            color,
            [
                (cx - size * 0.30, cy + size * 0.18),
                (cx - size * 0.34, cy - size * 0.16),
                (cx - size * 0.12, cy),
                (cx, cy - size * 0.25),
                (cx + size * 0.12, cy),
                (cx + size * 0.34, cy - size * 0.16),
                (cx + size * 0.30, cy + size * 0.18),
            ],
        )
        pygame.draw.rect(
            surf,
            color,
            pygame.Rect(
                int(cx - size * 0.30), int(cy + size * 0.15), int(size * 0.60), int(size * 0.10)
            ),
            border_radius=max(1, width // 2),
        )
    elif name == "calendar":
        rect = pygame.Rect(
            int(cx - size * 0.29), int(cy - size * 0.24), int(size * 0.58), int(size * 0.52)
        )
        pygame.draw.rect(surf, color, rect, width=width, border_radius=max(2, int(size * 0.07)))
        pygame.draw.line(
            surf,
            color,
            (rect.left + width, rect.top + int(size * 0.14)),
            (rect.right - width, rect.top + int(size * 0.14)),
            width,
        )
        for offset_x in (-size * 0.14, size * 0.14):
            pygame.draw.circle(
                surf, color, (int(cx + offset_x), int(cy + size * 0.12)), max(1, int(size * 0.04))
            )
    elif name == "slider":
        pygame.draw.rect(
            surf,
            color,
            pygame.Rect(int(cx - size * 0.30), int(cy - width / 2), int(size * 0.60), width),
            border_radius=max(1, width // 2),
        )
        pygame.draw.circle(surf, color, (int(cx + size * 0.06), int(cy)), int(size * 0.13))
    elif name == "shield":
        line(
            [
                (cx - size * 0.25, cy - size * 0.26),
                (cx + size * 0.25, cy - size * 0.26),
                (cx + size * 0.25, cy + size * 0.04),
                (cx, cy + size * 0.32),
                (cx - size * 0.25, cy + size * 0.04),
                (cx - size * 0.25, cy - size * 0.26),
            ],
            max(1, width - 1),
        )
        line(
            [
                (cx - size * 0.12, cy),
                (cx - size * 0.02, cy + size * 0.10),
                (cx + size * 0.14, cy - size * 0.10),
            ],
            max(1, width - 1),
        )
    elif name == "stats":
        for offset_x, height in ((-size * 0.22, 0.24), (0, 0.38), (size * 0.22, 0.31)):
            pygame.draw.rect(
                surf,
                color,
                pygame.Rect(
                    int(cx + offset_x - size * 0.06),
                    int(cy + size * 0.22 - size * height),
                    int(size * 0.12),
                    int(size * height),
                ),
                border_radius=max(1, width // 2),
            )
    elif name == "globe":
        radius = size * 0.30
        pygame.draw.circle(surf, color, (int(cx), int(cy)), int(radius), width=width)
        pygame.draw.line(
            surf, color, (int(cx - radius), int(cy)), (int(cx + radius), int(cy)), max(1, width - 1)
        )
        pygame.draw.ellipse(
            surf,
            color,
            pygame.Rect(
                int(cx - radius * 0.45), int(cy - radius), int(radius * 0.90), int(radius * 2)
            ),
            width=max(1, width - 1),
        )
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

        _draw_modern_icon(name, surf, cx, cy, s, color)

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
            screen.blit(
                _particle_surface(self.color, alpha, radius),
                (int(self.x) - glow_radius, int(self.y) - glow_radius),
            )


@lru_cache(maxsize=256)
def _particle_surface(color: tuple[int, int, int], alpha: int, radius: int) -> pygame.Surface:
    glow_radius = radius * 3
    surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    center = (glow_radius, glow_radius)
    pygame.draw.circle(surface, (*color, alpha // 4), center, glow_radius)
    pygame.draw.circle(surface, (*color, alpha), center, radius)
    return surface
