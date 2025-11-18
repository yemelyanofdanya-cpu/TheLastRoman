import pygame
import sys
from core.prologue import show_prologue


def draw_button(screen, rect, text, font, hovered):
    color = (200, 180, 140) if hovered else (100, 80, 50)
    pygame.draw.rect(screen, color, rect)
    label = font.render(text, True, (30, 20, 0))
    screen.blit(label, (rect.x + 20, rect.y + 10))


def main_menu(screen):
    bg = pygame.image.load("assets/images/menu_bg.jpg")
    font = pygame.font.Font("assets/fonts/gothic.ttf", 36)
    clock = pygame.time.Clock()

    buttons = [
        {"text": "Начать игру", "action": show_prologue},
        {"text": "Загрузить", "action": None},
        {"text": "Настройки", "action": None},
        {"text": "Выход", "action": sys.exit},
    ]

    rects = [pygame.Rect(500, 200 + i * 80, 300, 50) for i in range(len(buttons))]

    while True:
        screen.blit(pygame.transform.scale(bg, screen.get_size()), (0, 0))

        for i, btn in enumerate(buttons):
            hovered = rects[i].collidepoint(pygame.mouse.get_pos())
            draw_button(screen, rects[i], btn["text"], font, hovered)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        action = buttons[i]["action"]
                        if action:
                            action(screen)

        clock.tick(60)
