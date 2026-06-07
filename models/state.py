
class State:
    def __init__(self, jugs, capacities):
        """
        Biểu diễn trạng thái của các bình nước thuần túy.
        
        Tham số:
        - jugs: tuple các số nguyên, lượng nước hiện tại trong mỗi bình (ví dụ: (a, b, c)).
        - capacities: tuple các số nguyên, dung tích tối đa của mỗi bình (ví dụ: (C_A, C_B, C_C)).
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

    def is_goal(self, target):
        """
        Kiểm tra xem có bình nào chứa lượng nước bằng lượng nước đích hay không.
        """
        return target in self.jugs

    def get_successors(self):
        """
        Sinh ra tất cả các trạng thái kế tiếp hợp lệ từ trạng thái hiện tại.
        Trả về danh sách các cặp (State, mô_tả_hành_động).
        """
        # Import cục bộ để tránh circular import (operations.py import State từ state.py)
        from models.operations import fill_jug, empty_jug, pour_jug

        successors = []
        num_jugs = len(self.jugs)

        # 1. Thao tác đổ đầy các bình
        for idx in range(num_jugs):
            result = fill_jug(self, idx)
            if result:
                new_state, action = result
                successors.append((new_state, action))

        # 2. Thao tác xả rỗng các bình
        for idx in range(num_jugs):
            result = empty_jug(self, idx)
            if result:
                new_state, action = result
                successors.append((new_state, action))

        # 3. Thao tác rót nước qua lại giữa các bình
        for from_idx in range(num_jugs):
            for to_idx in range(num_jugs):
                if from_idx != to_idx:
                    result = pour_jug(self, from_idx, to_idx)
                    if result:
                        new_state, action = result
                        successors.append((new_state, action))

        return successors

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.jugs == other.jugs

    def __hash__(self):
        return hash(self.jugs)

    def __repr__(self):
        return f"State(jugs={self.jugs})"
