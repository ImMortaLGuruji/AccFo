import linecache
import pygame
import sys
import os
from assets.interface.config import *
from assets.interface.button import Button
from assets.interface.text import RenderText, RenderTextWithBg
from cryptography.fernet import Fernet

cwd = os.getcwd()
dir = os.path.join(cwd + "/data")
if not os.path.exists(dir):
    os.mkdir(dir)
with open(os.path.join(dir, "passwords.txt"), 'a') as file:
    pass

info = []
with open(PASSWORD_FILE, 'r') as file:
    info = file.readlines()


def keyGen():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as keyFile:
        keyFile.write(key)


def setKey():
    if os.path.isfile(KEY_FILE) == False:
        keyGen()
    with open(KEY_FILE, "r") as keyFile:
        key = keyFile.read()
    return key


fernet = Fernet(setKey())

pygame.init()

iconImg = pygame.image.load(ICON_IMAGE_PATH)

window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("AccFo")
pygame.display.set_icon(iconImg)

clock = pygame.time.Clock()
font = pygame.font.Font(FONT_FILE_PATH, 24)


def add():
    pygame.display.set_caption("AccFo - Add")
    addBackBtn = Button("Back", font, (250, 250))
    while True:
        window.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        addBackBtn.draw()
        if addBackBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


def generate():
    pygame.display.set_caption("AccFo - Generate")
    genBackBtn = Button("Back", font, (250, 250))
    while True:
        window.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        genBackBtn.draw()
        if genBackBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


def remove():
    pygame.display.set_caption("AccFo - Remove")
    rmvBackBtn = Button("Back", font, (250, 250))
    while True:
        window.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        rmvBackBtn.draw()
        if rmvBackBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


def view():
    pygame.display.set_caption("AccFo - View")
    viewLineNum = 1
    viewTitle = RenderText("Account Info", font, (250, 23))
    viewViewTitle = RenderText("View", font, (250, 62))
    viewUpBtn = Button("Up", font, (250, 111))
    viewDownBtn = Button("Down", font, (250, 379))
    viewBackBtn = Button("Back", font, (250, 446))

    viewServiceTxt = RenderTextWithBg(font, (250, 178))
    viewUsernameTxt = RenderTextWithBg(font, (250, 245))
    viewPasswordTxt = RenderTextWithBg(font, (250, 312))
    while True:
        window.fill(BACKGROUND_COLOR)

        data = []
        with open(PASSWORD_FILE, 'r') as file:
            data = file.readlines()

        if viewLineNum <= 0:
            viewLineNum = 1
        if viewLineNum > len(data):
            viewLineNum = len(data)

        line = (linecache.getline(PASSWORD_FILE, viewLineNum).rstrip())

        service, username, passw = line.split("\:-:/")
        password = (fernet.decrypt(passw.encode()).decode())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        viewServiceTxt.draw(service)
        viewUsernameTxt.draw(username)
        viewPasswordTxt.draw(password)

        viewServiceTxt.clickCheck()
        viewUsernameTxt.clickCheck()
        viewPasswordTxt.clickCheck()

        viewTitle.draw()
        viewViewTitle.draw()
        viewUpBtn.draw()
        viewDownBtn.draw()
        viewBackBtn.draw()
        if viewUpBtn.clickCheck():
            viewLineNum -= 1
        if viewDownBtn.clickCheck():
            viewLineNum += 1
        if viewBackBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


def saveError():
    pygame.display.set_caption("AccFo - Error")
    errorTitle = RenderText("Account Info", font, (250, 23))
    errorErrorTitle = RenderText("Error", font, (250, 62))
    errorErrorMsg = RenderText(
        "Sorry, you hanen't saved anything yet.", font, (250, 250))
    errorBackBtn = Button("Back", font, (250, 450))
    while True:
        window.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        errorTitle.draw()
        errorErrorTitle.draw()
        errorErrorMsg.draw()
        errorBackBtn.draw()
        if errorBackBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


title = RenderText("Account Info", font, (250, 53))
addBtn = Button("Add", font, (250, 130))
generateBtn = Button("Generate", font, (250, 210))
removeBtn = Button("Remove", font, (250, 290))
viewBtn = Button("View", font, (250, 370))
quitBtn = Button("Quit", font, (250, 450))


def main():
    pygame.display.set_caption("AccFo")
    while True:
        window.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        title.draw()
        addBtn.draw()
        generateBtn.draw()
        removeBtn.draw()
        viewBtn.draw()
        quitBtn.draw()

        if addBtn.clickCheck():
            add()
        if generateBtn.clickCheck():
            generate()
        if removeBtn.clickCheck():
            if len(info) <= 0:
                saveError()
            else:
                remove()
        if viewBtn.clickCheck():
            if len(info) <= 0:
                saveError()
            else:
                view()
        if quitBtn.clickCheck():
            pygame.quit()
            sys.exit()

        pygame.display.update()
        clock.tick(FPS)


main()
