# main.py
from components.app_window import AppWindow

if __name__ == "__main__":
    # Khởi tạo cửa sổ giao diện chính trống
    app = AppWindow()
    # Chạy vòng lặp ứng dụng Tkinter
    app.mainloop()