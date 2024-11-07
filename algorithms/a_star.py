import time
import heapq
import psutil
import os
import csv
from datetime import datetime


# import numpy as np

# def print_json(obj, indent=4):
#     def convert_to_serializable(o):
#         if isinstance(o, dict):
#             return {f"{k[0]},{k[1]}" if isinstance(k, tuple) else k: convert_to_serializable(v) for k, v in o.items()}
#         elif isinstance(o, list):
#             return [convert_to_serializable(i) for i in o]
#         else:
#             return o

#     serializable = convert_to_serializable(obj)
#     print(json.dumps(serializable, indent=indent))

def read_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    weights_line = lines[0]
    grid_lines = lines[1:]
    weights = [int(w) for w in weights_line.strip().split()]
    grid = [line.rstrip('\n') for line in grid_lines]
    return weights, grid

def write_output(filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution):
    with open(filename, 'a') as f:
        f.write(f"{algorithm_name}\n")
        f.write(f"Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.2f}\n")
        f.write(f"{solution}\n")

def compute_distance_grid(walls, switches, grid_width, grid_height):
    from collections import deque

    walls_set = set(walls)
    distance_grid = {}
    queue = deque()

    for switch in switches:
        distance_grid[switch] = 0
        queue.append(switch)

    while queue:
        position = queue.popleft()
        dist = distance_grid[position]
        x, y = position

        # For each direction, compute the position from which a stone could be pushed into the current position
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            pre_x, pre_y = x + dx, y + dy
            ares_x, ares_y = pre_x + dx, pre_y + dy

            # Check if positions are within the grid and not walls
            if (0 <= pre_x < grid_width and 0 <= pre_y < grid_height and
                0 <= ares_x < grid_width and 0 <= ares_y < grid_height):
                if ((pre_x, pre_y) not in walls_set and (ares_x, ares_y) not in walls_set):
                    if (pre_x, pre_y) not in distance_grid:
                        distance_grid[(pre_x, pre_y)] = dist + 1
                        queue.append((pre_x, pre_y))

    return distance_grid


def heuristic(state, switches, distance_grid):
    stones = state['stones'].keys()
    total_cost = 0

    for stone_pos in stones:
        if stone_pos in distance_grid:
            min_distance = distance_grid[stone_pos]
            total_cost += min_distance
        else:
            # If stone cannot reach any switch, set heuristic to a very high value (infinite)
            return float('inf')

    return total_cost

def is_goal_state(state, switches):
    stones = state['stones']
    return all(pos in switches for pos in stones.keys())

def is_deadlock(state, switches, walls, grid_width, grid_height):
    # Check for simple deadlock patterns
    stones = state['stones'].keys()
    for stone in stones:
        x, y = stone
        if (x, y) not in switches:
            if ((x == 0 or (x-1, y) in walls) and (y == 0 or (x, y-1) in walls)):
                return True
            if ((x == grid_width-1 or (x+1, y) in walls) and (y == 0 or (x, y-1) in walls)):
                return True
            if ((x == 0 or (x-1, y) in walls) and (y == grid_height-1 or (x, y+1) in walls)):
                return True
            if ((x == grid_width-1 or (x+1, y) in walls) and (y == grid_height-1 or (x, y+1) in walls)):
                return True
    return False

def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    return mem

def a_star_search(initial_state, walls, switches, grid_width, grid_height, distance_grid):
    start_time = time.time()
    nodes_generated = 0
    counter = 0  # Unique sequence count

    open_list = []
    h = heuristic(initial_state, switches, distance_grid)
    f = initial_state['cost_so_far'] + h
    heapq.heappush(open_list, (f, counter, initial_state))
    closed_set = set()


    while open_list:
        _, _, current_state = heapq.heappop(open_list)
        current_state_key = (current_state['ares_pos'], frozenset(current_state['stones'].items()))
        if current_state_key in closed_set:
            continue
        closed_set.add(current_state_key)

        nodes_generated += 1

        # if(nodes_generated % 10000 == 0):
        #     print(f"Nodes generated: {nodes_generated}")
        #     print(f"Cost so far: {current_state['cost_so_far']}")
        #     print(f"Total weight: {current_state['total_weight']}")
        #     print()

        if is_goal_state(current_state, switches):
            end_time = time.time()
            time_taken = (end_time - start_time) * 1000  # in ms
            memory_used = get_memory_usage()
            steps = len(current_state['actions'])
            total_weight = current_state['total_weight']
            solution = ''.join(current_state['actions'])
            return steps, total_weight, nodes_generated, time_taken, memory_used, solution

        if is_deadlock(current_state, switches, walls, grid_width, grid_height):
            continue  # Skip deadlocked states

        cost_so_far = current_state['cost_so_far']

        # Generate successors
        for move, action_char in [((0, -1), 'u'), ((0, 1), 'd'), ((-1, 0), 'l'), ((1, 0), 'r')]:
            new_ares_x = current_state['ares_pos'][0] + move[0]
            new_ares_y = current_state['ares_pos'][1] + move[1]
            if 0 <= new_ares_x < grid_width and 0 <= new_ares_y < grid_height:
                if (new_ares_x, new_ares_y) not in walls:
                    if (new_ares_x, new_ares_y) in current_state['stones']:
                        # Try to push the stone
                        new_stone_x = new_ares_x + move[0]
                        new_stone_y = new_ares_y + move[1]
                        if 0 <= new_stone_x < grid_width and 0 <= new_stone_y < grid_height:
                            if (new_stone_x, new_stone_y) not in walls and (new_stone_x, new_stone_y) not in current_state['stones']:
                                # Push is possible
                                new_stones = current_state['stones'].copy()
                                weight = new_stones.pop((new_ares_x, new_ares_y))
                                new_stones[(new_stone_x, new_stone_y)] = weight
                                action = action_char.upper()
                                new_total_weight = current_state['total_weight'] + weight
                                new_actions = current_state['actions'] + [action]
                                new_cost_so_far = cost_so_far + weight
                                new_state = {
                                    'ares_pos': (new_ares_x, new_ares_y),
                                    'stones': new_stones,
                                    'actions': new_actions,
                                    'total_weight': new_total_weight,
                                    'cost_so_far': new_cost_so_far
                                }

                                if not is_deadlock(new_state, switches, walls, grid_width, grid_height):
                                    h = heuristic(new_state, switches, distance_grid) #* weight
                                    if h == float('inf'):
                                        continue  # Skip unsolvable states
                                    f = new_cost_so_far + h
                                    counter += 1
                                    heapq.heappush(open_list, (f, counter, new_state))

                    else:
                        # Move without pushing
                        action = action_char.lower()
                        new_actions = current_state['actions'] + [action]
                        new_state = {
                            'ares_pos': (new_ares_x, new_ares_y),
                            'stones': current_state['stones'],
                            'actions': new_actions,
                            'total_weight': current_state['total_weight'],
                            'cost_so_far': cost_so_far + 1
                        }
                        if not is_deadlock(new_state, switches, walls, grid_width, grid_height):
                            h = heuristic(new_state, switches, distance_grid)
                            if h == float('inf'):
                                continue  # Skip unsolvable states
                            f = new_state['cost_so_far'] + h
                            counter += 1
                            heapq.heappush(open_list, (f, counter, new_state))
    # If no solution is found
    return None

def solve_sokoban(weights, grid):
    walls = set()
    switches = set()
    stones = {}
    ares_pos = None
    grid_height = len(grid)
    grid_width = max(len(row) for row in grid)
    weight_index = 0

    for y, line in enumerate(grid):
        for x, ch in enumerate(line):
            if ch == '#':
                walls.add((x, y))
            elif ch == '@':
                ares_pos = (x, y)
            elif ch == '+':
                ares_pos = (x, y)
                switches.add((x, y))
            elif ch == '$':
                stones[(x, y)] = weights[weight_index]
                weight_index += 1
            elif ch == '*':
                stones[(x, y)] = weights[weight_index]
                switches.add((x, y))
                weight_index += 1
            elif ch == '.':
                switches.add((x, y))
            elif ch == ' ':
                pass
    
    distance_grid = compute_distance_grid(walls, switches, grid_width, grid_height)

    initial_state = {
        'ares_pos': ares_pos,
        'stones': stones,
        'actions': [],
        'total_weight': 0,
        'cost_so_far': 0
    }

    # print_json(initial_state)

    result = a_star_search(initial_state, walls, switches, grid_width, grid_height, distance_grid)
    if result:
        steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
        return steps, total_weight, nodes_generated, time_taken, memory_used, solution
    else:
        return None


def solveAstar(input_filename, output_filename, csv_filename):
    weights, grid = read_input(input_filename)
    result = solve_sokoban(weights, grid)
    algorithm_name = "A*"

    # Initialize data to be written to CSV
    fields = ['Algorithm', 'Steps', 'Total Weight', 'Nodes Generated', 'Time Taken', 'Memory Used', 'Solution Found', 'Date']

    if result:
        steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
        # Write to the output file
        write_output(output_filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution)
        # Data for CSV
        data = [algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, 'Yes', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    else:
        # Write to the output file
        with open(output_filename, 'a') as f:
            f.write("A*\nNo solution found.\n")
        # Data for CSV
        data = [algorithm_name, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'No', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]

    # Append result to the CSV file
    with open(csv_filename, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        if file.tell() == 0:  # Write headers if file is empty
            csv_writer.writerow(fields)
        csv_writer.writerow(data)

# if __name__ == "__main__":

#     input_filename = './map/map/input-06.txt'
#     output_filename = './map/solution/output-06.txt'
#     if len(sys.argv) >= 2:
#         input_filename = sys.argv[1]
#     if len(sys.argv) >= 3:
#         output_filename = sys.argv[2]

#     weights, grid = read_input(input_filename)
#     result = solve_sokoban(weights, grid)
#     if result:
#         steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
#         algorithm_name = "A*"
#         write_output(output_filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution)
#     else:
#         with open(output_filename, 'w') as f:
#             f.write("No solution found.\n")
