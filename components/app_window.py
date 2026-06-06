# Cửa sổ chính chứa toàn bộ giao diện
# components/app_window.py
import tkinter as tk
from constants import ui_settings
from components.input_panel import InputPanel
from components.control_panel import ControlPanel
from components.result_panel import ResultPanel

class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chương trình Giải Bài Toán Đong Nước - Trí Tuệ Nhân Tạo")
        self.geometry("1280x720")
        self.configure(bg=ui_settings.BG_MAIN)
        
        # Khởi tạo 3 panel chính
        self.input_panel = InputPanel(self)
        self.result_panel = ResultPanel(self)
        self.control_panel = ControlPanel(self)
        
        # Đặt bố cục (Layout) trái - giữa - phải tương tự như ảnh mẫu
        self.input_panel.pack(side="left", fill="y", padx=15, pady=15, ipadx=10)
        self.control_panel.pack(side="right", fill="y", padx=15, pady=15, ipadx=10)
        self.result_panel.pack(side="left", expand=True, fill="both", pady=15)
        
        # Thiết lập kích thước cố định mong muốn cho các thanh panel biên
        self.input_panel.config(width=260)
        self.control_panel.config(width=280)
        
        # Kết nối sự kiện của ControlPanel với logic điều khiển
        self.control_panel.btn_visualize.config(command=self.apply_inputs)
        self.control_panel.btn_reset.config(command=self.reset_game)
        self.control_panel.sld_speed.config(command=self.update_speed)
        
        # Thiết lập tốc độ ban đầu
        self.update_speed(self.control_panel.sld_speed.get())
        # Khởi tạo trạng thái ban đầu dựa trên entry inputs
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
        self.result_panel.animation_engine.set_config(capacities)
        self.result_panel.log_message(
            f"Cấu hình: Bình A={jug_a}L, Bình B={jug_b}L, Bình C={jug_c}L. Lượng nước đích={target}L."
        )

    def reset_game(self):
        inputs = self.input_panel.get_inputs()
        try:
            jug_a = int(inputs["jug_a"])
            jug_b = int(inputs["jug_b"])
            jug_c = int(inputs["jug_c"])
        except ValueError:
            jug_a, jug_b, jug_c = 8, 5, 3
            
        self.result_panel.animation_engine.set_config([jug_a, jug_b, jug_c])
        self.result_panel.log_message("Đã thiết lập lại trạng thái ban đầu.")