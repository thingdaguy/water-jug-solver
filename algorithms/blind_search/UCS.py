# algorithms/blind_search/UCS.py
import heapq
from models.state import State

def ucs_search(start_state: State, target: int):
 
    # Frontier: hàng đợi ưu tiên lưu trữ các phần tử dạng (g_cost, counter, current_state)
    counter = 0
    start_g = 0
    frontier = []
    heapq.heappush(frontier, (start_g, counter, start_state))
    
    parent_map = {start_state: (None, "Bắt đầu")}
    visited_states = set()
    expanded_count = 0
    while frontier:
        g, _, current_state = heapq.heappop(frontier)
        if current_state in visited_states:
            continue
        visited_states.add(current_state)
        expanded_count += 1
        if current_state.is_goal(target):
            # Dựng lại đường đi (path)
            path = []
            curr = current_state
            while curr is not None:
                prev, action = parent_map[curr]
                path.append((curr, action))
                curr = prev
            path.reverse() 
            # Các trạng thái còn lại trong frontier chưa được mở rộng
            frontier_states = set(item[2] for item in frontier if item[2] not in visited_states)
            return path, expanded_count, visited_states, frontier_states, parent_map
        for next_state, action in current_state.get_successors():
            # Lượng nước thay đổi        
            max_difference = 0
            for i in range(len(current_state.jugs)):
                current_amount = current_state.jugs[i]
                next_amount = next_state.jugs[i]

                difference = abs(next_amount - current_amount)

                if difference > max_difference:
                    max_difference = difference

            next_g = g + max_difference 
            
            if next_state not in visited_states:
                # Kiểm tra xem có cần cập nhật parent_map không
                if next_state not in parent_map:
                    parent_map[next_state] = (current_state, action)
                    counter += 1
                    heapq.heappush(frontier, (next_g, counter, next_state))

    # Nếu không tìm thấy đường đi
    frontier_states = set(item[2] for item in frontier if item[2] not in visited_states)
    return None, expanded_count, visited_states, frontier_states, parent_map
