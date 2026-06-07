# test_informed_search.py
import sys
import os
import importlib

# Thêm thư mục gốc vào đường dẫn hệ thống để import models và algorithms
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from models.state import State
from algorithms.informed_search.Greedy import greedy_search

# Load động module "A-star.py" do chứa ký tự gạch ngang trong tên file
a_star_module = importlib.import_module("algorithms.informed_search.A-star")
a_star_search = a_star_module.a_star_search

def print_solution(path, expanded_count, algorithm_name):
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

    # 1. Tìm kiếm Tham lam (Greedy Best-First Search)
    greedy_path, greedy_expanded = greedy_search(start_state, target)
    print_solution(greedy_path, greedy_expanded, "Tìm kiếm Tham lam (Greedy Best-First)")

    # 2. Tìm kiếm A*
    astar_path, astar_expanded = a_star_search(start_state, target)
    print_solution(astar_path, astar_expanded, "Tìm kiếm A*")

    # 3. Bảng so sánh tổng hợp
    print(f"\n{'='*15} BẢNG SO SÁNH TỔNG HỢP {'='*15}")
    print(f"{'Thuật toán':<40} | {'Số bước (Chi phí)':<20} | {'Trạng thái đã mở rộng':<25}")
    print(f"{'-'*40}-+-{'-'*20}-+-{'-'*25}")
    
    greedy_steps = len(greedy_path) - 1 if greedy_path else "Không có"
    astar_steps = len(astar_path) - 1 if astar_path else "Không có"
    
    print(f"{'Tìm kiếm Tham lam (Greedy Best-First)':<40} | {greedy_steps:<20} | {greedy_expanded:<25}")
    print(f"{'Tìm kiếm A*':<40} | {astar_steps:<20} | {astar_expanded:<25}")
    print("=" * 91)

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
