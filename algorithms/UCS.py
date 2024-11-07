import heapq
import time
import psutil
import os
import csv
from datetime import datetime

def check(node):
    for row in node:
        if '$' in row:
            return False
    return True

def create_successors(grid, grid_cost, steps):
    successors = []
    rows = len(grid)
    ares_pos = None
    
    for r in range(rows):
        for c in range(len(grid[r])):
            if grid[r][c] == '@' or grid[r][c] == '+':
                ares_pos = (r, c)
                break
        if ares_pos:
            break

    directions = [(-1, 0, 'u', 'U'), (1, 0, 'd', 'D'), (0, -1, 'l', 'L'), (0, 1, 'r', 'R')]

    for dx, dy, move_action, push_action in directions:
        nx, ny = ares_pos[0] + dx, ares_pos[1] + dy
        if 0 <= nx < rows and 0 <= ny < len(grid[nx]):
            target_cell = grid[nx][ny]
            # Check for move to empty space or goal
            if target_cell in (' ', '.'):
                new_grid = [list(row) for row in grid]
                new_grid[ares_pos[0]][ares_pos[1]] = ' ' if grid[ares_pos[0]][ares_pos[1]] == '@' else '.'
                new_grid[nx][ny] = '@' if target_cell == ' ' else '+'
                successors.append((new_grid, grid_cost, 0, steps + 1, move_action))
            # Check for pushing a box
            elif target_cell in ('$','*'):
                box_nx, box_ny = nx + dx, ny + dy
                if 0 <= box_nx < rows and 0 <= box_ny < len(grid[box_nx]):
                    box_target_cell = grid[box_nx][box_ny]
                    if box_target_cell in (' ', '.'):
                        new_grid = [list(row) for row in grid]
                        new_grid_cost = [row[:] for row in grid_cost]

                        # Update positions
                        new_grid[ares_pos[0]][ares_pos[1]] = ' ' if grid[ares_pos[0]][ares_pos[1]] == '@' else '.'
                        new_grid[nx][ny] = '@' if target_cell == '$' else '+'
                        new_grid[box_nx][box_ny] = '$' if box_target_cell == ' ' else '*'

                        # Update costs
                        new_grid_cost[box_nx][box_ny] = new_grid_cost[nx][ny]
                        new_grid_cost[nx][ny] = 0

                        move_cost = new_grid_cost[box_nx][box_ny]
                        successors.append((new_grid, new_grid_cost, move_cost, steps + 1, push_action))
    return successors

def calculate_grid_cost(grid, stone_weights):
    grid_cost = []
    weight_index = 0

    for r in range(len(grid)):
        row_cost = []
        for c in range(len(grid[r])):
            if grid[r][c] in ('$','*'):
                row_cost.append(stone_weights[weight_index])
                weight_index += 1
            else:
                row_cost.append(0)
        grid_cost.append(row_cost)
    return grid_cost

def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    return mem

def ucs(grid, stone_weights):
    start_node = grid
    start_node_hash = ''.join(''.join(row) for row in grid)
    grid_cost = calculate_grid_cost(grid, stone_weights)
    frontier = [(0, 0, start_node, grid_cost, '')]
    explored = {start_node_hash: (0, None, 0)}
    nodes_generated = 0  

    start_time = time.time()

    while frontier:
        current_cost, steps, node, current_grid_cost, path  = heapq.heappop(frontier)
        nodes_generated += 1

        if check(node):
            end_time = time.time()
            time_taken = (end_time - start_time) * 1000  # in ms
            memory_used = get_memory_usage()
            return steps, current_cost, nodes_generated, time_taken, memory_used, path 

        successors = create_successors(node, current_grid_cost, steps)
        for successor, successor_grid_cost, move_cost, successor_steps, action in successors:
            successor_hash = ''.join(''.join(row) for row in successor)            
            total_cost = current_cost + move_cost
            new_path = path + action

            if successor_hash not in explored or (total_cost, successor_steps) < (explored[successor_hash][0], explored[successor_hash][2]):
                explored[successor_hash] = (total_cost, node, successor_steps)
                heapq.heappush(frontier, (total_cost, successor_steps, successor, successor_grid_cost, new_path))

    return None

def read_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    weights_line = lines[0]
    grid_lines = lines[1:]
    weights = [int(w) for w in weights_line.strip().split()]
    grid = [line.rstrip('\n') for line in grid_lines]

    # Pad rows to make the grid rectangular
    max_cols = max(len(row) for row in grid)
    grid = [row.ljust(max_cols) for row in grid]
    grid = [list(row) for row in grid]  # Convert each string into a list of characters
    return weights, grid

def write_output(filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution):
    with open(filename, 'a') as f:
        f.write(f"{algorithm_name}\n")
        f.write(f"Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.2f}\n")
        f.write(f"{solution}\n")

def solveUCS(input_filename, output_filename, csv_filename):
    stone_weights, grid = read_input(input_filename)
    result = ucs(grid, stone_weights)
    algorithm_name = "UCS"
    fields = ['Algorithm', 'Steps', 'Total Weight', 'Nodes Generated', 'Time Taken', 'Memory Used']

    if result:
        steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
        data = [algorithm_name, steps, total_weight, nodes_generated, f"{time_taken:.2f}", f"{memory_used:.4f}"]
    else:
        data = [algorithm_name, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

    with open(output_filename, 'a') as f:
        if result:
            f.write("UCS\n")
            f.write(f'Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.4f}\n')           
            f.write(f'{solution}\n')
        else:
            f.write("UCS\nNo solution found.\n")

    with open(csv_filename, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        if file.tell() == 0:
            csv_writer.writerow(fields)
        csv_writer.writerow(data)
# import sys
# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python Search.py <input_file> <output_file>")
#         sys.exit(1)
#     solveUCS(sys.argv[1], sys.argv[2], "results.csv")
