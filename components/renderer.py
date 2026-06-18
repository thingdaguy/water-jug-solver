import pygame
import math
from constants.colors import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_BORDER_OUTER, COLOR_BORDER_INNER,
    COLOR_LIQUID_WATER, COLOR_LIQUID_BUBBLE, COLOR_CORK, COLOR_GOLD
)

def draw_pixel_panel(surface, rect, title=None, is_raised=True):
    """Draws an SNES-style RPG double-bordered box."""
    # Base background
    pygame.draw.rect(surface, COLOR_PANEL_BG, rect)
    
    # Outer dark shadow line
    pygame.draw.rect(surface, COLOR_BG_DARK, rect, 2)
    
    # Inner border line
    inner_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, rect.height - 6)
    pygame.draw.rect(surface, COLOR_BORDER_OUTER, inner_rect, 2)
    
    # Draw double corners / accents
    corner_color = COLOR_BORDER_INNER if is_raised else COLOR_BORDER_OUTER
    pygame.draw.rect(surface, corner_color, (rect.x + 1, rect.y + 1, 3, 3))
    pygame.draw.rect(surface, corner_color, (rect.x + rect.width - 4, rect.y + 1, 3, 3))
    pygame.draw.rect(surface, corner_color, (rect.x + 1, rect.y + rect.height - 4, 3, 3))
    pygame.draw.rect(surface, corner_color, (rect.x + rect.width - 4, rect.y + rect.height - 4, 3, 3))

    if title:
        # Mini title box
        font_title = pygame.font.SysFont("Consolas", 14, bold=True)
        txt_surface = font_title.render(f" {title} ", True, COLOR_BORDER_INNER, COLOR_PANEL_BG)
        txt_rect = txt_surface.get_rect(centerx=rect.centerx, top=rect.y - 8)
        surface.blit(txt_surface, txt_rect)


def render_shadow_text(surface, text, font, color, pos, shadow_color=(0, 0, 0), offset=(2, 2)):
    """Renders retro style text with a thick drop shadow."""
    # Draw shadow
    shadow_surf = font.render(text, True, shadow_color)
    surface.blit(shadow_surf, (pos[0] + offset[0], pos[1] + offset[1]))
    # Draw foreground
    fg_surf = font.render(text, True, color)
    surface.blit(fg_surf, pos)


def make_bottle_surface(capacity, level, is_selected=False, wave_offset=0.0):
    """Generates a retro chemical flask / jar surface with cork, water, wave & markings."""
    w = 110
    h = 100 + int((capacity / 10.0) * 110)
    
    # Create scratch surface with alpha
    surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
    
    # 1. Draw liquid first so borders cover it
    if level > 0:
        ratio = min(level / float(capacity), 1.0)
        liq_h = int((h - 25) * ratio)
        y_top = h + 10 - liq_h
        
        points = []
        for x in range(12, w + 8):
            is_neck_col = (24 <= x <= w - 4)
            wave_displacement = int(3.0 * math.sin(wave_offset + x * 0.2))
            col_y_top = y_top + wave_displacement
            
            # Bound liquid below cork base (y=26)
            if col_y_top < 26:
                col_y_top = 26
                
            if is_neck_col:
                points.append((x, col_y_top))
            else:
                # Outside neck, liquid must clip under the shoulder (y=40)
                points.append((x, max(40, col_y_top)))
                
        # Close shape points
        points.append((w + 8, h + 8))
        points.append((12, h + 8))
        
        # Draw liquid polygon
        pygame.draw.polygon(surf, COLOR_LIQUID_WATER, points)
        
        # Bubbles simulation
        num_bubbles = int(capacity * 1.5)
        for b_idx in range(num_bubbles):
            bx = 15 + ((b_idx * 37) % (w - 15))
            by_base = h + 5 - ((b_idx * 23) % liq_h) if liq_h > 5 else h + 5
            by = by_base - int((pygame.time.get_ticks() * 0.04 + b_idx * 8) % 35)
            
            is_neck_b = (24 <= bx <= w - 4)
            limit_y = y_top if is_neck_b else max(40, y_top)
            if by > limit_y + 2 and by < h + 8:
                pygame.draw.rect(surf, COLOR_LIQUID_BUBBLE, (bx, by, 3, 3))

    # 2. Draw wooden cork
    pygame.draw.rect(surf, COLOR_CORK, (24, 14, w - 28, 12))
    pygame.draw.rect(surf, (90, 50, 20), (24, 23, w - 28, 3)) # Cork shadow

    # 3. Draw measurement tick marks
    for i in range(1, capacity):
        tick_ratio = i / float(capacity)
        tick_y = h + 10 - int((h - 25) * tick_ratio)
        pygame.draw.line(surf, COLOR_BORDER_OUTER, (10, tick_y), (18, tick_y), 2)

    # 4. Draw bottle silhouette outline
    outline_points = [
        (22, 25), (22, 40), (10, 40), (10, h + 10),
        (w + 10, h + 10), (w + 10, 40), (w - 2, 40), (w - 2, 25)
    ]
    pygame.draw.lines(surf, COLOR_BG_DARK, False, outline_points, 4)
    pygame.draw.line(surf, COLOR_BG_DARK, (10, h + 10), (w + 10, h + 10), 6)

    # 5. Draw reflection highlight
    highlight_color = (255, 255, 255, 90)
    pygame.draw.line(surf, highlight_color, (w + 4, 46), (w + 4, h + 4), 3)
    pygame.draw.line(surf, highlight_color, (w + 4, 46), (w - 4, 40), 2) # Shoulder reflection
    
    # 6. Selection Highlight
    if is_selected:
        pulse = 180 + int(70 * math.sin(pygame.time.get_ticks() * 0.01))
        sel_color = (COLOR_GOLD[0], COLOR_GOLD[1], COLOR_GOLD[2], pulse)
        pygame.draw.rect(surf, sel_color, (2, 2, w + 16, h + 16), 3)

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
