import pygame
import math
import sys
import time
import importlib

# Import package components
from constants.colors import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_BORDER_OUTER, COLOR_BORDER_INNER,
    COLOR_TEXT_WHITE, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED, COLOR_LIQUID_WATER,
    COLOR_RED_ERROR, COLOR_DARK_BLUE, COLOR_GOLD, COLOR_TEXT_GREEN, COLOR_TEXT_AMBER
)

# Import models and search algorithms
from models.state import State
from algorithms.blind_search.BFS import bfs_search
from algorithms.blind_search.DFS import dfs_search
from algorithms.blind_search.UCS import ucs_search
from algorithms.informed_search.Greedy import greedy_search

# Load dynamic A-star
a_star_module = importlib.import_module("algorithms.informed_search.A-star")
a_star_search = a_star_module.a_star_search

from algorithms.informed_search.Heuristic import heuristic_diff, heuristic_estimate


from components.renderer import (
    draw_pixel_panel, render_shadow_text, make_bottle_surface, blit_rotate_pivot
)
from components.widgets import (
    Button, Incrementer, RadioGroup, ScrollLogBox, SpeedSlider
)
from components.graph import (
    layout_graph, draw_graph_screen
)

class PygameWaterJugSolver:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Alchemist's Potion Jug Solver (Pygame Pixel Edition)")
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # Load fonts
        self.font_title = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_label = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_value = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 13)
        self.font_log = pygame.font.SysFont("Consolas", 13)

        # Simulation values
        self.capacities = [8, 5, 3]
        self.levels = [0, 0, 0]
        self.target = 4
        self.selected_jug = None
        self.simulation_speed = 5
        self.interactive = True

        # State transition playback state machine
        self.is_running_solution = False
        self.playback_paused = False
        self.animation_queue = []
        self.current_queue_index = 0
        self.last_search_results = None

        # Active transition metrics
        self.anim_active = False
        self.anim_type = None # "fill", "empty", "pour"
        self.anim_src = None
        self.anim_dest = None
        self.anim_phase = 0
        self.anim_x = 0.0
        self.anim_y = 0.0
        self.anim_angle = 0.0
        self.anim_pour_progress = 0.0
        self.lvl_src_start = 0.0
        self.lvl_src_end = 0.0
        self.lvl_dest_start = 0.0
        self.lvl_dest_end = 0.0

        # Particle systems
        self.pour_particles = []
        self.fill_particles = []
        self.empty_particles = []

        # Current screen toggle
        self.current_screen = "simulator"

        # Search Results Info
        self.nodes_explored = 0
        self.path_length = 0
        self.execution_time = 0.0
        self.search_status = "Ready"

        # Graph Interactive Settings
        self.graph_zoom = 1.0
        self.graph_pan_x = 0.0
        self.graph_pan_y = 0.0
        self.graph_positions = {}
        self.graph_dragging = False
        self.graph_drag_start = (0, 0)
        self.graph_hovered_node = None
        
        # Build layout UI panels
        self.init_ui()
        self.log_box.add_log("Hệ thống potion lab đã sẵn sàng.")
        self.log_box.add_log("Vui lòng cấu hình các bình và bấm 'VISUALIZE'.")

    def init_ui(self):
        # 1. Left Input panel
        self.inc_a = Incrementer(20, 50, 240, "Dung tích bình A:", 1, 10, 8, lambda v: self.set_capacity(0, v))
        self.inc_b = Incrementer(20, 130, 240, "Dung tích bình B:", 1, 10, 5, lambda v: self.set_capacity(1, v))
        self.inc_c = Incrementer(20, 210, 240, "Dung tích bình C:", 1, 10, 3, lambda v: self.set_capacity(2, v))
        self.inc_target = Incrementer(20, 290, 240, "Lượng nước đích:", 1, 10, 4, self.set_target)
        
        self.btn_clear = Button(20, 380, 240, 40, "CLEAR INPUTS", self.clear_all_inputs)

        # 2. Right control panel
        self.algo_group = RadioGroup(1020, 50, 240, [
            ("Breadth-First Search", "BFS"),
            ("Depth-First Search", "DFS"),
            ("Uniform Cost Search", "UCS"),
            ("Greedy Best-First", "Greedy Best-First"),
            ("A* Search Algorithm", "A* Search")
        ], "BFS")

        self.cbo_heuristic = RadioGroup(1020, 240, 240, [
            ("Hàm khoảng cách hiệu", "diff"),
            ("Hàm mục tiêu ước lượng", "estimate")
        ], "diff")

        self.btn_visualize = Button(1020, 325, 240, 45, "VISUALIZE SEARCH", self.run_search_and_playback, color=(246, 177, 122), text_color=COLOR_DARK_BLUE, is_visualize=True)
        self.speed_slider = SpeedSlider(1020, 390, 240, "Speed", 1, 10, 5, self.set_speed)
        
        self.btn_step = Button(1020, 455, 75, 35, "Step", self.play_single_step)
        self.btn_pause = Button(1102, 455, 75, 35, "Pause", self.toggle_pause)
        self.btn_reset = Button(1185, 455, 75, 35, "Reset", self.reset_game)

        self.btn_show_graph = Button(1020, 640, 240, 40, "XEM ĐỒ THỊ TÌM KIẾM", self.show_search_graph)
        self.btn_show_graph.is_disabled = True

        self.btn_graph_back = Button(1150, 15, 110, 35, "QUAY LẠI", self.back_to_simulator, color=COLOR_BORDER_INNER, text_color=COLOR_DARK_BLUE)
        self.btn_graph_fit = Button(1030, 15, 110, 35, "KHỚP MH", self.fit_graph_to_screen)

        # Bottom log box
        self.log_box = ScrollLogBox(280, 530, 720, 180)

        # Manual buttons in simulation area
        self.btn_fill_a = Button(310, 450, 80, 30, "Fill A", lambda: self.start_manual_action("fill", 0), color=(46, 204, 113))
        self.btn_empty_a = Button(400, 450, 80, 30, "Empty A", lambda: self.start_manual_action("empty", 0), color=(231, 76, 60))
        self.btn_fill_b = Button(550, 450, 80, 30, "Fill B", lambda: self.start_manual_action("fill", 1), color=(46, 204, 113))
        self.btn_empty_b = Button(640, 450, 80, 30, "Empty B", lambda: self.start_manual_action("empty", 1), color=(231, 76, 60))
        self.btn_fill_c = Button(790, 450, 80, 30, "Fill C", lambda: self.start_manual_action("fill", 2), color=(46, 204, 113))
        self.btn_empty_c = Button(880, 450, 80, 30, "Empty C", lambda: self.start_manual_action("empty", 2), color=(231, 76, 60))
        
        self.manual_buttons = [
            self.btn_fill_a, self.btn_empty_a,
            self.btn_fill_b, self.btn_empty_b,
            self.btn_fill_c, self.btn_empty_c
        ]

    def set_capacity(self, idx, val):
        self.capacities[idx] = val
        self.levels[idx] = min(self.levels[idx], val)
        self.log_box.add_log(f"Đã cập nhật dung tích bình {chr(65+idx)} = {val}L.")

    def set_target(self, val):
        self.target = val
        self.log_box.add_log(f"Đã thiết lập lượng nước đích = {val}L.")

    def set_speed(self, val):
        self.simulation_speed = val

    def clear_all_inputs(self):
        self.inc_a.value = 1
        self.inc_b.value = 1
        self.inc_c.value = 1
        self.inc_target.value = 1
        self.capacities = [1, 1, 1]
        self.levels = [0, 0, 0]
        self.target = 1
        self.log_box.add_log("Đã xóa trắng các cấu hình đầu vào.")

    def show_search_graph(self):
        if self.last_search_results:
            self.current_screen = "graph"
            self.fit_graph_to_screen()
            self.log_box.add_log("Đang xem bản đồ cây tìm kiếm.")

    def back_to_simulator(self):
        self.current_screen = "simulator"
        self.log_box.add_log("Quay lại không gian mô phỏng chính.")

    def start_manual_action(self, act_type, idx):
        if not self.interactive or self.anim_active:
            return
            
        if act_type == "fill":
            if self.levels[idx] == self.capacities[idx]:
                self.log_box.add_log(f"Bình {chr(65+idx)} đã đầy sẵn!")
                return
            self.lvl_src_start = self.levels[idx]
            self.lvl_src_end = self.capacities[idx]
            self.anim_active = True
            self.anim_type = "fill"
            self.anim_src = idx
            self.anim_pour_progress = 0.0
            self.log_box.add_log(f"Manual: Đang đổ đầy bình {chr(65+idx)}...")
        elif act_type == "empty":
            if self.levels[idx] == 0:
                self.log_box.add_log(f"Bình {chr(65+idx)} đã rỗng sẵn!")
                return
            self.lvl_src_start = self.levels[idx]
            self.lvl_src_end = 0
            self.anim_active = True
            self.anim_type = "empty"
            self.anim_src = idx
            self.anim_pour_progress = 0.0
            self.log_box.add_log(f"Manual: Đang làm rỗng bình {chr(65+idx)}...")

    def reset_game(self):
        self.is_running_solution = False
        self.playback_paused = False
        self.animation_queue = []
        self.current_queue_index = 0
        self.selected_jug = None
        self.anim_active = False
        self.btn_pause.text = "Pause"
        
        self.nodes_explored = 0
        self.path_length = 0
        self.execution_time = 0.0
        self.search_status = "Ready"
        self.levels = [0, 0, 0]
        self.interactive = True
        self.btn_show_graph.is_disabled = True
        self.log_box.clear()
        self.log_box.add_log("Đã thiết lập lại trạng thái bình rỗng (0, 0, 0).")

    def run_search_and_playback(self):
        if self.anim_active:
            return
            
        start_state = State(tuple(self.levels), tuple(self.capacities))
        algo_key = self.algo_group.selected_value
        heuristic_name = self.cbo_heuristic.selected_value
        
        heuristic_fn = heuristic_diff if heuristic_name == "diff" else heuristic_estimate
        self.log_box.add_log(f"--- Bắt đầu chạy giải thuật: {algo_key} ---")
        
        self.is_running_solution = False
        self.animation_queue = []
        self.current_queue_index = 0
        self.btn_pause.text = "Pause"
        
        start_time = time.perf_counter()
        
        if algo_key == "BFS":
            path, count, visited, frontier, parent_map = bfs_search(start_state, self.target)
        elif algo_key == "DFS":
            path, count, visited, frontier, parent_map = dfs_search(start_state, self.target)
        elif algo_key == "UCS":
            path, count, visited, frontier, parent_map = ucs_search(start_state, self.target)
        elif algo_key == "Greedy Best-First":
            path, count, visited, frontier, parent_map = greedy_search(start_state, self.target, heuristic_fn)
        elif algo_key == "A* Search":
            path, count, visited, frontier, parent_map = a_star_search(start_state, self.target, heuristic_fn)
        else:
            self.log_box.add_log("LỖI: Thuật toán không được hỗ trợ.")
            return

        exec_time_ms = (time.perf_counter() - start_time) * 1000.0
        self.last_search_results = (start_state, parent_map, path, visited, frontier, algo_key, self.target)
        self.btn_show_graph.is_disabled = False
        self.nodes_explored = count
        self.execution_time = exec_time_ms

        if path is None:
            self.path_length = 0
            self.search_status = "Unsolvable"
            self.log_box.add_log("Không tìm thấy đường đi tới lượng nước đích!")
            self.show_search_graph()
            return

        self.path_length = len(path) - 1
        self.search_status = "Running"
        self.log_box.add_log(f"Thành công! Số bước giải: {self.path_length}")
        
        for i in range(len(path) - 1):
            curr_state = path[i][0]
            next_state = path[i + 1][0]
            action_desc = path[i + 1][1]
            step_anim = self.parse_transition(curr_state, next_state)
            if step_anim:
                self.animation_queue.append((step_anim, action_desc))
                
        self.interactive = False
        self.is_running_solution = True
        self.playback_paused = False
        self.current_queue_index = 0
        self.play_next_queue_step()

    def parse_transition(self, state_from, state_to):
        diff = [t - f for f, t in zip(state_from.jugs, state_to.jugs)]
        dec_indices = [idx for idx, val in enumerate(diff) if val < 0]
        inc_indices = [idx for idx, val in enumerate(diff) if val > 0]
        
        if len(dec_indices) == 1 and len(inc_indices) == 1:
            return ("pour", dec_indices[0], inc_indices[0])
        elif len(inc_indices) == 1 and len(dec_indices) == 0:
            return ("fill", inc_indices[0])
        elif len(dec_indices) == 1 and len(inc_indices) == 0:
            return ("empty", dec_indices[0])
        return None

    def play_next_queue_step(self):
        if not self.is_running_solution or self.playback_paused:
            return
            
        if self.current_queue_index < len(self.animation_queue):
            step_data, action_desc = self.animation_queue[self.current_queue_index]
            self.current_queue_index += 1
            
            self.log_box.add_log(f"Bước {self.current_queue_index}: {action_desc}")
            
            anim_type = step_data[0]
            if anim_type == "fill":
                idx = step_data[1]
                self.lvl_src_start = self.levels[idx]
                self.lvl_src_end = self.capacities[idx]
                self.anim_active = True
                self.anim_type = "fill"
                self.anim_src = idx
                self.anim_pour_progress = 0.0
            elif anim_type == "empty":
                idx = step_data[1]
                self.lvl_src_start = self.levels[idx]
                self.lvl_src_end = 0
                self.anim_active = True
                self.anim_type = "empty"
                self.anim_src = idx
                self.anim_pour_progress = 0.0
            elif anim_type == "pour":
                src, dest = step_data[1], step_data[2]
                amount = min(self.levels[src], self.capacities[dest] - self.levels[dest])
                self.lvl_src_start = self.levels[src]
                self.lvl_src_end = self.levels[src] - amount
                self.lvl_dest_start = self.levels[dest]
                self.lvl_dest_end = self.levels[dest] + amount
                
                self.anim_active = True
                self.anim_type = "pour"
                self.anim_src = src
                self.anim_dest = dest
                self.anim_phase = 1
                
                centers = [400, 640, 880]
                self.anim_x = centers[src] - 55
                h_src = 100 + int((self.capacities[src] / 10.0) * 110)
                self.anim_y = 360 - h_src
                self.anim_angle = 0.0
                self.anim_pour_progress = 0.0
        else:
            self.is_running_solution = False
            self.interactive = True
            self.search_status = "Finished"
            self.log_box.add_log("Mô phỏng lời giải hoàn tất!")
            self.show_search_graph()

    def play_single_step(self):
        if not self.is_running_solution or self.anim_active:
            return
        self.playback_paused = True
        self.btn_pause.text = "Resume"
        self.search_status = "Paused"
        self.play_next_queue_step()

    def toggle_pause(self):
        if not self.is_running_solution:
            return
        self.playback_paused = not self.playback_paused
        if self.playback_paused:
            self.btn_pause.text = "Resume"
            self.search_status = "Paused"
            self.log_box.add_log("Đã tạm dừng mô phỏng.")
        else:
            self.btn_pause.text = "Pause"
            self.search_status = "Running"
            self.log_box.add_log("Tiếp tục mô phỏng...")
            self.play_next_queue_step()

    def update_physics(self):
        if not self.anim_active:
            return
            
        sp = self.simulation_speed
        
        if self.anim_type == "fill":
            if self.anim_pour_progress < 1.0:
                self.anim_pour_progress += 0.012 * sp
                if self.anim_pour_progress >= 1.0:
                    self.anim_pour_progress = 1.0
                self.levels[self.anim_src] = self.lvl_src_start + (self.lvl_src_end - self.lvl_src_start) * self.anim_pour_progress
                
                centers = [400, 640, 880]
                tx = centers[self.anim_src]
                ty_limit = 370 - int((100 + (self.capacities[self.anim_src] / 10.0) * 110) * (self.levels[self.anim_src] / float(self.capacities[self.anim_src])))
                for _ in range(2):
                    self.fill_particles.append({
                        "x": tx + int(10 * math.sin(pygame.time.get_ticks() * 0.05)),
                        "y": 100,
                        "limit_y": ty_limit
                    })
            else:
                self.levels[self.anim_src] = self.lvl_src_end
                self.anim_active = False
                self.fill_particles.clear()
                self.log_box.add_log(f"Bình {chr(65+self.anim_src)} đã làm đầy xong.")
                if self.is_running_solution and not self.playback_paused:
                    self.play_next_queue_step()

        elif self.anim_type == "empty":
            if self.anim_pour_progress < 1.0:
                self.anim_pour_progress += 0.015 * sp
                if self.anim_pour_progress >= 1.0:
                    self.anim_pour_progress = 1.0
                self.levels[self.anim_src] = self.lvl_src_start + (self.lvl_src_end - self.lvl_src_start) * self.anim_pour_progress
                
                centers = [400, 640, 880]
                tx = centers[self.anim_src]
                for _ in range(3):
                    self.empty_particles.append({
                        "x": tx + int(8 * math.sin(pygame.time.get_ticks() * 0.1)),
                        "y": 380,
                        "vy": 4 + sp // 2,
                        "life": 15
                    })
            else:
                self.levels[self.anim_src] = self.lvl_src_end
                self.anim_active = False
                self.empty_particles.clear()
                self.log_box.add_log(f"Xả rỗng bình {chr(65+self.anim_src)} hoàn tất.")
                if self.is_running_solution and not self.playback_paused:
                    self.play_next_queue_step()

        elif self.anim_type == "pour":
            src = self.anim_src
            dest = self.anim_dest
            centers = [400, 640, 880]
            
            h_src = 100 + int((self.capacities[src] / 10.0) * 110)
            h_dest = 100 + int((self.capacities[dest] / 10.0) * 110)
            
            if src < dest:
                tgt_x = centers[dest] - 25 - 110
                tgt_y = 360 - h_dest - 40 - h_src
            else:
                tgt_x = centers[dest] + 25
                tgt_y = 360 - h_dest - 40 - h_src

            if self.anim_phase == 1:
                target_y = 360 - h_src - 60
                if self.anim_y > target_y:
                    self.anim_y -= 3.0 * sp
                else:
                    self.anim_y = target_y
                    self.anim_phase = 2
                    
            elif self.anim_phase == 2:
                dx = tgt_x - self.anim_x
                dy = tgt_y - self.anim_y
                dist = math.sqrt(dx*dx + dy*dy)
                step = 4.0 * sp
                if dist > step:
                    self.anim_x += (dx / dist) * step
                    self.anim_y += (dy / dist) * step
                else:
                    self.anim_x = tgt_x
                    self.anim_y = tgt_y
                    self.anim_phase = 3
                    
            elif self.anim_phase == 3:
                tgt_angle = -50.0 if src < dest else 50.0
                if abs(self.anim_angle - tgt_angle) > 1.5 * sp:
                    self.anim_angle += (-1.5 * sp) if src < dest else (1.5 * sp)
                else:
                    self.anim_angle = tgt_angle
                    self.anim_phase = 4
                    
            elif self.anim_phase == 4:
                if self.anim_pour_progress < 1.0:
                    self.anim_pour_progress += 0.012 * sp
                    if self.anim_pour_progress >= 1.0:
                        self.anim_pour_progress = 1.0
                    self.levels[src] = self.lvl_src_start + (self.lvl_src_end - self.lvl_src_start) * self.anim_pour_progress
                    self.levels[dest] = self.lvl_dest_start + (self.lvl_dest_end - self.lvl_dest_start) * self.anim_pour_progress
                    
                    lip_local_x = 120 if src < dest else 0
                    lip_local_y = 20
                    rad = math.radians(-self.anim_angle)
                    px = self.anim_x + 65
                    py = self.anim_y + h_src + 10
                    
                    dx = lip_local_x - 65
                    dy = lip_local_y - (h_src + 10)
                    
                    rx = dx * math.cos(rad) - dy * math.sin(rad)
                    ry = dx * math.sin(rad) + dy * math.cos(rad)
                    
                    lip_x = px + rx
                    lip_y = py + ry
                    
                    dest_x = centers[dest]
                    dest_y = 365 - h_dest
                    
                    for _ in range(2):
                        self.pour_particles.append({
                            "x": lip_x,
                            "y": lip_y,
                            "tx": dest_x,
                            "ty": dest_y,
                            "progress": 0.0
                        })
                else:
                    self.levels[src] = self.lvl_src_end
                    self.levels[dest] = self.lvl_dest_end
                    self.anim_phase = 5
                    self.pour_particles.clear()
                    
            elif self.anim_phase == 5:
                if abs(self.anim_angle) > 1.5 * sp:
                    self.anim_angle += (1.5 * sp) if src < dest else (-1.5 * sp)
                else:
                    self.anim_angle = 0.0
                    self.anim_phase = 6
                    
            elif self.anim_phase == 6:
                tgt_x = centers[src] - 55
                tgt_y = 360 - h_src - 60
                dx = tgt_x - self.anim_x
                dy = tgt_y - self.anim_y
                dist = math.sqrt(dx*dx + dy*dy)
                step = 4.0 * sp
                if dist > step:
                    self.anim_x += (dx / dist) * step
                    self.anim_y += (dy / dist) * step
                else:
                    self.anim_x = tgt_x
                    self.anim_y = tgt_y
                    self.anim_phase = 7
                    
            elif self.anim_phase == 7:
                target_y = 360 - h_src
                if self.anim_y < target_y:
                    self.anim_y += 3.0 * sp
                else:
                    self.anim_y = target_y
                    self.anim_active = False
                    self.log_box.add_log(f"Rót nước thành công.")
                    if self.is_running_solution and not self.playback_paused:
                        self.play_next_queue_step()

        self.update_particles()

    def update_particles(self):
        for p in self.pour_particles[:]:
            p["progress"] += 0.08
            if p["progress"] >= 1.0:
                self.pour_particles.remove(p)
                
        for p in self.fill_particles[:]:
            p["y"] += 6 + self.simulation_speed
            if p["y"] >= p["limit_y"]:
                self.fill_particles.remove(p)

        for p in self.empty_particles[:]:
            p["y"] += p["vy"]
            p["x"] += int(2 * math.sin(p["y"] * 0.1))
            p["life"] -= 1
            if p["life"] <= 0 or p["y"] > 520:
                self.empty_particles.remove(p)

    def draw_simulator(self):
        self.screen.fill(COLOR_BG_DARK)

        # Draw beautiful brick texture grid background
        for row in range(0, 720, 40):
            for col in range(280, 1000, 80):
                offset = 20 if (row // 40) % 2 == 0 else 0
                rect = pygame.Rect(col + offset, row, 80, 40)
                pygame.draw.rect(self.screen, (24, 25, 34), rect, 1)

        # Draw wood shelf
        pygame.draw.rect(self.screen, (101, 67, 33), (290, 360, 700, 20))
        pygame.draw.rect(self.screen, (60, 35, 10), (290, 380, 700, 5))
        pygame.draw.rect(self.screen, (101, 67, 33), (330, 385, 25, 40))
        pygame.draw.rect(self.screen, (101, 67, 33), (905, 385, 25, 40))

        # 1. Left Sidebar: Input Panel
        panel_left = pygame.Rect(10, 10, 260, 700)
        draw_pixel_panel(self.screen, panel_left, title="INPUT PANEL")
        
        self.inc_a.draw(self.screen, self.font_label, self.font_value)
        self.inc_b.draw(self.screen, self.font_label, self.font_value)
        self.inc_c.draw(self.screen, self.font_label, self.font_value)
        self.inc_target.draw(self.screen, self.font_label, self.font_value)
        self.btn_clear.draw(self.screen, self.font_label)

        # Developer log
        parch_rect = pygame.Rect(20, 530, 240, 160)
        draw_pixel_panel(self.screen, parch_rect, title="DEVELOPERS", is_raised=False)
        render_shadow_text(self.screen, "NHÓM 3 - THỰC HÀNH AI", self.font_label, COLOR_TEXT_GOLD, (35, 555))
        render_shadow_text(self.screen, "1. Hồ Công Phong", self.font_small, COLOR_TEXT_WHITE, (35, 585))
        render_shadow_text(self.screen, "2. Phạm Uyên Thư", self.font_small, COLOR_TEXT_WHITE, (35, 615))
        render_shadow_text(self.screen, "3. Nguyễn Phước Thịnh", self.font_small, COLOR_TEXT_WHITE, (35, 645))

        # 2. Right Sidebar: Control Panel
        panel_right = pygame.Rect(1010, 10, 260, 700)
        draw_pixel_panel(self.screen, panel_right, title="CONTROL PANEL")
        
        self.algo_group.draw(self.screen, self.font_label)
        self.cbo_heuristic.draw(self.screen, self.font_label)
        self.btn_visualize.draw(self.screen, self.font_label)
        self.speed_slider.draw(self.screen, self.font_label)
        
        self.btn_step.draw(self.screen, self.font_small)
        self.btn_pause.draw(self.screen, self.font_small)
        self.btn_reset.draw(self.screen, self.font_small)

        # Metric stats grid
        stats_rect = pygame.Rect(1020, 500, 240, 130)
        draw_pixel_panel(self.screen, stats_rect, title="RESULTS STATS", is_raised=False)
        render_shadow_text(self.screen, f"Nodes Explored: {self.nodes_explored}", self.font_small, COLOR_TEXT_WHITE, (1035, 520))
        render_shadow_text(self.screen, f"Path Length:    {self.path_length}", self.font_small, COLOR_TEXT_WHITE, (1035, 545))
        render_shadow_text(self.screen, f"Execution Time: {self.execution_time:.2f} ms", self.font_small, COLOR_TEXT_WHITE, (1035, 570))
        
        status_color = COLOR_TEXT_GREEN
        if self.search_status in ["Unsolvable", "Error"]:
            status_color = COLOR_RED_ERROR
        elif self.search_status in ["Paused", "Running"]:
            status_color = COLOR_TEXT_GOLD
        render_shadow_text(self.screen, f"Status:         {self.search_status}", self.font_small, status_color, (1035, 595))

        self.btn_show_graph.draw(self.screen, self.font_label)

        # 3. Central Simulation Area
        render_shadow_text(self.screen, "ALCHEMIST'S POTION JUG SIMULATION SPACE", self.font_title, COLOR_BORDER_INNER, (370, 20))
        render_shadow_text(self.screen, "CHẠM VÀO BÌNH ĐỂ LỰA CHỌN & RÓT THỦ CÔNG", self.font_small, COLOR_TEXT_MUTED, (460, 48))

        # Render 3 potion jars on the shelf
        centers = [400, 640, 880]
        ticks_wave = pygame.time.get_ticks() * 0.006
        for idx in range(3):
            is_selected = (self.selected_jug == idx)
            is_moving = (self.anim_active and self.anim_type == "pour" and self.anim_src == idx)
            
            cap = self.capacities[idx]
            level = self.levels[idx]
            h = 100 + int((cap / 10.0) * 110)
            
            bottle_surf = make_bottle_surface(cap, level, is_selected, ticks_wave + idx * 1.5)
            
            if is_moving:
                local_pivot = (65, h + 10)
                screen_pivot = (self.anim_x + 65, self.anim_y + h + 10)
                blit_rotate_pivot(self.screen, bottle_surf, screen_pivot, local_pivot, self.anim_angle)
            else:
                bx = centers[idx] - 55
                by = 360 - h
                self.screen.blit(bottle_surf, (bx - 10, by - 10))

            lbl_name = f"Bình {chr(65+idx)}"
            lbl_level = f"{level:.1f}/{cap} L" if isinstance(level, float) else f"{level}/{cap} L"
            
            lbl_surf1 = self.font_label.render(lbl_name, True, COLOR_TEXT_WHITE)
            lbl_surf2 = self.font_small.render(lbl_level, True, COLOR_TEXT_GOLD)
            
            self.screen.blit(lbl_surf1, lbl_surf1.get_rect(center=(centers[idx], 395)))
            self.screen.blit(lbl_surf2, lbl_surf2.get_rect(center=(centers[idx], 415)))

        # 4. Render particle streams
        for fp in self.fill_particles:
            pygame.draw.rect(self.screen, COLOR_LIQUID_WATER, (fp["x"] - 2, fp["y"], 5, 25))
        for ep in self.empty_particles:
            pygame.draw.rect(self.screen, COLOR_LIQUID_WATER, (ep["x"] - 2, ep["y"], 4, 15))
        for pp in self.pour_particles:
            t = pp["progress"]
            arc_y = -15 * math.sin(math.pi * t)
            cur_x = int((1 - t) * pp["x"] + t * pp["tx"])
            cur_y = int((1 - t) * pp["y"] + t * pp["ty"] + arc_y)
            pygame.draw.rect(self.screen, COLOR_LIQUID_WATER, (cur_x - 3, cur_y - 3, 6, 6))

        if self.anim_active and self.anim_type == "fill":
            tx = centers[self.anim_src]
            pygame.draw.rect(self.screen, (130, 130, 140), (tx - 15, 60, 30, 40))
            pygame.draw.rect(self.screen, COLOR_TEXT_GOLD, (tx - 5, 100, 10, 5))

        self.log_box.draw(self.screen, self.font_log)
        
        for btn in self.manual_buttons:
            btn.draw(self.screen, self.font_small)

    def fit_graph_to_screen(self):
        self.graph_positions = layout_graph(self.last_search_results)
        if not self.graph_positions:
            return
            
        xs = [p[0] for p in self.graph_positions.values()]
        ys = [p[1] for p in self.graph_positions.values()]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        tree_w = max_x - min_x
        tree_h = max_y - min_y
        
        if tree_w == 0: tree_w = 1
        if tree_h == 0: tree_h = 1
        
        scale_x = (1280 - 100) / float(tree_w)
        scale_y = (720 - 150) / float(tree_h)
        self.graph_zoom = min(scale_x, scale_y, 1.2)
        if self.graph_zoom < 0.15:
            self.graph_zoom = 0.15
            
        mid_x = (min_x + max_x) // 2
        mid_y = (min_y + max_y) // 2
        
        self.graph_pan_x = -mid_x
        self.graph_pan_y = -mid_y + 40

    def handle_simulator_clicks(self, pos):
        centers = [400, 640, 880]
        clicked_idx = None
        
        for idx in range(3):
            cap = self.capacities[idx]
            h = 100 + int((cap / 10.0) * 110)
            bx = centers[idx] - 55
            by = 360 - h
            
            bottle_rect = pygame.Rect(bx - 10, by - 10, 130, h + 20)
            if bottle_rect.collidepoint(pos):
                clicked_idx = idx
                break
                
        if clicked_idx is None:
            return
            
        if self.selected_jug is None:
            self.selected_jug = clicked_idx
            self.log_box.add_log(f"Đã chọn Bình {chr(65+clicked_idx)} ({self.levels[clicked_idx]}/{self.capacities[clicked_idx]}L). Chọn bình tiếp theo để rót.")
        elif self.selected_jug == clicked_idx:
            self.selected_jug = None
            self.log_box.add_log("Bỏ chọn bình.")
        else:
            src = self.selected_jug
            dest = clicked_idx
            self.selected_jug = None
            
            if self.levels[src] == 0:
                self.log_box.add_log(f"Không thể rót: Bình {chr(65+src)} rỗng!")
                return
            if self.levels[dest] == self.capacities[dest]:
                self.log_box.add_log(f"Không thể rót: Bình {chr(65+dest)} đầy!")
                return
                
            amount = min(self.levels[src], self.capacities[dest] - self.levels[dest])
            self.lvl_src_start = self.levels[src]
            self.lvl_src_end = self.levels[src] - amount
            self.lvl_dest_start = self.levels[dest]
            self.lvl_dest_end = self.levels[dest] + amount
            
            self.anim_active = True
            self.anim_type = "pour"
            self.anim_src = src
            self.anim_dest = dest
            self.anim_phase = 1
            
            h_src = 100 + int((self.capacities[src] / 10.0) * 110)
            self.anim_x = centers[src] - 55
            self.anim_y = 360 - h_src
            self.anim_angle = 0.0
            self.anim_pour_progress = 0.0
            self.log_box.add_log(f"Đang rót {amount}L từ bình {chr(65+src)} sang {chr(65+dest)}...")

    def run(self):
        while self.is_running:
            self.clock.tick(60)
            self.update_physics()
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.quit()
                    sys.exit()

                if self.current_screen == "simulator":
                    self.inc_a.handle_event(event)
                    self.inc_b.handle_event(event)
                    self.inc_c.handle_event(event)
                    self.inc_target.handle_event(event)
                    self.btn_clear.handle_event(event)

                    self.algo_group.handle_event(event)
                    self.cbo_heuristic.handle_event(event)
                    self.btn_visualize.handle_event(event)
                    self.speed_slider.handle_event(event)
                    self.btn_step.handle_event(event)
                    self.btn_pause.handle_event(event)
                    self.btn_reset.handle_event(event)
                    
                    self.btn_show_graph.handle_event(event)

                    for btn in self.manual_buttons:
                        btn.handle_event(event)

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1 and not self.anim_active:
                            px, py = event.pos
                            if 280 <= px <= 1000 and py < 450:
                                self.handle_simulator_clicks(event.pos)

                elif self.current_screen == "graph":
                    self.btn_graph_back.handle_event(event)
                    self.btn_graph_fit.handle_event(event)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if not (self.btn_graph_back.rect.collidepoint(event.pos) or self.btn_graph_fit.rect.collidepoint(event.pos)):
                                self.graph_dragging = True
                                self.graph_drag_start = event.pos
                        elif event.button == 4:
                            self.graph_zoom = min(self.graph_zoom * 1.15, 6.0)
                        elif event.button == 5:
                            self.graph_zoom = max(self.graph_zoom * 0.85, 0.15)
                            
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.graph_dragging = False
                            
                    elif event.type == pygame.MOUSEMOTION:
                        if self.graph_dragging:
                            dx = event.pos[0] - self.graph_drag_start[0]
                            dy = event.pos[1] - self.graph_drag_start[1]
                            self.graph_pan_x += dx / self.graph_zoom
                            self.graph_pan_y += dy / self.graph_zoom
                            self.graph_drag_start = event.pos

            if self.is_running:
                if self.current_screen == "simulator":
                    self.draw_simulator()
                elif self.current_screen == "graph":
                    draw_graph_screen(self)
                
                pygame.display.flip()


def run_app():
    app = PygameWaterJugSolver()
    app.run()
