# importing modules
import pygame
from settings import *
from assets.functions.inputBox import InputBox
from assets.functions.button import Button
from assets.functions.textRender import RenderText, RenderTextWithBg

# starting pygame
pygame.init()

# loading icon image
iconImg = pygame.image.load(ICONIMG)

# window setup
app = pygame.display.set_mode(SIZE)
pygame.display.set_caption("AccFo")
pygame.display.set_icon(iconImg)

# limiting FPS
clock = pygame.time.Clock()

# examples
title = RenderText("AccFo", (250, 100))
text = RenderTextWithBg("Generate", (250, 200))
input = InputBox("Password", (250, 300))
button = Button("Exit", (250, 400))

# main loop
running = True
while running:
    # drawing background color
    app.fill(BGCOLOR)

    # checking if user wants to close the appliction
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        input.update(event)

    title.draw()
    text.draw()
    input.draw()
    if button.draw():
        running = False

    # updaing display
    pygame.display.update()

    # setting FPS
    clock.tick(FPS)

# closing pygame
pygame.quit()
