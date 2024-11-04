import time
from collections import deque
import numpy as np
import sys
import tracemalloc  # Import tracemalloc for memory tracking

# Utility Functions

def print_state(state, shape):
    if not state:
        return
    m, n = shape
    matrix = np.array(list(state)).reshape(m, n)
    for row in matrix:
        print(''.join(row))

def get_state(matrix):
    return ''.join(''.join(row) for row in matrix)

def is_solved(state):
    return '$' not in state and '*' in state  # Puzzle is solved when all stones are on goals

def is_deadlock(state, shape):
    # Implement deadlock detection if necessary
    return False  # For simplicity, deadlock detection is not implemented here

def can_move(state, shape, player_pos, move):
    x, y = player_pos
    height, width = shape
    dx, dy = move
    target = x + dx, y + dy
    boxtarget = x + 2 * dx, y + 2 * dy
    curr1d = x * width + y

    # Check bounds for target position
    if not (0 <= target[0] < height and 0 <= target[1] < width):
        return None

    target1d = target[0] * width + target[1]
    target_cell = state[target1d]

    if target_cell == '#':  # Wall
        return None

    new_state = list(state)
    player_on_goal = state[curr1d] == '+'

    # If target is empty space or goal
    if target_cell in ' .':
        # Update current position
        new_state[curr1d] = '.' if player_on_goal else ' '
        # Update target position
        new_state[target1d] = '+' if target_cell == '.' else '@'
        return ''.join(new_state), target, False  # False indicates no push
    # If target is a box
    elif target_cell in '$*':
        # Check bounds for box target position
        if not (0 <= boxtarget[0] < height and 0 <= boxtarget[1] < width):
            return None
        boxtarget1d = boxtarget[0] * width + boxtarget[1]
        boxtarget_cell = state[boxtarget1d]

        if boxtarget_cell in '#$*':  # Wall or another box
            return None
        # Move the box
        # Update box target position
        if boxtarget_cell == '.':
            new_state[boxtarget1d] = '*'
        else:
            new_state[boxtarget1d] = '$'
        # Update box current position
        new_state[target1d] = '+' if target_cell == '*' else '@' if target_cell == '$' else ' '
        # Update player current position
        new_state[curr1d] = '.' if player_on_goal else ' '
        return ''.join(new_state), target, True  # True indicates a push
    else:
        return None

# BFS Algorithm

def bfs(matrix, player_pos):
    initial_state = get_state(matrix)
    shape = matrix.shape
    seen = {initial_state}
    q = deque([(initial_state, player_pos, 0, '')])
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
        state, pos, depth, path = q.popleft()
        nodes_explored += 1  # Increment node counter
        for move in moves:
            result = can_move(state, shape, pos, move)
            if result is None:
                continue
            new_state, new_pos, pushed = result
            if new_state in seen:
                continue
            seen.add(new_state)
            # Append uppercase if pushed, else lowercase
            move_char = direction[move].upper() if pushed else direction[move].lower()
            new_path = path + move_char
            if is_solved(new_state):
                return new_path, depth + 1, nodes_explored
            q.append((new_state, new_pos, depth + 1, new_path))
    return None, -1, nodes_explored

# DFS Algorithm

def dfs(matrix, player_pos):
    initial_state = get_state(matrix)
    shape = matrix.shape
    seen = {initial_state}
    stack = [(initial_state, player_pos, 0, '')]
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
        state, pos, depth, path = stack.pop()
        nodes_explored += 1  # Increment node counter
        for move in moves:
            result = can_move(state, shape, pos, move)
            if result is None:
                continue
            new_state, new_pos, pushed = result
            if new_state in seen:
                continue
            seen.add(new_state)
            # Append uppercase if pushed, else lowercase
            move_char = direction[move].upper() if pushed else direction[move].lower()
            new_path = path + move_char
            if is_solved(new_state):
                return new_path, depth + 1, nodes_explored
            stack.append((new_state, new_pos, depth + 1, new_path))
    return None, -1, nodes_explored

def solve_algorithm(puzzle, algorithm='bfs'):
    matrix = puzzle
    where = np.where((matrix == '@') | (matrix == '+'))
    if len(where[0]) == 0:
        print("No player found in the puzzle.")
        return None, -1, 0
    player_pos = where[0][0], where[1][0]
    if algorithm == 'bfs':
        return bfs(matrix, player_pos)
    elif algorithm == 'dfs':
        return dfs(matrix, player_pos)
    else:
        print(f"Unknown algorithm: {algorithm}")
        return None, -1, 0

def read_input_file(filename):
    with open(filename, 'r') as file:
        first_line = file.readline().strip()
        numbers = list(map(int, first_line.split()))

        grid = []
        for line in file:
            grid.append(list(line)[:-1] if line[-1] == '\n' else list(line))

        max_length = max(len(row) for row in grid)

        for row in grid:
            row.extend([' '] * (max_length - len(row)))

    return numbers, grid

def solveDFS(input_file, output_file):
    _, level = read_input_file(input_file)
    matrix = np.array(level)
    solution, depth, nodes_explored = solve_algorithm(matrix, 'dfs')
    with open(output_file, 'a') as f:
        if solution:
            f.write(f'Steps: {depth}, Weight: 0, Node: {nodes_explored}\n')
            f.write(f'{solution}\n')
        else:
            f.write("No solution found.\n")

def solveBFS(input_file, output_file):
    _, level = read_input_file(input_file)
    matrix = np.array(level)
    solution, depth, nodes_explored = solve_algorithm(matrix, 'bfs')
    with open(output_file, 'a') as f:
        if solution:
            f.write(f'Steps: {depth}, Weight: 0, Node: {nodes_explored}\n')
            f.write(f'{solution}\n')
        else:
            f.write("No solution found.\n")

# if __name__ == '__main__':
#     if len(sys.argv) != 3:
#         print("Usage: python Search.py <input_file> <algorithm>")
#         print("Algorithms: bfs, dfs")
#         sys.exit(1)
        
#     _, level = read_input_file(sys.argv[1])
#     # Convert level to numpy array
#     matrix = np.array(level)
#     algorithm = sys.argv[2]

#     # Start tracing memory allocations
#     tracemalloc.start()

#     # Solve the puzzle using the specified algorithm
#     start_time = time.time()
#     solution, depth, nodes_explored = solve_algorithm(matrix, algorithm)
#     end_time = time.time()

#     # Get memory usage
#     current, peak = tracemalloc.get_traced_memory()
#     tracemalloc.stop()

#     with open('output.txt', 'w') as f:
#         if algorithm == 'bfs':
#             f.write('Breadth-First Search\n')
#         elif algorithm == 'dfs':
#             f.write('Depth-First Search\n')
#         else:
#             f.write(f'{algorithm} is not a valid algorithm.\n')
#             sys.exit(1)
#         if solution:
#             f.write(f'Steps: {depth}, Weight: 0, Node: {nodes_explored}, Time (ms): {(end_time - start_time) * 1000 :.2f}, Memory (MB): {peak / (1024 * 1024):.4f}\n')
#             f.write(f'{solution}\n')
#         else:
#             f.write("No solution found.\n")
