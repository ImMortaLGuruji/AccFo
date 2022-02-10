import pygame
from settings import *


class Button:
    def __init__(self, text, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = pygame.font.Font(FONTFILE, 24)
        self.clicked = False
        self.bgRectColor = BUTTONCOLOR

        self.textSurface = self.font.render(str(text), True, TEXTCOLOR)
        self.textRect = self.textSurface.get_rect(center=pos)

        self.bgRect = pygame.Rect((0, 0), (0, 0))
        self.bgRect.height = 50
        self.bgRect.width = max(250, (self.textSurface.get_width() + 26))
        self.bgRect.center = self.textRect.center

    def draw(self):
        action = False

        pygame.draw.rect(self.displaySurface, self.bgRectColor, self.bgRect)
        self.displaySurface.blit(self.textSurface, self.textRect)

        mousePos = pygame.mouse.get_pos()
        if self.bgRect.collidepoint(mousePos):
            self.bgRectColor = HOVERCOLOR
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True
            else:
                if self.clicked == True:
                    action = True
                    self.clicked = False
        else:
            self.bgRectColor = BUTTONCOLOR

        return action
