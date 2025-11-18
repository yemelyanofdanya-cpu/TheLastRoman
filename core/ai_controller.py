# core/ai_controller.py
class AIController:
    def __init__(self, battle_map, enemy_units):
        self.battle_map = battle_map
        self.enemy_units = enemy_units  # список Unit команды enemy

    # --- один полный ход ИИ ---
    def make_turn(self):
        for unit in list(self.enemy_units):
            if not unit.is_alive():
                continue
            target = self.find_closest_target(unit)
            if not target:
                continue
            dist = self.distance(unit, target)
            if dist <= unit.attack_range:
                unit.attack(target)
            else:
                self.step_towards(unit, target)

    # --- поиск ближайшей цели ---
    def find_closest_target(self, unit):
        closest = None
        best = 9999
        for y in range(self.battle_map.height):
            for x in range(self.battle_map.width):
                other = self.battle_map.get_unit(x, y)
                if not other or other.team == unit.team or not other.is_alive():
                    continue
                d = self.distance(unit, other)
                if d < best:
                    best = d
                    closest = other
        return closest

    @staticmethod
    def distance(u, v):
        return abs(u.x - v.x) + abs(u.y - v.y)

    def step_towards(self, unit, target):
        dx = 0
        if target.x > unit.x:
            dx = 1
        elif target.x < unit.x:
            dx = -1

        dy = 0
        if target.y > unit.y:
            dy = 1
        elif target.y < unit.y:
            dy = -1

        new_x = unit.x + dx
        new_y = unit.y + dy
        if self.battle_map.is_cell_empty(new_x, new_y):
            self.battle_map.move_unit(unit, new_x, new_y)
