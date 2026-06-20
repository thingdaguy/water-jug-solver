import pygame
import math
from constants.colors import (
    COLOR_PANEL_BG, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_GOLD,
    COLOR_BORDER_OUTER, COLOR_BORDER_INNER, COLOR_DARK_BLUE, COLOR_RED_ERROR,
    COLOR_TEXT_GREEN, COLOR_TEXT_AMBER, clamp_color
)
from components.renderer import draw_pixel_panel

class Button:
    def __init__(self, x, y, w, h, text, callback=None, color=COLOR_PANEL_BG, text_color=COLOR_TEXT_WHITE, is_visualize=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.text_color = text_color
        self.is_visualize = is_visualize
        self.is_disabled = False
        self.is_hovered = False

    def draw(self, surface, font):
        # Determine colors based on state
        draw_color = self.color
        if self.is_disabled:
            draw_color = (55, 60, 80)
            txt_color = COLOR_TEXT_MUTED
        else:
            if self.is_hovered:
                if self.is_visualize:
                    draw_color = (16, 210, 210)
                else:
                    draw_color = (
                        clamp_color(self.color[0] + 20),
                        clamp_color(self.color[1] + 20),
                        clamp_color(self.color[2] + 20)
                    )
            txt_color = self.text_color
            if self.is_visualize and not self.is_hovered:
                # Animate active pulse with clamped values
                pulse = int(25 * math.sin(pygame.time.get_ticks() * 0.006))
                r = clamp_color(COLOR_BORDER_INNER[0] + pulse)
                g = clamp_color(COLOR_BORDER_INNER[1] + pulse)
                b = clamp_color(COLOR_BORDER_INNER[2] // 2)
                draw_color = (r, g, b)

        # Draw panel box
        draw_pixel_panel(surface, self.rect, is_raised=not self.is_hovered)
        
        # Highlight top surface
        pygame.draw.rect(surface, draw_color, (self.rect.x + 4, self.rect.y + 4, self.rect.width - 8, self.rect.height - 8))

        # Render button text
        txt_surf = font.render(self.text, True, txt_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

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


class Incrementer:
    def __init__(self, x, y, w, label, min_val, max_val, default_val, callback=None):
        self.rect = pygame.Rect(x, y, w, 70)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.callback = callback
        
        # Draw controls internally
        btn_y = y + 25
        self.btn_minus = Button(x + 10, btn_y, 40, 30, "-", callback=self.decrement)
        self.btn_plus = Button(x + w - 50, btn_y, 40, 30, "+", callback=self.increment)

    def draw(self, surface, font_lbl, font_val):
        # Draw label
        txt_lbl = font_lbl.render(self.label, True, COLOR_TEXT_MUTED)
        surface.blit(txt_lbl, (self.rect.x + 10, self.rect.y))

        # Draw box backgrounds
        self.btn_minus.draw(surface, font_lbl)
        self.btn_plus.draw(surface, font_lbl)

        # Draw current value
        val_surf = font_val.render(str(self.value), True, COLOR_TEXT_GOLD)
        val_rect = val_surf.get_rect(center=(self.rect.x + self.rect.width // 2, self.rect.y + 40))
        surface.blit(val_surf, val_rect)

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


class RadioGroup:
    def __init__(self, x, y, w, options, default_val, callback=None):
        self.rect = pygame.Rect(x, y, w, len(options) * 35)
        self.options = options # lists of tuples (label, value)
        self.selected_value = default_val
        self.callback = callback
        self.hovered_idx = -1
        self.is_disabled = False

    def draw(self, surface, font):
        for idx, (label, val) in enumerate(self.options):
            opt_y = self.rect.y + idx * 35
            
            # Checkbox frame
            box_rect = pygame.Rect(self.rect.x + 10, opt_y + 3, 20, 20)
            draw_pixel_panel(surface, box_rect, is_raised=(self.selected_value != val))
            
            if self.selected_value == val:
                # Draw checkmark inside
                color = COLOR_TEXT_MUTED if self.is_disabled else COLOR_BORDER_INNER
                pygame.draw.rect(surface, color, (box_rect.x + 5, box_rect.y + 5, 10, 10))

            # Label text
            if self.is_disabled:
                text_color = (80, 85, 100) # disabled color
            else:
                text_color = COLOR_TEXT_WHITE if idx == self.hovered_idx or self.selected_value == val else COLOR_TEXT_MUTED
            
            txt_surf = font.render(label, True, text_color)
            surface.blit(txt_surf, (self.rect.x + 40, opt_y + 4))

    def handle_event(self, event):
        if self.is_disabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered_idx = -1
            for idx in range(len(self.options)):
                opt_rect = pygame.Rect(self.rect.x, self.rect.y + idx * 35, self.rect.width, 30)
                if opt_rect.collidepoint(event.pos):
                    self.hovered_idx = idx
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for idx, (label, val) in enumerate(self.options):
                    opt_rect = pygame.Rect(self.rect.x, self.rect.y + idx * 35, self.rect.width, 30)
                    if opt_rect.collidepoint(event.pos):
                        self.selected_value = val
                        if self.callback:
                            self.callback(val)
                        return True
        return False


class Dropdown:
    def __init__(self, x, y, w, h, options, default_val, callback=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.selected_value = default_val
        self.callback = callback
        self.is_expanded = False
        self.hovered_idx = -1

    def draw(self, surface, font):
        draw_pixel_panel(surface, self.rect, is_raised=not self.is_expanded)
        current_label = next((l for l, v in self.options if v == self.selected_value), "")
        txt_surf = font.render(current_label + "  v", True, COLOR_TEXT_WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)
        
        if self.is_expanded:
            list_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * 35)
            draw_pixel_panel(surface, list_rect, is_raised=True)
            pygame.draw.rect(surface, COLOR_PANEL_BG, (list_rect.x+2, list_rect.y+2, list_rect.width-4, list_rect.height-4))
            
            for idx, (label, val) in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + idx * 35, self.rect.width, 35)
                if idx == self.hovered_idx:
                    pygame.draw.rect(surface, (55, 60, 80), (opt_rect.x+2, opt_rect.y, opt_rect.width-4, opt_rect.height))
                color = COLOR_TEXT_GOLD if val == self.selected_value else COLOR_TEXT_WHITE
                opt_surf = font.render(label, True, color)
                surface.blit(opt_surf, (opt_rect.x + 10, opt_rect.y + 8))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.is_expanded:
                self.hovered_idx = -1
                for idx in range(len(self.options)):
                    opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + idx * 35, self.rect.width, 35)
                    if opt_rect.collidepoint(event.pos):
                        self.hovered_idx = idx
                        break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.is_expanded:
                    for idx, (label, val) in enumerate(self.options):
                        opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + idx * 35, self.rect.width, 35)
                        if opt_rect.collidepoint(event.pos):
                            self.selected_value = val
                            self.is_expanded = False
                            if self.callback:
                                self.callback(val)
                            return True
                    self.is_expanded = False
                    if self.rect.collidepoint(event.pos):
                        return True
                else:
                    if self.rect.collidepoint(event.pos):
                        self.is_expanded = True
                        return True
        return False


class ScrollLogBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.logs = []
        self.max_lines = 7
        self.scroll_offset = 0
        self.is_dragging = False
        self.track_rect = pygame.Rect(self.rect.right - 20, self.rect.y + 20, 10, self.rect.height - 40)

    def add_log(self, text):
        self.logs.append(text)
        if len(self.logs) > 500: # Clamp array length
            self.logs.pop(0)
        self.scroll_offset = max(0, len(self.logs) - self.max_lines)

    def clear(self):
        self.logs.clear()
        self.scroll_offset = 0

    def draw(self, surface, font):
        draw_pixel_panel(surface, self.rect, title="TEXT STEPS LOG", is_raised=False)
        
        start_y = self.rect.y + 15
        visible_logs = self.logs[self.scroll_offset : self.scroll_offset + self.max_lines]
        
        for idx, log in enumerate(visible_logs):
            txt_color = COLOR_TEXT_GREEN if "LỖI" not in log and "WARNING" not in log else COLOR_RED_ERROR
            if "Tìm thấy lời giải" in log or "hoàn tất" in log:
                txt_color = COLOR_TEXT_GOLD
            txt_surf = font.render(f"> {log}", True, txt_color)
            surface.blit(txt_surf, (self.rect.x + 15, start_y + idx * 22))
            
        # Draw scrollbar
        if len(self.logs) > self.max_lines:
            pygame.draw.rect(surface, (30, 35, 45), self.track_rect) # Track bg
            pygame.draw.rect(surface, COLOR_BORDER_OUTER, self.track_rect, 1)
            
            handle_h = max(20, int((self.max_lines / len(self.logs)) * self.track_rect.height))
            max_offset = len(self.logs) - self.max_lines
            ratio = self.scroll_offset / float(max_offset) if max_offset > 0 else 0
            handle_y = self.track_rect.y + int(ratio * (self.track_rect.height - handle_h))
            
            handle_rect = pygame.Rect(self.track_rect.x, handle_y, self.track_rect.width, handle_h)
            draw_pixel_panel(surface, handle_rect, is_raised=not self.is_dragging)

    def handle_event(self, event):
        max_offset = max(0, len(self.logs) - self.max_lines)
        if max_offset == 0:
            return False
            
        if event.type == pygame.MOUSEWHEEL:
            # Check if mouse is hovering over the log box
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.scroll_offset = max(0, min(self.scroll_offset - event.y, max_offset))
                return True
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Calculate handle rect
                handle_h = max(20, int((self.max_lines / len(self.logs)) * self.track_rect.height))
                ratio = self.scroll_offset / float(max_offset) if max_offset > 0 else 0
                handle_y = self.track_rect.y + int(ratio * (self.track_rect.height - handle_h))
                handle_rect = pygame.Rect(self.track_rect.x, handle_y, self.track_rect.width, handle_h)
                
                if handle_rect.collidepoint(event.pos) or self.track_rect.collidepoint(event.pos):
                    self.is_dragging = True
                    self.update_scroll_from_mouse(event.pos[1], handle_h, max_offset)
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                self.is_dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                handle_h = max(20, int((self.max_lines / len(self.logs)) * self.track_rect.height))
                self.update_scroll_from_mouse(event.pos[1], handle_h, max_offset)
                return True
                
        return False

    def update_scroll_from_mouse(self, mouse_y, handle_h, max_offset):
        click_y = max(self.track_rect.y, min(mouse_y, self.track_rect.bottom))
        usable_h = self.track_rect.height - handle_h
        if usable_h <= 0: return
        ratio = (click_y - self.track_rect.y - handle_h/2) / float(usable_h)
        ratio = max(0.0, min(1.0, ratio))
        self.scroll_offset = int(ratio * max_offset)


class SpeedSlider:
    def __init__(self, x, y, w, label, min_val=1, max_val=10, default_val=5, callback=None):
        self.rect = pygame.Rect(x, y, w, 50)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.callback = callback
        self.is_dragging = False

        self.track_rect = pygame.Rect(x + 10, y + 25, w - 20, 8)
        self.handle_w = 14
        self.handle_h = 22

    def draw(self, surface, font):
        txt_surf = font.render(f"{self.label}: {self.value}", True, COLOR_TEXT_MUTED)
        surface.blit(txt_surf, (self.rect.x + 10, self.rect.y))

        pygame.draw.rect(surface, COLOR_DARK_BLUE, self.track_rect)
        pygame.draw.rect(surface, COLOR_BORDER_OUTER, self.track_rect, 1)

        ratio = (self.value - self.min_val) / float(self.max_val - self.min_val)
        handle_x = self.track_rect.x + int(ratio * self.track_rect.width) - self.handle_w // 2
        handle_y = self.track_rect.y + self.track_rect.height // 2 - self.handle_h // 2
        
        handle_rect = pygame.Rect(handle_x, handle_y, self.handle_w, self.handle_h)
        draw_pixel_panel(surface, handle_rect, is_raised=not self.is_dragging)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                ratio = (self.value - self.min_val) / float(self.max_val - self.min_val)
                handle_x = self.track_rect.x + int(ratio * self.track_rect.width) - self.handle_w // 2
                handle_y = self.track_rect.y + self.track_rect.height // 2 - self.handle_h // 2
                handle_rect = pygame.Rect(handle_x, handle_y, self.handle_w, self.handle_h)
                
                if handle_rect.collidepoint(event.pos) or self.track_rect.collidepoint(event.pos):
                    self.is_dragging = True
                    self.update_val_from_mouse(event.pos[0])
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.update_val_from_mouse(event.pos[0])
                return True
        return False

    def update_val_from_mouse(self, mouse_x):
        click_x = max(self.track_rect.x, min(mouse_x, self.track_rect.x + self.track_rect.width))
        ratio = (click_x - self.track_rect.x) / float(self.track_rect.width)
        new_val = self.min_val + int(ratio * (self.max_val - self.min_val))
        if new_val != self.value:
            self.value = new_val
            if self.callback:
                self.callback(self.value)
