import heapq
import sys
import time
import heapq
import psutil
import os
import json


def check(node):
    n = len(node)  # Số dòng
    m = max(len(row) for row in node)  # Độ dài dòng dài nhất

    for i in range(n):
        for j in range(len(node[i])):  # Duyệt trong giới hạn của từng dòng
            if node[i][j] == '$':
                return False
    return True


def create_successors(grid, grid_cost, steps):
    successors = []
    rows, cols = len(grid), len(grid[0])
    ares_pos = None
    
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == '@' or grid[r][c] == '+':
                ares_pos = (r, c)
                break
        if ares_pos:
            break
    
    directions = [(-1, 0, 'u', 'U'), (1, 0, 'd', 'D'), (0, -1, 'l', 'L'), (0, 1, 'r', 'R')]

    # print(ares_pos)
    for dx, dy, move_action, push_action in directions:
        nx, ny = ares_pos[0] + dx, ares_pos[1] + dy
        cols = len(grid[nx])
        if 0 < nx < rows - 1 and 0 < ny < cols - 1:
            
            if grid[nx][ny] == ' ':
                new_grid = [list(row) for row in grid]  
                # new_grid[ares_pos[0]][ares_pos[1]] = ' '
                new_grid[ares_pos[0]][ares_pos[1]] = ' ' if grid[ares_pos[0]][ares_pos[1]] == '@' else '.' # Ares rời vị trí cũ
                new_grid[nx][ny] = '@'                
                # successors.append((''.join(''.join(row) for row in new_grid),grid_cost, 0, steps + 1))  # (trạng thái, chi phí)
                successors.append((new_grid, grid_cost, 0, steps + 1, move_action))  # (trạng thái, chi phí)
                
            elif grid[nx][ny] == '$':
                if grid[nx + dx][ny + dy] != ' ' and grid[nx + dx][ny + dy] != '.':
                    continue

                stone_x, stone_y = nx, ny
                new_stone_x = stone_x + dx
                new_stone_y = stone_y + dy

                if grid[new_stone_x][new_stone_y] == ' ': # Đẩy hòn đá vào chỗ trống                    
                    new_grid = [list(row) for row in grid]  # Tạo bản sao của grid
                    new_grid_cost = [row[:] for row in grid_cost] # sao chép grid_cost

                    # new_grid[ares_pos[0]][ares_pos[1]] = ' '  # Ares rời vị trí cũ
                    new_grid[ares_pos[0]][ares_pos[1]] = ' ' if grid[ares_pos[0]][ares_pos[1]] == '@' else '.' # Ares rời vị trí cũ
                    new_grid[nx][ny] = '@'  # Ares đến vị trí mới
                    new_grid[new_stone_x][new_stone_y] = '$'  # Hòn đá đến vị trí mới
                    
                    new_grid_cost[new_stone_x][new_stone_y] = new_grid_cost[stone_x][stone_y]
                    new_grid_cost[stone_x][stone_y] = 0 

                    # successors.append((''.join(''.join(row) for row in new_grid), new_grid_cost, grid_cost[new_stone_x][new_stone_y], steps + 1))
                    successors.append((new_grid, new_grid_cost, new_grid_cost[new_stone_x][new_stone_y], steps + 1,push_action))

                    continue
                if grid[new_stone_x][new_stone_y] == '.': # Đẩy hòn đá vào nút
                    new_grid = [list(row) for row in grid]  # Tạo bản sao của grid
                    new_grid_cost = [row[:] for row in grid_cost] # sao chép grid_cost

                    # new_grid[ares_pos[0]][ares_pos[1]] = ' '  # Ares rời vị trí cũ
                    new_grid[ares_pos[0]][ares_pos[1]] = ' ' if grid[ares_pos[0]][ares_pos[1]] == '@' else '.' # Ares rời vị trí cũ
                    new_grid[nx][ny] = '@'  # Ares đến vị trí mới
                    new_grid[new_stone_x][new_stone_y] = '*'  # Hòn đá đến vị trí mới
                    new_grid_cost[new_stone_x][new_stone_y] = grid_cost[stone_x][stone_y] # cost den vi tri moi
                    # successors.append((''.join(''.join(row) for row in new_grid),new_grid_cost , grid_cost[stone_x][stone_y], steps + 1))
                    new_grid_cost[stone_x][stone_y] = 0 
                    successors.append((new_grid,new_grid_cost , grid_cost[stone_x][stone_y], steps + 1, push_action))

            elif grid[nx][ny] == '.':
                new_grid = [list(row) for row in grid]  
                new_grid[ares_pos[0]][ares_pos[1]] = ' '
                new_grid[nx][ny] = '+'
                successors.append((new_grid, grid_cost, 0, steps + 1, move_action))
            elif grid[nx][ny] == '*':
                if grid[nx + dx][ny + dy] != ' ' and grid[nx + dx][ny + dy] != '.':
                    continue

                stone_x, stone_y = nx, ny
                new_stone_x = stone_x + dx
                new_stone_y = stone_y + dy

                if grid[new_stone_x][new_stone_y] == ' ': # Đẩy hòn đá vào chỗ trống                    
                    new_grid = [list(row) for row in grid]  # Tạo bản sao của grid
                    new_grid_cost = [row[:] for row in grid_cost] # sao chép grid_cost

                    new_grid[ares_pos[0]][ares_pos[1]] = ' ' if grid[ares_pos[0]][ares_pos[1]] == '@' else '.' # Ares rời vị trí cũ

                    new_grid[nx][ny] = '+'  # Ares đến vị trí mới
                    new_grid[new_stone_x][new_stone_y] = '$'  # Hòn đá đến vị trí mới
                    
                    new_grid_cost[new_stone_x][new_stone_y] = new_grid_cost[stone_x][stone_y]
                    new_grid_cost[stone_x][stone_y] = 0 

                    # successors.append((''.join(''.join(row) for row in new_grid), new_grid_cost, grid_cost[new_stone_x][new_stone_y], steps + 1))
                    successors.append((new_grid, new_grid_cost, new_grid_cost[new_stone_x][new_stone_y], steps + 1,push_action))

                    continue
                if grid[new_stone_x][new_stone_y] == '.': # Đẩy hòn đá vào nút
                    new_grid = [list(row) for row in grid]  # Tạo bản sao của grid
                    new_grid_cost = [row[:] for row in grid_cost] # sao chép grid_cost

                    new_grid[ares_pos[0]][ares_pos[1]] = ' ' if grid[ares_pos[0]][ares_pos[1]] == '@' else '.'  # Ares rời vị trí cũ
                    new_grid[nx][ny] = '+'  # Ares đến vị trí mới
                    new_grid[new_stone_x][new_stone_y] = '*'  # Hòn đá đến vị trí mới
                    new_grid_cost[new_stone_x][new_stone_y] = grid_cost[stone_x][stone_y] # cost den vi tri moi
                    
                    # successors.append((''.join(''.join(row) for row in new_grid),new_grid_cost , grid_cost[stone_x][stone_y], steps + 1))
                    new_grid_cost[stone_x][stone_y] = 0 
                    successors.append((new_grid,new_grid_cost , grid_cost[stone_x][stone_y], steps + 1, push_action))



    return successors       



def calculate_grid_cost(grid, stone_weights):
    grid_cost = []
    weight_index = 0

    for r in range(len(grid)):
        row_cost = []
        for c in range(len(grid[r])):
            if grid[r][c] == '$' or grid[r][c] == '*':
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
    n, m = len(grid), len(grid[0])

    start_time = time.time()
    nodes_generated = 0  

    while frontier:
        current_cost, steps, node, current_grid_cost, path  = heapq.heappop(frontier)

        # for row in node:
        #     print(row)
        # print('\n')
        nodes_generated += 1
        if check(node) == True:
            end_time = time.time()
            time_taken = (end_time - start_time) * 1000  # in ms
            memory_used = get_memory_usage()
            return steps, current_cost, nodes_generated, time_taken, memory_used, path 
        
        # tạo các trạng thái có thể của ma trận node

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
    return weights, grid

# def write_output(filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution):
#     with open(filename, 'w') as f:
#         f.write(f"{algorithm_name}\n")
#         f.write(f"Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.2f}\n")
#         f.write(f"{solution}\n")

def write_output(filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used,solution):
    with open(filename, 'a') as f:
        f.write(f"{algorithm_name}\n")
        f.write(f"Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.2f}\n")
        f.write(f"{solution}\n")


def solveUCS(input_filename, output_filename):
    stone_weights, grid = read_input(input_filename)

    result  = ucs(grid, stone_weights)

    if result:
        steps, total_weight, nodes_generated, time_taken, memory_used, solution  = result
        algorithm_name = "UCS"
        write_output(output_filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution )
    else:
        with open(output_filename, 'a') as f:
            f.write("UCS\nNo solution found.\n")

# if __name__ == "__main__":

#     input_filename = 'algorithms/input.txt'
#     output_filename = 'algorithms/output.txt'

#     stone_weights, grid = read_input(input_filename)

#     result  = ucs(grid, stone_weights)

#     if result:
#         steps, total_weight, nodes_generated, time_taken, memory_used, solution  = result
#         algorithm_name = "UCS"
#         write_output(output_filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution )
#     else:
#         with open(output_filename, 'w') as f:
#             f.write("No solution found.\n")