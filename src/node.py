import pygame
from utils.colors import Color
from pygame import gfxdraw


class Node:
    def __init__(self, name, pos=(0, 0), heuristic=0):
        self.radius = 10
        self.name = str(name)
        self.pos = pos
        self.heuristic = heuristic
        self.color = Color.BLUE.value
        self._cached_font = pygame.font.SysFont("Tahoma", 12)
        self.visit_order = []

    def set_color(self, color):
        self.color = color

    def set_order(self, order):
        self.visit_order = order

    def draw(self, screen):
        # Anti-aliased cirle nodes
        gfxdraw.aacircle(screen, self.pos[0], self.pos[1], self.radius, self.color)
        gfxdraw.filled_circle(screen, self.pos[0], self.pos[1], self.radius, self.color)

        # Draw node name
        name_surf = self._cached_font.render(self.name, True, Color.BLACK.value, Color.WHITE.value)
        tw, th = name_surf.get_size()
        name_x = self.pos[0] - tw // 2
        name_y = self.pos[1] - self.radius - th - 2  # 2px padding above circle
        screen.blit(name_surf, (name_x, name_y))

        # Draw visit order (if any), centered below the circle
        if self.visit_order:
            order_surf = self._cached_font.render(str(self.visit_order), True, Color.BLACK.value, Color.WHITE.value)
            ow, oh = order_surf.get_size()
            order_x = self.pos[0] - ow // 2
            order_y = self.pos[1] + self.radius + 2  # 2px padding below circle
            screen.blit(order_surf, (order_x, order_y))

    def get_heuristic(self):
        return self.heuristic

    def reset_surf_order(self):
        self.visit_order = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
