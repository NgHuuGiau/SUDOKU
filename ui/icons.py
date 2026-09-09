"""Smooth supersampled icons for Sudoku UI."""
import math
import pygame
import random


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