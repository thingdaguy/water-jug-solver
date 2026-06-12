from models.state import State

def dfs_search(start_state: State, target: int):
  
    if start_state.is_goal(target):
        parent_map = {start_state: (None, "Bắt đầu")}
        return [(start_state, "Bắt đầu")], 0, {start_state}, set(), parent_map

    stack = [start_state]
    enqueued = {start_state}
    expanded = set()
    parent = {start_state: (None, "Bắt đầu")}

    while stack:
        current = stack.pop()
        expanded.add(current)

        if current.is_goal(target):
            path = []
            curr = current
            while curr is not None:
                prev, action = parent[curr]
                path.append((curr, action))
                curr = prev
            path.reverse()
            return path, len(expanded), expanded, set(stack), parent

        for next_state, action in reversed(current.get_successors()):
            if next_state not in enqueued:
                enqueued.add(next_state)
                parent[next_state] = (current, action)
                stack.append(next_state)

    return None, len(expanded), expanded, set(stack), parent
