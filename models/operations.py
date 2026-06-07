# operations.py
# Các phép toán được định nghĩa làm luật chuyển trạng thái trong models/state.py.
# File này có thể dùng cho các hàm tiện ích bổ sung hoặc chạy phép toán riêng lẻ.

def fill_jug(jugs, capacities, i):
    new_jugs = list(jugs)
    new_jugs[i] = capacities[i]
    return tuple(new_jugs)

def empty_jug(jugs, i):
    new_jugs = list(jugs)
    new_jugs[i] = 0
    return tuple(new_jugs)

def pour_jug(jugs, capacities, i, j):
    new_jugs = list(jugs)
    amount = min(jugs[i], capacities[j] - jugs[j])
    new_jugs[i] -= amount
    new_jugs[j] += amount
    return tuple(new_jugs)
