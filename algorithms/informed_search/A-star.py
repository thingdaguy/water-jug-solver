# A-star.py
import heapq
from models.state import State
from algorithms.informed_search.Heuristic import heuristic_estimate

def a_star_search(start_state: State, target: int, heuristic_fn=heuristic_estimate):
    counter = 0
    start_g = 0
    start_h = heuristic_fn(start_state, target)
    start_f = start_g + start_h
    # Frontier lưu: (f_cost, counter, g_cost, current_state)
    frontier = []
    heapq.heappush(frontier, (start_f, counter, start_g, start_state))
    
    parent_map = {start_state: (None, "Bắt đầu")}
    best_g = {start_state: start_g}
    visited = set()
    expanded_count = 0
    while frontier:
        f, _, g, current_state = heapq.heappop(frontier)
        if current_state in visited:
            continue
        visited.add(current_state)
        expanded_count += 1
        if current_state.is_goal(target):
            # Dựng lại đường đi
            path = []
            curr = current_state
            while curr is not None:
                prev, action = parent_map[curr]
                path.append((curr, action))
                curr = prev
            path.reverse()
            
            frontier_states = set(item[3] for item in frontier if item[3] not in visited)
            return path, expanded_count, visited, frontier_states, parent_map
        for next_state, action in current_state.get_successors():
            next_g = g + 1
            if next_g < best_g.get(next_state, float('inf')):
                best_g[next_state] = next_g
                parent_map[next_state] = (current_state, action)
                next_h = heuristic_fn(next_state, target)
                next_f = next_g + next_h
                counter += 1
                heapq.heappush(frontier, (next_f, counter, next_g, next_state))

    frontier_states = set(item[3] for item in frontier if item[3] not in visited)
    return None, expanded_count, visited, frontier_states, parent_map
