import pygame
import math
from constants.colors import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_BORDER_OUTER, COLOR_BORDER_INNER,
    COLOR_LIQUID_WATER, COLOR_LIQUID_BUBBLE, COLOR_GOLD, COLOR_TEXT_MUTED,
    COLOR_TEXT_WHITE
)

pygame.font.init()
# Modern sans-serif tick font
_TICK_FONTS = {}
def _get_tick_font(size=11, bold=True):
    key = (size, bold)
    if key not in _TICK_FONTS:
        for name in ("Segoe UI", "Arial", "FreeSans", ""):
            try:
                f = pygame.font.SysFont(name, size, bold=bold) if name else pygame.font.Font(None, size + 4)
                _TICK_FONTS[key] = f
                break
            except Exception:
                continue
    return _TICK_FONTS[key]


def draw_modern_panel(surface, rect, title=None, border_radius=12, alpha=240):
    """Draw a modern rounded panel with a glowing cyan border and subtle 3D depth."""
    # ── Outer drop shadow (3D separation) ─────────────────────────────────
    shadow_offset = 6
    shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 150), shadow_surf.get_rect(), border_radius=border_radius)
    surface.blit(shadow_surf, (rect.x + shadow_offset, rect.y + shadow_offset))

    # ── Panel background — brighter slate ─────────────────────────────────
    bg_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    r, g, b = COLOR_PANEL_BG
    # Slightly brighter base (add ~15 to each channel)
    rb, gb, bb = min(r + 15, 255), min(g + 15, 255), min(b + 15, 255)
    pygame.draw.rect(bg_surf, (rb, gb, bb, alpha), bg_surf.get_rect(), border_radius=border_radius)
    surface.blit(bg_surf, rect.topleft)

    # ── Inner top-edge highlight (3D raised effect) ────────────────────────
    hl_surf = pygame.Surface((rect.width - 4, 3), pygame.SRCALPHA)
    pygame.draw.rect(hl_surf, (255, 255, 255, 40), hl_surf.get_rect(), border_radius=2)
    surface.blit(hl_surf, (rect.x + 2, rect.y + 2))

    # ── Inner bottom shadow (3D depth) ────────────────────────────────────
    sh_surf = pygame.Surface((rect.width - 4, 3), pygame.SRCALPHA)
    pygame.draw.rect(sh_surf, (0, 0, 0, 60), sh_surf.get_rect(), border_radius=2)
    surface.blit(sh_surf, (rect.x + 2, rect.y + rect.height - 5))

    # ── Outer subtle glow border ──────────────────────────────────────────
    glow_surf = pygame.Surface((rect.width + 6, rect.height + 6), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (*COLOR_BORDER_OUTER, 60),
                     glow_surf.get_rect(), border_radius=border_radius + 3, width=3)
    surface.blit(glow_surf, (rect.x - 3, rect.y - 3))

    # ── Main border — glowing cyan (2px for visibility) ────────────────────
    pygame.draw.rect(surface, COLOR_BORDER_INNER, rect, width=2, border_radius=border_radius)

    if title:
        font = _get_tick_font(13, bold=True)  # bold title
        txt_surf = font.render(f"  {title}  ", True, COLOR_TEXT_WHITE)
        pill_w = txt_surf.get_width() + 14
        pill_h = 22
        pill_x = rect.centerx - pill_w // 2
        pill_y = rect.y - pill_h // 2

        # Pill background — same panel color but fully opaque
        pill_bg = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pygame.draw.rect(pill_bg, (rb, gb, bb, 255), pill_bg.get_rect(), border_radius=11)
        surface.blit(pill_bg, (pill_x, pill_y))

        # Pill border
        pygame.draw.rect(surface, COLOR_BORDER_INNER,
                         pygame.Rect(pill_x, pill_y, pill_w, pill_h), width=2, border_radius=11)

        # Title text — bright white, bold
        title_surf = font.render(f"  {title}  ", True, COLOR_TEXT_WHITE)
        surface.blit(title_surf, title_surf.get_rect(center=(rect.centerx, pill_y + pill_h // 2)))


# Alias used by older code imports
def draw_pixel_panel(surface, rect, title=None, is_raised=True):
    draw_modern_panel(surface, rect, title=title)


def render_shadow_text(surface, text, font, color, pos, shadow_color=(0, 0, 0), offset=(1, 1)):
    """Renders modern text with a light drop shadow."""
    shadow_surf = font.render(text, True, shadow_color)
    surface.blit(shadow_surf, (pos[0] + offset[0], pos[1] + offset[1]))
    fg_surf = font.render(text, True, color)
    surface.blit(fg_surf, pos)


def make_bottle_surface(capacity, level, is_selected=False, wave_offset=0.0):
    """Generates a modern vector glass beaker surface."""
    w = 100        # inner body width
    margin_l = 30  # left margin for tick numbers
    total_w = margin_l + w + 35  # +35 for handle
    h_body = 110 + int((capacity / 10.0) * 100)  # body height
    total_h = h_body + 40  # top rim + bottom

    surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

    # Beaker geometry
    bx = margin_l        # body left x
    by = 15              # body top y (below rim)
    bw = w               # body width
    bb = by + h_body     # body bottom y

    # ── 1. Draw liquid ──────────────────────────────────────────────────
    if level > 0:
        ratio = min(level / float(capacity), 1.0)
        liq_h = int((h_body - 4) * ratio)
        y_top = bb - liq_h

        # Wave surface polygon
        wave_pts = []
        for x in range(bx + 3, bx + bw - 2):
            disp = int(2.5 * math.sin(wave_offset + x * 0.18))
            wy = max(by + 3, y_top + disp)
            wave_pts.append((x, wy))
        wave_pts.append((bx + bw - 2, bb - 2))
        wave_pts.append((bx + 3, bb - 2))

        # Main liquid body
        liq_color = (14, 165, 233, 160)
        pygame.draw.polygon(surf, liq_color, wave_pts)

        # Bright highlight strip at liquid top
        for x in range(bx + 4, bx + bw - 4):
            disp = int(2.5 * math.sin(wave_offset + x * 0.18))
            wy = max(by + 3, y_top + disp)
            pygame.draw.line(surf, (147, 219, 255, 100), (x, wy), (x, wy + 2))

        # Bubbles
        num_b = max(2, int(capacity * 1.2))
        for b_i in range(num_b):
            bub_x = bx + 8 + ((b_i * 31) % (bw - 16))
            base_y = bb - 4 - ((b_i * 19) % max(1, liq_h))
            bub_y = base_y - int((pygame.time.get_ticks() * 0.035 + b_i * 7) % 30)
            if y_top + 3 < bub_y < bb - 4:
                pygame.draw.circle(surf, (200, 235, 255, 130), (bub_x, bub_y), 2)

    # ── 2. Beaker glass body ──────────────────────────────────────────
    # Dark shadow behind the glass walls
    wall_dark = (15, 25, 50, 200)

    # Left wall
    pygame.draw.rect(surf, wall_dark, (bx, by, 6, h_body))
    # Right wall
    pygame.draw.rect(surf, wall_dark, (bx + bw - 6, by, 6, h_body))
    # Bottom wall
    pygame.draw.rect(surf, wall_dark, (bx, bb - 6, bw, 6))

    # Glass outline (thin bright line)
    glass_color = (180, 215, 245, 220)
    pygame.draw.rect(surf, glass_color, (bx, by, bw, h_body), width=2)

    # Glass rim (top opening lip)
    pygame.draw.rect(surf, glass_color, (bx - 4, by - 8, bw + 8, 8), border_radius=2)

    # Inner left highlight (specular reflection)
    for i in range(3):
        alpha = 90 - i * 25
        pygame.draw.line(surf, (255, 255, 255, alpha),
                         (bx + 4 + i, by + 10),
                         (bx + 4 + i, bb - 15))

    # ── 3. Measurement tick marks ────────────────────────────────────
    tick_font = _get_tick_font(10)
    for i in range(1, capacity + 1):
        show_num = (capacity <= 8) or (i % 2 == 0)
        tick_ratio = i / float(capacity)
        tick_y = int(bb - (h_body - 4) * tick_ratio)

        # Tick line inside beaker
        tick_len = 8 if show_num else 5
        pygame.draw.line(surf, (180, 215, 245, 180),
                         (bx + 6, tick_y),
                         (bx + 6 + tick_len, tick_y), 1)

        if show_num:
            num_surf = tick_font.render(str(i), True, (180, 215, 245, 200))
            num_rect = num_surf.get_rect(midright=(bx - 3, tick_y))
            surf.blit(num_surf, num_rect)

    # ── 4. Handle ─────────────────────────────────────────────────────
    hx = bx + bw  # handle start x
    h_top = by + 15
    h_bot = bb - 20
    h_out = hx + 22   # outer right of handle

    handle_pts = [
        (hx, h_top),
        (hx + 8, h_top - 4),
        (h_out, h_top + 8),
        (h_out, h_bot - 8),
        (hx + 8, h_bot + 4),
        (hx, h_bot),
    ]
    # Shadow
    shadow_pts = [(p[0] + 2, p[1] + 2) for p in handle_pts]
    pygame.draw.lines(surf, (0, 0, 0, 80), False, shadow_pts, 7)
    # Handle body
    pygame.draw.lines(surf, wall_dark, False, handle_pts, 8)
    # Handle highlight
    pygame.draw.lines(surf, glass_color, False, handle_pts, 2)

    # ── 5. Selection highlight ────────────────────────────────────────
    if is_selected:
        pulse = 160 + int(70 * math.sin(pygame.time.get_ticks() * 0.008))
        sel_color = (56, 189, 248, pulse)
        outer = pygame.Rect(bx - 6, by - 12, bw + 12, h_body + 12)
        glow_s = pygame.Surface((outer.width, outer.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_s, sel_color, glow_s.get_rect(), width=2, border_radius=4)
        surf.blit(glow_s, outer.topleft)

    return surf


def blit_rotate_pivot(surface, image, pos, originPos, angle):
    """Blits an image rotated around a local pivot coordinate onto screen at pos."""
    rotated_image = pygame.transform.rotate(image, angle)

    w, h = image.get_size()
    cx, cy = w / 2, h / 2

    dx = originPos[0] - cx
    dy = originPos[1] - cy

    rad = math.radians(-angle)
    rx = dx * math.cos(rad) - dy * math.sin(rad)
    ry = dx * math.sin(rad) + dy * math.cos(rad)

    new_cx = pos[0] - rx
    new_cy = pos[1] - ry

    rect = rotated_image.get_rect()
    rect.center = (new_cx, new_cy)
    surface.blit(rotated_image, rect)
