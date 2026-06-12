# components/animation/engine.py
import tkinter as tk
import math
from constants import ui_settings

class WaterJugAnimationEngine(tk.Canvas):
    def __init__(self, parent, on_log=None, on_state_changed=None, **kwargs):
        # Set default dimensions and styling
        kwargs.setdefault("width", 700)
        kwargs.setdefault("height", 320)
        kwargs.setdefault("bg", "#FFFFFF")
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)
        
        self.on_log = on_log
        self.on_state_changed = on_state_changed
        
        # State vectors
        self.capacities = [8, 5, 3]
        self.levels = [8, 0, 0]
        
        # UI Coordinates & layout parameters
        self.cup_w = 100
        self.base_y = 240
        self.centers = [175, 350, 525]
        self.base_x = [c - self.cup_w / 2 for c in self.centers]
        
        # Selected jug for interactive manual play
        self.selected_jug = None
        
        # Speed setting (from 1 to 10)
        self.simulation_speed = 5
        
        # Animation state variables
        self.is_animating = False
        self.anim_type = None      # "pour", "fill", "empty"
        self.anim_src = None
        self.anim_dest = None
        
        self.anim_phase = 0
        self.anim_x = 0.0
        self.anim_y = 0.0
        self.anim_angle = 0.0
        self.anim_pour_progress = 0.0
        
        # Starting levels for interpolation
        self.lvl_src_start = 0.0
        self.lvl_src_end = 0.0
        self.lvl_dest_start = 0.0
        self.lvl_dest_end = 0.0
        
        # Cho phép tắt tương tác thủ công khi AI đang chạy lời giải
        self.interactive = True

        # Bind mouse click for interactive play
        self.bind("<Button-1>", self.on_canvas_click)
        
        # Bind resize event to handle dynamic positioning & center alignment
        self.bind("<Configure>", self.on_resize)
        
        # Draw initial state
        self.redraw()

    def set_interactive(self, enabled):
        """Bật/tắt điều khiển thủ công (click cốc, fill/empty)."""
        self.interactive = enabled
        if not enabled:
            self.selected_jug = None
            self.redraw()

    def set_config(self, capacities, initial_levels=None):
        """Configure capacities and levels of the 3 jugs."""
        if self.is_animating:
            return
        
        self.capacities = list(capacities)
        if initial_levels is not None:
            self.levels = list(initial_levels)
        else:
            # Default: Fill the first jug completely, others empty
            self.levels = [self.capacities[0]] + [0] * (len(self.capacities) - 1)
            
        # Ensure levels don't exceed capacities
        for i in range(len(self.levels)):
            self.levels[i] = min(self.levels[i], self.capacities[i])
            
        self.selected_jug = None
        self.redraw()
        if self.on_state_changed:
            self.on_state_changed(self.levels)

    def set_speed(self, speed):
        """Set the simulation speed (1 to 10)."""
        self.simulation_speed = speed

    def on_resize(self, event):
        """Called when the canvas is resized to update centers and redraw."""
        # Update base_y relative to canvas height
        self.base_y = event.height - 80
        
        # Recalculate centers to be exactly at 1/6, 3/6, 5/6 of the canvas width
        self.centers = [event.width * (2 * i + 1) / 6 for i in range(3)]
        self.base_x = [c - self.cup_w / 2 for c in self.centers]
        self.redraw()

    def get_cup_heights(self):
        """Calculate dynamic cup heights based on capacities to look proportional."""
        max_cap = max(self.capacities) if self.capacities else 8
        if max_cap == 0:
            max_cap = 8
        base_height = 80
        height_range = 120
        
        heights = []
        for cap in self.capacities:
            h = base_height + (cap / max_cap) * height_range
            heights.append(h)
        return heights

    def rotate_points(self, local_pts, px, py, deg_angle):
        """Rotates a list of local (x, y) coordinates around pivot point (px, py)."""
        rad = math.radians(deg_angle)
        rotated = []
        for lx, ly in local_pts:
            rx = px + (lx * math.cos(rad) - ly * math.sin(rad))
            ry = py + (lx * math.sin(rad) + ly * math.cos(rad))
            rotated.extend([rx, ry])
        return rotated

    def on_canvas_click(self, event):
        """Handles selecting and pouring between cups interactively."""
        if not self.interactive or self.is_animating:
            return
            
        click_x, click_y = event.x, event.y
        cup_heights = self.get_cup_heights()
        
        clicked_idx = None
        for i in range(3):
            # Define click bounding box
            x0 = self.base_x[i] - 15
            x1 = self.base_x[i] + self.cup_w + 15
            y0 = self.base_y - cup_heights[i] - 20
            y1 = self.base_y + 15
            
            if x0 <= click_x <= x1 and y0 <= click_y <= y1:
                clicked_idx = i
                break
                
        if clicked_idx is None:
            return
            
        # Handle selection logic
        if self.selected_jug is None:
            # Select
            self.selected_jug = clicked_idx
            self.redraw()
            self.log(f"Đã chọn Bình {['A', 'B', 'C'][clicked_idx]} ({self.levels[clicked_idx]}/{self.capacities[clicked_idx]}L). Chọn bình đích để rót nước.")
        elif self.selected_jug == clicked_idx:
            # Deselect
            self.selected_jug = None
            self.redraw()
            self.log("Bỏ chọn bình.")
        else:
            # Try to pour from self.selected_jug to clicked_idx
            src = self.selected_jug
            dest = clicked_idx
            self.selected_jug = None
            self.redraw()
            
            # Check if pour is valid
            if self.levels[src] == 0:
                self.log(f"Không thể rót: Bình {['A', 'B', 'C'][src]} đang rỗng!")
                return
            if self.levels[dest] == self.capacities[dest]:
                self.log(f"Không thể rót: Bình {['A', 'B', 'C'][dest]} đã đầy!")
                return
                
            # Start pour animation
            self.start_pour(src, dest)

    def log(self, msg):
        if self.on_log:
            self.on_log(msg)
        else:
            print(msg)

    # --- ACTION TRIGGERS ---
    def start_pour(self, src, dest):
        if self.is_animating:
            return
            
        amount = min(self.levels[src], self.capacities[dest] - self.levels[dest])
        if amount <= 0:
            self.log("Lượng nước rót không hợp lệ hoặc bằng 0.")
            return
            
        self.is_animating = True
        self.anim_type = "pour"
        self.anim_src = src
        self.anim_dest = dest
        self.anim_phase = 1
        
        self.lvl_src_start = self.levels[src]
        self.lvl_src_end = self.levels[src] - amount
        self.lvl_dest_start = self.levels[dest]
        self.lvl_dest_end = self.levels[dest] + amount
        
        cup_heights = self.get_cup_heights()
        self.anim_x = self.base_x[src]
        self.anim_y = self.base_y - cup_heights[src]
        self.anim_angle = 0.0
        self.anim_pour_progress = 0.0
        
        self.log(f"Đang rót {amount}L nước từ Bình {['A', 'B', 'C'][src]} sang Bình {['A', 'B', 'C'][dest]}...")
        self.tick()

    def start_fill(self, idx):
        if self.is_animating:
            return
            
        if self.levels[idx] == self.capacities[idx]:
            self.log(f"Bình {['A', 'B', 'C'][idx]} đã đầy sẵn!")
            return
            
        self.is_animating = True
        self.anim_type = "fill"
        self.anim_src = idx
        self.anim_phase = 1
        
        self.lvl_src_start = self.levels[idx]
        self.lvl_src_end = self.capacities[idx]
        self.anim_pour_progress = 0.0
        
        self.log(f"Đang làm đầy Bình {['A', 'B', 'C'][idx]} từ vòi nước...")
        self.tick()

    def start_empty(self, idx):
        if self.is_animating:
            return
            
        if self.levels[idx] == 0:
            self.log(f"Bình {['A', 'B', 'C'][idx]} đã rỗng sẵn!")
            return
            
        self.is_animating = True
        self.anim_type = "empty"
        self.anim_src = idx
        self.anim_phase = 1
        
        self.lvl_src_start = self.levels[idx]
        self.lvl_src_end = 0
        self.anim_pour_progress = 0.0
        
        self.log(f"Đang đổ hết nước trong Bình {['A', 'B', 'C'][idx]} ra ngoài...")
        self.tick()

    # --- ANIMATION LOOP ---
    def tick(self):
        if not self.is_animating:
            return
            
        # Speed modifier
        sp = self.simulation_speed
        
        if self.anim_type == "pour":
            src = self.anim_src
            dest = self.anim_dest
            cup_heights = self.get_cup_heights()
            h_src = cup_heights[src]
            h_dest = cup_heights[dest]
            
            # Target positions for pouring alignment
            # Left to Right: align bottom-right of src near top-left of dest
            if src < dest:
                tgt_x = self.base_x[dest] - 15 - self.cup_w
                tgt_y = self.base_y - h_dest - 25 - h_src
            # Right to Left: align bottom-left of src near top-right of dest
            else:
                tgt_x = self.base_x[dest] + self.cup_w + 15
                tgt_y = self.base_y - h_dest - 25 - h_src
                
            # PHASE 1: Lift
            if self.anim_phase == 1:
                target_y = self.base_y - h_src - 70
                if self.anim_y > target_y:
                    self.anim_y -= 4 * sp
                else:
                    self.anim_y = target_y
                    self.anim_phase = 2
                    
            # PHASE 2: Move to destination
            elif self.anim_phase == 2:
                dx = tgt_x - self.anim_x
                dy = tgt_y - self.anim_y
                dist = math.sqrt(dx*dx + dy*dy)
                step = 5 * sp
                if dist > step:
                    self.anim_x += (dx / dist) * step
                    self.anim_y += (dy / dist) * step
                else:
                    self.anim_x = tgt_x
                    self.anim_y = tgt_y
                    self.anim_phase = 3
                    
            # PHASE 3: Tilt
            elif self.anim_phase == 3:
                tgt_angle = 50.0 if src < dest else -50.0
                if abs(self.anim_angle - tgt_angle) > 2 * sp:
                    self.anim_angle += (2 * sp) if src < dest else (-2 * sp)
                else:
                    self.anim_angle = tgt_angle
                    self.anim_phase = 4
                    
            # PHASE 4: Pouring water flow
            elif self.anim_phase == 4:
                if self.anim_pour_progress < 1.0:
                    self.anim_pour_progress += 0.03 * sp
                    if self.anim_pour_progress > 1.0:
                        self.anim_pour_progress = 1.0
                        
                    # Interpolate levels dynamically
                    self.levels[src] = self.lvl_src_start + (self.lvl_src_end - self.lvl_src_start) * self.anim_pour_progress
                    self.levels[dest] = self.lvl_dest_start + (self.lvl_dest_end - self.lvl_dest_start) * self.anim_pour_progress
                else:
                    self.levels[src] = self.lvl_src_end
                    self.levels[dest] = self.lvl_dest_end
                    self.anim_phase = 5
                    
            # PHASE 5: Untilt
            elif self.anim_phase == 5:
                if abs(self.anim_angle) > 2 * sp:
                    self.anim_angle += (-2 * sp) if src < dest else (2 * sp)
                else:
                    self.anim_angle = 0.0
                    self.anim_phase = 6
                    
            # PHASE 6: Return horizontally & vertically to lifted state
            elif self.anim_phase == 6:
                tgt_x = self.base_x[src]
                tgt_y = self.base_y - h_src - 70
                dx = tgt_x - self.anim_x
                dy = tgt_y - self.anim_y
                dist = math.sqrt(dx*dx + dy*dy)
                step = 5 * sp
                if dist > step:
                    self.anim_x += (dx / dist) * step
                    self.anim_y += (dy / dist) * step
                else:
                    self.anim_x = tgt_x
                    self.anim_y = tgt_y
                    self.anim_phase = 7
                    
            # PHASE 7: Lower to starting base
            elif self.anim_phase == 7:
                target_y = self.base_y - h_src
                if self.anim_y < target_y:
                    self.anim_y += 4 * sp
                else:
                    self.anim_y = target_y
                    self.is_animating = False
                    self.anim_type = None
                    self.log(f"Rót nước hoàn tất!")
                    if self.on_state_changed:
                        self.on_state_changed(self.levels)
                        
        elif self.anim_type == "fill":
            src = self.anim_src
            if self.anim_pour_progress < 1.0:
                self.anim_pour_progress += 0.04 * sp
                if self.anim_pour_progress > 1.0:
                    self.anim_pour_progress = 1.0
                self.levels[src] = self.lvl_src_start + (self.lvl_src_end - self.lvl_src_start) * self.anim_pour_progress
            else:
                self.levels[src] = self.lvl_src_end
                self.is_animating = False
                self.anim_type = None
                self.log("Làm đầy hoàn tất!")
                if self.on_state_changed:
                    self.on_state_changed(self.levels)
                    
        elif self.anim_type == "empty":
            src = self.anim_src
            if self.anim_pour_progress < 1.0:
                self.anim_pour_progress += 0.04 * sp
                if self.anim_pour_progress > 1.0:
                    self.anim_pour_progress = 1.0
                self.levels[src] = self.lvl_src_start + (self.lvl_src_end - self.lvl_src_start) * self.anim_pour_progress
            else:
                self.levels[src] = self.lvl_src_end
                self.is_animating = False
                self.anim_type = None
                self.log("Đã làm rỗng bình!")
                if self.on_state_changed:
                    self.on_state_changed(self.levels)
                    
        self.redraw()
        
        # Schedule next tick frame (approx 25ms delay for 40fps)
        self.after(25, self.tick)

    # --- RENDERING ENGINE ---
    def redraw(self):
        """Clears and fully renders the current visual state of the jugs."""
        self.delete("all")
        
        cup_heights = self.get_cup_heights()
        
        # 1. Draw static background grid or target water goal text
        canvas_w = self.winfo_width()
        draw_x = canvas_w / 2 if canvas_w > 1 else 350
        self.create_text(draw_x, 25, text="CHẠM BÌNH ĐỂ LỰA CHỌN & RÓT NƯỚC", 
                         font=("Segoe UI", 10, "italic"), fill=ui_settings.COLOR_ACCENT)
        
        # 2. Render each of the 3 jugs
        for i in range(3):
            # Check if this jug is currently the one animating
            is_moving = (self.is_animating and self.anim_type == "pour" and self.anim_src == i)
            
            # Position of the cup
            cx = self.anim_x if is_moving else self.base_x[i]
            cy = self.anim_y if is_moving else (self.base_y - cup_heights[i])
            ch = cup_heights[i]
            angle = self.anim_angle if is_moving else 0.0
            
            # Water level calculations
            lvl = self.levels[i]
            cap = self.capacities[i]
            water_ratio = (lvl / cap) if cap > 0 else 0.0
            water_h = ch * water_ratio
            
            # Selected highlight
            if self.selected_jug == i and not self.is_animating:
                # Draw a rounded highlight rectangle behind the cup
                self.create_rectangle(cx - 8, cy - 8, cx + self.cup_w + 8, self.base_y + 8,
                                      outline="#FFD700", width=3, dash=(4, 2))
                self.create_text(self.centers[i], cy - 18, text="SELECTED", 
                                 font=("Segoe UI", 8, "bold"), fill="#FF8C00")

            # Pivot selection based on pouring direction
            if is_moving:
                if self.anim_src < self.anim_dest:
                    # Clockwise tilt pivot: bottom-right corner of cup
                    px, py = cx + self.cup_w, cy + ch
                    # Local coords relative to bottom-right
                    local_cup = [(-self.cup_w, -ch), (-self.cup_w, 0), (0, 0), (0, -ch)]
                    local_water = [
                        (-self.cup_w, -water_h + (angle / 50.0) * 20),
                        (0, -water_h - (angle / 50.0) * 20),
                        (0, 0),
                        (-self.cup_w, 0)
                    ]
                else:
                    # Counter-clockwise tilt pivot: bottom-left corner of cup
                    px, py = cx, cy + ch
                    # Local coords relative to bottom-left
                    local_cup = [(0, -ch), (0, 0), (self.cup_w, 0), (self.cup_w, -ch)]
                    local_water = [
                        (0, -water_h + (angle / 50.0) * 20),
                        (self.cup_w, -water_h - (angle / 50.0) * 20),
                        (self.cup_w, 0),
                        (0, 0)
                    ]
                
                cup_coords = self.rotate_points(local_cup, px, py, angle)
                water_coords = self.rotate_points(local_water, px, py, angle)
            else:
                # Stationary cup points
                cup_coords = [cx, cy, cx, cy + ch, cx + self.cup_w, cy + ch, cx + self.cup_w, cy]
                water_coords = [
                    cx + 1, cy + ch - water_h, 
                    cx + self.cup_w - 1, cy + ch - water_h,
                    cx + self.cup_w - 1, cy + ch - 1,
                    cx + 1, cy + ch - 1
                ]
            
            # Draw water polygon
            if water_h > 0.5:
                # Fill color is sleek blue
                self.create_polygon(water_coords, fill="#3A86FF", outline="")
            
            # Draw cup outline (U-shaped, so we draw it as a thick open line)
            # Connecting: top-left -> bottom-left -> bottom-right -> top-right
            self.create_line(cup_coords[0:2] + cup_coords[2:4] + cup_coords[4:6] + cup_coords[6:8], 
                             fill=ui_settings.COLOR_DARK, width=4, capstyle="round", joinstyle="miter")
            
            # Draw cup measurements (graduations / markings) on side
            # This makes the jugs look extremely premium!
            self.draw_graduations(cx, cy, ch, cap, is_moving, angle, i)

            # Draw labels
            label_y = self.base_y + 22
            name_label = f"Bình {['A', 'B', 'C'][i]}"
            info_label = f"{lvl:.1f} / {cap} L" if isinstance(lvl, float) else f"{lvl} / {cap} L"
            
            self.create_text(self.centers[i], label_y, text=name_label, 
                             font=("Segoe UI", 11, "bold"), fill=ui_settings.COLOR_DARK)
            self.create_text(self.centers[i], label_y + 18, text=info_label, 
                             font=("Segoe UI", 10), fill=ui_settings.COLOR_MUTED)

        # 3. Draw Water Streams for Fill/Empty/Pour
        if self.is_animating:
            if self.anim_type == "pour" and self.anim_phase == 4:
                # Calculate rotated pouring lip
                src = self.anim_src
                dest = self.anim_dest
                ch_src = cup_heights[src]
                angle = self.anim_angle
                
                # Bottom-right pivot if src < dest, else bottom-left pivot
                if src < dest:
                    px, py = self.anim_x + self.cup_w, self.anim_y + ch_src
                else:
                    px, py = self.anim_x, self.anim_y + ch_src
                    
                # The pouring lip local coord is always at (0, -ch_src) relative to pivot
                lip_x, lip_y = self.rotate_points([(0, -ch_src)], px, py, angle)
                
                # Target opening of dest cup
                target_x = self.base_x[dest] + self.cup_w / 2
                target_y = self.base_y - cup_heights[dest]
                
                # Draw dynamic pouring stream polygon
                stream_coords = [
                    lip_x - 3, lip_y,
                    lip_x + 3, lip_y,
                    target_x + 6, target_y,
                    target_x - 6, target_y
                ]
                self.create_polygon(stream_coords, fill="#3A86FF", outline="")
                
            elif self.anim_type == "fill":
                # Tap fill stream
                src = self.anim_src
                x = self.base_x[src] + self.cup_w / 2
                water_h = cup_heights[src] * (self.levels[src] / self.capacities[src])
                bottom_y = self.base_y - water_h
                
                # Draw water faucet/tap symbol above
                self.create_rectangle(x - 10, 10, x + 10, 20, fill="#7F8C8D", outline="#7F8C8D")
                self.create_line(x, 20, x, bottom_y, fill="#3A86FF", width=8, capstyle="projecting")
                
            elif self.anim_type == "empty":
                # Drain stream out of the bottom of the cup
                src = self.anim_src
                x = self.base_x[src] + self.cup_w / 2
                self.create_line(x, self.base_y, x, self.base_y + 55, fill="#3A86FF", width=6)

    def draw_graduations(self, cx, cy, ch, cap, is_moving, angle, idx):
        """Draws measurement ticks and markings on the side of the cups."""
        if cap <= 0:
            return
            
        # Draw 4 tick marks (at 25%, 50%, 75% capacity)
        for pct in [0.25, 0.50, 0.75]:
            tick_y_local = -ch * pct
            tick_val = cap * pct
            
            # Local coordinates of the tick mark line: 10px long from left edge
            local_tick = [(0, tick_y_local), (10, tick_y_local)]
            
            if is_moving:
                ch_src = ch
                if idx == self.anim_src:
                    if self.anim_src < self.anim_dest:
                        px, py = cx + self.cup_w, cy + ch_src
                        local_tick_adj = [(lx - self.cup_w, ly) for lx, ly in local_tick]
                    else:
                        px, py = cx, cy + ch_src
                        local_tick_adj = local_tick
                    tick_coords = self.rotate_points(local_tick_adj, px, py, angle)
            else:
                tick_coords = [cx, cy + ch + tick_y_local, cx + 10, cy + ch + tick_y_local]
                
            # Draw tick line
            self.create_line(tick_coords, fill=ui_settings.COLOR_MUTED, width=1.5)
            
            # Draw small tick text next to it
            text_x = tick_coords[2] + 8
            text_y = tick_coords[3]
            tick_text = f"{tick_val:.1f}" if tick_val % 1 != 0 else f"{int(tick_val)}"
            
            # Only draw tick labels for stationary cups to keep it readable, 
            # or draw them along with rotating coordinates. Let's draw for stationary.
            if not is_moving:
                self.create_text(text_x, text_y, text=tick_text, anchor="w", 
                                 font=("Segoe UI", 7), fill=ui_settings.COLOR_MUTED)
