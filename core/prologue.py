import pygame
from core.dialog_scene import run_dialog_scene


def show_prologue(screen):
    screen.fill((0, 0, 0))
    font_big = pygame.font.Font("assets/fonts/gothic.ttf", 60)
    font_mid = pygame.font.Font("assets/fonts/gothic.ttf", 42)
    font_small = pygame.font.Font("assets/fonts/gothic.ttf", 28)

    title = font_big.render("Пролог", True, (255, 255, 255))
    chapter = font_mid.render("Глава I", True, (200, 200, 200))
    subtitle = font_small.render(
        "Когда оглядываешься назад — всё кажется ясным и предсказуемым...",
        True,
        (180, 180, 180),
    )

    screen.blit(title, title.get_rect(center=(640, 260)))
    screen.blit(chapter, chapter.get_rect(center=(640, 320)))
    screen.blit(subtitle, subtitle.get_rect(center=(640, 380)))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False
        pygame.time.delay(100)

    run_dialog_scene(screen)
