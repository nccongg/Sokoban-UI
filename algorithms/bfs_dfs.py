import time
from collections import deque
import numpy as np
import sys
import tracemalloc  # Import tracemalloc for memory tracking

# Utility Functions

def print_state(state, shape):
    if not state.any():
        return
    m, n = shape
    for row in state:
        print(''.join(row))

def get_state(matrix):
    return ''.join(''.join(row) for row in matrix)

def is_solved(state, goals, box_ids):
    # Puzzle is solved when all goals have boxes on them
    for (x, y) in goals:
        if not is_box(state[x, y], box_ids):
            return False
    return True

def is_box(cell, box_ids):
    return cell in box_ids.keys()

def is_wall(cell):
    return cell == '#'

def can_move(state, shape, player_pos, move, box_ids, goals):
    x, y = player_pos
    height, width = shape
    dx, dy = move
    target = x + dx, y + dy
    boxtarget = x + 2 * dx, y + 2 * dy

    # Check bounds for target position
    if not (0 <= target[0] < height and 0 <= target[1] < width):
        return None

    target_cell = state[target]

    if is_wall(target_cell):  # Wall
        return None

    new_state = np.copy(state)
    player_on_goal = (x, y) in goals

    # If target is empty space or goal
    if not is_box(target_cell, box_ids):
        # Update current position
        new_state[x, y] = '.' if player_on_goal else ' '
        # Update target position
        new_state[target] = '+' if target in goals else '@'
        return new_state, target, False, 0  # False indicates no push, weight 0
    # If target is a box
    elif is_box(target_cell, box_ids):
        # Check bounds for box target position
        if not (0 <= boxtarget[0] < height and 0 <= boxtarget[1] < width):
            return None
        boxtarget_cell = state[boxtarget]

        if is_wall(boxtarget_cell) or is_box(boxtarget_cell, box_ids):  # Wall or another box
            return None
        box_id = target_cell
        # Move the box
        # Update box target position
        new_state[boxtarget] = box_id
        # Update box current position
        new_state[target] = '+' if target in goals else '@'
        # Update player current position
        new_state[x, y] = '.' if player_on_goal else ' '
        return new_state, target, True, box_ids[box_id]  # True indicates a push, return box weight
    else:
        return None

# BFS Algorithm

def bfs(matrix, player_pos, box_ids, goals):
    initial_state = matrix
    shape = matrix.shape
    seen = set()
    q = deque([(initial_state, player_pos, 0, '', 0)])
    nodes_explored = 0  # Initialize node counter
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    direction = {
        (-1, 0): 'U',  # Up
        (1, 0): 'D',   # Down
        (0, -1): 'L',  # Left
        (0, 1): 'R',   # Right
    }
    height, width = shape
    while q:
        state, pos, depth, path, total_weight = q.popleft()
        nodes_explored += 1  # Increment node counter
        state_key = (tuple(map(tuple, state)), pos)
        if state_key in seen:
            continue
        seen.add(state_key)
        for move in moves:
            result = can_move(state, shape, pos, move, box_ids, goals)
            if result is None:
                continue
            new_state, new_pos, pushed, weight = result
            new_total_weight = total_weight + weight
            move_char = direction[move].upper() if pushed else direction[move].lower()
            new_path = path + move_char
            if is_solved(new_state, goals, box_ids):
                return new_path, depth + 1, nodes_explored, new_total_weight
            q.append((new_state, new_pos, depth + 1, new_path, new_total_weight))
    return None, -1, nodes_explored, 0

# DFS Algorithm

def dfs(matrix, player_pos, box_ids, goals):
    initial_state = matrix
    shape = matrix.shape
    seen = set()
    stack = [(initial_state, player_pos, 0, '', 0)]
    nodes_explored = 0  # Initialize node counter
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    direction = {
        (-1, 0): 'U',  # Up
        (1, 0): 'D',   # Down
        (0, -1): 'L',  # Left
        (0, 1): 'R',   # Right
    }
    height, width = shape
    while stack:
        state, pos, depth, path, total_weight = stack.pop()
        nodes_explored += 1  # Increment node counter
        state_key = (tuple(map(tuple, state)), pos)
        if state_key in seen:
            continue
        seen.add(state_key)
        for move in moves:
            result = can_move(state, shape, pos, move, box_ids, goals)
            if result is None:
                continue
            new_state, new_pos, pushed, weight = result
            new_total_weight = total_weight + weight
            move_char = direction[move].upper() if pushed else direction[move].lower()
            new_path = path + move_char
            if is_solved(new_state, goals, box_ids):
                return new_path, depth + 1, nodes_explored, new_total_weight
            stack.append((new_state, new_pos, depth + 1, new_path, new_total_weight))
    return None, -1, nodes_explored, 0

def solve_algorithm(puzzle, box_ids, goals, algorithm='bfs'):
    matrix = puzzle
    where = np.where((matrix == '@') | (matrix == '+'))
    if len(where[0]) == 0:
        print("No player found in the puzzle.")
        return None, -1, 0, 0, 0, 0
    player_pos = where[0][0], where[1][0]
    # Start tracing memory allocations
    tracemalloc.start()
    solution, depth, nodes_explored, total_weight = None, -1, 0, 0
    # Solve the puzzle using the specified algorithm
    start_time = time.time()
    if algorithm == 'bfs':
        solution, depth, nodes_explored, total_weight = bfs(matrix, player_pos, box_ids, goals)
    elif algorithm == 'dfs':
        solution, depth, nodes_explored, total_weight =  dfs(matrix, player_pos, box_ids, goals)
    else:
        print(f"Unknown algorithm: {algorithm}")
    end_time = time.time()

    # Get memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return solution, depth, nodes_explored, (end_time - start_time) * 1000, peak / (1024 * 1024), total_weight

def read_input_file(filename):
    with open(filename, 'r') as file:
        first_line = file.readline().strip()
        weights = list(map(int, first_line.split()))
    
        grid = []
        box_id = 1
        box_ids = {}
        goals = set()
        for row_idx, line in enumerate(file):
            row = list(line.rstrip('\n'))
            new_row = []
            for col_idx, cell in enumerate(row):
                if cell in ('$','*'):
                    # Assign ID to box
                    box_char = str(box_id)
                    box_ids[box_char] = weights[box_id - 1]  # Assuming weights are in order
                    box_id += 1
                    # Replace cell with box ID
                    new_row.append(box_char)
                    if cell == '*':
                        goals.add((row_idx, col_idx))
                elif cell == '.':
                    goals.add((row_idx, col_idx))
                    new_row.append(' ')
                elif cell == '+':
                    # Player on goal
                    new_row.append('@')
                    goals.add((row_idx, col_idx))
                else:
                    new_row.append(cell)
            grid.append(new_row)
    
        max_length = max(len(row) for row in grid)
    
        for row in grid:
            row.extend([' '] * (max_length - len(row)))
    
    return weights, grid, box_ids, goals

def solveDFS(input_file, output_file):
    weights, level, box_ids, goals = read_input_file(input_file)
    matrix = np.array(level)
    solution, depth, nodes_explored, time_ms, memory, total_weight = solve_algorithm(matrix, box_ids, goals, 'dfs')
    with open(output_file, 'a') as f:
        if solution:
            f.write("DFS\n")
            f.write(f'Steps: {depth}, Weight: {total_weight}, Nodes: {nodes_explored}, Time (ms): {time_ms :.2f}, Memory (MB): {memory:.4f}\n')
            f.write(f'{solution}\n')
        else:
            f.write("No solution found.\n")

def solveBFS(input_file, output_file):
    weights, level, box_ids, goals = read_input_file(input_file)
    matrix = np.array(level)
    solution, depth, nodes_explored, time_ms, memory, total_weight = solve_algorithm(matrix, box_ids, goals, 'bfs')
    with open(output_file, 'a') as f:
        if solution:
            f.write("BFS\n")
            f.write(f'Steps: {depth}, Weight: {total_weight}, Nodes: {nodes_explored}, Time (ms): {time_ms :.2f}, Memory (MB): {memory:.4f}\n')
            f.write(f'{solution}\n')
        else:
            f.write("No solution found.\n")

# if __name__ == '__main__':
#     if len(sys.argv) != 3:
#         print("Usage: python Search.py <input_file> <output_file>")
#         sys.exit(1)
        
#     solveBFS(sys.argv[1], sys.argv[2])
