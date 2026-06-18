import pygame
import math
from constants.colors import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_BORDER_OUTER, COLOR_BORDER_INNER,
    COLOR_TEXT_WHITE, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED, COLOR_GREEN_SUCCESS,
    COLOR_RED_ERROR, COLOR_GOLD
)
from components.renderer import draw_pixel_panel, render_shadow_text

def layout_graph(last_search_results):
    """Calculates tree positions for search space nodes based on DFS/BFS hierarchies."""
    if not last_search_results:
        return {}
        
    start_state, parent_map, path, visited, frontier, algo_name, target = last_search_results
    
    adj = {}
    for child, (parent, _) in parent_map.items():
        if parent is not None:
            adj.setdefault(parent, []).append(child)

    level_spacing = 150
    node_spacing = 120
    positions = {}
    leaf_x = 0

    def setup_coords(node, depth=0):
        nonlocal leaf_x
        children = adj.get(node, [])
        y = depth * level_spacing

        if not children:
            x = leaf_x
            leaf_x += node_spacing
            positions[node] = (x, y)
            return x

        child_xs = [setup_coords(child, depth + 1) for child in children]
        x = sum(child_xs) / len(child_xs)
        positions[node] = (x, y)
        return x

    setup_coords(start_state)
    return positions


def draw_graph_screen(app):
    """Renders the tree graph screen with panning, zooming, and tooltips."""
    screen = app.screen
    screen.fill(COLOR_BG_DARK)
    
    # Render background grid
    grid_space = int(50 * app.graph_zoom)
    if grid_space >= 8:
        offset_x = int((app.graph_pan_x * app.graph_zoom) % grid_space)
        offset_y = int((app.graph_pan_y * app.graph_zoom) % grid_space)
        for x in range(offset_x, 1280, grid_space):
            pygame.draw.line(screen, (24, 25, 34), (x, 0), (x, 720))
        for y in range(offset_y, 720, grid_space):
            pygame.draw.line(screen, (24, 25, 34), (0, y), (1280, y))

    if not app.last_search_results:
        return
        
    start_state, parent_map, path, visited, frontier, algo_name, target = app.last_search_results
    path_states = set(state for state, _ in path) if path else set()
    
    # Screen projection converter
    def get_screen_pos(wx, wy):
        sx = int((wx + app.graph_pan_x) * app.graph_zoom + 640)
        sy = int((wy + app.graph_pan_y) * app.graph_zoom + 360)
        return sx, sy

    # 1. Draw connecting lines
    for child, (parent, action) in parent_map.items():
        if parent is None:
            continue
            
        px, py = app.graph_positions[parent]
        cx, cy = app.graph_positions[child]
        
        psx, psy = get_screen_pos(px, py)
        csx, csy = get_screen_pos(cx, cy)
        
        # Edge styling
        if child in path_states and parent in path_states:
            edge_color = COLOR_GREEN_SUCCESS
            edge_width = 3
        else:
            edge_color = (80, 85, 120)
            edge_width = 1
            
        pygame.draw.line(screen, edge_color, (psx, psy), (csx, csy), edge_width)
        
        # Directional arrows
        mx = (psx + csx) // 2
        my = (psy + csy) // 2
        angle = math.atan2(csy - psy, csx - psx)
        arr_len = int(6 * app.graph_zoom)
        if arr_len >= 3:
            arrow_points = [
                (mx, my),
                (mx - arr_len * math.cos(angle - 0.5), my - arr_len * math.sin(angle - 0.5)),
                (mx - arr_len * math.cos(angle + 0.5), my - arr_len * math.sin(angle + 0.5))
            ]
            pygame.draw.polygon(screen, edge_color, arrow_points)

    # 2. Draw nodes
    mouse_pos = pygame.mouse.get_pos()
    app.graph_hovered_node = None
    
    node_r = int(24 * app.graph_zoom)
    node_r = max(5, node_r)
    
    for state, (wx, wy) in app.graph_positions.items():
        sx, sy = get_screen_pos(wx, wy)
        
        # Color mapping depending on node class
        node_color = COLOR_PANEL_BG
        text_color = COLOR_TEXT_WHITE
        outline_color = COLOR_BORDER_OUTER
        outline_w = 2
        
        if state in path_states:
            node_color = (39, 174, 96)
            outline_color = COLOR_TEXT_GOLD
        elif state in visited:
            node_color = (41, 128, 185)
        elif state in frontier:
            node_color = (230, 126, 34)
        else:
            node_color = (127, 140, 141)
            
        if state == start_state:
            outline_color = COLOR_RED_ERROR
            outline_w = 3
        elif state.is_goal(target):
            outline_color = COLOR_GOLD
            outline_w = 4
            
        # Draw base sphere
        pygame.draw.circle(screen, node_color, (sx, sy), node_r)
        pygame.draw.circle(screen, outline_color, (sx, sy), node_r, outline_w)
        
        # Render text coordinates inside node
        if app.graph_zoom > 0.4:
            lbl_txt = ",".join(map(str, state.jugs))
            lbl_surf = app.font_small.render(lbl_txt, True, text_color)
            lbl_rect = lbl_surf.get_rect(center=(sx, sy))
            screen.blit(lbl_surf, lbl_rect)
            
        # Labels tags
        if state == start_state and app.graph_zoom > 0.5:
            render_shadow_text(screen, "START", app.font_small, COLOR_RED_ERROR, (sx - 20, sy - node_r - 20))
        elif state.is_goal(target) and app.graph_zoom > 0.5:
            render_shadow_text(screen, "GOAL", app.font_small, COLOR_GOLD, (sx - 18, sy + node_r + 5))

        # Check collision details for tooltip display
        dist = math.sqrt((mouse_pos[0] - sx)**2 + (mouse_pos[1] - sy)**2)
        if dist <= node_r:
            app.graph_hovered_node = state

    # 3. Tooltip overlay rendering
    if app.graph_hovered_node:
        state = app.graph_hovered_node
        state_str = f"Trạng thái: ({','.join(map(str, state.jugs))})"
        parent_info = parent_map.get(state)
        action_str = f"Hành động: {parent_info[1]}" if parent_info else "Bắt đầu"
        parent_state = parent_info[0] if parent_info else None
        parent_str = f"Cha: ({','.join(map(str, parent_state.jugs))})" if parent_state else "None"
        
        # Adjust tooltip window size
        tt_w = 320
        tt_h = 95
        tt_x = mouse_pos[0] + 15
        tt_y = mouse_pos[1] + 15
        
        # Ensure tooltip does not overflow screen boundaries
        if tt_x + tt_w > 1260: tt_x = mouse_pos[0] - tt_w - 15
        if tt_y + tt_h > 700: tt_y = mouse_pos[1] - tt_h - 15
        
        tt_rect = pygame.Rect(tt_x, tt_y, tt_w, tt_h)
        draw_pixel_panel(screen, tt_rect, title="STATE INFO", is_raised=False)
        
        screen.blit(app.font_small.render(state_str, True, COLOR_TEXT_GOLD), (tt_x + 15, tt_y + 20))
        screen.blit(app.font_small.render(action_str, True, COLOR_TEXT_WHITE), (tt_x + 15, tt_y + 42))
        screen.blit(app.font_small.render(parent_str, True, COLOR_TEXT_MUTED), (tt_x + 15, tt_y + 64))

    # 4. Draw overlays
    guide_rect = pygame.Rect(20, 660, 990, 45)
    draw_pixel_panel(screen, guide_rect, is_raised=False)
    render_shadow_text(screen, "RÊ CHUỘT VÀO NÚT TRẠNG THÁI ĐỂ XEM CHI TIẾT | KÉO CHUỘT ĐỂ CUỘN | CUỘN CHUỘT ĐỂ ZOOM", 
                       app.font_small, COLOR_TEXT_MUTED, (40, 672))

    title_rect = pygame.Rect(20, 10, 990, 45)
    draw_pixel_panel(screen, title_rect)
    render_shadow_text(screen, f"CÂY TÌM KIẾM KHÔNG GIAN TRẠNG THÁI (Thuật toán: {algo_name})", 
                       app.font_label, COLOR_TEXT_GOLD, (40, 22))

    app.btn_graph_back.draw(screen, app.font_label)
    app.btn_graph_fit.draw(screen, app.font_label)
