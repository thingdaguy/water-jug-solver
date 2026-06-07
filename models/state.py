class State:
    def __init__(self, jugs, capacities, parent=None, action=None, cost=0):
        """
        Biểu diễn trạng thái của các bình nước.
        
        Tham số:
        - jugs: tuple các số nguyên, lượng nước hiện tại trong mỗi bình (ví dụ: (a, b, c)).
        - capacities: tuple các số nguyên, dung tích tối đa của mỗi bình (ví dụ: (C_A, C_B, C_C)).
        - parent: State, trạng thái trước đó dẫn đến trạng thái này.
        - action: str, mô tả hành động đã thực hiện để đạt đến trạng thái này.
        - cost: int, chi phí để đạt đến trạng thái này (g(n)).
        """
                # Kiểm tra tính hợp lệ của dữ liệu đầu vào
        if len(jugs) != len(capacities):
            raise ValueError("Số lượng bình trong jugs và capacities phải khớp nhau.")
        for i, (w, cap) in enumerate(zip(jugs, capacities)):
            if cap <= 0:
                raise ValueError(f"Dung tích bình tại vị trí {i} phải lớn hơn 0.")
            if w < 0:
                raise ValueError(f"Lượng nước trong bình tại vị trí {i} không được nhỏ hơn 0.")
            if w > cap:
                raise ValueError(f"Lượng nước trong bình tại vị trí {i} ({w}L) vượt quá dung tích tối đa ({cap}L).")

        self.jugs = tuple(jugs)
        self.capacities = tuple(capacities)
        self.parent = parent
        self.action = action
        self.g = cost  # Chi phí đường đi g(n)
        self.h = 0     # Giá trị Heuristic h(n)
        self.f = self.g + self.h     # f(n) = g(n) + h(n)

    def is_goal(self, target):
        """
        Kiểm tra xem có bình nào chứa lượng nước bằng lượng nước đích hay không.
        """
        return target in self.jugs

    def get_path(self):
        """
        Truy vết đường đi từ trạng thái bắt đầu đến trạng thái hiện tại.
        Trả về một danh sách các đối tượng State.
        """
        path = []
        current = self
        while current is not None:
            path.append(current)
            current = current.parent
        return path[::-1]
    
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

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.jugs == other.jugs

    def __hash__(self):
        return hash(self.jugs)

    def __repr__(self):
        return f"State(jugs={self.jugs}, action='{self.action}', g={self.g}, h={self.h})"
