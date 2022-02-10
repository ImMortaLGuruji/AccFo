# importing modules
import pygame
import os
from cryptography.fernet import Fernet
from settings import *
from assets.functions.textRender import RenderText
from assets.functions.button import Button

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

# main functions
cwd = os.getcwd()
dir = os.path.join(cwd + "/data")
if not os.path.exists(dir):
    os.mkdir(dir)
with open(os.path.join(dir, "passwords.txt"), 'a') as file:
    pass


# generating key
def keyGen():
    key = Fernet.generate_key()
    with open(KEYFILE, "wb") as keyFile:
        keyFile.write(key)


# setting key
def setKey():
    if os.path.isfile(KEYFILE) == False:
        keyGen()
    with open(KEYFILE, "r") as keyFile:
        key = keyFile.read()
    return key


# fernet setup
fernet = Fernet(setKey())

# title
title = RenderText("Account Info - AccFo", (250, 53))

# buttons
addBtn = Button('Add', (250, 130))
generateBtn = Button('Generate', (250, 210))
removeBtn = Button('Remove', (250, 290))
viewBtn = Button('View', (250, 370))
quitBtn = Button('Quit', (250, 450))

# main loop
running = True
while running:
    # drawing background color
    app.fill(BGCOLOR)

    # checking if user wants to close the appliction
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # drawing background
    title.draw()

    # drawing buttons
    if addBtn.draw():
        print("Add")
    if generateBtn.draw():
        print("Generate")
    if removeBtn.draw():
        print("Remove")
    if viewBtn.draw():
        print("View")
    if quitBtn.draw():
        running = False

    # updaing display
    pygame.display.update()

    # setting FPS
    clock.tick(FPS)

# closing pygame
pygame.quit()
