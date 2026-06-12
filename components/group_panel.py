# components/group_panel.py
import tkinter as tk
from constants import ui_settings

class GroupPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=ui_settings.BG_PANEL, bd=1, relief="solid", highlightthickness=0)
        self.config(highlightbackground="#D0D5DD")
        
        # Tiêu đề Nhóm
        lbl_title = tk.Label(self, text="Nhóm 3", font=ui_settings.FONT_TITLE, 
                             bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_DARK)
        lbl_title.pack(pady=(15, 10))
        
        # Tên các thành viên (không dấu, mỗi cái xuống hàng)
        members = [
            "Hồ Công Phong",
            "Phạm Uyên Thư",
            "Nguyễn Phước Thịnh"
        ]
        
        for member in members:
            lbl_member = tk.Label(self, text=member, font=ui_settings.FONT_LABEL, 
                                  bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_MUTED)
            lbl_member.pack(pady=5)
