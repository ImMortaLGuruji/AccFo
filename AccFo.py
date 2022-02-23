import pygame
import sys
import os
import random
import array
from assets.interface.config import *
from assets.interface.button import Button
from assets.interface.text import RenderText, RenderTextWithBg
from assets.interface.input import InputBox
from cryptography.fernet import Fernet

cwd = os.getcwd()
dir = os.path.join(cwd + "/data")
if not os.path.exists(dir):
    os.mkdir(dir)
with open(os.path.join(dir, "passwords.txt"), 'a') as file:
    pass


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


def generatePassword(passLen):
    if passLen <= 7:
        passLen = 8
    elif passLen >= 26:
        passLen = 25

    digits = ['0', '2', '3', '4', '5', '6', '7', '8', '9']

    lowerCase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                 'z']

    upperCase = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                 'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                 'Z']

    symbols = ['!', '@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>',
               '*', '(', ')', '<']

    combinedList = digits + lowerCase + upperCase + symbols
    randDigit = random.choice(digits)
    randLower = random.choice(lowerCase)
    randUpper = random.choice(upperCase)
    randSymbol = random.choice(symbols)

    tempPwd = randDigit + randLower + randUpper + randSymbol

    for x in range(passLen - 4):
        tempPwd = tempPwd + random.choice(combinedList)
        tempPwdList = array.array('u', tempPwd)
        random.shuffle(tempPwdList)

    password = ""
    for x in tempPwdList:
        password = password + x

    return(password)


pygame.init()

iconImg = pygame.image.load(ICON_IMAGE_PATH)

window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("AccFo")
pygame.display.set_icon(iconImg)

clock = pygame.time.Clock()
font = pygame.font.Font(FONT_FILE_PATH, 24)


def add():
    pygame.display.set_caption("AccFo - Add")
    addTitle = RenderText("Account Info", font, (250, 23))
    addAddTitle = RenderText("Add", font, (250, 62))
    addSaveBtn = Button("Save", font, (250, 373))
    addBackBtn = Button("Back", font, (250, 452))

    addServiceName = InputBox("Service Name", font, (250, 139))
    addUsername = InputBox("Username", font, (250, 217))
    addPassword = InputBox("Password", font, (250, 295))

    while True:
        window.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            addServiceName.update(event)
            addUsername.update(event)
            addPassword.update(event)

        addTitle.draw()
        addAddTitle.draw()
        addServiceName.draw()
        addUsername.draw()
        addPassword.draw()

        addSaveBtn.draw()
        if addSaveBtn.clickCheck():
            with open(PASSWORD_FILE, 'a') as file:
                file.write(addServiceName.save() + "\:-:/" + addUsername.save() + "\:-:/" +
                           fernet.encrypt(addPassword.save().encode()).decode() + "\n")
            main()

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

    data = []
    with open(PASSWORD_FILE, 'r') as file:
        data = file.readlines()

    rmvLineNum = 1
    rmvTitle = RenderText("Account Info", font, (250, 23))
    rmvRmvTitle = RenderText("Remove", font, (250, 62))
    rmvUpBtn = Button("Up", font, (250, 86+25))
    rmvDownBtn = Button("Down", font, (250, 347))
    rmvRmvBtn = Button("Remove", font, (250, 406))
    rmvBackBtn = Button("Back", font, (250, 465))

    rmvServiceTxt = RenderTextWithBg(font, (250, 170))
    rmvUsernameTxt = RenderTextWithBg(font, (250, 229))
    rmvPasswordTxt = RenderTextWithBg(font, (250, 288))
    while True:
        window.fill(BACKGROUND_COLOR)

        if rmvLineNum <= 0:
            rmvLineNum = 1
        if rmvLineNum > len(data):
            rmvLineNum = len(data)

        line = (data[rmvLineNum - 1].rstrip())

        service, username, passw = line.split("\:-:/")
        password = (fernet.decrypt(passw.encode()).decode())

        rmvServiceTxt.draw(service)
        rmvUsernameTxt.draw(username)
        rmvPasswordTxt.draw(password)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        rmvTitle.draw()
        rmvRmvTitle.draw()
        rmvUpBtn.draw()
        rmvDownBtn.draw()
        rmvRmvBtn.draw()
        rmvBackBtn.draw()
        if rmvUpBtn.clickCheck():
            rmvLineNum -= 1
        if rmvDownBtn.clickCheck():
            rmvLineNum += 1
        if rmvRmvBtn.clickCheck():
            with open(PASSWORD_FILE, 'w') as file:
                for number, line in enumerate(data):
                    if number not in [rmvLineNum - 1]:
                        file.write(line)
            main()
        if rmvBackBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


def view():
    pygame.display.set_caption("AccFo - View")

    data = []
    with open(PASSWORD_FILE, 'r') as file:
        data = file.readlines()

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

        if viewLineNum <= 0:
            viewLineNum = 1
        if viewLineNum > len(data):
            viewLineNum = len(data)

        line = (data[viewLineNum - 1].rstrip())

        service, username, passw = line.split("\:-:/")
        password = (fernet.decrypt(passw.encode()).decode())

        viewServiceTxt.draw(service)
        viewUsernameTxt.draw(username)
        viewPasswordTxt.draw(password)

        viewServiceTxt.clickCheck()
        viewUsernameTxt.clickCheck()
        viewPasswordTxt.clickCheck()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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
        "Sorry, you haven't saved anything yet.", font, (250, 250))
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


def main():
    info = []
    with open(PASSWORD_FILE, 'r') as file:
        info = file.readlines()

    pygame.display.set_caption("AccFo")
    title = RenderText("Account Info - AccFo", font, (250, 53))
    addBtn = Button("Add", font, (250, 130))
    generateBtn = Button("Generate", font, (250, 210))
    removeBtn = Button("Remove", font, (250, 290))
    viewBtn = Button("View", font, (250, 370))
    quitBtn = Button("Quit", font, (250, 450))
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
