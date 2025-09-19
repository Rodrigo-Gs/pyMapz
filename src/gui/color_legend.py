import pygame
from utils.colors import Color


class ColorLegend:
    WIDTH = 575
    HEIGHT = 20

    def __init__(self, x, y, container=None):
        self.x = x
        self.y = y
        self.colors = [
            {"color": Color.BLACK.value, "label": "Initial node"},
            {"color": Color.RED.value, "label": "Goal node"},
            {"color": Color.BLUE.value, "label": "Unvisited node"},
            {"color": Color.GREEN.value, "label": "Visited node"},
            {"color": Color.YELLOW.value, "label": "Path node"}
        ]
        self.font = pygame.font.SysFont('Tahoma', 12)
        self.container = container

    def draw(self, screen):
        initial_x = self.x
        border_size = 20
        for color_info in self.colors:
            square_border = pygame.draw.rect(screen, Color.WHITE.value, (initial_x, self.container.centery - 10, border_size + 2, border_size + 2))
            pygame.draw.rect(screen, color_info["color"], (square_border.x + 1, square_border.y + 1, 20, 20))
            text = self.font.render(color_info["label"], True, Color.WHITE.value)
            screen.blit(text, (initial_x + 25, self.container.centery - 7))
            initial_x += 125  # Change this to adjust space between legend items
