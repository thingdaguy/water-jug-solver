class State:
    def __init__(self, jugs, capacities):
        """
        jugs: tuple chứa lượng nước hiện tại của các bình, ví dụ: (x1, x2, x3)
        capacities: tuple chứa dung tích tối đa của các bình, ví dụ: (C1, C2, C3)
        """
        self.jugs = tuple(jugs)
        self.capacities = tuple(capacities)

    def is_goal(self, target):
        """
        Kiểm tra xem có ít nhất một bình chứa đúng lượng nước mục tiêu (target) hay không.
        """
        return any(x == target for x in self.jugs)

    def get_successors(self):
        """
        Sinh ra tất cả các trạng thái kế tiếp hợp lệ và mô tả hành động dẫn đến chúng.
        Trả về một danh sách các tuple: (trạng_thái_tiếp_theo, mô_tả_hành_động)
        """
        successors = []
        n = len(self.jugs)

        # 1. Đổ đầy nước vào một bình từ nguồn nước vô hạn
        for i in range(n):
            if self.jugs[i] < self.capacities[i]:
                new_jugs = list(self.jugs)
                new_jugs[i] = self.capacities[i]
                successors.append((State(new_jugs, self.capacities), f"Đổ đầy bình {i+1}"))

        # 2. Đổ hết nước trong một bình ra ngoài
        for i in range(n):
            if self.jugs[i] > 0:
                new_jugs = list(self.jugs)
                new_jugs[i] = 0
                successors.append((State(new_jugs, self.capacities), f"Đổ hết nước bình {i+1}"))

        # 3. Rót nước từ bình i sang bình j
        for i in range(n):
            for j in range(n):
                if i != j and self.jugs[i] > 0 and self.jugs[j] < self.capacities[j]:
                    amount = min(self.jugs[i], self.capacities[j] - self.jugs[j])
                    if amount > 0:
                        new_jugs = list(self.jugs)
                        new_jugs[i] -= amount
                        new_jugs[j] += amount
                        successors.append((State(new_jugs, self.capacities), f"Rót từ bình {i+1} sang bình {j+1}"))

        return successors

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.jugs == other.jugs

    def __hash__(self):
        return hash(self.jugs)

    def __repr__(self):
        return str(self.jugs)
