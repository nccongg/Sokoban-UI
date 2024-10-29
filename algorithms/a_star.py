import sys
import time
import heapq
import psutil
import os
import json

def print_json(obj, indent=4):
    def convert_to_serializable(o):
        if isinstance(o, dict):
            return {f"{k[0]},{k[1]}" if isinstance(k, tuple) else k: convert_to_serializable(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [convert_to_serializable(i) for i in o]
        else:
            return o

    serializable = convert_to_serializable(obj)
    print(json.dumps(serializable, indent=indent))

def read_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    weights_line = lines[0]
    grid_lines = lines[1:]
    weights = [int(w) for w in weights_line.strip().split()]
    grid = [line.rstrip('\n') for line in grid_lines]
    return weights, grid

def write_output(filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution):
    with open(filename, 'w') as f:
        f.write(f"{algorithm_name}\n")
        f.write(f"Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.2f}\n")
        f.write(f"{solution}\n")

def heuristic(state, switches):
    # Use sum of Manhattan distances from stones to nearest switches
    stones = state['stones']
    total = 0
    for stone_pos in stones.keys():
        min_dist = min(abs(stone_pos[0]-s[0])+abs(stone_pos[1]-s[1]) for s in switches)
        total += min_dist
    return total

def is_goal_state(state, switches):
    stones = state['stones']
    return all(pos in switches for pos in stones.keys())

def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    return mem

def a_star_search(initial_state, walls, switches, grid_width, grid_height):
    start_time = time.time()
    nodes_generated = 0
    counter = 0  # Unique sequence count

    open_list = []
    h = heuristic(initial_state, switches)
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

        if is_goal_state(current_state, switches):
            end_time = time.time()
            time_taken = (end_time - start_time) * 1000  # in ms
            memory_used = get_memory_usage()
            steps = len(current_state['actions'])
            total_weight = current_state['total_weight']
            solution = ''.join(current_state['actions'])
            return steps, total_weight, nodes_generated, time_taken, memory_used, solution

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
                                h = heuristic(new_state, switches)
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
                        h = heuristic(new_state, switches)
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
    initial_state = {
        'ares_pos': ares_pos,
        'stones': stones,
        'actions': [],
        'total_weight': 0,
        'cost_so_far': 0  
    }

    print_json(initial_state)

    result = a_star_search(initial_state, walls, switches, grid_width, grid_height)
    if result:
        steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
        return steps, total_weight, nodes_generated, time_taken, memory_used, solution
    else:
        return None

if __name__ == "__main__":

    input_filename = 'input.txt'
    output_filename = 'output.txt'
    if len(sys.argv) >= 2:
        input_filename = sys.argv[1]
    if len(sys.argv) >= 3:
        output_filename = sys.argv[2]

    weights, grid = read_input(input_filename)
    result = solve_sokoban(weights, grid)
    if result:
        steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
        algorithm_name = "A*"
        write_output(output_filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution)
    else:
        with open(output_filename, 'w') as f:
            f.write("No solution found.\n")
