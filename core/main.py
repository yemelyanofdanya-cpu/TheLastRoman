import pygame
from core.loading import show_loading_screen
from core.menu import main_menu


def start_game():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("The Last Roman")
    show_loading_screen(screen)
    main_menu(screen)
    pygame.quit()
