# Water Jug Problem Solver

Dự án này giải quyết bài toán đong nước (Water Jug Problem) kinh điển bằng ngôn ngữ Python, áp dụng các thuật toán tìm kiếm trí tuệ nhân tạo (AI) cơ bản: BFS, DFS, UCS, Greedy và A\*.

## 🌟 Các Thuật Toán Trọng Tâm

- **Breadth-First Search (BFS):** Tìm kiếm theo chiều rộng. Đảm bảo tìm được đường đi (số bước) ngắn nhất.
- **Depth-First Search (DFS):** Tìm kiếm theo chiều sâu. Nhanh nhưng không đảm bảo nghiệm tìm được là ngắn nhất.
- **Uniform Cost Search (UCS):** Tìm kiếm với chi phí đồng nhất. Trong bài toán này, nếu mỗi thao tác đổ nước tính phí bằng nhau (1 đơn vị), UCS hoạt động tương tự BFS.
- **Greedy Search:** Tìm kiếm tham lam, lựa chọn bước đi tiếp theo có vẻ gần đích nhất dựa trên hàm ước lượng heuristic.
- **A\* Search (A-Star):** Kết hợp giữa chi phí thực tế đã đi và hàm heuristic ước lượng. Thuật toán tối ưu và phổ biến nhất để tìm đường đi ngắn nhất.

## 📦 Thư Viện Gợi Ý

Bạn có thể xây dựng toàn bộ dự án bằng các thư viện chuẩn (Standard Library) của Python mà không cần cài thêm package bên ngoài:

- `collections.deque`: Dành cho cấu trúc dữ liệu Queue (sử dụng trong BFS).
- `heapq`: Dành cho Priority Queue (sử dụng trong UCS, Greedy và A\*).
- `typing`: Dùng để type hinting giúp code tường minh hơn.

Nếu muốn mở rộng, bạn có thể cân nhắc:

- **Trực quan hóa đồ thị**: `networkx`, `matplotlib` (để vẽ biểu đồ không gian trạng thái).
- **Giao diện người dùng (UI)**: `streamlit`, `gradio` (web UI nhanh), hoặc `tkinter`, `PyQt` (Desktop App).

## 📂 Kiến Trúc Hệ Thống Đề Xuất

Kiến trúc dự án được tổ chức theo module, giúp dễ dàng bảo trì và mở rộng khi muốn thêm thuật toán mới.

```text
water-jug-solver/
│
├── algorithms/           # Chứa logic của từng thuật toán tìm kiếm
│   ├── __init__.py
│   ├── bfs.py
│   ├── dfs.py
│   ├── ucs.py
│   ├── greedy.py
│   └── a_star.py
│
├── core/                 # Chứa các class cốt lõi cấu thành bài toán
│   ├── __init__.py
│   ├── state.py          # Định nghĩa đối tượng Trạng thái (VD: lượng nước hiện tại ở 2 bình)
│   └── problem.py        # Định nghĩa bài toán (Hàm sinh trạng thái kế tiếp, kiểm tra đích)
│
├── utils/                # Các tiện ích hỗ trợ
│   ├── __init__.py
│   └── heuristics.py     # Định nghĩa các hàm heuristic dùng cho Greedy và A*
│
├── main.py               # File chạy chính của chương trình
├── requirements.txt      # Chứa danh sách các thư viện ngoài (nếu có sử dụng)
└── README.md             # File tài liệu hướng dẫn (chính là file này)
```

## 🚀 Hướng Dẫn Sử Dụng (Demo)

### 1. Cài đặt

Clone dự án về máy:

```bash
git clone https://github.com/your-username/water-jug-solver.git
cd water-jug-solver
```

_(Nếu có sử dụng thư viện ngoài, chạy `pip install -r requirements.txt`)_

### 2. Ví dụ chạy chương trình

Cấu trúc cơ bản trong file `main.py` của bạn có thể sẽ như sau:

```python
from core.problem import WaterJugProblem
from algorithms.a_star import a_star_search
from algorithms.bfs import bfs_search

# Khởi tạo bài toán: Bình 1 dung tích 4L, Bình 2 dung tích 3L. Cần đong chính xác 2L.
problem = WaterJugProblem(capacity_x=4, capacity_y=3, target=2)

print("--- Giải bằng thuật toán A* ---")
path_a_star = a_star_search(problem)

if path_a_star:
    print(f"Đã tìm thấy cách giải trong {len(path_a_star) - 1} bước!")
    for step, state in enumerate(path_a_star):
        print(f"Bước {step}: Bình 1 có {state.x}L, Bình 2 có {state.y}L  | Hành động: {state.action}")
else:
    print("Không tồn tại cách đong nước thỏa mãn!")

# Tương tự, bạn có thể thử với BFS
# path_bfs = bfs_search(problem)
```

### 3. Thực thi

Chạy lệnh sau trong terminal:

```bash
python main.py
```
