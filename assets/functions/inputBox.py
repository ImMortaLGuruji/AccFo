import pygame
from settings import *


class InputBox:
    def __init__(self, placeholder, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = pygame.font.Font(FONTFILE, 24)
        self.placeholder = placeholder
        self.userInput = self.placeholder
        self.bgRectColor = BUTTONCOLOR
        self.active = False
        self.pos = pos

    def draw(self):
        self.textSurface = self.font.render(
            str(self.userInput), True, TEXTCOLOR)
        self.textRect = self.textSurface.get_rect(center=self.pos)

        self.bgRect = pygame.Rect((0, 0), (0, 0))
        self.bgRect.height = 50
        self.bgRect.width = max(250, (self.textSurface.get_width() + 26))
        self.bgRect.center = self.textRect.center

        pygame.draw.rect(self.displaySurface, self.bgRectColor, self.bgRect)
        self.displaySurface.blit(self.textSurface, self.textRect)

        if self.active == True:
            self.bgRectColor = HOVERCOLOR
        else:
            self.bgRectColor = BUTTONCOLOR

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.bgRect.collidepoint(event.pos):
                self.active = True
                if self.userInput == self.placeholder:
                    self.userInput = ''
            else:
                self.active = False
                if self.userInput == '':
                    self.userInput = self.placeholder

        if self.active == True:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.userInput = self.userInput[:-1]
                else:
                    self.userInput += event.unicode
