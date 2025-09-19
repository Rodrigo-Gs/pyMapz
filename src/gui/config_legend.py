import pygame

from utils.colors import Color


class ConfigLegend:
    """A legend to display configurations applied to the graph visualization."""
    def __init__(self, position, graph, configs):
        self.position = position
        self.graph = graph
        self.configs = configs
        self._cached_font = pygame.font.SysFont("Tahoma", 13)

    def update_configs(self, configs):
        self.configs = configs

    def draw(self, screen):
        x, y = self.position
        rect_width, rect_height = 100, 25

        # Config items
        items = list(self.configs.items())
        for idx, (key, value) in enumerate(items):
            pygame.draw.rect(screen, Color.WHITE.value, (x, y + (idx + 1) * rect_height, rect_width, rect_height))
            text = f"{key}: {value}"
            screen.blit(self._cached_font.render(text, True, Color.BLACK.value), (x, y + (idx + 1) * rect_height))

