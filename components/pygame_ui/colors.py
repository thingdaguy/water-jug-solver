# components/pygame_ui/colors.py

COLOR_BG_DARK = (20, 20, 28)      # Deep dark space background
COLOR_PANEL_BG = (36, 39, 58)     # Dark slate for panel backdrops
COLOR_BORDER_OUTER = (112, 119, 161) # Slate gray outline
COLOR_BORDER_INNER = (246, 177, 122) # Warm cream accent highlight
COLOR_TEXT_WHITE = (245, 245, 250)
COLOR_TEXT_GOLD = (255, 215, 0)
COLOR_TEXT_MUTED = (160, 165, 200)
COLOR_TEXT_GREEN = (57, 255, 20)  # Lime green console log
COLOR_TEXT_AMBER = (255, 176, 0)  # Amber console log
COLOR_LIQUID_WATER = (76, 201, 240, 200) # Luminous translucent cyan
COLOR_LIQUID_BUBBLE = (255, 255, 255, 180)
COLOR_CORK = (139, 90, 43)
COLOR_GOLD = (255, 215, 0)
COLOR_GREEN_SUCCESS = (46, 204, 113)
COLOR_RED_ERROR = (231, 76, 60)
COLOR_DARK_BLUE = (25, 28, 45)


def clamp_color(val):
    """Clamps a numeric value between 0 and 255 for safe Pygame color parsing."""
    return max(0, min(255, int(val)))
