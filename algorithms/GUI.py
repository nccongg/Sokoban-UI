
### import thư viện
import pygame
import time
import os
import copy
import pygame, sys, threading
# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from components import Button

###

### Khởi tạo 

pygame.init()
screen_width, screen_height = 1280, 720
FPS = 2  # Số lần cập nhật mỗi giây (điều chỉnh để tăng/giảm tốc độ di chuyển)
cell_size = 40 # Kích thước của mỗi ô trong lưới
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ares Movement Simulation")

def get_font(size):
    # Trả về một đối tượng font với kích thước đã chỉ định
    return pygame.font.Font(None, size) 

images = {
    '#': pygame.image.load('img/wall.png'),
    ' ': pygame.image.load('img/space.png'),
    '$': pygame.image.load('img/stone.png'),
    '.': pygame.image.load('img/switch.png'),
    '@': pygame.image.load('img/ares.png'),
    '+': pygame.image.load('img/ares_on_switch.png'),
    '*': pygame.image.load('img/stone_on_switch.png'),
}
for key in images:
    images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))

button_image = pygame.image.load("img/Play Rect.png")
original_width, original_height = button_image.get_size()
new_width = 150  # Thay đổi chiều rộng theo mong muốn
resized_button_image = pygame.transform.scale(button_image, (new_width, original_height))
resized_test_button_image = pygame.transform.scale(button_image, (75, original_height))
###




class Game:
    def __init__(self, grids_list, solutions_list):
        
        self.grids_list = grids_list
        self.solutions_list = solutions_list
        
        # Lấy grid đầu tiên từ danh sách grids_list
        self.init_grid = [list(row) for row in grids_list[0]]  
        self.grid = [list(row) for row in grids_list[0]]  
        
        # Lấy solution đầu tiên từ danh sách solutions_list
        self.solution = solutions_list[0]
        self.current_solution = self.solution[0]['solution']

        self.rows = len(self.grid)
        self.cols = max(len(row) for row in self.grid)
        self.cell_size = cell_size
        self.ares_pos = self.find_ares_position()
        self.clock = pygame.time.Clock()


        # Khởi tạo nút
        self.PLAY_BUTTON = Button(image=pygame.image.load("img/Play Rect.png"), pos=((screen_width) // 2, 650), 
                                   text_input="Pause", font=get_font(30), 
                                   base_color="cyan", hovering_color="hotpink")
        self.buttons = [
            Button(image=resized_button_image, pos=(100, 400),
                text_input="BFS", font=get_font(30), base_color="cyan", hovering_color="hotpink"),
            Button(image=resized_button_image, pos=(300, 400),
                text_input="DFS", font=get_font(30), base_color="cyan", hovering_color="hotpink"),
            Button(image=resized_button_image, pos=(100, 500),
                text_input="UCS", font=get_font(30), base_color="cyan", hovering_color="hotpink"),
            Button(image=resized_button_image, pos=(300, 500),
                text_input="A*", font=get_font(30), base_color="cyan", hovering_color="hotpink")
            ]
        
        # Khởi tạo 10 nút test_button
        self.test_buttons = []
        for i in range(10):
            pos_x = 1000 + (i % 2) * 100  # Cách đều 100 pixel ngang
            pos_y = 100 + (i // 2) * 100  # Xuống hàng sau 2 nút
            button = Button(
                image=resized_test_button_image,
                pos=(pos_x, pos_y),
                text_input=f"Test {i+1}",  # Đặt tên là Test 1, Test 2, ...
                font=get_font(30),
                base_color="cyan",
                hovering_color="hotpink"
            )
            self.test_buttons.append(button)


    def handle_test_button_click(self, test_index):
        # Lấy solution từ solutions_list tương ứng với nút được bấm
        if 0 <= test_index < len(self.solutions_list):
            self.solution = self.solutions_list[test_index]  # Lấy solution đầu tiên từ test tương ứng
            self.current_solution = self.solution[0]['solution']
            self.init_grid = [list(row) for row in grids_list[test_index]]  
            self.reset_game()

    def reset_game(self):
        # Khởi tạo lại trạng thái game với solution mới
        # self.grid = [list(row) for row in self.init_grid]
        self.grid = copy.deepcopy(self.init_grid)
        self.ares_pos = self.find_ares_position()
        self.rows = len(self.grid)
        self.cols = max(len(row) for row in self.grid)
        # for row in self.grid:
        #     print(row)

    
        
    def find_ares_position(self):
        """Tìm vị trí bắt đầu của Ares."""
        for r in range(len(self.init_grid)):
            for c in range(len(self.init_grid[r])):
                if self.init_grid[r][c] == '@' or self.init_grid[r][c] == '+':
                    return (r, c)
        return None

    def draw_buttons(self, screen, mouse_pos): # vẽ buttons
        for button in self.buttons:
            button.changeColor(mouse_pos)
            button.update(screen)
        for button in self.test_buttons:
            button.changeColor(mouse_pos)
            button.update(screen)

    def draw_grid(self):
        screen.fill((0, 0, 0))  # Làm trắng màn hình
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        max_width = max(len(row) for row in self.grid)
        start_x = (screen_width - max_width * self.cell_size) // 2  # Căn giữa theo chiều ngang
        start_y = (screen_height - self.rows * self.cell_size) // 2  # Căn giữa theo chiều dọc
        for r in range(self.rows):
            for c in range(max_width):
                col = len(self.grid[r])
                x = start_x + c * self.cell_size 
                y = start_y + r * self.cell_size
                if c >= col:
                    screen.blit(images[' '], (x, y))
                else:
                    cell_value = self.grid[r][c]
                    # Lấy hình ảnh tương ứng và vẽ nó
                    if cell_value in images:
                        screen.blit(images[cell_value], (x, y))
        self.draw_buttons(screen, PLAY_MOUSE_POS)
        self.PLAY_BUTTON.changeColor(PLAY_MOUSE_POS)
        self.PLAY_BUTTON.update(screen)


    

    def move_ares(self, direction):
        """Di chuyển hoặc đẩy đá dựa trên hướng."""
        r, c = self.ares_pos
        dr, dc = {"u": -1, "d": 1, "l": 0, "r": 0}[direction.lower()], {"u": 0, "d": 0, "l": -1, "r": 1}[direction.lower()]
        new_r, new_c = r + dr, c + dc

        if direction.islower():  # Di chuyển thường
            if self.grid[new_r][new_c] in [" ", "."]:
                self.grid[r][c] = " " if self.grid[r][c] == "@" else "."
                self.grid[new_r][new_c] = "@" if self.grid[new_r][new_c] == " " else "+"
                self.ares_pos = (new_r, new_c)
        elif direction.isupper():  # Đẩy đá
            stone_r, stone_c = new_r + dr, new_c + dc
            if self.grid[new_r][new_c] in ["$", "*"] and self.grid[stone_r][stone_c] in [" ", "."]:
                self.grid[r][c] = " " if self.grid[r][c] == "@" else "."
                self.grid[new_r][new_c] = "@" if self.grid[new_r][new_c] == "$" else "+"
                self.grid[stone_r][stone_c] = "$" if self.grid[stone_r][stone_c] == " " else "*"
                self.ares_pos = (new_r, new_c)  


    

    def run(self):
        """Chạy vòng lặp chính để xử lý từng bước di chuyển trong solution."""
        running = True
        step = 0   
        moving = 1

        while running:
            
            PLAY_MOUSE_POS = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.PLAY_BUTTON.checkForInput(PLAY_MOUSE_POS):
                        if step == len(self.current_solution):
                            step = 0
                            moving = 1
                            # self.PLAY_BUTTON.changeText("Again")
                            self.grid = copy.deepcopy(self.init_grid)
                            self.ares_pos = self.find_ares_position()
                        else:
                            moving = (moving + 1) % 2
                        if moving == 1:
                            self.PLAY_BUTTON.changeText("Pause")
                        else:
                            self.PLAY_BUTTON.changeText("Continue")
                    # Kiểm tra nút thuật toán
                    for i, button in enumerate(self.buttons):
                        if button.checkForInput(PLAY_MOUSE_POS):
                            self.current_solution = self.solution[i]['solution']
                            step = 0  # Đặt lại bước đầu tiên
                            moving = 1  # Bắt đầu di chuyển
                            self.grid = copy.deepcopy(self.init_grid)
                            self.ares_pos = self.find_ares_position()   
                            self.PLAY_BUTTON.changeText("Pause")
                            continue
                    # Kiểm tra nút test
                    for i, button in enumerate(self.test_buttons):
                        if button.checkForInput(pygame.mouse.get_pos()):
                            self.handle_test_button_click(i)
                            step = 0
                            moving = 1

            # Vẽ lưới và di chuyển Ares theo các bước trong solution
            if moving and step < len(self.current_solution):
                self.draw_grid()
                self.move_ares(self.current_solution[step])
                step += 1
                pygame.display.flip()
                self.clock.tick(FPS)  # Điều chỉnh tốc độ di chuyển
            else:
                if(step == len(self.current_solution)):
                    self.PLAY_BUTTON.changeText("Again")                  
                self.draw_grid()
                pygame.display.flip()
                self.clock.tick(FPS)
        pygame.quit()




def read_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    weights_line = lines[0]
    grid_lines = lines[1:]
    weights = [int(w) for w in weights_line.strip().split()]
    grid = [line.rstrip('\n') for line in grid_lines]
    return weights, grid


def read_output(filename):
    results = []
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    for i in range(0, len(lines), 3):
        algorithm = lines[i]
        stats = {key: float(val) if '.' in val else int(val) 
                 for key, val in (item.split(": ") for item in lines[i + 1].split(", "))}
        solution = lines[i + 2]

        results.append({
            'algorithm': algorithm,
            'steps': stats['Steps'],
            'weight': stats['Weight'],
            'node': stats['Node'],
            'time_ms': stats['Time (ms)'],
            'memory_mb': stats['Memory (MB)'],
            'solution': solution
        })

    return results

def load_test_cases(input_folder, output_folder, num_tests):
    grids_list = []
    solutions_list = []

    for i in range(1, num_tests + 1):
        # Định dạng tên file input và output
        input_filename = os.path.join(input_folder, f"input-{i:02}.txt")
        output_filename = os.path.join(output_folder, f"output-{i:02}.txt")
        
        stone_weights, grid = read_input(input_filename)
        grids_list.append(grid)

        # Đọc file output
        solutions = read_output(output_filename)
        solutions_list.append(solutions)

    return grids_list, solutions_list


# Đầu vào mẫu
if __name__ == "__main__":

    input_folder = "algorithms/map/map"
    output_folder = "algorithms/map/solution"
    num_tests = 2
    grids_list, solutions_list = load_test_cases(input_folder, output_folder, num_tests)

    # print(solutions_list[0][0]['solution'])
    game = Game(grids_list, solutions_list)  # Bắt đầu với solution đầu tiên (ví dụ: BFS)
    game.run()
    # print(solutions[0]['solution'])
 