# Cửa sổ chính chứa toàn bộ giao diện
# components/app_window.py
import tkinter as tk
import time
import importlib
from constants import ui_settings
from components.input_panel import InputPanel
from components.control_panel import ControlPanel
from components.result_panel import ResultPanel
from models.state import State
from components.graph_visualizer import GraphWindow

# Import các thuật toán tìm kiếm
from algorithms.blind_search.BFS import bfs_search
from algorithms.blind_search.DFS import dfs_search
from algorithms.blind_search.UCS import ucs_search
from algorithms.informed_search.Greedy import greedy_search

# Load động module "A-star.py" do chứa ký tự gạch ngang trong tên file
a_star_module = importlib.import_module("algorithms.informed_search.A-star")
a_star_search = a_star_module.a_star_search

# Import các hàm Heuristic
from algorithms.informed_search.Heuristic import heuristic_diff, heuristic_estimate


class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chương trình Giải Bài Toán Đong Nước - Trí Tuệ Nhân Tạo")
        self.geometry("1280x720")
        self.configure(bg=ui_settings.BG_MAIN)
        
        # Trạng thái điều khiển mô phỏng/chạy tự động
        self.is_running_solution = False
        self.playback_paused = False
        self.animation_queue = []
        self.current_queue_index = 0
        self.last_search_results = None # Lưu kết quả lần chạy gần nhất để xem đồ thị
        
        # Tạo khung chứa phía bên trái để gom nhóm GroupPanel và InputPanel
        self.left_container = tk.Frame(self, bg=ui_settings.BG_MAIN)
        self.left_container.pack(side="left", fill="y", padx=15, pady=15)
        self.left_container.config(width=260)
        self.left_container.pack_propagate(False)
        
        # Khởi tạo các panel chính
        from components.group_panel import GroupPanel
        self.group_panel = GroupPanel(self.left_container)
        self.input_panel = InputPanel(self.left_container)
        self.result_panel = ResultPanel(self)
        self.control_panel = ControlPanel(self)
        
        # Đặt bố cục các panel bên trái
        self.group_panel.pack(side="top", fill="x", pady=(0, 15))
        self.input_panel.pack(side="top", fill="both", expand=True)
        
        # Đặt bố cục các panel giữa và phải
        self.control_panel.pack(side="right", fill="y", padx=15, pady=15, ipadx=10)
        self.result_panel.pack(side="left", expand=True, fill="both", pady=15)
        
        # Thiết lập kích thước cố định mong muốn cho các thanh panel biên
        self.group_panel.config(width=260)
        self.input_panel.config(width=260)
        self.control_panel.config(width=280)
        
        # Kết nối sự kiện của ControlPanel với logic điều khiển
        self.control_panel.btn_visualize.config(command=self.run_search_and_playback)
        self.control_panel.btn_reset.config(command=self.reset_game)
        self.control_panel.sld_speed.config(command=self.update_speed)
        
        # Thêm liên kết cho các nút điều khiển mô phỏng bổ sung
        self.control_panel.btn_step.config(command=self.play_single_step)
        self.control_panel.btn_pause.config(command=self.toggle_pause)
        self.control_panel.btn_show_graph.config(command=self.show_search_graph)
        
        # Callback báo khi vòi/cốc vẽ xong 1 hành động
        self.result_panel.animation_engine.on_state_changed = self.on_animation_step_complete
        
        # Thiết lập tốc độ ban đầu
        self.update_speed(self.control_panel.sld_speed.get())
        # Khởi tạo trạng thái ban đầu (Bình rỗng 0,0,0)
        self.after(100, self.apply_inputs)

    def update_speed(self, val):
        self.result_panel.animation_engine.set_speed(int(val))

    def apply_inputs(self):
        inputs = self.input_panel.get_inputs()
        try:
            jug_a = int(inputs["jug_a"])
            jug_b = int(inputs["jug_b"])
            jug_c = int(inputs["jug_c"])
            target = int(inputs["target"])
        except ValueError:
            self.result_panel.log_message("LỖI: Vui lòng nhập số nguyên hợp lệ cho dung tích các bình.")
            return
 
        if jug_a <= 0 or jug_b <= 0 or jug_c <= 0:
            self.result_panel.log_message("LỖI: Dung tích các bình phải lớn hơn 0.")
            return
            
        capacities = [jug_a, jug_b, jug_c]
        # Khởi tạo toàn bộ bình rỗng [0, 0, 0] theo GameRule.md
        self.result_panel.animation_engine.set_config(capacities, [0, 0, 0])
        self.result_panel.log_message(
            f"Cấu hình: Bình A={jug_a}L, Bình B={jug_b}L, Bình C={jug_c}L. Lượng nước đích={target}L."
        )

    def reset_game(self):
        # Dừng mô phỏng đang chạy nếu có
        self.is_running_solution = False
        self.playback_paused = False
        self.animation_queue = []
        self.current_queue_index = 0
        self.control_panel.btn_pause.config(text="Pause")
        self.control_panel.btn_show_graph.config(state="disabled")
        
        # Reset các nhãn metrics
        self.control_panel.metric_labels["Nodes Explored"].config(text="0")
        self.control_panel.metric_labels["Path Length"].config(text="0")
        self.control_panel.metric_labels["Execution Time"].config(text="0.0 ms")
        self.control_panel.metric_labels["Status"].config(text="Ready")
        
        inputs = self.input_panel.get_inputs()
        try:
            jug_a = int(inputs["jug_a"])
            jug_b = int(inputs["jug_b"])
            jug_c = int(inputs["jug_c"])
        except ValueError:
            jug_a, jug_b, jug_c = 8, 5, 3
            
        self.result_panel.animation_engine.set_config([jug_a, jug_b, jug_c], [0, 0, 0])
        self.result_panel.set_manual_controls_enabled(True)
        self.result_panel.clear_log()
        self.result_panel.log_message("Đã thiết lập lại trạng thái ban đầu rỗng (0, 0, 0).")

    def run_search_and_playback(self):
        """Chạy thuật toán AI đã chọn và thiết lập kịch bản mô phỏng."""
        # 1. Đọc và kiểm tra thông số đầu vào
        inputs = self.input_panel.get_inputs()
        try:
            jug_a = int(inputs["jug_a"])
            jug_b = int(inputs["jug_b"])
            jug_c = int(inputs["jug_c"])
            target = int(inputs["target"])
        except ValueError:
            self.result_panel.log_message("LỖI: Vui lòng nhập thông số hợp lệ!")
            return
            
        if jug_a <= 0 or jug_b <= 0 or jug_c <= 0:
            self.result_panel.log_message("LỖI: Dung tích bình phải lớn hơn 0.")
            return

        capacities = (jug_a, jug_b, jug_c)
        start_state = State((0, 0, 0), capacities)
        
        # Reset engine về ban đầu trước khi chạy thuật toán
        self.reset_game()
        self.result_panel.animation_engine.set_config(capacities, [0, 0, 0])
        
        # 2. Xác định thuật toán và Heuristic
        algo_key = self.control_panel.selected_algo.get()
        heuristic_name = self.control_panel.cbo_heuristic.get()
        
        # Chọn hàm heuristic
        if heuristic_name == "Hàm khoảng cách hiệu":
            heuristic_fn = heuristic_diff
        else:
            heuristic_fn = heuristic_estimate
            
        self.result_panel.log_message(f"--- Đang thực thi tìm kiếm bằng {algo_key} ---")
        
        # 3. Chạy thuật toán và đo thời gian
        start_time = time.perf_counter()
        
        if algo_key == "BFS":
            path, count, visited, frontier, parent_map = bfs_search(start_state, target)
        elif algo_key == "DFS":
            path, count, visited, frontier, parent_map = dfs_search(start_state, target)
        elif algo_key == "UCS":
            path, count, visited, frontier, parent_map = ucs_search(start_state, target)
        elif algo_key == "Greedy Best-First":
            path, count, visited, frontier, parent_map = greedy_search(start_state, target, heuristic_fn)
        elif algo_key == "A* Search":
            path, count, visited, frontier, parent_map = a_star_search(start_state, target, heuristic_fn)
        else:
            self.result_panel.log_message("LỖI: Thuật toán không được nhận diện.")
            return
            
        end_time = time.perf_counter()
        exec_time_ms = (end_time - start_time) * 1000.0
        
        # Lưu kết quả tìm kiếm
        self.last_search_results = (start_state, parent_map, path, visited, frontier, algo_key, target)
        self.control_panel.btn_show_graph.config(state="normal")
        
        # Cập nhật kết quả lên ControlPanel
        self.control_panel.metric_labels["Nodes Explored"].config(text=str(count))
        self.control_panel.metric_labels["Execution Time"].config(text=f"{exec_time_ms:.2f} ms")
        
        if path is None:
            self.control_panel.metric_labels["Path Length"].config(text="None")
            self.control_panel.metric_labels["Status"].config(text="Unsolvable")
            self.result_panel.log_message("Không tìm thấy đường đi tới lượng nước đích!")
            # Tự động hiển thị đồ thị tìm kiếm kể cả khi thất bại để người dùng khám phá
            self.show_search_graph()
            return
            
        # Tìm thấy lời giải
        steps = len(path) - 1
        self.control_panel.metric_labels["Path Length"].config(text=str(steps))
        self.control_panel.metric_labels["Status"].config(text="Running")
        self.result_panel.log_message(f"Tìm thấy lời giải! (Tổng số bước: {steps})")
        
        # 4. Phân tích đường đi và tạo hàng đợi mô phỏng
        self.animation_queue = []
        for i in range(len(path) - 1):
            curr_state = path[i][0]
            next_state = path[i + 1][0]
            action_desc = path[i + 1][1]
            
            step_anim = self.parse_transition(curr_state, next_state)
            if step_anim:
                self.animation_queue.append((step_anim, action_desc))
            else:
                self.result_panel.log_message(
                    f"CẢNH BÁO: Không thể chuyển đổi bước {i + 1}: "
                    f"{curr_state.jugs} -> {next_state.jugs} ({action_desc})"
                )

        if not self.animation_queue:
            self.result_panel.log_message("LỖI: Không tạo được hàng đợi hoạt họa từ lời giải.")
            self.control_panel.metric_labels["Status"].config(text="Error")
            self.show_search_graph()
            return
                
        # 5. Khởi động chạy tự động các bước mô phỏng
        self.result_panel.set_manual_controls_enabled(False)
        self.is_running_solution = True
        self.playback_paused = False
        self.current_queue_index = 0
        self.play_next_step()

    def parse_transition(self, state_from, state_to):
        """So sánh 2 trạng thái và trả về cấu trúc hành động hoạt họa."""
        diff = [t - f for f, t in zip(state_from.jugs, state_to.jugs)]
        dec_indices = [idx for idx, val in enumerate(diff) if val < 0]
        inc_indices = [idx for idx, val in enumerate(diff) if val > 0]
        
        # Rót nước: 1 bình giảm, 1 bình tăng lượng nước
        if len(dec_indices) == 1 and len(inc_indices) == 1:
            return ("pour", dec_indices[0], inc_indices[0])
        # Đổ đầy bình: chỉ có 1 bình tăng và lượng tăng không có bình nào giảm
        elif len(inc_indices) == 1 and len(dec_indices) == 0:
            return ("fill", inc_indices[0])
        # Xả rỗng bình: chỉ có 1 bình giảm
        elif len(dec_indices) == 1 and len(inc_indices) == 0:
            return ("empty", dec_indices[0])
        return None

    def play_next_step(self):
        """Chạy bước tiếp theo trong hàng đợi mô phỏng."""
        if not self.is_running_solution or self.playback_paused:
            return
            
        if self.current_queue_index < len(self.animation_queue):
            step_data, action_desc = self.animation_queue[self.current_queue_index]
            self.current_queue_index += 1
            
            # Ghi log mô tả hành động
            self.result_panel.log_message(f"Bước {self.current_queue_index}: {action_desc}")
            
            # Kích hoạt hiệu ứng hoạt họa tương ứng
            anim_type = step_data[0]
            if anim_type == "fill":
                self.result_panel.animation_engine.start_fill(step_data[1])
            elif anim_type == "empty":
                self.result_panel.animation_engine.start_empty(step_data[1])
            elif anim_type == "pour":
                self.result_panel.animation_engine.start_pour(step_data[1], step_data[2])
        else:
            self.is_running_solution = False
            self.result_panel.set_manual_controls_enabled(True)
            self.control_panel.metric_labels["Status"].config(text="Finished")
            self.result_panel.log_message("Mô phỏng lời giải hoàn tất!")
            self.show_search_graph()

    def play_single_step(self):
        """Chạy thủ công đúng 1 bước tiếp theo (khi bấm nút Step)."""
        if not self.is_running_solution:
            # Nếu chưa chạy lời giải nào, không làm gì
            return
            
        if self.result_panel.animation_engine.is_animating:
            # Đang có hiệu ứng chạy dở, bỏ qua
            return
            
        # Đóng băng chế độ tự động chạy
        self.playback_paused = True
        self.control_panel.btn_pause.config(text="Resume")
        self.control_panel.metric_labels["Status"].config(text="Paused")
        
        if self.current_queue_index < len(self.animation_queue):
            step_data, action_desc = self.animation_queue[self.current_queue_index]
            self.current_queue_index += 1
            
            self.result_panel.log_message(f"Bước {self.current_queue_index} (Từng bước): {action_desc}")
            
            anim_type = step_data[0]
            if anim_type == "fill":
                self.result_panel.animation_engine.start_fill(step_data[1])
            elif anim_type == "empty":
                self.result_panel.animation_engine.start_empty(step_data[1])
            elif anim_type == "pour":
                self.result_panel.animation_engine.start_pour(step_data[1], step_data[2])
        else:
            self.is_running_solution = False
            self.result_panel.set_manual_controls_enabled(True)
            self.control_panel.metric_labels["Status"].config(text="Finished")
            self.result_panel.log_message("Mô phỏng lời giải hoàn tất!")
            self.show_search_graph()

    def toggle_pause(self):
        """Tạm dừng / Tiếp tục mô phỏng tự động."""
        if not self.is_running_solution:
            return
            
        self.playback_paused = not self.playback_paused
        if self.playback_paused:
            self.control_panel.btn_pause.config(text="Resume")
            self.control_panel.metric_labels["Status"].config(text="Paused")
            self.result_panel.log_message("Đã tạm dừng mô phỏng.")
        else:
            self.control_panel.btn_pause.config(text="Pause")
            self.control_panel.metric_labels["Status"].config(text="Running")
            self.result_panel.log_message("Tiếp tục mô phỏng...")
            self.play_next_step()

    def on_animation_step_complete(self, levels):
        """Được gọi mỗi khi hoạt họa của Canvas hoàn tất."""
        if not self.is_running_solution:
            return
        if self.result_panel.animation_engine.is_animating:
            return
        if self.playback_paused:
            return
            
        # Thêm độ trễ nhỏ 400ms giữa các bước để người dùng kịp quan sát
        self.after(400, self.play_next_step)

    def show_search_graph(self):
        """Hiển thị đồ thị cây tìm kiếm trong một cửa sổ riêng."""
        if not self.last_search_results:
            return
            
        start_state, parent_map, path, visited, frontier, algo_name, target = self.last_search_results
        
        # Mở cửa sổ đồ thị mới
        GraphWindow(self, start_state, parent_map, path, visited, frontier, algo_name, target)