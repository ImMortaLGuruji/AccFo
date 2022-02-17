import pygame
from assets.interface.config import *


class Button():
    def __init__(self, text, font, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = font
        self.bgRectColor = BUTTON_COLOR
        self.pressed = False
        self.action = False

        self.textSurface = self.font.render(text, True, TEXT_COLOR)
        self.textRect = self.textSurface.get_rect(center=pos)

        self.bgRect = pygame.Rect((0, 0), (0, 0))
        self.bgRect.height = 50
        self.bgRect.width = max(250, (self.textSurface.get_width() + 26))
        self.bgRect.center = self.textRect.center

    def draw(self):
        pygame.draw.rect(self.displaySurface, self.bgRectColor, self.bgRect)
        self.displaySurface.blit(self.textSurface, self.textRect)

        mousePos = pygame.mouse.get_pos()
        if self.bgRect.collidepoint(mousePos):
            self.bgRectColor = HOVER_COLOR
        else:
            self.bgRectColor = BUTTON_COLOR

    def clickCheck(self):
        self.action = False
        mousePos = pygame.mouse.get_pos()

        if self.bgRect.collidepoint(mousePos):
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed == True:
                    self.action = True
                    self.pressed = False

        return self.action
