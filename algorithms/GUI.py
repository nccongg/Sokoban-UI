
### import thư viện
import pygame
import time
import os
import pygame, sys, threading
# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from components import Button

###

### Khởi tạo 

pygame.init()
screen_width, screen_height = 1280, 720
FPS = 2  # Số lần cập nhật mỗi giây (điều chỉnh để tăng/giảm tốc độ di chuyển)
cell_size = 50 # Kích thước của mỗi ô trong lưới
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

###




class Game:
    def __init__(self, grid, solution):
        self.init_grid = [list(row) for row in grid]
        self.grid = [list(row) for row in grid]
        self.solution = solution
        self.rows = len(self.grid)
        self.cols = max(len(row) for row in self.grid)
        self.cell_size = cell_size
        self.ares_pos = self.find_ares_position()
        self.clock = pygame.time.Clock()
        # Khởi tạo nút
        self.PLAY_BUTTON = Button(image=pygame.image.load("img/Play Rect.png"), pos=((screen_width) // 2, 600), 
                                   text_input="Pause", font=get_font(30), 
                                   base_color="cyan", hovering_color="hotpink")
        self.buttons = [
            Button(image=pygame.image.load("img/Play Rect.png"), pos=(200, 200),
                text_input="BFS", font=get_font(30), base_color="cyan", hovering_color="hotpink"),
            Button(image=pygame.image.load("img/Play Rect.png"), pos=(200, 300),
                text_input="DFS", font=get_font(30), base_color="cyan", hovering_color="hotpink"),
            Button(image=pygame.image.load("img/Play Rect.png"), pos=(200, 400),
                text_input="UCS", font=get_font(30), base_color="cyan", hovering_color="hotpink"),
            Button(image=pygame.image.load("img/Play Rect.png"), pos=(200, 500),
                text_input="A*", font=get_font(30), base_color="cyan", hovering_color="hotpink")
]
        
        
        
    def find_ares_position(self):
        """Tìm vị trí bắt đầu của Ares."""
        for r in range(self.rows):
            for c in range(len(self.grid[r])):
                if self.grid[r][c] == '@' or self.grid[r][c] == '+':
                    return (r, c)
        return None

    def draw_buttons(self, screen, mouse_pos): # vẽ buttons
        for button in self.buttons:
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
                        if step == len(self.solution):
                            step = 0
                            moving = 1
                            self.grid = self.init_grid
                            self.ares_pos = self.find_ares_position()
                        else:
                            moving = (moving + 1) % 2
                        if moving == 1:
                            self.PLAY_BUTTON.changeText("Pause")
                        else:
                            self.PLAY_BUTTON.changeText("Continue")


            # Vẽ lưới và di chuyển Ares theo các bước trong solution
            if moving and step < len(self.solution):
                self.draw_grid()
                self.move_ares(self.solution[step])
                step += moving
                pygame.display.flip()
                self.clock.tick(FPS)  # Điều chỉnh tốc độ di chuyển
            else:
                running = False  # Kết thúc khi hoàn thành các bước di chuyển
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
    with open(filename, 'r') as f:
        lines = f.readlines()
        algorithm = lines[0].strip()  
        
        steps, weight, node, time_ms, memory_mb = map(lambda x: float(x.split(": ")[1]) if '.' in x else int(x.split(": ")[1]), lines[1].strip().split(", "))
        
        solution = lines[2].strip()
        return solution


# Đầu vào mẫu
if __name__ == "__main__":
   

    input_filename = 'algorithms/input.txt'
    output_filename = 'algorithms/output.txt'

    stone_weights, grid = read_input(input_filename)
    solution = read_output(output_filename)
    print(solution)
    
    game = Game(grid, solution)
    game.run()
