import pygame
import pyperclip
from settings import *


class RenderText:
    def __init__(self, text, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = pygame.font.Font(FONTFILE, 24)

        self.textSurface = self.font.render(str(text), True, TEXTCOLOR)
        self.textRect = self.textSurface.get_rect(center=pos)

    def draw(self):
        self.displaySurface.blit(self.textSurface, self.textRect)


class RenderTextWithBg:
    def __init__(self, text, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = pygame.font.Font(FONTFILE, 24)
        self.text = text
        self.pressed = False

        self.textSurface = self.font.render(
            str(self.text), True, TEXTCOLOR)
        self.textRect = self.textSurface.get_rect(center=pos)

        self.bgRect = pygame.Rect((0, 0), (0, 0))
        self.bgRect.height = 50
        self.bgRect.width = self.textSurface.get_width() + 26
        self.bgRect.center = self.textRect.center

    def draw(self):
        pygame.draw.rect(self.displaySurface, BUTTONCOLOR, self.bgRect)
        self.displaySurface.blit(self.textSurface, self.textRect)
        self.clickCheck()

    def clickCheck(self):
        mousePos = pygame.mouse.get_pos()
        if self.bgRect.collidepoint(mousePos):
            if pygame.mouse.get_pressed()[2]:
                self.pressed = True
            else:
                if self.pressed == True:
                    pyperclip.copy(self.text)
                    self.pressed = False
