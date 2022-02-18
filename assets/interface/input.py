import pygame
from assets.interface.config import *


class InputBox():
    def __init__(self, placeHolder, font, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = font
        self.placeHolder = placeHolder
        self.userInput = self.placeHolder
        self.bgRectColor = BUTTON_COLOR
        self.pos = pos
        self.active = False

    def draw(self):
        self.textSurface = self.font.render(self.userInput, True, TEXT_COLOR)
        self.textRect = self.textSurface.get_rect(center=self.pos)

        self.bgRect = pygame.Rect((0, 0), (0, 0))
        self.bgRect.height = 50
        self.bgRect.width = max(250, (self.textSurface.get_width() + 26))
        self.bgRect.center = self.textRect.center

        pygame.draw.rect(self.displaySurface, self.bgRectColor, self.bgRect)
        self.displaySurface.blit(self.textSurface, self.textRect)

        if self.active == True:
            self.bgRectColor = HOVER_COLOR
        else:
            self.bgRectColor = BUTTON_COLOR

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.bgRect.collidepoint(event.pos):
                self.active = True
                if self.userInput == self.placeHolder:
                    self.userInput = ''
            else:
                self.active = False
                if self.userInput == '':
                    self.userInput = self.placeHolder

        if self.active == True:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.userInput = self.userInput[:-1]
                else:
                    self.userInput += event.unicode

    def save(self):
        return self.userInput
