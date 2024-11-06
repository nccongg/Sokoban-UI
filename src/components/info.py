import pygame

class InfoButton:
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        # Xử lý text_input là một mảng chuỗi
        self.text_input = text_input if isinstance(text_input, list) else [text_input]
        self.text_surfaces = [self.font.render(line, True, self.base_color) for line in self.text_input]

        # Nếu không có hình ảnh, tạo bề mặt trống vừa khít văn bản
        if self.image is None:
            width = max(text_surface.get_width() for text_surface in self.text_surfaces)
            height = sum(text_surface.get_height() for text_surface in self.text_surfaces) + 5 * (len(self.text_surfaces) - 1)
            self.image = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)  # Thêm padding

        # Căn chỉnh vị trí cho văn bản sao cho ở giữa trong nút
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        total_text_height = sum(surface.get_height() for surface in self.text_surfaces) + 5 * (len(self.text_surfaces) - 1)
        start_y = self.rect.centery - total_text_height // 2  # Bắt đầu từ giữa nút
        # start_y = 0
        # Cập nhật rect của từng dòng văn bản để căn giữa
        self.text_rects = [
            text_surface.get_rect(center=(self.rect.centerx, start_y + i * (text_surface.get_height() + 5)))
            for i, text_surface in enumerate(self.text_surfaces)
        ]

    def update(self, screen):
        # Vẽ nút
        if self.image is not None:
            screen.blit(self.image, self.rect)
        
        # Vẽ từng dòng văn bản
        for text_surface, text_rect in zip(self.text_surfaces, self.text_rects):
            screen.blit(text_surface, text_rect)

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        color = self.hovering_color if self.rect.collidepoint(position) else self.base_color
        self.text_surfaces = [self.font.render(line, True, color) for line in self.text_input]

    def changeText(self, new_text):
        # Cập nhật lại văn bản
        self.text_input = new_text if isinstance(new_text, list) else [new_text]
        self.text_surfaces = [self.font.render(line, True, self.base_color) for line in self.text_input]

        # Tính toán lại vị trí cho từng dòng văn bản
        total_text_height = sum(surface.get_height() for surface in self.text_surfaces) + 5 * (len(self.text_surfaces) - 1)
        start_y = self.rect.centery - total_text_height // 2 + 12

        self.text_rects = [
            text_surface.get_rect(center=(self.rect.centerx, start_y + i * (text_surface.get_height() + 5)))
            for i, text_surface in enumerate(self.text_surfaces)
        ]
