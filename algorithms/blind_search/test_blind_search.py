import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from models.state import State
from algorithms.blind_search.BFS import bfs_search
from algorithms.blind_search.DFS import dfs_search

def print_solution(path, expanded_count, algorithm_name):
    """In kết quả tìm kiếm ra màn hình."""
    print(f"\n{'='*20} {algorithm_name} {'='*20}")
    if path is None:
        print("Không tìm thấy lời giải!")
        print(f"Số trạng thái đã mở rộng: {expanded_count}")
        return

    print(f"Đường đi đến đích (Tổng số bước: {len(path) - 1}):")
    for step, (state, action) in enumerate(path):
        print(f"  Bước {step:02d}: {state}  <-  [{action}]")
    print(f"Số trạng thái đã mở rộng: {expanded_count}")

def run_tests(capacities, target):
    print(f"\nĐang chạy kiểm thử với dung tích = {capacities} và mục tiêu = {target}")
    start_state = State((0, 0, 0), capacities)

    # 1. Tìm kiếm theo chiều rộng (BFS)
    bfs_path, bfs_expanded = bfs_search(start_state, target)
    print_solution(bfs_path, bfs_expanded, "Tìm kiếm theo chiều rộng (BFS)")

    # 2. Tìm kiếm theo chiều sâu (DFS)
    dfs_path, dfs_expanded = dfs_search(start_state, target)
    print_solution(dfs_path, dfs_expanded, "Tìm kiếm theo chiều sâu (DFS)")

    # 3. Bảng so sánh tổng hợp
    print(f"\n{'='*15} BẢNG SO SÁNH TỔNG HỢP {'='*15}")
    print(f"{'Thuật toán':<35} | {'Số bước (Chi phí)':<20} | {'Trạng thái đã mở rộng':<25}")
    print(f"{'-'*35}-+-{'-'*20}-+-{'-'*25}")

    bfs_steps = len(bfs_path) - 1 if bfs_path else "Không có"
    dfs_steps = len(dfs_path) - 1 if dfs_path else "Không có"

    print(f"{'BFS (Tìm kiếm theo chiều rộng)':<35} | {str(bfs_steps):<20} | {bfs_expanded:<25}")
    print(f"{'DFS (Tìm kiếm theo chiều sâu)':<35} | {str(dfs_steps):<20} | {dfs_expanded:<25}")
    print("=" * 86)

if __name__ == "__main__":
    print("BÀI TOÁN ĐONG NƯỚC - 3 BÌNH (WATER JUG SOLVER)")
    print("---------------------------------------------")

    # Cho phép người dùng nhập dữ liệu tùy chỉnh hoặc sử dụng mặc định
    choice = input("Bạn có muốn nhập dung tích và mục tiêu tùy chỉnh không? (y/n): ").strip().lower()
    if choice == 'y':
        try:
            c1 = int(input("Nhập dung tích bình 1: ").strip())
            c2 = int(input("Nhập dung tích bình 2: ").strip())
            c3 = int(input("Nhập dung tích bình 3: ").strip())

            if c1 > 10 or c2 > 10 or c3 > 10:
                print("Lỗi: Dung tích tối đa của mỗi bình không được vượt quá 10 lít!")
                raise ValueError("Dung tích vượt quá giới hạn")

            target = int(input("Nhập lượng nước mục tiêu: ").strip())
            run_tests((c1, c2, c3), target)
        except ValueError:
            print("Nhập sai định dạng hoặc vượt quá dung tích tối đa! Chạy với trường hợp mặc định: dung tích=(8, 5, 3), mục tiêu=4")
            run_tests((8, 5, 3), 4)
    else:
        run_tests((8, 5, 3), 4)
