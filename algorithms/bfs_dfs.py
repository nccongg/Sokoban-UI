import time
from collections import deque
import tracemalloc  # Import tracemalloc for memory tracking
import csv
from datetime import datetime

# Utility Functions

def get_state_string(grid):
    return ''.join(''.join(row) for row in grid)

def is_solved(state_string, goals, box_ids):
    # Puzzle is solved when all goals have boxes on them
    for pos in goals:
        idx = pos[0] * width + pos[1]
        if state_string[idx] not in box_ids:
            return False
    return True

def is_box(cell, box_ids):
    return cell in box_ids

def is_wall(cell):
    return cell == '#'

def can_move(state_string, pos, move, box_ids, goals):
    x, y = pos
    dx, dy = move
    target_x, target_y = x + dx, y + dy
    boxtarget_x, boxtarget_y = x + 2 * dx, y + 2 * dy

    # Check bounds for target position
    if not (0 <= target_x < height and 0 <= target_y < width):
        return None

    idx_current = x * width + y
    idx_target = target_x * width + target_y

    target_cell = state_string[idx_target]

    if is_wall(target_cell):  # Wall
        return None

    new_state = list(state_string)
    player_on_goal = pos in goals

    # If target is empty space or goal
    if not is_box(target_cell, box_ids) and not is_wall(target_cell):
        # Update current position
        new_state[idx_current] = '.' if player_on_goal else ' '
        # Update target position
        new_state[idx_target] = '+' if (target_x, target_y) in goals else '@'
        return ''.join(new_state), (target_x, target_y), False, 0  # False indicates no push, weight 0
    # If target is a box
    elif is_box(target_cell, box_ids):
        # Check bounds for box target position
        if not (0 <= boxtarget_x < height and 0 <= boxtarget_y < width):
            return None
        idx_boxtarget = boxtarget_x * width + boxtarget_y
        boxtarget_cell = state_string[idx_boxtarget]

        if is_wall(boxtarget_cell) or is_box(boxtarget_cell, box_ids):  # Wall or another box
            return None
        box_id = target_cell
        # Move the box
        # Update box target position
        new_state[idx_boxtarget] = box_id
        # Update box current position
        new_state[idx_target] = '+' if (target_x, target_y) in goals else '@'
        # Update player current position
        new_state[idx_current] = '.' if player_on_goal else ' '
        return ''.join(new_state), (target_x, target_y), True, box_ids[box_id]  # True indicates a push, return box weight
    else:
        return None

# BFS Algorithm

def bfs(initial_state_string, player_pos, box_ids, goals):
    seen = set()
    q = deque([(initial_state_string, player_pos, 0, '', 0)])
    nodes_explored = 0  # Initialize node counter
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    direction = {
        (-1, 0): 'U',  # Up
        (1, 0): 'D',   # Down
        (0, -1): 'L',  # Left
        (0, 1): 'R',   # Right
    }
    while q:
        state_string, pos, depth, path, total_weight = q.popleft()
        nodes_explored += 1  # Increment node counter
        state_key = (state_string, pos)
        if state_key in seen:
            continue
        seen.add(state_key)
        for move in moves:
            result = can_move(state_string, pos, move, box_ids, goals)
            if result is None:
                continue
            new_state_string, new_pos, pushed, weight = result
            new_total_weight = total_weight + weight
            move_char = direction[move].upper() if pushed else direction[move].lower()
            new_path = path + move_char
            if is_solved(new_state_string, goals, box_ids):
                return new_path, depth + 1, nodes_explored, new_total_weight
            q.append((new_state_string, new_pos, depth + 1, new_path, new_total_weight))
    return None, -1, nodes_explored, 0

# DFS Algorithm

def dfs(initial_state_string, player_pos, box_ids, goals):
    seen = set()
    stack = [(initial_state_string, player_pos, 0, '', 0)]
    nodes_explored = 0  # Initialize node counter
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    direction = {
        (-1, 0): 'U',  # Up
        (1, 0): 'D',   # Down
        (0, -1): 'L',  # Left
        (0, 1): 'R',   # Right
    }
    while stack:
        state_string, pos, depth, path, total_weight = stack.pop()
        nodes_explored += 1  # Increment node counter
        state_key = (state_string, pos)
        if state_key in seen:
            continue
        seen.add(state_key)
        for move in moves:
            result = can_move(state_string, pos, move, box_ids, goals)
            if result is None:
                continue
            new_state_string, new_pos, pushed, weight = result
            new_total_weight = total_weight + weight
            move_char = direction[move].upper() if pushed else direction[move].lower()
            new_path = path + move_char
            if is_solved(new_state_string, goals, box_ids):
                return new_path, depth + 1, nodes_explored, new_total_weight
            stack.append((new_state_string, new_pos, depth + 1, new_path, new_total_weight))
    return None, -1, nodes_explored, 0

def solve_algorithm(grid, box_ids, goals, algorithm='bfs'):
    global height, width
    height = len(grid)
    width = len(grid[0])
    initial_state_string = get_state_string(grid)
    # Find player position
    player_found = False
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == '@':
                player_pos = (i, j)
                player_found = True
                break  # Breaks out of inner loop
        if player_found:
            break  # Breaks out of outer loop
    if not player_found:
        print("No player found in the puzzle.")
        return None, -1, 0, 0, 0, 0
    # Start tracing memory allocations
    tracemalloc.start()
    solution, depth, nodes_explored, total_weight = None, -1, 0, 0
    # Solve the puzzle using the specified algorithm
    start_time = time.time()
    if algorithm == 'bfs':
        solution, depth, nodes_explored, total_weight = bfs(initial_state_string, player_pos, box_ids, goals)
    elif algorithm == 'dfs':
        solution, depth, nodes_explored, total_weight =  dfs(initial_state_string, player_pos, box_ids, goals)
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
                elif cell == '@':
                    new_row.append('@')
                else:
                    new_row.append(cell)
            grid.append(new_row)
        max_length = max(len(row) for row in grid)
        for row in grid:
            row.extend([' '] * (max_length - len(row)))
    return weights, grid, box_ids, goals

def solveDFS(input_file, output_file, csv_file):
    weights, grid, box_ids, goals = read_input_file(input_file)
    solution, depth, nodes_explored, time_ms, memory, total_weight = solve_algorithm(grid, box_ids, goals, 'dfs')
    algorithm_name = "DFS"
    fields = ['Algorithm', 'Steps', 'Total Weight', 'Nodes Explored', 'Time (ms)', 'Memory (MB)']

    if solution:
        data = [algorithm_name, depth, total_weight, nodes_explored, f"{time_ms:.2f}", f"{memory:.4f}", 'Yes', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    else:
        data = [algorithm_name, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

    with open(output_file, 'a') as f:
        if solution:
            f.write("DFS\n")
            f.write(f'Steps: {depth}, Weight: {total_weight}, Node: {nodes_explored}, Time (ms): {time_ms:.2f}, Memory (MB): {memory:.4f}\n')
            f.write(f'{solution}\n')
        else:
            f.write("DFS\nNo solution found.\n")

    with open(csv_file, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        if file.tell() == 0:
            csv_writer.writerow(fields)
        csv_writer.writerow(data)

def solveBFS(input_file, output_file, csv_file):
    weights, grid, box_ids, goals = read_input_file(input_file)
    solution, depth, nodes_explored, time_ms, memory, total_weight = solve_algorithm(grid, box_ids, goals, 'bfs')
    algorithm_name = "BFS"
    fields = ['Algorithm', 'Steps', 'Total Weight', 'Nodes Explored', 'Time (ms)', 'Memory (MB)']

    if solution:
        data = [algorithm_name, depth, total_weight, nodes_explored, f"{time_ms:.2f}", f"{memory:.4f}"]
    else:
        data = [algorithm_name, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

    with open(output_file, 'a') as f:
        if solution:
            f.write("BFS\n")
            f.write(f'Steps: {depth}, Weight: {total_weight}, Node: {nodes_explored}, Time (ms): {time_ms:.2f}, Memory (MB): {memory:.4f}\n')
            f.write(f'{solution}\n')
        else:
            f.write("BFS\nNo solution found.\n")

    with open(csv_file, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        if file.tell() == 0:
            csv_writer.writerow(fields)
        csv_writer.writerow(data)

# if __name__ == '__main__':
#     if len(sys.argv) != 3:
#         print("Usage: python Search.py <input_file> <output_file>")
#         sys.exit(1)
        
#     solveBFS(sys.argv[1], sys.argv[2])
#     solveDFS(sys.argv[1], sys.argv[2])
