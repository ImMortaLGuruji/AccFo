import pygame
import linecache
import os
from cryptography.fernet import Fernet
from settings import *
from assets.functions.textRender import RenderText, RenderTextWithBg
from assets.functions.button import Button

cwd = os.getcwd()
dir = os.path.join(cwd + "/data")
if not os.path.exists(dir):
    os.mkdir(dir)
with open(os.path.join(dir, "passwords.txt"), 'a') as file:
    pass


def keyGen():
    key = Fernet.generate_key()
    with open("data/key.key", "wb") as keyFile:
        keyFile.write(key)


def setKey():
    if os.path.isfile("data/key.key") == False:
        keyGen()
    with open("data/key.key", "r") as keyFile:
        key = keyFile.read()
    return key


fernet = Fernet(setKey())

pygame.init()

iconImg = pygame.image.load(ICONIMG)

app = pygame.display.set_mode(SIZE)
pygame.display.set_caption("AccFo - view")
pygame.display.set_icon(iconImg)

clock = pygame.time.Clock()

lineNum = 1


def increase():
    global lineNum
    lineNum -= 1


def decrease():
    global lineNum
    lineNum += 1


title = RenderText("Account Info", (250, 23))
viewTitle = RenderText("View", (250, 62))
upBtn = Button("Up", (250, 111))
downBtn = Button("Down", (250, 379))
backBtn = Button("Back", (250, 446))

running = True
while running:
    app.fill(BGCOLOR)

    data = []
    with open(PASSWORDSFILE, 'r') as file:
        data = file.readlines()

    if lineNum <= 0:
        lineNum = 1
    if lineNum > len(data):
        lineNum = len(data)

    line = (linecache.getline(PASSWORDSFILE, lineNum).rstrip())

    service, username, passw = line.split("\:-:/")
    password = (fernet.decrypt(passw.encode()).decode())

    serviceTxt = RenderTextWithBg(service, (250, 178))
    usernameTxt = RenderTextWithBg(username, (250, 245))
    passwordTxt = RenderTextWithBg(password, (250, 312))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    title.draw()
    viewTitle.draw()
    if upBtn.draw():
        increase()
    if downBtn.draw():
        decrease()
    if backBtn.draw():
        running = False
    serviceTxt.draw()
    usernameTxt.draw()
    passwordTxt.draw()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
