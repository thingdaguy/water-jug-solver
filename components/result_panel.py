# Khu vực hiển thị kết quả và quá trình thực thi
# components/result_panel.py
import tkinter as tk
from constants import ui_settings

class ResultPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=ui_settings.BG_MAIN)
        
        # Tiêu đề khu vực mô phỏng chính
        lbl_main = tk.Label(self, text="KHÔNG GIAN MÔ PHỎNG & TRỰC QUAN HÓA BƯỚC ĐONG NƯỚC", 
                            font=ui_settings.FONT_TITLE, bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK)
        lbl_main.pack(pady=15)
        
        # --- KHU VỰC GIỮ CHỖ (Để vẽ đồ thị bình nước hoặc animation sau này) ---
        self.canvas_area = tk.Frame(self, bg="#FFFFFF", bd=1, relief="solid")
        self.canvas_area.pack(expand=True, fill="both", padx=20, pady=10)
        
        lbl_placeholder = tk.Label(self.canvas_area, text="[ Khu vực trống thiết kế Mô phỏng trực quan Đồ họa ]",
                                   font=ui_settings.FONT_LABEL, bg="#FFFFFF", fg=ui_settings.COLOR_ACCENT)
        lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
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