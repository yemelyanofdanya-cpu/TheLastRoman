# core/unit.py
import pygame
import random

# Размер спрайта юнита (в пикселях).
# Должен совпадать с CELL_SIZE в battle_map.py (у тебя 72).
SPRITE_SIZE = 72


class Unit:
    """
    Простой, единый класс юнита.
    С ним работают battle_scene.py, battle_map.py и ai_controller.py.
    """

    def __init__(
        self,
        name: str,
        max_health: int,
        morale: int,
        attack: int,
        defense: int,
        attack_range: int,
        movement: int,
        image_path: str,
        team: str,  # "player" или "enemy"
    ):
        self.name = name

        # Численность
        self.max_health = max_health
        self.health = max_health

        # Мораль (0–100)
        self.morale = morale

        # Боевая часть
        self.attack_power = attack
        self.defense = defense
        self.attack_range = attack_range  # дальность удара в клетках
        self.movement = movement  # сколько клеток может пройти за ход

        # Принадлежность
        self.team = team

        # Положение на сетке
        self.x = None
        self.y = None

        # Флаг бегства
        self.fleeing = False

        # Картинка юнита — сразу подгоняем под размер клетки
        original_img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(
            original_img, (SPRITE_SIZE, SPRITE_SIZE)
        )

    # --------- служебные методы ---------

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y

    def is_alive(self) -> bool:
        return self.health > 0 and not self.fleeing

    # --------- боевая логика ---------

    def take_damage(self, damage: int):
        """Получение урона + падение морали."""
        if damage <= 0:
            return

        self.health -= damage
        if self.health < 0:
            self.health = 0

        # Потери → падение морали (грубая формула, потом подправим)
        ratio_lost = 1.0 - (self.health / self.max_health if self.max_health > 0 else 0)
        morale_loss = int(ratio_lost * 15)
        self.morale -= morale_loss
        if self.morale < 0:
            self.morale = 0

        # При 0 морали юнит бежит
        if self.morale == 0:
            self.fleeing = True

    def attack(self, enemy: "Unit"):
        """Атака по врагу с учётом численности и рандома."""
        if not self.is_alive():
            return

        # Чем меньше людей в отряде, тем слабее удар
        ratio = self.health / self.max_health if self.max_health > 0 else 0
        base_damage = self.attack_power * (0.7 + 0.3 * ratio)  # 70–100% от силы

        # Разброс ±20%
        spread = base_damage * 0.2
        raw = base_damage + random.uniform(-spread, spread)

        # Учёт защиты врага
        damage = raw - enemy.defense
        if damage < 1:
            damage = 1

        enemy.take_damage(int(damage))
