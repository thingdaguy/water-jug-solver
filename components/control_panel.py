# Khu vực lựa chọn thuật toán và nút điều khiển
# components/control_panel.py
import tkinter as tk
from tkinter import ttk
from constants import ui_settings

class ControlPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=ui_settings.BG_PANEL, bd=1, relief="solid", highlightthickness=0)
        self.pack_propagate(False)
        
        # Tiêu đề Panel chính
        lbl_title = tk.Label(self, text="Control & Result Panel", font=ui_settings.FONT_TITLE, 
                             bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_DARK)
        lbl_title.pack(pady=15)
        
        # --- KHU VỰC CHỌN THUẬT TOÁN ---
        # Biến lưu thuật toán đang chọn (Dùng Radio Button nhóm lại trực quan như ảnh)
        self.selected_algo = tk.StringVar(value="BFS")
        
        frame_algos = tk.Frame(self, bg=ui_settings.BG_PANEL)
        frame_algos.pack(pady=5)
        
        algos = [("BFS", "BFS"), ("DFS", "DFS"), ("UCS", "UCS"), 
                 ("Greedy", "Greedy Best-First"), ("A*", "A* Search")]
        
        for text, value in algos:
            rb = tk.Radiobutton(frame_algos, text=text, value=value, variable=self.selected_algo,
                                font=ui_settings.FONT_TEXT, bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_DARK,
                                indicatoron=0, width=22, pady=5, selectcolor=ui_settings.BG_MAIN,
                                bd=1, relief="groove", cursor="hand2")
            rb.pack(pady=3)
            
        # Dropdown chọn Heuristic cho Informed Search (Greedy/A*)
        lbl_heuristic = tk.Label(self, text="Heuristic Metric:", font=ui_settings.FONT_TEXT, 
                                 bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_MUTED)
        lbl_heuristic.pack(pady=(10, 2))
        self.cbo_heuristic = ttk.Combobox(self, values=["Hàm khoảng cách hiệu", "Hàm mục tiêu ước lượng"], 
                                          state="readonly", width=20, font=ui_settings.FONT_TEXT)
        self.cbo_heuristic.current(0)
        self.cbo_heuristic.pack(pady=(0, 15))
        
        # --- NÚT VISUALIZE ---
        self.btn_visualize = tk.Button(self, text="Visualize", font=ui_settings.FONT_TITLE,
                                       bg=ui_settings.BTN_PRIMARY, fg=ui_settings.TEXT_IN_BTN,
                                       activebackground=ui_settings.COLOR_DARK, activeforeground="white",
                                       bd=0, cursor="hand2", width=18, height=1)
        self.btn_visualize.pack(pady=10)
        
        # --- THANH ĐIỀU KHIỂN CHẠY TỪNG BƯỚC (Step, Pause, Reset) ---
        frame_ctrl = tk.Frame(self, bg=ui_settings.BG_PANEL)
        frame_ctrl.pack(pady=5)
        
        self.btn_step = tk.Button(frame_ctrl, text="Step", font=ui_settings.FONT_TEXT, bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK, width=6)
        self.btn_pause = tk.Button(frame_ctrl, text="Pause", font=ui_settings.FONT_TEXT, bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK, width=6)
        self.btn_reset = tk.Button(frame_ctrl, text="Reset", font=ui_settings.FONT_TEXT, bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK, width=6)
        
        self.btn_step.pack(side="left", padx=3)
        self.btn_pause.pack(side="left", padx=3)
        self.btn_reset.pack(side="left", padx=3)
        
        # Slider điều chỉnh tốc độ mô phỏng
        self.sld_speed = tk.Scale(self, from_=1, to=10, orient="horizontal", bg=ui_settings.BG_PANEL, 
                                  troughcolor=ui_settings.BG_MAIN, activebackground=ui_settings.BTN_PRIMARY,
                                  bd=0, highlightthickness=0, label="Simulation Speed")
        self.sld_speed.set(5)
        self.sld_speed.pack(fill="x", padx=30, pady=15)
        
        # --- KHU VỰC KẾT QUẢ (RESULTS) ---
        lbl_res_title = tk.Label(self, text="Results", font=ui_settings.FONT_TITLE, 
                                 bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_DARK)
        lbl_res_title.pack(pady=(15, 5))
        
        # Bố cục Grid hiển thị 4 nhãn thông số dạng text giống như bản thiết kế mẫu của bạn
        frame_grid = tk.Frame(self, bg=ui_settings.BG_PANEL)
        frame_grid.pack(pady=5, fill="x", padx=20)
        
        metrics = [
            ("Nodes Explored", "0", 0, 0),
            ("Path Length", "0", 0, 1),
            ("Execution Time", "0.0 ms", 1, 0),
            ("Status", "Ready", 1, 1)
        ]
        
        self.metric_labels = {}
        for label_text, default_val, r, c in metrics:
            f = tk.Frame(frame_grid, bg=ui_settings.BG_MAIN, bd=1, relief="groove", padx=5, pady=5)
            f.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
            
            lbl_title_m = tk.Label(f, text=label_text, font=("Segoe UI", 9, "bold"), bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_MUTED)
            lbl_title_m.pack()
            
            lbl_val_m = tk.Label(f, text=default_val, font=ui_settings.FONT_TEXT, bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK)
            lbl_val_m.pack()
            
            self.metric_labels[label_text] = lbl_val_m
            
        frame_grid.grid_columnconfigure(0, weight=1)
        frame_grid.grid_columnconfigure(1, weight=1)
        
        # Nút xem đồ thị tìm kiếm
        self.btn_show_graph = tk.Button(self, text="Xem Đồ Thị Tìm Kiếm", font=ui_settings.FONT_LABEL,
                                        bg=ui_settings.BTN_PRIMARY, fg="white",
                                        activebackground=ui_settings.COLOR_ACCENT, activeforeground="white",
                                        bd=0, cursor="hand2", width=20, height=1, state="disabled")
        self.btn_show_graph.pack(pady=15)