import pygame
import time


def show_loading_screen(screen):
    loading_image = pygame.image.load("assets/images/loading.jpg")
    font = pygame.font.Font(None, 48)
    text = font.render("Загрузка...", True, (255, 255, 255))
    screen.blit(pygame.transform.scale(loading_image, screen.get_size()), (0, 0))
    screen.blit(text, (50, 650))
    pygame.display.flip()
    time.sleep(2)
