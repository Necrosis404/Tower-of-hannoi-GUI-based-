import time
from collections import deque
from hanoi_game import TowerOfHanoi

class EnhancedHanoiSearch:
    def __init__(self, initial_state, on_state_change=None, on_search_complete=None):
        self.initial_state = initial_state
        self.pause_search = False
        self.on_state_change = on_state_change
        self.on_search_complete = on_search_complete
        self.search_stats = {
            "nodes_explored": 0,
            "states_visited": 0,
            "max_queue_size": 0,
            "success": False,
            "search_time": 0,
            "path_length": 0
        }
    
    def bfs(self):
        start_time = time.time()
        start_state = self.initial_state.get_state()
        queue = deque([(start_state, [])])
        visited = {start_state}
        
        while queue and not self.pause_search:
            self.search_stats["nodes_explored"] += 1
            current_state, path = queue.popleft()
            game = TowerOfHanoi(self.initial_state.num_disks)
            game.set_state(current_state)
            
            if self.on_state_change:
                self.on_state_change(game, "Exploring", path)
            
            if game.is_goal_state():
                self.search_stats["success"] = True
                self.search_stats["search_time"] = time.time() - start_time
                self.search_stats["path_length"] = len(path)
                if self.on_search_complete:
                    self.on_search_complete(True, path, self.search_stats)
                return path
            
            for move in game.get_valid_moves():
                game_copy = game.copy()
                game_copy.move(move[0], move[1])
                new_state = game_copy.get_state()
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [move]))
            
            self.search_stats["states_visited"] = len(visited)
            self.search_stats["max_queue_size"] = max(self.search_stats["max_queue_size"], len(queue))
        
        self.search_stats["search_time"] = time.time() - start_time
        if self.on_search_complete:
            self.on_search_complete(False, [], self.search_stats)
        return None if self.pause_search else []

    def dfs(self):
        start_time = time.time()
        start_state = self.initial_state.get_state()
        stack = [(start_state, [])]
        visited = {start_state}
        
        while stack and not self.pause_search:
            self.search_stats["nodes_explored"] += 1
            current_state, path = stack.pop()
            game = TowerOfHanoi(self.initial_state.num_disks)
            game.set_state(current_state)
            
            if self.on_state_change:
                self.on_state_change(game, "Exploring", path)
            
            if game.is_goal_state():
                self.search_stats["success"] = True
                self.search_stats["search_time"] = time.time() - start_time
                self.search_stats["path_length"] = len(path)
                if self.on_search_complete:
                    self.on_search_complete(True, path, self.search_stats)
                return path
            
            for move in reversed(game.get_valid_moves()):
                game_copy = game.copy()
                game_copy.move(move[0], move[1])
                new_state = game_copy.get_state()
                if new_state not in visited:
                    visited.add(new_state)
                    stack.append((new_state, path + [move]))
            
            self.search_stats["states_visited"] = len(visited)
            self.search_stats["max_queue_size"] = max(self.search_stats["max_queue_size"], len(stack))
        
        self.search_stats["search_time"] = time.time() - start_time
        if self.on_search_complete:
            self.on_search_complete(False, [], self.search_stats)
        return None if self.pause_search else []

    def bidirectional(self):
        start_time = time.time()
        start_state = self.initial_state.get_state()
        goal_state = (tuple(), tuple(), tuple(range(self.initial_state.num_disks, 0, -1)))
        
        forward_queue = deque([(start_state, [])])
        backward_queue = deque([(goal_state, [])])
        forward_visited = {start_state: []}
        backward_visited = {goal_state: []}
        
        while forward_queue and backward_queue and not self.pause_search:
            self.search_stats["nodes_explored"] += 1
            
            current_state, path = forward_queue.popleft()
            game = TowerOfHanoi(self.initial_state.num_disks)
            game.set_state(current_state)
            
            if self.on_state_change:
                self.on_state_change(game, "Exploring Forward", path)
            
            if current_state in backward_visited:
                self.search_stats["success"] = True
                self.search_stats["search_time"] = time.time() - start_time
                full_path = path + list(reversed(backward_visited[current_state]))
                self.search_stats["path_length"] = len(full_path)
                if self.on_search_complete:
                    self.on_search_complete(True, full_path, self.search_stats)
                return full_path
            
            for move in game.get_valid_moves():
                game_copy = game.copy()
                game_copy.move(move[0], move[1])
                new_state = game_copy.get_state()
                if new_state not in forward_visited:
                    forward_visited[new_state] = path + [move]
                    forward_queue.append((new_state, path + [move]))
            
            current_state, path = backward_queue.popleft()
            game.set_state(current_state)
            
            if self.on_state_change:
                self.on_state_change(game, "Exploring Backward", path)
            
            if current_state in forward_visited:
                self.search_stats["success"] = True
                self.search_stats["search_time"] = time.time() - start_time
                full_path = forward_visited[current_state] + list(reversed(path))
                self.search_stats["path_length"] = len(full_path)
                if self.on_search_complete:
                    self.on_search_complete(True, full_path, self.search_stats)
                return full_path
            
            for move in game.get_valid_moves():
                game_copy = game.copy()
                game_copy.move(move[0], move[1])
                new_state = game_copy.get_state()
                if new_state not in backward_visited:
                    backward_visited[new_state] = path + [move]
                    backward_queue.append((new_state, path + [move]))
            
            self.search_stats["states_visited"] = len(forward_visited) + len(backward_visited)
            self.search_stats["max_queue_size"] = max(self.search_stats["max_queue_size"], 
                                                    len(forward_queue) + len(backward_queue))
        
        self.search_stats["search_time"] = time.time() - start_time
        if self.on_search_complete:
            self.on_search_complete(False, [], self.search_stats)
        return None if self.pause_search else []