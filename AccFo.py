# importing modules
import pygame
import random
import pyperclip
from assets.interface.config import *
from sys import exit
from os import getcwd, path, mkdir
from cryptography.fernet import Fernet
from array import array


# Button class
class Button():
    def __init__(self, text, font, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = font
        self.bgRectColor = BUTTON_COLOR
        self.pressed = False
        self.action = False

        self.textSurface = self.font.render(text, True, TEXT_COLOR)
        self.textRect = self.textSurface.get_rect(center=pos)

        self.bgRect = pygame.Rect((0, 0), (0, 0))
        self.bgRect.height = 50
        self.bgRect.width = max(250, (self.textSurface.get_width() + 26))
        self.bgRect.center = self.textRect.center

    def draw(self):
        pygame.draw.rect(self.displaySurface, self.bgRectColor, self.bgRect)
        self.displaySurface.blit(self.textSurface, self.textRect)

        mousePos = pygame.mouse.get_pos()
        if self.bgRect.collidepoint(mousePos):
            self.bgRectColor = HOVER_COLOR
        else:
            self.bgRectColor = BUTTON_COLOR

    def clickCheck(self):
        self.action = False
        mousePos = pygame.mouse.get_pos()

        if self.bgRect.collidepoint(mousePos):
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed == True:
                    self.action = True
                    self.pressed = False

        return self.action


# InputBox class
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


# RenderText class
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


# RenderTextWithBg class
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


# PasswordText class
class PasswordText():
    def __init__(self, font, pos):
        self.displaySurface = pygame.display.get_surface()
        self.font = font
        self.bgRectColor = BUTTON_COLOR
        self.pos = pos
        self.pressed = False
        self.hovering = False

    def draw(self, text):
        if self.hovering == True:
            self.text = text
        else:
            self.text = "*" * len(text)

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
            self.hovering = True
            if pygame.mouse.get_pressed()[2]:
                self.pressed = True
            else:
                if self.pressed == True:
                    pyperclip.copy(self.text)
                    self.pressed = False
        else:
            self.hovering = False


# creating the password file if it doesn't exist
cwd = getcwd()
dir = path.join(cwd + "/data")
if not path.exists(dir):
    mkdir(dir)
with open(path.join(dir, "passwords.txt"), 'a') as file:
    pass


# generating key
def keyGen():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as keyFile:
        keyFile.write(key)


# setting the key
def setKey():
    if path.isfile(KEY_FILE) == False:
        keyGen()
    with open(KEY_FILE, "r") as keyFile:
        key = keyFile.read()
    return key


# initializing fernet
fernet = Fernet(setKey())

# initializing pygame
pygame.init()

# loading icon image
iconImg = pygame.image.load(ICON_IMAGE_PATH)

# window settings
app = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_icon(iconImg)

# limiting FPS
clock = pygame.time.Clock()

# font
font = pygame.font.Font(FONT_FILE_PATH, 24)


# function to generate password of a given length
def generatePassword(passwordLength):
    if passwordLength <= 7:
        passwordLength = 8
    elif passwordLength >= 26:
        passwordLength = 25

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

    for x in range(passwordLength - 4):
        tempPwd = tempPwd + random.choice(combinedList)
        tempPwdList = array('u', tempPwd)
        random.shuffle(tempPwdList)

    password = ""
    for x in tempPwdList:
        password = password + x

    return(password)


# error function
def error():
    pygame.display.set_caption("AccFo - Error")
    # title
    title = RenderText("Account Info", font, (250, 23))
    errorTitle = RenderText("Error", font, (250, 62))
    # text
    errorMsg = RenderText(
        "Sorry, you haven't saved anything yet.", font, (250, 250))
    # button
    backBtn = Button("Back", font, (250, 450))

    UIElements = [title, errorTitle, errorMsg, backBtn]

    while True:
        app.fill(BACKGROUND_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        for element in UIElements:
            element.draw()

        if backBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


# add function
def add():
    pygame.display.set_caption("AccFo - Add")
    # title
    title = RenderText("Account Info", font, (250, 23))
    addTitle = RenderText("Add", font, (250, 62))
    # buttons
    saveBtn = Button("Save", font, (250, 373))
    backBtn = Button("Back", font, (250, 452))
    # input boxes
    serviceName = InputBox("Service Name", font, (250, 139))
    username = InputBox("Username", font, (250, 217))
    password = InputBox("Password", font, (250, 295))

    UIElements = [title, addTitle, saveBtn,
                  backBtn, serviceName, username, password]

    while True:
        app.fill(BACKGROUND_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            serviceName.update(event)
            username.update(event)
            password.update(event)

        for element in UIElements:
            element.draw()

        if saveBtn.clickCheck():
            with open(PASSWORD_FILE, 'a') as file:
                file.write(serviceName.save() + "\:-:/" + username.save() + "\:-:/" +
                           fernet.encrypt(password.save().encode()).decode() + "\n")
            main()

        if backBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


# generate function
def generate():
    pygame.display.set_caption("AccFo - Generate")
    password = ''
    # title
    title = RenderText("Account Info", font, (250, 23))
    genTitle = RenderText("Generate", font, (250, 62))
    # button
    genBtn = Button("Generate", font, (250, 312))
    saveBtn = Button("Save", font, (250, 379))
    backBtn = Button("Back", font, (250, 446))
    # text with BG
    passwordTxt = RenderTextWithBg(font, (250, 245))
    # input box
    serviceName = InputBox("Service Name", font, (250, 111))
    username = InputBox("Username", font, (250, 178))
    passwordLen = InputBox("Password Length(8-25)", font, (250, 245))

    UIElements = [title, genTitle, genBtn,
                  saveBtn, backBtn, serviceName, username]

    while True:
        app.fill(BACKGROUND_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            serviceName.update(event)
            username.update(event)
            if password == '':
                passwordLen.update(event)

        if password == '':
            passwordLen.draw()

        for element in UIElements:
            element.draw()

        if genBtn.clickCheck():
            passwordLength = int(passwordLen.save())
            password = generatePassword(passwordLength)
        if saveBtn.clickCheck():
            with open(PASSWORD_FILE, 'a') as file:
                file.write(serviceName.save() + "\:-:/" + username.save() + "\:-:/" +
                           fernet.encrypt((passwordTxt.text).encode()).decode() + "\n")
            main()
        if backBtn.clickCheck():
            main()

        if not password == '':
            passwordTxt.draw(password)

        pygame.display.update()
        clock.tick(FPS)


# remove function
def remove():
    pygame.display.set_caption("AccFo - Remove")
    data = []
    with open(PASSWORD_FILE, 'r') as file:
        data = file.readlines()
    lineNum = 1
    # title
    title = RenderText("Account Info", font, (250, 23))
    rmvTitle = RenderText("Remove", font, (250, 62))
    # button
    upBtn = Button("Up", font, (250, 86+25))
    downBtn = Button("Down", font, (250, 347))
    rmvBtn = Button("Remove", font, (250, 406))
    backBtn = Button("Back", font, (250, 465))
    # text
    serviceTxt = RenderTextWithBg(font, (250, 170))
    usernameTxt = RenderTextWithBg(font, (250, 229))
    passwordTxt = PasswordText(font, (250, 288))

    UIElements = [title, rmvTitle, upBtn, downBtn, rmvBtn, backBtn]

    while True:
        app.fill(BACKGROUND_COLOR)

        if lineNum <= 0:
            lineNum = 1
        elif lineNum > len(data):
            lineNum = len(data)

        line = data[lineNum - 1].rstrip()

        service, username, passw = line.split("\:-:/")
        password = (fernet.decrypt(passw.encode()).decode())

        serviceTxt.draw(service)
        usernameTxt.draw(username)
        passwordTxt.draw(password)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        for element in UIElements:
            element.draw()

        if upBtn.clickCheck():
            lineNum -= 1
        if downBtn.clickCheck():
            lineNum += 1
        if rmvBtn.clickCheck():
            with open(PASSWORD_FILE, 'w') as file:
                for number, line in enumerate(data):
                    if number not in [lineNum - 1]:
                        file.write(line)
            main()
        if backBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


# view function
def view():
    pygame.display.set_caption("AccFo - View")
    data = []
    with open(PASSWORD_FILE, 'r') as file:
        data = file.readlines()
    lineNum = 1
    # title
    title = RenderText("Account Info", font, (250, 23))
    viewTitle = RenderText("View", font, (250, 62))
    # button
    upBtn = Button("Up", font, (250, 111))
    downBtn = Button("Down", font, (250, 379))
    backBtn = Button("Back", font, (250, 446))
    # text
    serviceTxt = RenderTextWithBg(font, (250, 178))
    usernameTxt = RenderTextWithBg(font, (250, 245))
    passwordTxt = PasswordText(font, (250, 312))

    UIElements = [title, viewTitle, upBtn, downBtn, backBtn]

    while True:
        app.fill(BACKGROUND_COLOR)
        if lineNum <= 0:
            lineNum = 1
        if lineNum > len(data):
            lineNum = len(data)

        line = (data[lineNum - 1].rstrip())

        service, username, passw = line.split("\:-:/")
        password = (fernet.decrypt(passw.encode()).decode())

        serviceTxt.draw(service)
        usernameTxt.draw(username)
        passwordTxt.draw(password)

        serviceTxt.clickCheck()
        usernameTxt.clickCheck()
        passwordTxt.clickCheck()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        for element in UIElements:
            element.draw()

        if upBtn.clickCheck():
            lineNum -= 1
        if downBtn.clickCheck():
            lineNum += 1
        if backBtn.clickCheck():
            main()

        pygame.display.update()
        clock.tick(FPS)


# main function
def main():
    pygame.display.set_caption("AccFo")

    info = []
    with open(PASSWORD_FILE, 'r') as file:
        info = file.readlines()

    title = RenderText("Account Info - AccFo", font, (250, 53))
    addBtn = Button("Add", font, (250, 130))
    generateBtn = Button("Generate", font, (250, 210))
    removeBtn = Button("Remove", font, (250, 290))
    viewBtn = Button("View", font, (250, 370))
    quitBtn = Button("Quit", font, (250, 450))

    UIElements = [title, addBtn, generateBtn, removeBtn, viewBtn, quitBtn]

    while True:
        app.fill(BACKGROUND_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        for element in UIElements:
            element.draw()

        if addBtn.clickCheck():
            add()
        if generateBtn.clickCheck():
            generate()
        if removeBtn.clickCheck():
            if len(info) <= 0:
                error()
            else:
                remove()
        if viewBtn.clickCheck():
            if len(info) <= 0:
                error()
            else:
                view()
        if quitBtn.clickCheck():
            pygame.quit()
            exit()

        pygame.display.update()
        clock.tick(FPS)


# running main
main()
