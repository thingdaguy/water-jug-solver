from models.state import State

def get_jug_name(idx):
    """Lấy tên bình theo chỉ số: 0 → A, 1 → B, 2 → C, ..."""
    if idx < 26:
        return chr(ord('A') + idx)
    return str(idx + 1)

def fill_jug(state, jug_idx):
    """
    Đổ đầy bình jug_idx đến dung tích tối đa.
    Trả về (State mới, mô_tả_hành_động) hoặc None nếu bình đã đầy.
    """
    if state.jugs[jug_idx] == state.capacities[jug_idx]:
        return None
    new_jugs = list(state.jugs)
    new_jugs[jug_idx] = state.capacities[jug_idx]
    action_str = f"Đổ đầy bình {get_jug_name(jug_idx)}"
    return State(new_jugs, state.capacities), action_str

def empty_jug(state, jug_idx):
    """
    Xả rỗng bình jug_idx.
    Trả về (State mới, mô_tả_hành_động) hoặc None nếu bình đã rỗng.
    """
    if state.jugs[jug_idx] == 0:
        return None
    new_jugs = list(state.jugs)
    new_jugs[jug_idx] = 0
    action_str = f"Xả rỗng bình {get_jug_name(jug_idx)}"
    return State(new_jugs, state.capacities), action_str

def pour_jug(state, from_idx, to_idx):
    """
    Rót nước từ bình from_idx sang bình to_idx cho đến khi
    bình nguồn hết hoặc bình đích đầy.
    Trả về (State mới, mô_tả_hành_động) hoặc None nếu không thể rót.
    """
    if from_idx == to_idx or state.jugs[from_idx] == 0 or state.jugs[to_idx] == state.capacities[to_idx]:
        return None
    pour_amount = min(state.jugs[from_idx], state.capacities[to_idx] - state.jugs[to_idx])
    if pour_amount == 0:
        return None
    new_jugs = list(state.jugs)
    new_jugs[from_idx] -= pour_amount
    new_jugs[to_idx] += pour_amount
    action_str = f"Rót {pour_amount}L từ bình {get_jug_name(from_idx)} sang bình {get_jug_name(to_idx)}"
    return State(new_jugs, state.capacities), action_str