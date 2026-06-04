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