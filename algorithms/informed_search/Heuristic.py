# Heuristic.py
from models.state import State

def heuristic_diff(state: State, target: int) -> int:
    """
    Hàm khoảng cách hiệu: Khoảng cách ngắn nhất từ lượng nước hiện tại của các bình tới target.
    """
    if state.is_goal(target):
        return 0
    return min(abs(w - target) for w in state.jugs)

def heuristic_estimate(state: State, target: int) -> int:
    """
    Hàm mục tiêu ước lượng (Nhìn trước một bước):
    - Trả về 0 nếu bản thân trạng thái hiện tại đã là trạng thái đích.
    - Trả về 1 nếu có thể đạt đến trạng thái đích sau đúng 1 bước đổ/rót/chứa nước.
    - Trả về 2 cho các trường hợp còn lại.
    """
    if state.is_goal(target):
        return 0

    # Kiểm tra xem có trạng thái kế tiếp nào đạt đích hay không
    for successor, _ in state.get_successors():
        if successor.is_goal(target):
            return 1

    return 2

# Mặc định để đảm bảo tương thích ngược
def heuristic(state: State, target: int) -> int:
    return heuristic_estimate(state, target)
