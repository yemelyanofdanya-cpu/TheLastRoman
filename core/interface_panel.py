# core/interface_panel.py
import pygame


def draw_panel(screen, unit, font):
    """Нижняя панель с описанием юнита."""
    panel_rect = pygame.Rect(0, 720, 1024, 48)
    pygame.draw.rect(screen, (30, 30, 30), panel_rect)

    if unit is None:
        text = font.render(
            "ЛКМ: выбрать / походить / атаковать   |   ПКМ: закончить ход",
            True,
            (200, 200, 200),
        )
        screen.blit(text, (20, 730))
        return

    text = f"{unit.name} — HP: {unit.health}/{unit.max_health}   Morale: {unit.morale}%"
    text_surf = font.render(text, True, (230, 230, 230))
    screen.blit(text_surf, (20, 730))


def draw_turn_label(screen, font, player_turn: bool):
    """Надпись сверху: чей сейчас ход."""
    label = "Ход игрока" if player_turn else "Ход противника"
    color = (200, 220, 255) if player_turn else (255, 210, 160)
    text_surf = font.render(label, True, color)
    screen.blit(text_surf, (780, 10))


# Заглушка, чтобы старый импорт show_buttons не ломал ничего
def show_buttons(*args, **kwargs):
    pass
