import os
import sys
import tkinter as tk

# Add project root directory to sys.path to enable components import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.animation.engine import WaterJugAnimationEngine

def main():
    root = tk.Tk()
    root.geometry("800x500")
    root.title("Water Jug 3-Cup Animation Engine Demo")
    root.configure(bg="#EDF1F6")
    
    # Title Label
    lbl_title = tk.Label(root, text="DEMO HOẠT HỌA ĐỘNG CƠ ĐONG NƯỚC (3 BÌNH)", 
                         font=("Segoe UI", 14, "bold"), bg="#EDF1F6", fg="#262B63")
    lbl_title.pack(pady=10)
    
    # Subtitle / Instructions
    lbl_sub = tk.Label(root, text="Hệ thống tự động chạy kịch bản demo. Bạn cũng có thể click trực tiếp để chơi thủ công.",
                        font=("Segoe UI", 10, "italic"), bg="#EDF1F6", fg="#4B5083")
    lbl_sub.pack(pady=(0, 10))

    # Frame containing the canvas
    canvas_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
    canvas_frame.pack(padx=20, pady=10)
    
    # Instantiate animation engine
    engine = WaterJugAnimationEngine(canvas_frame, width=760, height=300, bg="white")
    engine.pack(expand=True, fill="both")
    
    # Configure 8L, 5L, 3L jugs and fill the first jug
    engine.set_config([8, 5, 3], [8, 0, 0])
    engine.set_speed(4) # reasonable speed for demonstration
    
    # Status bar
    lbl_status = tk.Label(root, text="Trạng thái: Bắt đầu demo...", font=("Segoe UI", 10, "bold"), bg="#EDF1F6", fg="#262B63")
    lbl_status.pack(pady=5)
    
    # Override log function to update status label
    engine.on_log = lambda msg: lbl_status.config(text=f"Trạng thái: {msg}")
    
    # Automated Demo Script: Schedule actions using root.after
    # Time offsets are calculated to allow each animation phase to complete before starting the next
    
    # Step 1: Pour A (index 0) -> B (index 1) [8,0,0] -> [3,5,0]
    root.after(1500, lambda: engine.start_pour(0, 1))
    
    # Step 2: Pour B (index 1) -> C (index 2) [3,5,0] -> [3,2,3]
    root.after(6000, lambda: engine.start_pour(1, 2))
    
    # Step 3: Empty C (index 2) [3,2,3] -> [3,2,0]
    root.after(10500, lambda: engine.start_empty(2))
    
    # Step 4: Pour B (index 1) -> C (index 2) [3,2,0] -> [3,0,2]
    root.after(14000, lambda: engine.start_pour(1, 2))
    
    # Step 5: Fill A (index 0) [3,0,2] -> [8,0,2]
    root.after(18500, lambda: engine.start_fill(0))

    root.mainloop()

if __name__ == "__main__":
    main()