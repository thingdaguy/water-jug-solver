import pygame
import math
from constants.colors import (
    COLOR_PANEL_BG, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_GOLD,
    COLOR_BORDER_OUTER, COLOR_BORDER_INNER, COLOR_DARK_BLUE, COLOR_RED_ERROR,
    COLOR_TEXT_GREEN, COLOR_TEXT_AMBER, clamp_color, COLOR_BG_DARK
)
from components.renderer import draw_modern_panel, draw_pixel_panel

# ── Module-level font helper ──────────────────────────────────────────────────
pygame.font.init()
_FONT_CACHE = {}

def _ui_font(size=14, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        for name in ("Segoe UI", "Arial", "FreeSans", ""):
            try:
                if name:
                    _FONT_CACHE[key] = pygame.font.SysFont(name, size, bold=bold)
                else:
                    _FONT_CACHE[key] = pygame.font.Font(None, size + 6)
                break
            except Exception:
                continue
    return _FONT_CACHE[key]


def draw_rounded_button(surface, rect, color, hover=False, radius=8):
    """Draw a modern rounded button with optional highlight."""
    # Shadow
    sh = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 60), sh.get_rect(), border_radius=radius + 2)
    surface.blit(sh, (rect.x - 2, rect.y + 2))

    # Main body
    body_color = tuple(clamp_color(c + 30) for c in color) if hover else color
    pygame.draw.rect(surface, body_color, rect, border_radius=radius)

    # Highlight (top strip)
    hl = pygame.Surface((rect.width - 4, rect.height // 2), pygame.SRCALPHA)
    pygame.draw.rect(hl, (255, 255, 255, 30), hl.get_rect(), border_radius=radius)
    surface.blit(hl, (rect.x + 2, rect.y + 1))


# ─────────────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, callback=None,
                 color=COLOR_PANEL_BG, text_color=COLOR_TEXT_WHITE,
                 is_visualize=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.text_color = text_color
        self.is_visualize = is_visualize
        self.is_disabled = False
        self.is_hovered = False

    def draw(self, surface, font):
        if self.is_disabled:
            draw_color = (40, 48, 70)
            txt_color = COLOR_TEXT_MUTED
        else:
            if self.is_visualize and not self.is_hovered:
                # Pulsing blue for the main action button
                t = pygame.time.get_ticks() * 0.005
                pulse = int(20 * math.sin(t))
                draw_color = (
                    clamp_color(46 + pulse),
                    clamp_color(113 + pulse),
                    clamp_color(204 + pulse)
                )
            else:
                draw_color = self.color
            txt_color = self.text_color

        draw_rounded_button(surface, self.rect, draw_color, hover=self.is_hovered)

        # Glowing border for main visualize button
        if self.is_visualize:
            pygame.draw.rect(surface, COLOR_BORDER_INNER, self.rect, width=1, border_radius=8)

        # Border for non-visualize buttons (subtle)
        else:
            border_c = COLOR_BORDER_OUTER if not self.is_disabled else (40, 48, 70)
            pygame.draw.rect(surface, border_c, self.rect, width=1, border_radius=8)

        # ── Icon + text ──────────────────────────────────────────────
        lbl_font = _ui_font(13, bold=True) if self.is_visualize else font

        if "ĐẶT LẠI TẤT CẢ" in self.text:
            txt_surf = lbl_font.render(self.text, True, txt_color)
            total_w = txt_surf.get_width() + 20
            sx = self.rect.centerx - total_w // 2
            cy = self.rect.centery
            # Refresh icon
            pygame.draw.circle(surface, txt_color, (sx + 7, cy), 6, 2)
            pygame.draw.polygon(surface, txt_color, [(sx + 7, cy - 6), (sx + 13, cy - 6), (sx + 13, cy)])
            surface.blit(txt_surf, (sx + 18, cy - txt_surf.get_height() // 2))

        elif "VISUALIZE SEARCH" in self.text:
            txt_surf = lbl_font.render(self.text, True, txt_color)
            total_w = txt_surf.get_width() + 18
            sx = self.rect.centerx - total_w // 2
            cy = self.rect.centery
            # Play triangle
            pygame.draw.polygon(surface, txt_color, [(sx, cy - 7), (sx, cy + 7), (sx + 11, cy)])
            surface.blit(txt_surf, (sx + 15, cy - txt_surf.get_height() // 2))

        elif "XEM ĐỒ THỊ TÌM KIẾM" in self.text:
            txt_surf = lbl_font.render(self.text, True, txt_color)
            total_w = txt_surf.get_width() + 22
            sx = self.rect.centerx - total_w // 2
            cy = self.rect.centery
            gx, gy = sx + 8, cy
            pygame.draw.line(surface, txt_color, (gx - 6, gy + 5), (gx, gy - 6), 2)
            pygame.draw.line(surface, txt_color, (gx + 6, gy + 5), (gx, gy - 6), 2)
            pygame.draw.line(surface, txt_color, (gx - 6, gy + 5), (gx + 6, gy + 5), 2)
            pygame.draw.circle(surface, txt_color, (gx - 6, gy + 5), 3)
            pygame.draw.circle(surface, txt_color, (gx + 6, gy + 5), 3)
            pygame.draw.circle(surface, txt_color, (gx, gy - 6), 3)
            surface.blit(txt_surf, (sx + 20, cy - txt_surf.get_height() // 2))

        else:
            txt_surf = font.render(self.text, True, txt_color)
            surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if self.is_disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
class Incrementer:
    """Rounded dark container with icon, label, minus/plus buttons and value."""
    _ICON_COLORS = {
        "A": (52, 152, 219),
        "B": (39, 174, 96),
        "C": (155, 89, 182),
    }

    def __init__(self, x, y, w, label, min_val, max_val, default_val, callback=None):
        self.rect = pygame.Rect(x, y, w, 72)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.callback = callback

        btn_size = 28
        # Minus button — left side
        self.btn_minus = Button(x + 44, y + 26, btn_size, btn_size, "−",
                                callback=self.decrement, color=(30, 40, 65))
        # Plus button — right side
        self.btn_plus = Button(x + w - 44 - btn_size, y + 26, btn_size, btn_size, "+",
                               callback=self.increment, color=(30, 40, 65))

    def draw(self, surface, font_lbl, font_val):
        # Container
        draw_modern_panel(surface, self.rect, border_radius=10, alpha=200)

        # Label text (top)
        lbl_font = _ui_font(12)
        lbl_surf = lbl_font.render(self.label, True, COLOR_TEXT_MUTED)
        surface.blit(lbl_surf, (self.rect.x + 46, self.rect.y + 8))

        # Buttons
        self.btn_minus.draw(surface, font_lbl)
        self.btn_plus.draw(surface, font_lbl)

        # Value (center between buttons)
        val_font = _ui_font(18, bold=True)
        val_surf = val_font.render(str(self.value), True, COLOR_TEXT_GOLD)
        val_cx = (self.btn_minus.rect.right + self.btn_plus.rect.left) // 2
        val_rect = val_surf.get_rect(center=(val_cx, self.rect.y + 40))
        surface.blit(val_surf, val_rect)

        # "LÍT" unit
        lit_font = _ui_font(11)
        lit_surf = lit_font.render("LÍT", True, COLOR_TEXT_MUTED)
        surface.blit(lit_surf, (self.rect.right - 40, self.rect.y + 34))

        # Decorative icon on the left
        ix = self.rect.x + 10
        iy = self.rect.y + 14
        if "đích" in self.label:
            # Bullseye target icon
            cx, cy = ix + 12, iy + 16
            pygame.draw.circle(surface, (234, 88, 12), (cx, cy), 11, 2)
            pygame.draw.circle(surface, COLOR_TEXT_WHITE, (cx, cy), 7, 2)
            pygame.draw.circle(surface, COLOR_RED_ERROR, (cx, cy), 3)
        else:
            # Color pill matching the jug
            for key, col in self.ICON_COLORS.items() if hasattr(self, 'ICON_COLORS') else Incrementer._ICON_COLORS.items():
                if f"bình {key}" in self.label.lower() or self.label.endswith(key):
                    liq_color = col
                    break
            else:
                liq_color = Incrementer._ICON_COLORS["A"]

            # Mini beaker icon
            pygame.draw.rect(surface, liq_color, (ix + 5, iy + 14, 14, 14), border_radius=2)
            pygame.draw.rect(surface, (180, 210, 240), (ix + 3, iy + 12, 18, 18), width=2, border_radius=3)
            pygame.draw.rect(surface, (180, 210, 240), (ix + 7, iy + 6, 10, 6), width=2)

    def increment(self):
        if self.value < self.max_val:
            self.value += 1
            if self.callback:
                self.callback(self.value)

    def decrement(self):
        if self.value > self.min_val:
            self.value -= 1
            if self.callback:
                self.callback(self.value)

    def handle_event(self, event):
        r1 = self.btn_minus.handle_event(event)
        r2 = self.btn_plus.handle_event(event)
        return r1 or r2


# ─────────────────────────────────────────────────────────────────────────────
class RadioGroup:
    def __init__(self, x, y, w, options, default_val, callback=None):
        self.rect = pygame.Rect(x, y, w, len(options) * 34)
        self.options = options
        self.selected_value = default_val
        self.callback = callback
        self.hovered_idx = -1

    def draw(self, surface, font):
        lbl_font = _ui_font(13)
        for idx, (label, val) in enumerate(self.options):
            opt_y = self.rect.y + idx * 34
            cx = self.rect.x + 18
            cy = opt_y + 14
            r = 8

            is_sel = (self.selected_value == val)
            is_hov = (idx == self.hovered_idx)

            if is_sel:
                # Green glowing selected ring
                pygame.draw.circle(surface, (34, 197, 94), (cx, cy), r, 2)
                pygame.draw.circle(surface, (34, 197, 94), (cx, cy), 4)
            elif is_hov:
                pygame.draw.circle(surface, COLOR_BORDER_INNER, (cx, cy), r, 2)
            else:
                pygame.draw.circle(surface, COLOR_BORDER_OUTER, (cx, cy), r, 2)

            text_color = COLOR_TEXT_WHITE if (is_sel or is_hov) else COLOR_TEXT_MUTED
            txt_surf = lbl_font.render(label, True, text_color)
            surface.blit(txt_surf, (self.rect.x + 36, opt_y + 6))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered_idx = -1
            for idx in range(len(self.options)):
                r = pygame.Rect(self.rect.x, self.rect.y + idx * 34, self.rect.width, 30)
                if r.collidepoint(event.pos):
                    self.hovered_idx = idx
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, (label, val) in enumerate(self.options):
                r = pygame.Rect(self.rect.x, self.rect.y + idx * 34, self.rect.width, 30)
                if r.collidepoint(event.pos):
                    self.selected_value = val
                    if self.callback:
                        self.callback(val)
                    return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
class ComboBox:
    def __init__(self, x, y, w, h, options, default_text, callback=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.default_text = default_text
        self.selected_index = -1
        self.callback = callback
        self.is_open = False
        self.hovered_idx = -1
        self.is_hovered = False

    @property
    def selected_value(self):
        if self.selected_index == -1:
            return None
        return self.options[self.selected_index][1]

    def draw(self, surface, font):
        lbl_font = _ui_font(13)

        # Header box
        draw_modern_panel(surface, self.rect, border_radius=8, alpha=220)

        text = self.default_text if self.selected_index == -1 else self.options[self.selected_index][0]
        text_color = COLOR_TEXT_MUTED if self.selected_index == -1 else COLOR_TEXT_WHITE

        txt_surf = lbl_font.render(text, True, text_color)
        surface.blit(txt_surf, txt_surf.get_rect(midleft=(self.rect.x + 12, self.rect.centery)))

        # Dropdown arrow
        ax = self.rect.right - 16
        ay = self.rect.centery
        if self.is_open:
            pts = [(ax - 5, ay + 3), (ax + 5, ay + 3), (ax, ay - 3)]
        else:
            pts = [(ax - 5, ay - 3), (ax + 5, ay - 3), (ax, ay + 3)]
        pygame.draw.polygon(surface, COLOR_BORDER_INNER, pts)

        # Dropdown list
        if self.is_open:
            opt_h = 34
            total_h = len(self.options) * opt_h
            drop_rect = pygame.Rect(self.rect.x, self.rect.bottom + 3, self.rect.width, total_h)
            draw_modern_panel(surface, drop_rect, border_radius=8, alpha=240)

            lbl_font2 = _ui_font(13)
            for idx, (label, _) in enumerate(self.options):
                row_rect = pygame.Rect(drop_rect.x + 4, drop_rect.y + idx * opt_h + 4,
                                       drop_rect.width - 8, opt_h - 4)
                if idx == self.hovered_idx:
                    pygame.draw.rect(surface, (30, 58, 138), row_rect, border_radius=6)
                    opt_color = COLOR_TEXT_WHITE
                else:
                    opt_color = COLOR_TEXT_MUTED
                opt_surf = lbl_font2.render(label, True, opt_color)
                surface.blit(opt_surf, opt_surf.get_rect(midleft=(row_rect.x + 10, row_rect.centery)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_open:
                drop_rect = pygame.Rect(self.rect.x, self.rect.bottom + 3,
                                        self.rect.width, len(self.options) * 34)
                if drop_rect.collidepoint(event.pos):
                    self.hovered_idx = (event.pos[1] - drop_rect.y) // 34
                else:
                    self.hovered_idx = -1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            if self.is_open:
                drop_rect = pygame.Rect(self.rect.x, self.rect.bottom + 3,
                                        self.rect.width, len(self.options) * 34)
                if drop_rect.collidepoint(event.pos):
                    idx = (event.pos[1] - drop_rect.y) // 34
                    if 0 <= idx < len(self.options):
                        self.selected_index = idx
                        self.is_open = False
                        if self.callback:
                            self.callback(self.options[idx][1])
                        return True
                else:
                    self.is_open = False
        return False


# ─────────────────────────────────────────────────────────────────────────────
class ScrollLogBox:
    LINE_H = 22   # px per log line

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.logs = []
        self.scroll_offset = 0   # 0 = show latest; positive = scrolled up
        self.is_dragging = False

    def add_log(self, text):
        self.logs.append(text)
        if len(self.logs) > 200:
            self.logs.pop(0)
        # Auto-scroll to bottom on new entry only if already at bottom
        if self.scroll_offset == 0:
            pass  # stay at bottom

    def clear(self):
        self.logs.clear()
        self.scroll_offset = 0

    # ── visible area maths ──────────────────────────────────────────────────
    def _inner_h(self):
        return self.rect.height - 32  # space below title pill

    def _max_lines(self):
        return max(1, self._inner_h() // self.LINE_H)

    def _total_lines(self):
        return len(self.logs)

    def _clamped_offset(self):
        max_off = max(0, self._total_lines() - self._max_lines())
        return max(0, min(self.scroll_offset, max_off))

    # ── scroll wheel handler ─────────────────────────────────────────────────
    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()
        inner_top = self.rect.y + 24
        sb_x = self.rect.right - 10
        sb_rect = pygame.Rect(sb_x - 5, inner_top, 16, self._inner_h()) # wider hit area

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if sb_rect.collidepoint(mx, my):
                self.is_dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            # calculate scroll offset based on mouse Y
            total = self._total_lines()
            max_vis = self._max_lines()
            if total > max_vis:
                # ratio from top (0.0) to bottom (1.0)
                ratio = (my - inner_top) / float(self._inner_h())
                ratio = max(0.0, min(1.0, ratio))
                # offset 0 = bottom, max_off = top
                max_off = total - max_vis
                self.scroll_offset = int((1.0 - ratio) * max_off)
            return True

        if not self.rect.collidepoint(mx, my):
            return False
            
        if event.type == pygame.MOUSEWHEEL:
            # wheel y>0 = scroll up = show older logs
            self.scroll_offset = self._clamped_offset() + event.y * 3  # Increase scroll speed and fix direction
            self.scroll_offset = max(0, self.scroll_offset)
            return True
        return False

    def draw(self, surface, font):
        import re
        draw_modern_panel(surface, self.rect, title="TEXT STEPS LOG", border_radius=10)

        log_font = _ui_font(13, bold=True)   # slightly larger + bold
        inner_top = self.rect.y + 24
        inner_h   = self._inner_h()
        max_vis   = self._max_lines()

        # Clip drawing to log area
        clip_rect = pygame.Rect(self.rect.x + 4, inner_top, self.rect.width - 22, inner_h)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        offset   = self._clamped_offset()
        # offset==0 means show tail; offset==N means show from index (total-max-N) … 
        total    = len(self.logs)
        # first_idx: index of the first log line shown (0 = oldest)
        # We scroll from the BOTTOM: offset=0 => show last max_vis lines
        first_idx = max(0, total - max_vis - offset)
        last_idx  = min(total, first_idx + max_vis)
        visible   = self.logs[first_idx:last_idx]

        for row, log in enumerate(visible):
            clean = re.sub(r'^\d{2}:\d{2}:\d{2}(?:\s*>\s*|\s+)?', '', log)
            if "LỖI" in clean or "WARNING" in clean or "Lỗi" in clean:
                col = (255, 90, 90)          # brighter red
            elif "Tìm thấy" in clean or "hoàn tất" in clean or "thành công" in clean:
                col = (255, 215, 60)         # bright gold
            elif "---" in clean:
                col = (100, 200, 255)        # bright blue for section dividers
            else:
                col = (100, 230, 100)        # bright green
            txt_s = log_font.render(f"› {clean}", True, col)
            surface.blit(txt_s, (self.rect.x + 10, inner_top + row * self.LINE_H))

        surface.set_clip(old_clip)

        # ── Scrollbar ──────────────────────────────────────────────────────
        if total > max_vis:
            sb_x   = self.rect.right - 10
            sb_top = inner_top
            sb_h   = inner_h
            # Track
            pygame.draw.rect(surface, (25, 35, 60),
                             pygame.Rect(sb_x, sb_top, 6, sb_h), border_radius=3)
            # Thumb
            thumb_ratio  = max_vis / total
            thumb_h      = max(20, int(sb_h * thumb_ratio))
            # scroll position in [0, total-max_vis]; 0=bottom, max=top
            max_off      = total - max_vis
            off          = self._clamped_offset()
            # When offset=0 thumb is at BOTTOM; when offset=max_off thumb at TOP
            thumb_y_frac = 1.0 - (off / max_off) if max_off > 0 else 1.0
            thumb_y      = sb_top + int((sb_h - thumb_h) * thumb_y_frac)
            pygame.draw.rect(surface, COLOR_BORDER_INNER,
                             pygame.Rect(sb_x, thumb_y, 6, thumb_h), border_radius=3)


# ─────────────────────────────────────────────────────────────────────────────
class SpeedSlider:
    def __init__(self, x, y, w, label, min_val=1, max_val=10, default_val=5, callback=None):
        self.rect = pygame.Rect(x, y, w, 48)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.callback = callback
        self.is_dragging = False

        self.track_rect = pygame.Rect(x + 10, y + 30, w - 20, 6)
        self.handle_w = 16
        self.handle_h = 24

    def draw(self, surface, font):
        lbl_font = _ui_font(12)
        lbl_surf = lbl_font.render(f"{self.label}: {self.value}", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_surf, (self.rect.x + 10, self.rect.y + 8))

        # Track background
        pygame.draw.rect(surface, (20, 28, 48), self.track_rect, border_radius=3)

        # Track fill (progress)
        ratio = (self.value - self.min_val) / float(self.max_val - self.min_val)
        fill_w = int(self.track_rect.width * ratio)
        fill_rect = pygame.Rect(self.track_rect.x, self.track_rect.y, fill_w, self.track_rect.height)
        pygame.draw.rect(surface, COLOR_BORDER_INNER, fill_rect, border_radius=3)

        # Track border
        pygame.draw.rect(surface, COLOR_BORDER_OUTER, self.track_rect, width=1, border_radius=3)

        # Slider handle
        hx = self.track_rect.x + int(ratio * self.track_rect.width) - self.handle_w // 2
        hy = self.track_rect.centery - self.handle_h // 2
        h_rect = pygame.Rect(hx, hy, self.handle_w, self.handle_h)
        draw_rounded_button(surface, h_rect, (46, 113, 204), hover=self.is_dragging, radius=6)
        pygame.draw.rect(surface, COLOR_BORDER_INNER, h_rect, width=1, border_radius=6)

    def handle_event(self, event):
        ratio = (self.value - self.min_val) / float(self.max_val - self.min_val)
        hx = self.track_rect.x + int(ratio * self.track_rect.width) - self.handle_w // 2
        hy = self.track_rect.centery - self.handle_h // 2
        h_rect = pygame.Rect(hx, hy, self.handle_w, self.handle_h)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if h_rect.collidepoint(event.pos) or self.track_rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.is_dragging:
            self.is_dragging = False
            return True
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self._update(event.pos[0])
            return True
        return False

    def _update(self, mx):
        cx = max(self.track_rect.x, min(mx, self.track_rect.right))
        ratio = (cx - self.track_rect.x) / float(self.track_rect.width)
        v = self.min_val + int(ratio * (self.max_val - self.min_val))
        if v != self.value:
            self.value = v
            if self.callback:
                self.callback(self.value)

    def update_val_from_mouse(self, mx):
        self._update(mx)
