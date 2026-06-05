# Khu vực nhập dữ liệu (dung tích bình, đích)
# components/input_panel.py
import tkinter as tk
from constants import ui_settings

class InputPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=ui_settings.BG_PANEL, bd=1, relief="solid", highlightthickness=0)
        self.config(highlightbackground="#D0D5DD")
        self.pack_propagate(False)
        
        # Tiêu đề Panel
        lbl_title = tk.Label(self, text="Input Panel", font=ui_settings.FONT_TITLE, 
                             bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_DARK)
        lbl_title.pack(pady=15)
        
        # --- Khu vực nhập thông số cấu hình bình nước ---
        # Bình A
        lbl_jug_a = tk.Label(self, text="Dung tích bình A (Lít):", font=ui_settings.FONT_LABEL, 
                             bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_MUTED)
        lbl_jug_a.pack(anchor="w", padx=20, pady=(10, 2))
        self.ent_jug_a = tk.Entry(self, font=ui_settings.FONT_TEXT, width=20, justify="center")
        self.ent_jug_a.pack(pady=(0, 10))
        
        # Bình B
        lbl_jug_b = tk.Label(self, text="Dung tích bình B (Lít):", font=ui_settings.FONT_LABEL, 
                             bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_MUTED)
        lbl_jug_b.pack(anchor="w", padx=20, pady=(10, 2))
        self.ent_jug_b = tk.Entry(self, font=ui_settings.FONT_TEXT, width=20, justify="center")
        self.ent_jug_b.pack(pady=(0, 10))

        # Bình C
        lbl_jug_c = tk.Label(self, text="Dung tích bình C (Lít):", font=ui_settings.FONT_LABEL, 
                             bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_MUTED)
        lbl_jug_c.pack(anchor="w", padx=20, pady=(10, 2))
        self.ent_jug_c = tk.Entry(self, font=ui_settings.FONT_TEXT, width=20, justify="center")
        self.ent_jug_c.pack(pady=(0, 10))
        
        # Lượng nước Đích
        lbl_target = tk.Label(self, text="Lượng nước đích (Lít):", font=ui_settings.FONT_LABEL, 
                              bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_MUTED)
        lbl_target.pack(anchor="w", padx=20, pady=(10, 2))
        self.ent_target = tk.Entry(self, font=ui_settings.FONT_TEXT, width=20, justify="center")
        self.ent_target.pack(pady=(0, 25))
        
        # --- Các nút thao tác xóa nhanh ---
        self.btn_clear_all = tk.Button(self, text="Clear All", font=ui_settings.FONT_LABEL,
                                       bg=ui_settings.BTN_PRIMARY, fg=ui_settings.TEXT_IN_BTN,
                                       activebackground=ui_settings.COLOR_ACCENT, activeforeground="white",
                                       bd=0, cursor="hand2", width=15, height=1)
        self.btn_clear_all.pack(pady=10)

    def get_inputs(self):
        """Trả về giá trị người dùng đã nhập"""
        return {
            "jug_a": self.ent_jug_a.get(),
            "jug_b": self.ent_jug_b.get(),
            "jug_c": self.ent_jug_c.get(),
            "target": self.ent_target.get()
        }