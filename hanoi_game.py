import random

class TowerOfHanoi:
    def __init__(self, num_disks=3):
        self.num_disks = num_disks
        self.reset()
    
    def reset(self):
        self.towers = [[], [], []]
        self.towers[0] = list(range(self.num_disks, 0, -1))
        
    def randomize(self):
        self.towers = [[], [], []]
        disks = list(range(self.num_disks, 0, -1))
        available_towers = [0, 1, 2]
        empty_tower = random.choice(available_towers)
        available_towers.remove(empty_tower)
        
        for disk in disks:
            tower = random.choice(available_towers)
            if not self.towers[tower] or self.towers[tower][-1] > disk:
                self.towers[tower].append(disk)
            else:
                other_tower = available_towers[0] if tower == available_towers[1] else available_towers[1]
                if not self.towers[other_tower] or self.towers[other_tower][-1] > disk:
                    self.towers[other_tower].append(disk)
    
    def is_valid_move(self, from_tower, to_tower):
        if not self.towers[from_tower]:
            return False
        if not self.towers[to_tower] or self.towers[from_tower][-1] < self.towers[to_tower][-1]:
            return True
        return False
    
    def move(self, from_tower, to_tower):
        if self.is_valid_move(from_tower, to_tower):
            disk = self.towers[from_tower].pop()
            self.towers[to_tower].append(disk)
            return True
        return False
    
    def is_goal_state(self):
        return len(self.towers[2]) == self.num_disks
    
    def get_state(self):
        return (tuple(self.towers[0]), tuple(self.towers[1]), tuple(self.towers[2]))
    
    def set_state(self, state):
        self.towers[0] = list(state[0])
        self.towers[1] = list(state[1])
        self.towers[2] = list(state[2])
    
    def get_valid_moves(self):
        valid_moves = []
        for from_tower in range(3):
            for to_tower in range(3):
                if from_tower != to_tower and self.is_valid_move(from_tower, to_tower):
                    valid_moves.append((from_tower, to_tower))
        return valid_moves
    
    def copy(self):
        new_hanoi = TowerOfHanoi(self.num_disks)
        new_hanoi.towers = [tower.copy() for tower in self.towers]
        return new_hanoi