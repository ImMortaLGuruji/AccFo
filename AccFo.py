# Importing Required Modules
from tkinter import *
from os import getcwd, mkdir, path
from cryptography.fernet import Fernet
from random import choice, shuffle
from array import array
from pyperclip import copy
from sys import exit

# Initializing Application Window
window = Tk()
icon = PhotoImage(file="assets/images/icon.png")
window.iconphoto(True, icon)
window.geometry("925x500")
window.title("AccFo")
window.configure(bg="white")
window.resizable(False, False)

# Loading Images
ArrowLeftImg = PhotoImage(file='assets/images/ArrowLeftImg.png')
ArrowRightImg = PhotoImage(file='assets/images/ArrowRightImg.png')
HomeTextImg = PhotoImage(file='assets/images/HomeTextImg.png')
SignUpImg = PhotoImage(file='assets/images/SignUpImg.png')
SignInImg = PhotoImage(file='assets/images/SignInImg.png')
HomeImg = PhotoImage(file='assets/images/HomeImg.png')
ErrorImg = PhotoImage(file='assets/images/ErrorImg.png')
AddImg = PhotoImage(file='assets/images/AddImg.png')
GenerateImg = PhotoImage(file='assets/images/GenerateImg.png')
RemoveImg = PhotoImage(file='assets/images/RemoveImg.png')
ViewImg = PhotoImage(file='assets/images/ViewImg.png')

# Defigning Variables
show = 'show'
hide = 'hide'
lineNum = 0
info = []

# Defigning Fonts
HEADING_FONT = ('Regular', 22)
LARGE_TEXT_FONT = ('Regular', 16)
MEDIUM_TEXT_FONT = ('Regular', 12)
SMALL_TEXT_FONT = ('Regular', 9)

# Defigning Colours
PRIMARY = '#FF4E5A'
TEXT = '#4E4E4E'
SECONDARY = '#1C2F37'

# Defigning Files
KEY_FILE = "assets/config/key.key"
USERS_FILE = "assets/config/users.txt"

# Creating Config Folder
cwd = getcwd()
dir = path.join(cwd + "/assets/config")
if not path.exists(dir):
    mkdir(dir)
with open(path.join(dir, "users.txt"), 'a') as file:
    pass


# Function To Generate Key
def keyGen():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as keyFile:
        keyFile.write(key)


# Function To Set Key
def setKey():
    if path.isfile(KEY_FILE) == False:
        keyGen()
    with open(KEY_FILE, "r") as keyFile:
        key = keyFile.read()
    return key


# Initializing Fernet
fernet = Fernet(setKey())


# Read And Edit Users
class Users():
    def __init__(self):
        self.file = USERS_FILE
        self.divider = "|_]-[_|"

    def addUser(self, username, password):
        with open(self.file, 'a') as file:
            file.write(username + self.divider +
                       fernet.encrypt(password.encode()).decode() + '\n')

    def login(self, username, password):
        data = []
        with open(USERS_FILE, 'r') as file:
            data = file.readlines()
        for lineNum in range(len(data)):
            line = data[lineNum].rstrip()
            name, pwd = line.split(self.divider)
            pwd = (fernet.decrypt(pwd.encode()).decode())
            if username == name and password == pwd:
                return True
        return False


# Assigning Users
users = Users()


# Text Input Box
class TextInput():
    def __init__(self, value, frame, x, y):
        self.value = value
        self.place = Entry(frame, width=32, fg=TEXT, border=0,
                           bg="white", font=MEDIUM_TEXT_FONT)
        self.place.place(x=x, y=y)
        self.place.insert(0, self.value)
        self.place.bind("<FocusIn>", self.onEnter)
        self.place.bind("<FocusOut>", self.onLeave)
        Frame(frame, width=295, height=2, bg=SECONDARY).place(x=(x-5), y=(y+25))

    def onEnter(self, e):
        self.data = self.place.get()
        if self.data == self.value:
            self.place.delete(0, "end")

    def onLeave(self, e):
        self.data = self.place.get()
        if self.data == "":
            self.place.insert(0, self.value)

    def get(self):
        self.data = self.place.get()
        return (self.data)


# Password Input Box
class PasswordInput():
    def __init__(self, value, frame, x, y):
        self.value = value
        if self.value != "Password":
            self.place = Entry(frame, width=32, fg=TEXT, border=0,
                               bg="white", font=MEDIUM_TEXT_FONT, show="-")
            self.btn = Button(frame, text=show, font=("Bold", 12),
                              bg="white", fg="black", cursor="hand2", command=self.showHide, border=0)
        else:
            self.place = Entry(frame, width=32, fg=TEXT, border=0,
                               bg="white", font=MEDIUM_TEXT_FONT)
            self.btn = Button(frame, text=hide, font=("Bold", 12),
                              bg="white", fg="black", cursor="hand2", command=self.showHide, border=0)
        self.place.place(x=x, y=y)
        self.place.insert(0, self.value)
        self.place.bind("<FocusIn>", self.onEnter)
        self.place.bind("<FocusOut>", self.onLeave)
        self.btn.place(x=x+295, y=y)
        Frame(frame, width=295, height=2, bg=SECONDARY).place(x=(x-5), y=(y+25))

    def showHide(self):
        if self.place['show'] == '-':
            self.place.configure(show='')
            self.btn.configure(text=hide)
        else:
            self.place.configure(show='-')
            self.btn.configure(text=show)

    def onEnter(self, e):
        self.data = self.place.get()
        if self.data == self.value:
            self.place.delete(0, "end")

    def onLeave(self, e):
        self.data = self.place.get()
        if self.data == "":
            self.place.insert(0, self.value)
        elif self.data == "Password" and self.place[show] == '':
            self.place.configure(show='')
            self.btn.configure(text=hide)

    def get(self):
        self.data = self.place.get()
        return (self.data)


# User Output Box
class UserOutput():
    def __init__(self, value, frame, x, y):
        self.value = value
        self.button = Button(frame, text=self.value, font=MEDIUM_TEXT_FONT, bg="white", fg=TEXT, cursor="hand2",
                             command=lambda: copy(self.value), border=0)
        self.button.place(x=x, y=y, width=281, height=29)

    def updateText(self, value):
        self.value = value
        self.button['text'] = self.value


# Read And Write Passwords
class Passwords():
    def __init__(self):
        self.divider = "[)-|-(]"

    def addData(self, passwordFile, serviceName, username, password):
        with open(passwordFile, 'a') as file:
            file.write(serviceName + self.divider + username + self.divider +
                       fernet.encrypt(password.encode()).decode() + "\n")

    def getData(self, passwordFile, lineNum, value):
        with open(passwordFile, 'r') as file:
            data = file.readlines()
            line = data[lineNum].rstrip()
            service, username, pwd = line.split(self.divider)
            password = fernet.decrypt(pwd.encode()).decode()
        if value == 'service':
            return service
        elif value == 'username':
            return username
        elif value == 'password':
            return password

    def removeData(self, passwordFile, lineNum):
        with open(passwordFile, 'r') as file:
            data = file.readlines()
        with open(passwordFile, 'w') as file:
            for number, line in enumerate(data):
                if number is not lineNum:
                    file.write(line)


# Assigning Passwords
passwords = Passwords()


# Function to generate a password with given length
def genPwd(passLen):
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

    symbols = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>',
               '*', '(', ')', '<']

    combinedList = digits + lowerCase + upperCase + symbols
    randDigit = choice(digits)
    randLower = choice(lowerCase)
    randUpper = choice(upperCase)
    randSymbol = choice(symbols)

    tempPwd = randDigit + randLower + randUpper + randSymbol

    for x in range(passLen - 4):
        tempPwd = tempPwd + choice(combinedList)
        tempPwdList = array('u', tempPwd)
        shuffle(tempPwdList)

    password = ""
    for x in tempPwdList:
        password = password + x

    return (password)


# Popup window
def popup(message):
    popupWin = Toplevel(window)
    popupWin.title("AccFo")
    popupWin.configure(bg="white")
    popupWin.resizable(False, False)
    Label(popupWin, text=message, fg=TEXT,
          bg='white', font=LARGE_TEXT_FONT).pack()
    Button(popupWin, text="OK", fg='white', bg=PRIMARY, font=LARGE_TEXT_FONT,
           border=0, cursor="hand2", command=popupWin.destroy).pack()


# SignUp Frame
def SignUp():
    window.title("AccFo - SignUp")
    frame = Frame(window, width=925, height=500, bg='white').place(x=0, y=0)
    Label(frame, image=SignUpImg, bg="white").place(x=42, y=124)
    Label(frame, text="AccFo", bg="white", fg=PRIMARY,
          font=HEADING_FONT).place(x=655, y=50)
    Label(frame, text="Sign Up", bg="white", fg=PRIMARY,
          font=LARGE_TEXT_FONT).place(x=653, y=100)

    username = TextInput("Username", frame, 553, 180)
    password = PasswordInput("Password", frame, 553, 262)

    def logUser():
        users.addUser(username.get(), password.get())
        popup('Successfully signed up!')
        SignIn()

    Button(frame, text="Sign Up", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=logUser).place(x=614, y=350, width=160, height=34)
    Label(frame, text="Already have an account?", bg='white', fg=TEXT,
          font=SMALL_TEXT_FONT).place(x=576, y=420)
    Button(frame, text="Sign In", bg='white', fg=PRIMARY, border=0,
           cursor='hand2', font=SMALL_TEXT_FONT, command=SignIn).place(x=718, y=420)


# SignIn Frame
def SignIn():
    window.title("AccFo - SignIn")
    frame = Frame(window, width=925, height=500, bg='white').place(x=0, y=0)
    Label(frame, image=SignInImg, bg="white").place(x=42, y=124)
    Label(frame, text="AccFo", bg="white", fg=PRIMARY,
          font=HEADING_FONT).place(x=655, y=50)
    Label(frame, text="Sign In", bg="white", fg=PRIMARY,
          font=LARGE_TEXT_FONT).place(x=658, y=100)

    username = TextInput("Username", frame, 553, 180)
    password = PasswordInput("Password", frame, 553, 262)

    def validate():
        if users.login(username.get(), password.get()):
            popup(f'Successfully logged in as {username.get()}!')
            Home(username.get())
        else:
            popup('Invalid username or password')

    Button(frame, text="Sign In", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=validate).place(x=614, y=350, width=160, height=34)
    Label(frame, text="Don't have an account?", bg='white', fg=TEXT,
          font=SMALL_TEXT_FONT).place(x=581, y=420)
    Button(frame, text="Sign Up", bg='white', fg=PRIMARY, border=0,
           cursor='hand2', font=SMALL_TEXT_FONT, command=SignUp).place(x=710, y=420)


# Home Frame
def Home(username):
    cwd = getcwd()
    dir = path.join(cwd + "/assets/data")
    if not path.exists(dir):
        mkdir(dir)
    with open(path.join(dir, f"{username}.txt"), 'a') as file:
        pass

    passwordFile = f"assets/data/{username}.txt"

    window.title("AccFo")
    frame = Frame(window, width=925, height=500, bg='white').place(x=0, y=0)
    Label(frame, image=HomeImg, bg="white").place(x=42, y=124)
    Label(frame, image=HomeTextImg, bg="white").place(x=348, y=444)
    Label(frame, text="AccFo", bg="white", fg=PRIMARY,
          font=HEADING_FONT).place(x=655, y=50)
    Label(frame, text="Home", bg="white", fg=PRIMARY,
          font=LARGE_TEXT_FONT).place(x=663, y=100)

    Button(frame, text="Add", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=lambda: Add(passwordFile, username)).place(x=614, y=168, width=160, height=34)
    Button(frame, text="Generate", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=lambda: Generate(passwordFile, username)).place(x=614, y=215, width=160, height=34)
    Button(frame, text="Remove", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=lambda: Remove(passwordFile, username)).place(x=614, y=262, width=160, height=34)
    Button(frame, text="View", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=lambda: View(passwordFile, username)).place(x=614, y=309, width=160, height=34)
    Button(frame, text="Quit", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=exit).place(x=614, y=356, width=160, height=34)


# Error Frame
def Error(username):
    window.title("AccFo - Error")
    frame = Frame(window, width=925, height=500, bg='white').place(x=0, y=0)
    Label(frame, image=ErrorImg, bg="white").place(x=42, y=124)
    Label(frame, text="AccFo", bg="white", fg=PRIMARY,
          font=HEADING_FONT).place(x=655, y=50)
    Label(frame, text="Error", bg="white", fg=PRIMARY,
          font=LARGE_TEXT_FONT).place(x=668, y=100)

    Label(frame, text="You have not saved anything yet!",
          bg='white', fg=TEXT, font=LARGE_TEXT_FONT).place(x=535, y=202)
    Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=lambda: Home(username)).place(x=614, y=367, width=160, height=34)


# Add Frame
def Add(passwordFile, user):
    window.title("AccFo - Add")
    frame = Frame(window, width=925, height=500, bg='white').place(x=0, y=0)
    Label(frame, image=AddImg, bg="white").place(x=42, y=124)
    Label(frame, text="AccFo", bg="white", fg=PRIMARY,
          font=HEADING_FONT).place(x=655, y=50)
    Label(frame, text="Add", bg="white", fg=PRIMARY,
          font=LARGE_TEXT_FONT).place(x=668, y=100)

    service = TextInput("Service Name", frame, 553, 171)
    username = TextInput("Username", frame, 553, 230)
    password = TextInput("Password", frame, 553, 289)

    def addData():
        passwords.addData(passwordFile, service.get(),
                          username.get(), password.get())
        popup('Successfully saved informaton!')
        Add(passwordFile, user)

    Button(frame, text="Save", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=addData).place(x=524, y=367, width=160, height=34)
    Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=lambda: Home(user)).place(x=704, y=367, width=160, height=34)


# Generate Frame
def Generate(passwordFile, user):
    window.title("AccFo - Generate")
    frame = Frame(window, width=925, height=500, bg='white').place(x=0, y=0)
    Label(frame, image=GenerateImg, bg="white").place(x=42, y=124)
    Label(frame, text="AccFo", bg="white", fg=PRIMARY,
          font=HEADING_FONT).place(x=655, y=50)
    Label(frame, text="Generate", bg="white", fg=PRIMARY,
          font=LARGE_TEXT_FONT).place(x=646, y=100)

    service = TextInput("Service Name", frame, 553, 151)
    username = TextInput("Username", frame, 553, 203)
    passwordLength = TextInput("Password Length (8 - 25)", frame, 553, 255)
    password = TextInput("Password", frame, 553, 307)

    def place():
        password.place.delete(0, "end")
        password.place.insert(0, genPwd(int(passwordLength.get())))

    def addData():
        passwords.addData(passwordFile, service.get(),
                          username.get(), password.get())
        popup('Successfully saved informaton!')
        Generate(passwordFile, user)

    Button(frame, text="Save", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=addData).place(x=524, y=367, width=160, height=34)
    Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=lambda: Home(user)).place(x=704, y=367, width=160, height=34)
    Button(frame, text="Generate", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=place).place(x=615, y=411, width=160, height=34)


# Remove Frame
def Remove(passwordFile, user):
    global lineNum, info
    lineNum = 0
    info = []
    with open(passwordFile, 'r') as file:
        info = file.readlines()

    if len(info) <= 0:
        Error(user)
    else:
        window.title("AccFo - Remove")
        frame = Frame(window, width=925, height=500,
                      bg='white').place(x=0, y=0)
        Label(frame, image=RemoveImg, bg="white").place(x=42, y=124)
        Label(frame, text="AccFo", bg="white", fg=PRIMARY,
              font=HEADING_FONT).place(x=655, y=50)
        Label(frame, text="Remove", bg="white", fg=PRIMARY,
              font=LARGE_TEXT_FONT).place(x=651, y=100)

        def update():
            global info, lineNum
            info = []
            with open(passwordFile, 'r') as file:
                info = file.readlines()
            service.updateText(passwords.getData(
                passwordFile, lineNum, 'service'))
            username.updateText(passwords.getData(
                passwordFile, lineNum, 'username'))
            password.updateText(passwords.getData(
                passwordFile, lineNum, 'password'))
            if lineNum > (len(info) - 1):
                lineNum = (len(info) - 1)
            elif lineNum < 0:
                lineNum = 0

        def next():
            global lineNum
            lineNum += 1
            if lineNum > (len(info) - 1):
                lineNum = (len(info) - 1)
            update()

        def prev():
            global lineNum
            lineNum -= 1
            if lineNum < 0:
                lineNum = 0
            update()

        def removeData():
            passwords.removeData(passwordFile, lineNum)
            popup('Successfully removed information!')
            Remove(passwordFile, user)

        Button(frame, image=ArrowRightImg, bg="white",
               cursor="hand2", command=next, border=0).place(x=864, y=251)
        Button(frame, image=ArrowLeftImg, bg="white",
               cursor="hand2", command=prev, border=0).place(x=524, y=251)
        service = UserOutput('Service Name', frame, 553, 171)
        username = UserOutput('Username', frame, 553, 230)
        password = UserOutput('Password', frame, 553, 289)
        update()
        Button(frame, text="Remove", bg=PRIMARY, fg='white', border=0, cursor='hand2', font=LARGE_TEXT_FONT,
               command=removeData).place(x=524, y=367, width=160, height=34)
        Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
               font=LARGE_TEXT_FONT, command=lambda: Home(user)).place(x=704, y=367, width=160, height=34)


# View Frame
def View(passwordFile, user):
    global lineNum
    lineNum = 0
    info = []
    with open(passwordFile, 'r') as file:
        info = file.readlines()

    if len(info) <= 0:
        Error(user)
    else:
        lineNum = 0
        window.title("AccFo - View")
        frame = Frame(window, width=925, height=500,
                      bg='white').place(x=0, y=0)
        Label(frame, image=ViewImg, bg="white").place(x=42, y=124)
        Label(frame, text="AccFo", bg="white", fg=PRIMARY,
              font=HEADING_FONT).place(x=655, y=50)
        Label(frame, text="View", bg="white", fg=PRIMARY,
              font=LARGE_TEXT_FONT).place(x=668, y=100)

        def update():
            service.updateText(passwords.getData(
                passwordFile, lineNum, 'service'))
            username.updateText(passwords.getData(
                passwordFile, lineNum, 'username'))
            password.updateText(passwords.getData(
                passwordFile, lineNum, 'password'))

        def next():
            global lineNum
            lineNum += 1
            if lineNum > (len(info) - 1):
                lineNum = (len(info) - 1)
            update()

        def prev():
            global lineNum
            lineNum -= 1
            if lineNum < 0:
                lineNum = 0
            update()

        Button(frame, image=ArrowRightImg, bg="white",
               cursor="hand2", command=next, border=0).place(x=864, y=251)
        Button(frame, image=ArrowLeftImg, bg="white",
               cursor="hand2", command=prev, border=0).place(x=524, y=251)
        service = UserOutput('Service Name', frame, 553, 171)
        username = UserOutput('Username', frame, 553, 230)
        password = UserOutput('Password', frame, 553, 289)
        update()
        Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
               font=LARGE_TEXT_FONT, command=lambda: Home(user)).place(x=614, y=367, width=160, height=34)


# Checking User Data
with open(USERS_FILE, 'r') as file:
    config = file.readline().rstrip()
if not len(config) > 0:
    SignUp()
else:
    SignIn()

# Executing Mainloop
window.mainloop()
