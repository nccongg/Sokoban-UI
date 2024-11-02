import pygame
import time
import os
# Khởi tạo pygame và đặt kích thước màn hình
pygame.init()
screen_width, screen_height = 1280, 720
FPS = 2  # Số lần cập nhật mỗi giây (điều chỉnh để tăng/giảm tốc độ di chuyển)
cell_size = 50 # Kích thước của mỗi ô trong lưới
rows, cols = 10, 10

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ares Movement Simulation")

# Màu sắc cho các loại ô
COLORS = {
    "#": (0, 0, 0),         # Tường - đen
    " ": (255, 255, 255),   # Ô trống - trắng
    "$": (139, 69, 19),     # Đá - nâu
    "*": (0, 128, 0),       # Đá trên công tắc - xanh lá
    "@": (0, 0, 255),       # Ares - xanh dương
    ".": (255, 165, 0),     # Công tắc - cam
    "+": (0, 255, 255)      # Ares trên công tắc - xanh ngọc
}

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




start_x = (screen_width - cols * cell_size) // 2
start_y = (screen_height - rows * cell_size) // 2

class Game:
    def __init__(self, grid, solution):
        self.grid = [list(row) for row in grid]
        self.solution = solution
        self.rows = len(self.grid)
        self.cols = max(len(row) for row in self.grid)
        self.cell_size = cell_size
        self.ares_pos = self.find_ares_position()
        self.clock = pygame.time.Clock()

    def find_ares_position(self):
        """Tìm vị trí bắt đầu của Ares."""
        for r in range(self.rows):
            for c in range(len(self.grid[r])):
                if self.grid[r][c] == '@' or self.grid[r][c] == '+':
                    return (r, c)
        return None

    # def draw_grid(self):
    #     """Vẽ lưới dựa trên `self.grid`."""
    #     screen.fill((255, 255, 255))  # Làm trắng màn hình
    #     for r in range(self.rows):
    #         for c in range(len(self.grid[r])):
    #             cell_value = self.grid[r][c]
    #             color = COLORS.get(cell_value, (255, 255, 255))
    #             x, y = c * self.cell_size, r * self.cell_size
    #             pygame.draw.rect(screen, color, (start_x + x, start_y + y, self.cell_size, self.cell_size))
    #             pygame.draw.rect(screen, (128, 128, 128), (start_x + x, start_y + y, self.cell_size, self.cell_size), 1)

    def draw_grid(self):
        """Vẽ lưới dựa trên `self.grid` bằng hình ảnh tương ứng."""
        screen.fill((255, 255, 255))  # Làm trắng màn hình
        for r in range(self.rows):
            for c in range(len(self.grid[r])):
                cell_value = self.grid[r][c]
                x = c * self.cell_size + (1280 - len(self.grid[r]) * self.cell_size) // 2  # Căn giữa theo chiều ngang
                y = r * self.cell_size + (720 - len(self.grid) * self.cell_size) // 2    # Căn giữa theo chiều dọc
            
                # Lấy hình ảnh tương ứng và vẽ nó
                if cell_value in images:
                    screen.blit(images[cell_value], (x, y))


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
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Vẽ lưới và di chuyển Ares theo các bước trong solution
            if step < len(self.solution):
                self.draw_grid()
                self.move_ares(self.solution[step])
                step += 1
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
        algorithm = lines[0].strip()  # Dòng đầu tiên là tên thuật toán
        
        # Dòng thứ hai chứa các thông số
        steps, weight, node, time_ms, memory_mb = map(lambda x: float(x.split(": ")[1]) if '.' in x else int(x.split(": ")[1]), lines[1].strip().split(", "))
        
        # Dòng thứ ba là chuỗi giải pháp
        solution = lines[2].strip()
        return solution


# Đầu vào mẫu
if __name__ == "__main__":
    # grid = [
    #     "#######",
    #     "#     #",
    #     "# .$. #",
    #     "#  @  #",
    #     "#######"
    # ]
    # solution = "drruLUlDR"  # Chuỗi mô phỏng chuyển động của Ares

    input_filename = 'algorithms/input.txt'
    output_filename = 'algorithms/output.txt'

    stone_weights, grid = read_input(input_filename)
    solution = read_output(output_filename)
    game = Game(grid, solution)
    game.run()
