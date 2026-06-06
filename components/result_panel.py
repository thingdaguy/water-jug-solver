import tkinter as tk
from constants import ui_settings
from components.animation.engine import WaterJugAnimationEngine

class ResultPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=ui_settings.BG_MAIN)
        
        # Tiêu đề khu vực mô phỏng chính
        lbl_main = tk.Label(self, text="KHÔNG GIAN MÔ PHỎNG & TRỰC QUAN HÓA BƯỚC ĐONG NƯỚC", 
                            font=ui_settings.FONT_TITLE, bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK)
        lbl_main.pack(pady=15)
        
        # --- KHU VỰC HOẠT HỌA ---
        self.canvas_area = tk.Frame(self, bg="#FFFFFF", bd=1, relief="solid")
        self.canvas_area.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Tạo canvas của động cơ animation
        self.animation_engine = WaterJugAnimationEngine(self.canvas_area, on_log=self.log_message)
        self.animation_engine.pack(expand=True, fill="both")
        
        # --- THANH PHÍM ĐIỀU KHIỂN THỦ CÔNG ---
        self.btn_frame = tk.Frame(self, bg=ui_settings.BG_MAIN)
        self.btn_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.fill_buttons = []
        self.empty_buttons = []
        
        for i in range(3):
            lbl_name = ["A", "B", "C"][i]
            frame_jug_ctrl = tk.Frame(self.btn_frame, bg=ui_settings.BG_MAIN)
            frame_jug_ctrl.pack(side="left", expand=True)
            
            lbl_jug = tk.Label(frame_jug_ctrl, text=f"Bình {lbl_name}:", font=ui_settings.FONT_LABEL, bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK)
            lbl_jug.pack(side="left", padx=5)
            
            btn_f = tk.Button(frame_jug_ctrl, text=f"Fill {lbl_name}", font=("Segoe UI", 9, "bold"),
                              bg="#2ECC71", fg="white", activebackground="#27AE60", activeforeground="white",
                              bd=0, cursor="hand2", width=7, command=lambda idx=i: self.animation_engine.start_fill(idx))
            btn_f.pack(side="left", padx=2)
            self.fill_buttons.append(btn_f)
            
            btn_e = tk.Button(frame_jug_ctrl, text=f"Empty {lbl_name}", font=("Segoe UI", 9, "bold"),
                              bg="#E74C3C", fg="white", activebackground="#C0392B", activeforeground="white",
                              bd=0, cursor="hand2", width=7, command=lambda idx=i: self.animation_engine.start_empty(idx))
            btn_e.pack(side="left", padx=2)
            self.empty_buttons.append(btn_e)
        
        # --- KHU VỰC TEXT LOG VISUALIZE STEPS (Chừa sẵn hiển thị các bước bằng text) ---
        lbl_log = tk.Label(self, text="Chi tiết các bước thực hiện (Text Steps Log):", 
                           font=ui_settings.FONT_LABEL, bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK)
        lbl_log.pack(anchor="w", padx=20, pady=(10, 2))
        
        frame_log = tk.Frame(self, bg=ui_settings.BG_MAIN)
        frame_log.pack(fill="x", padx=20, pady=(0, 20))
        
        self.scrollbar = tk.Scrollbar(frame_log)
        self.scrollbar.pack(side="right", fill="y")
        
        # Khung Text hiển thị các bước chuyển đổi trạng thái bằng chữ
        self.txt_logger = tk.Text(frame_log, height=8, font=("Consolas", 10), 
                                  yscrollcommand=self.scrollbar.set, bg="#FFFFFF", fg=ui_settings.COLOR_DARK)
        self.txt_logger.pack(side="left", fill="x", expand=True)
        self.scrollbar.config(command=self.txt_logger.yview)
        
        # Trạng thái ban đầu của Log text
        self.log_message("Hệ thống đã sẵn sàng. Vui lòng cấu hình dữ liệu đầu vào và bấm 'Visualize'.")

    def log_message(self, message):
        """Hàm hỗ trợ ghi log tiến trình bằng text ra màn hình chính"""
        self.txt_logger.config(state="normal")
        self.txt_logger.insert(tk.END, message + "\n")
        self.txt_logger.see(tk.END)
        self.txt_logger.config(state="disabled")
        
    def clear_log(self):
        """Xóa toàn bộ nội dung text log"""
        self.txt_logger.config(state="normal")
        self.txt_logger.delete("1.0", tk.END)
        self.txt_logger.config(state="disabled")