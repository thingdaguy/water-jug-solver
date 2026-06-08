import tkinter as tk
import math
from constants import ui_settings


class ZoomPanCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", "#F9FAFB")
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)

        self.bind("<ButtonPress-1>", self.start_pan)
        self.bind("<B1-Motion>", self.pan)
        self.bind("<MouseWheel>", self.zoom)
        self.bind("<Button-4>", self.zoom_up)
        self.bind("<Button-5>", self.zoom_down)

        self.zoom_level = 1.0
        self._base_bbox = None

    def start_pan(self, event):
        self.scan_mark(event.x, event.y)

    def pan(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event):
        factor = 1.15 if event.delta > 0 else 0.85
        self.apply_zoom(factor, event.x, event.y)

    def zoom_up(self, event):
        self.apply_zoom(1.15, event.x, event.y)

    def zoom_down(self, event):
        self.apply_zoom(0.85, event.x, event.y)

    def apply_zoom(self, factor, x, y):
        if 0.15 < self.zoom_level * factor < 8.0:
            self.zoom_level *= factor
            cx = self.canvasx(x)
            cy = self.canvasy(y)
            self.scale("all", cx, cy, factor, factor)
            self.configure(scrollregion=self.bbox("all"))

    def reset_transform(self):
        self.zoom_level = 1.0
        if self._base_bbox:
            self.configure(scrollregion=self._base_bbox)


def draw_mini_cups(canvas, cx, cy, state, tag, cup_w=14, cup_gap=4, max_h=36):
    """Vẽ 3 cốc thu nhỏ đại diện cho một trạng thái."""
    capacities = state.capacities
    levels = state.jugs
    max_cap = max(capacities) if capacities else 1
    names = ["A", "B", "C"]

    total_w = 3 * cup_w + 2 * cup_gap
    start_x = cx - total_w / 2
    base_y = cy + max_h / 2

    for i in range(3):
        cup_x = start_x + i * (cup_w + cup_gap)
        cap = capacities[i]
        lvl = levels[i]
        ch = max_h * (cap / max_cap) if max_cap > 0 else max_h
        cup_top = base_y - ch
        water_ratio = (lvl / cap) if cap > 0 else 0.0
        water_h = ch * water_ratio

        cup_coords = [cup_x, cup_top, cup_x, base_y, cup_x + cup_w, base_y, cup_x + cup_w, cup_top]
        canvas.create_line(
            cup_coords, fill=ui_settings.COLOR_DARK, width=2,
            capstyle="round", joinstyle="miter", tags=tag
        )

        if water_h > 0.5:
            water_top = base_y - water_h
            canvas.create_rectangle(
                cup_x + 1, water_top, cup_x + cup_w - 1, base_y - 1,
                fill="#3A86FF", outline="", tags=tag
            )

        label_y = base_y + 10
        canvas.create_text(
            cup_x + cup_w / 2, label_y, text=names[i],
            font=("Segoe UI", 6, "bold"), fill=ui_settings.COLOR_MUTED, tags=tag
        )
        canvas.create_text(
            cup_x + cup_w / 2, label_y + 9, text=str(lvl),
            font=("Segoe UI", 6), fill=ui_settings.COLOR_DARK, tags=tag
        )


class GraphWindow(tk.Toplevel):
    NODE_W = 72
    NODE_H = 58

    def __init__(self, parent, start_state, parent_map, path, visited_states, frontier_states, algo_name, target):
        super().__init__(parent)
        self.title(f"State Space Graph - {algo_name}")
        self.geometry("1000x700")
        self.configure(bg=ui_settings.BG_MAIN)
        self.transient(parent)

        self.start_state = start_state
        self.parent_map = parent_map
        self.target = target
        self.path_states = set(state for state, _ in path) if path else set()
        self.visited_states = visited_states
        self.frontier_states = frontier_states
        self.node_positions = {}
        self.node_map = {}
        self.node_outlines = {}

        self.create_toolbar()
        self.create_canvas_area()
        self.create_legend_panel(algo_name, len(visited_states), len(path) - 1 if path else 0)

        self.layout_and_draw()
        self.after(100, self.fit_to_screen)

    def create_toolbar(self):
        tb = tk.Frame(self, bg=ui_settings.BG_MAIN, pady=5)
        tb.pack(fill="x", padx=15)

        tk.Label(
            tb, text="CÂY TÌM KIẾM KHÔNG GIAN TRẠNG THÁI",
            font=("Segoe UI", 12, "bold"), bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_DARK
        ).pack(side="left", padx=5)

        tk.Button(
            tb, text="Đóng", font=ui_settings.FONT_TEXT, bg="#E74C3C", fg="white",
            bd=0, padx=10, cursor="hand2", command=self.destroy
        ).pack(side="right", padx=5)

        tk.Button(
            tb, text="Khớp màn hình", font=ui_settings.FONT_TEXT, bg=ui_settings.BTN_PRIMARY,
            fg="white", bd=0, padx=10, cursor="hand2", command=self.fit_to_screen
        ).pack(side="right", padx=5)

        tk.Button(
            tb, text="Zoom Out (-)", font=ui_settings.FONT_TEXT, bg=ui_settings.BG_PANEL,
            fg=ui_settings.COLOR_DARK, bd=1, padx=10, cursor="hand2",
            command=lambda: self.canvas.apply_zoom(0.85, 500, 350)
        ).pack(side="right", padx=5)

        tk.Button(
            tb, text="Zoom In (+)", font=ui_settings.FONT_TEXT, bg=ui_settings.BG_PANEL,
            fg=ui_settings.COLOR_DARK, bd=1, padx=10, cursor="hand2",
            command=lambda: self.canvas.apply_zoom(1.15, 500, 350)
        ).pack(side="right", padx=5)

    def create_canvas_area(self):
        self.canvas_frame = tk.Frame(self, bg=ui_settings.BG_PANEL, bd=1, relief="solid")
        self.canvas_frame.pack(expand=True, fill="both", padx=15, pady=(5, 10))

        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient="horizontal")
        self.h_scroll.pack(side="bottom", fill="x")
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient="vertical")
        self.v_scroll.pack(side="right", fill="y")

        self.canvas = ZoomPanCanvas(
            self.canvas_frame,
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        self.canvas.pack(expand=True, fill="both")
        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)

    def create_legend_panel(self, algo_name, explored, steps):
        legend_frame = tk.Frame(self, bg=ui_settings.BG_PANEL, bd=1, relief="solid")
        legend_frame.pack(fill="x", padx=15, pady=(0, 5))

        tk.Label(
            legend_frame,
            text=f"Thuật toán: {algo_name}  |  Đã mở rộng: {explored}  |  Đường đi: {steps} bước",
            font=("Segoe UI", 10, "bold"), bg=ui_settings.BG_PANEL, fg=ui_settings.COLOR_DARK
        ).pack(side="left", padx=15, pady=10)

        colors_container = tk.Frame(legend_frame, bg=ui_settings.BG_PANEL)
        colors_container.pack(side="right", padx=15, pady=10)

        for name, bg_color, fg_color in [
            ("Solution Path", "#2ECC71", "white"),
            ("Visited (Expanded)", "#00B894", "white"),
            ("Frontier (Queue/Stack)", "#F4A261", "black"),
            ("Unexplored", "#E8ECF0", "black"),
        ]:
            f = tk.Frame(colors_container, bg=bg_color, padx=8, pady=3, bd=1, relief="ridge")
            f.pack(side="left", padx=4)
            tk.Label(f, text=name, bg=bg_color, fg=fg_color, font=("Segoe UI", 8, "bold")).pack()

        self.status_lbl = tk.Label(
            self,
            text="Rê chuột vào nút trạng thái để xem chi tiết  |  Kéo để cuộn  |  Cuộn chuột để zoom",
            font=("Segoe UI", 9, "italic"), bg=ui_settings.BG_MAIN, fg=ui_settings.COLOR_MUTED
        )
        self.status_lbl.pack(fill="x", side="bottom", pady=(0, 5))

    def _node_color(self, state):
        if state in self.path_states:
            return "#2ECC71"
        if state in self.visited_states:
            return "#D6E4FF"
        if state in self.frontier_states:
            return "#F4A261"
        return "#E8ECF0"

    def _node_outline(self, state):
        if state == self.start_state:
            return "#E74C3C", 3
        if state.is_goal(self.target):
            return "#FFD700", 3.5
        return ui_settings.COLOR_DARK, 1.5

    def layout_and_draw(self):
        adj = {}
        for child, (parent, _) in self.parent_map.items():
            if parent is not None:
                adj.setdefault(parent, []).append(child)

        level_spacing = 130
        node_spacing = 100
        positions = {}
        leaf_x = 0

        def setup_coords(node, depth=0):
            nonlocal leaf_x
            children = adj.get(node, [])
            y = depth * level_spacing

            if not children:
                x = leaf_x
                leaf_x += node_spacing
                positions[node] = (x, y)
                return x

            child_xs = [setup_coords(child, depth + 1) for child in children]
            x = sum(child_xs) / len(child_xs)
            positions[node] = (x, y)
            return x

        setup_coords(self.start_state)
        self.node_positions = positions

        half_w = self.NODE_W / 2
        half_h = self.NODE_H / 2

        for child, (parent, action) in self.parent_map.items():
            if parent is None:
                continue
            px, py = positions[parent]
            cx, cy = positions[child]
            dx = cx - px
            dy = cy - py
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > 0:
                sx = px + half_h * (dx / dist)
                sy = py + half_h * (dy / dist)
                ex = cx - half_h * (dx / dist)
                ey = cy - half_h * (dy / dist)
            else:
                sx, sy, ex, ey = px, py, cx, cy

            self.canvas.create_line(
                sx, sy, ex, ey, fill="#8085B8", width=2,
                arrow=tk.LAST, arrowshape=(8, 10, 3), smooth=True
            )

            simple_action = self._simplify_action(action)
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            self.canvas.create_text(
                mx, my - 10, text=simple_action,
                font=("Segoe UI", 7, "bold"), fill=ui_settings.COLOR_MUTED
            )

        node_idx = 0
        for state, (x, y) in positions.items():
            node_idx += 1
            tag_name = f"node_{node_idx}"
            color = self._node_color(state)
            outline, width = self._node_outline(state)

            self.canvas.create_rectangle(
                x - half_w, y - half_h, x + half_w, y + half_h,
                fill=color, outline=outline, width=width, tags=("node", tag_name)
            )
            draw_mini_cups(self.canvas, x, y - 4, state, ("node", tag_name))

            if state == self.start_state:
                self.canvas.create_text(x, y - half_h - 10, text="START", font=("Segoe UI", 8, "bold"), fill="#E74C3C")
            elif state.is_goal(self.target):
                self.canvas.create_text(x, y + half_h + 12, text="GOAL", font=("Segoe UI", 8, "bold"), fill="#FF9F43")

            state_str = ",".join(map(str, state.jugs))
            parent_info = self.parent_map.get(state)
            action_str = parent_info[1] if parent_info else "Bắt đầu"
            parent_state = parent_info[0] if parent_info else None
            parent_str = ",".join(map(str, parent_state.jugs)) if parent_state else "None"
            status_text = f"Trạng thái: ({state_str}) | Hành động: {action_str} | Cha: ({parent_str})"

            for item_id in self.canvas.find_withtag(tag_name):
                self.node_map[item_id] = status_text
            self.node_outlines[tag_name] = (outline, width)

        self.canvas.tag_bind("node", "<Enter>", self.on_node_enter)
        self.canvas.tag_bind("node", "<Leave>", self.on_node_leave)

        bbox = self.canvas.bbox("all")
        if bbox:
            pad = 60
            self.canvas._base_bbox = (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
            self.canvas.configure(scrollregion=self.canvas._base_bbox)

    def _simplify_action(self, action):
        if "Đổ đầy bình" in action:
            return "Fill " + action[-1]
        if "Xả rỗng bình" in action:
            return "Empty " + action[-1]
        if "Rót" in action:
            parts = action.split()
            try:
                return f"{parts[5]}➔{parts[8]}"
            except IndexError:
                pass
        return action

    def on_node_enter(self, event):
        item = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))[0]
        info = self.node_map.get(item, "")
        if info:
            self.status_lbl.config(text=info, fg=ui_settings.COLOR_DARK, font=("Segoe UI", 9, "bold"))
            tags = self.canvas.gettags(item)
            node_tag = next((t for t in tags if t.startswith("node_")), None)
            if node_tag:
                rect = [x for x in self.canvas.find_withtag(node_tag) if self.canvas.type(x) == "rectangle"]
                if rect:
                    self.canvas.itemconfig(rect[0], width=4)

    def on_node_leave(self, event):
        self.status_lbl.config(
            text="Rê chuột vào nút trạng thái để xem chi tiết  |  Kéo để cuộn  |  Cuộn chuột để zoom",
            fg=ui_settings.COLOR_MUTED, font=("Segoe UI", 9, "italic")
        )
        item = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))[0]
        tags = self.canvas.gettags(item)
        node_tag = next((t for t in tags if t.startswith("node_")), None)
        if node_tag and node_tag in self.node_outlines:
            outline, width = self.node_outlines[node_tag]
            rect = [x for x in self.canvas.find_withtag(node_tag) if self.canvas.type(x) == "rectangle"]
            if rect:
                self.canvas.itemconfig(rect[0], outline=outline, width=width)

    def fit_to_screen(self):
        self.canvas.delete("all")
        self.node_map.clear()
        self.node_outlines.clear()
        self.canvas.zoom_level = 1.0
        self.layout_and_draw()
        self.canvas.update_idletasks()

        bbox = self.canvas.bbox("all")
        if not bbox:
            return

        x1, y1, x2, y2 = bbox
        w_width = max(self.canvas.winfo_width(), 850)
        w_height = max(self.canvas.winfo_height(), 450)
        bbox_w = x2 - x1
        bbox_h = y2 - y1
        if bbox_w == 0 or bbox_h == 0:
            return

        factor = min((w_width - 80) / bbox_w, (w_height - 80) / bbox_h, 1.0)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        self.canvas.scale("all", cx, cy, factor, factor)
        new_bbox = self.canvas.bbox("all")
        if new_bbox:
            ncx = (new_bbox[0] + new_bbox[2]) / 2
            ncy = (new_bbox[1] + new_bbox[3]) / 2
            self.canvas.move("all", w_width / 2 - ncx, w_height / 2 - ncy)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.zoom_level = factor
