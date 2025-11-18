# core/battle_scene.py
import pygame

from core.unit import Unit
from core.battle_map import BattleMap, CELL_SIZE
from core.interface_panel import draw_panel, draw_turn_label
from core.ai_controller import AIController

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768


def create_battle():
    """Создаём карту и отряды для тестового боя."""
    battle_map = BattleMap(12, 10)

    # --- наши войска ---
    player_units = []

    limitan = Unit(
        name="Лимитаны-копья",
        max_health=120,
        morale=100,
        attack=10,
        defense=5,
        attack_range=1,
        movement=3,
        image_path="assets/units/limitanus.png",
        team="player",
    )
    comitat = Unit(
        name="Комитаты-мечи",
        max_health=140,
        morale=100,
        attack=12,
        defense=7,
        attack_range=1,
        movement=3,
        image_path="assets/units/comitatus.png",
        team="player",
    )
    archer = Unit(
        name="Сагиттарии",
        max_health=80,
        morale=90,
        attack=8,
        defense=2,
        attack_range=3,
        movement=2,
        image_path="assets/units/archer.png",
        team="player",
    )

    battle_map.add_unit(limitan, 4, 8)
    battle_map.add_unit(comitat, 5, 8)
    battle_map.add_unit(archer, 6, 8)

    player_units.extend([limitan, comitat, archer])

    # --- враги ---
    enemy_units = []

    enemy1 = Unit(
        name="Персидская пехота",
        max_health=100,
        morale=100,
        attack=9,
        defense=4,
        attack_range=1,
        movement=3,
        image_path="assets/units/enemy_spear.png",
        team="enemy",
    )
    enemy2 = Unit(
        name="Персидские лучники",
        max_health=70,
        morale=90,
        attack=7,
        defense=2,
        attack_range=3,
        movement=2,
        image_path="assets/units/enemy_archer.png",
        team="enemy",
    )

    battle_map.add_unit(enemy1, 5, 2)
    battle_map.add_unit(enemy2, 7, 3)

    enemy_units.extend([enemy1, enemy2])

    ai = AIController(battle_map, enemy_units)

    return battle_map, player_units, enemy_units, ai


def manhattan_dist(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)


def run_battle_scene(screen):
    """Запускается из dialog_scene после выбора 'защитить империю'."""
    clock = pygame.time.Clock()
    font = pygame.font.Font("assets/fonts/gothic.ttf", 24)

    battle_map, player_units, enemy_units, ai_controller = create_battle()

    selected_unit = None
    player_turn = True  # по умолчанию ходит игрок
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # --- ХОД ИГРОКА ---
            if player_turn:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    grid_x = mx // CELL_SIZE
                    grid_y = my // CELL_SIZE

                    # выбор юнита
                    if selected_unit is None:
                        unit = battle_map.get_unit(grid_x, grid_y)
                        if unit and unit.team == "player" and unit.is_alive():
                            selected_unit = unit
                    else:
                        # попытка походить или атаковать
                        target = battle_map.get_unit(grid_x, grid_y)
                        if target is None:
                            # ход
                            dist = abs(grid_x - selected_unit.x) + abs(
                                grid_y - selected_unit.y
                            )
                            if (
                                dist <= selected_unit.movement
                                and battle_map.is_cell_empty(grid_x, grid_y)
                            ):
                                battle_map.move_unit(selected_unit, grid_x, grid_y)
                        else:
                            # атака
                            if target.team != selected_unit.team and target.is_alive():
                                dist = abs(grid_x - selected_unit.x) + abs(
                                    grid_y - selected_unit.y
                                )
                                if dist <= selected_unit.attack_range:
                                    selected_unit.attack(target)
                        selected_unit = None

                # ПКМ — закончить ход
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    selected_unit = None
                    player_turn = False

        # --- ХОД ИИ (один раз, после того как игрок закончил ход) ---
        if not player_turn:
            ai_controller.make_turn()
            player_turn = True

        # --- ОТРИСОВКА ---
        screen.fill((0, 0, 0))
        battle_map.draw(screen)
        draw_panel(screen, selected_unit, font)
        draw_turn_label(screen, font, player_turn)

        pygame.display.flip()
        clock.tick(60)
