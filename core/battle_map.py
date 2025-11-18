# core/battle_map.py
import pygame

CELL_SIZE = 72  # размер клетки


class BattleMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # grid[y][x] -> Unit или None
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    # --- работа с клетками ---

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_unit(self, x: int, y: int):
        if self.in_bounds(x, y):
            return self.grid[y][x]
        return None

    def is_cell_empty(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.grid[y][x] is None

    def add_unit(self, unit, x: int, y: int) -> bool:
        if not self.is_cell_empty(x, y):
            return False
        self.grid[y][x] = unit
        unit.set_position(x, y)
        return True

    def move_unit(self, unit, new_x: int, new_y: int) -> bool:
        if not self.is_cell_empty(new_x, new_y):
            return False
        if unit.y is None or unit.x is None:
            return False
        self.grid[unit.y][unit.x] = None
        self.grid[new_y][new_x] = unit
        unit.set_position(new_x, new_y)
        return True

    # --- отрисовка ---

    def draw(self, surface):
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, (60, 60, 60), rect, 1)

                unit = self.grid[y][x]
                if unit and unit.is_alive():
                    # Просто ставим картинку в левый угол клетки
                    surface.blit(unit.image, (x * CELL_SIZE, y * CELL_SIZE))
