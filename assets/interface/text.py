import pygame
import pyperclip
from assets.interface.config import *


class RenderText():
    def __init__(self, text, font, pos):
        self.displaySurface = pygame.display.get_surface()
        self.text = text
        self.font = font
        self.pos = pos

        self.textSurface = self.font.render(self.text, True, TEXT_COLOR)
        self.textRect = self.textSurface.get_rect(center=self.pos)

    def draw(self):
        self.displaySurface.blit(self.textSurface, self.textRect)


class RenderTextWithBg():
    def __init__(self, font, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = font
        self.bgRectColor = BUTTON_COLOR
        self.pos = pos
        self.pressed = False

    def draw(self, text):
        self.text = text

        self.textSurface = self.font.render(self.text, True, TEXT_COLOR)
        self.textRect = self.textSurface.get_rect(center=self.pos)

        self.bgRect = pygame.Rect((0, 0), (0, 0))
        self.bgRect.height = 50
        self.bgRect.width = (self.textSurface.get_width() + 26)
        self.bgRect.center = self.textRect.center

        pygame.draw.rect(self.displaySurface, self.bgRectColor, self.bgRect)
        self.displaySurface.blit(self.textSurface, self.textRect)

    def clickCheck(self):
        mousePos = pygame.mouse.get_pos()
        if self.bgRect.collidepoint(mousePos):
            if pygame.mouse.get_pressed()[2]:
                self.pressed = True
            else:
                if self.pressed == True:
                    pyperclip.copy(self.text)
                    self.pressed = False
