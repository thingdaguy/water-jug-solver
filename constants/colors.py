COLOR_BG_DARK = (20, 24, 34)         # Brighter dark navy/slate background
COLOR_PANEL_BG = (28, 36, 54)        # Brighter deep slate/blue panel background
COLOR_BORDER_OUTER = (30, 58, 138)   # Slate blue outline
COLOR_BORDER_INNER = (56, 189, 248)  # Glowing cyan/sky blue accent border
COLOR_TEXT_WHITE = (245, 245, 250)
COLOR_TEXT_GOLD = (250, 204, 21)     # Amber yellow text for values
COLOR_TEXT_MUTED = (148, 163, 184)   # Slate gray text for labels
COLOR_TEXT_GREEN = (34, 197, 94)     # Success green
COLOR_TEXT_AMBER = (245, 158, 11)    # Warning amber
COLOR_LIQUID_WATER = (14, 165, 233, 160) # Vibrant translucent cyan water
COLOR_LIQUID_BUBBLE = (255, 255, 255, 120)
COLOR_CORK = (139, 90, 43)
COLOR_GOLD = (250, 204, 21)
COLOR_GREEN_SUCCESS = (34, 197, 94)
COLOR_RED_ERROR = (239, 68, 68)      # Warning red
COLOR_DARK_BLUE = (15, 23, 42)       # Dark slate blue for text

def clamp_color(val):
    """Clamps a numeric value between 0 and 255 for safe Pygame color parsing."""
    return max(0, min(255, int(val)))
