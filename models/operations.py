from models.state import State

def get_jug_name(idx):
    """
    Lấy tên của bình nước dựa trên chỉ số (0 -> A, 1 -> B, 2 -> C,...).
    """
    if idx < 26:
        return chr(ord('A') + idx)
    return f"{idx + 1}"

def fill_jug(state, jug_idx):
    """
    Đổ đầy bình nước tại vị trí jug_idx đến dung tích tối đa.
    Trả về một đối tượng State mới, hoặc None nếu thao tác không hợp lệ (bình đã đầy).
    """
    if state.jugs[jug_idx] == state.capacities[jug_idx]:
        return None
        
    new_jugs = list(state.jugs)
    new_jugs[jug_idx] = state.capacities[jug_idx]
    
    action_str = f"Đổ đầy bình {get_jug_name(jug_idx)}"
    return State(new_jugs, state.capacities, parent=state, action=action_str, cost=state.g + 1)

def empty_jug(state, jug_idx):
    """
    Xả rỗng hoàn toàn bình nước tại vị trí jug_idx.
    Trả về một đối tượng State mới, hoặc None nếu thao tác không hợp lệ (bình đã rỗng sẵn).
    """
    if state.jugs[jug_idx] == 0:
        return None
        
    new_jugs = list(state.jugs)
    new_jugs[jug_idx] = 0
    
    action_str = f"Xả rỗng bình {get_jug_name(jug_idx)}"
    return State(new_jugs, state.capacities, parent=state, action=action_str, cost=state.g + 1)

def pour_jug(state, from_idx, to_idx):
    """
    Rót nước từ bình from_idx sang bình to_idx cho đến khi bình from_idx hết nước
    hoặc bình to_idx đầy.
    Trả về một đối tượng State mới, hoặc None nếu thao tác không hợp lệ.
    """
    if from_idx == to_idx:
        return None
    if state.jugs[from_idx] == 0:
        return None
    if state.jugs[to_idx] == state.capacities[to_idx]:
        return None
        
    # Tính toán lượng nước thực tế rót được
    pour_amount = min(state.jugs[from_idx], state.capacities[to_idx] - state.jugs[to_idx])
    if pour_amount == 0:
        return None
        
    new_jugs = list(state.jugs)
    new_jugs[from_idx] -= pour_amount
    new_jugs[to_idx] += pour_amount
    
    action_str = f"Rót {pour_amount} lít từ bình {get_jug_name(from_idx)} sang bình {get_jug_name(to_idx)}"
    return State(new_jugs, state.capacities, parent=state, action=action_str, cost=state.g + 1)

def get_successors(state):
    """
    Sinh ra tất cả các trạng thái kế tiếp hợp lệ từ trạng thái hiện tại.
    Trả về một danh sách các đối tượng State.
    """
    successors = []
    num_jugs = len(state.jugs)
    
    # 1. Thao tác đổ đầy các bình
    for idx in range(num_jugs):
        new_state = fill_jug(state, idx)
        if new_state:
            successors.append(new_state)
            
    # 2. Thao tác xả rỗng các bình
    for idx in range(num_jugs):
        new_state = empty_jug(state, idx)
        if new_state:
            successors.append(new_state)
            
    # 3. Thao tác rót nước qua lại giữa các bình
    for from_idx in range(num_jugs):
        for to_idx in range(num_jugs):
            if from_idx != to_idx:
                new_state = pour_jug(state, from_idx, to_idx)
                if new_state:
                    successors.append(new_state)
                    
    return successors
