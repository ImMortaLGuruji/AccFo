# Importing Required Modules
from tkinter import Tk, PhotoImage, Toplevel, Entry, Frame, Button, Label
from os import getcwd, path, mkdir, urandom, listdir
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode
from sqlite3 import connect
from cryptography.fernet import Fernet
from random import choice, shuffle
from array import array
from pyperclip import copy
from sys import exit
from fnmatch import filter

# Initializing Application Window In The Center Of Screen
window = Tk()
icon = PhotoImage(file="assets/images/icon.png")
window.iconphoto(True, icon)
window.resizable(False, False)
window.title("AccFo")
windowWidth = 925
windowHeight = 500
screenWidth = window.winfo_screenwidth()
screenHeight = window.winfo_screenheight()
x = int((screenWidth/2) - (windowWidth/2))
y = int((screenHeight/2) - (windowHeight/2))
window.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
window.configure(bg="white")

# Loading Images
ArrowLeftImg = PhotoImage(file='assets/images/ArrowLeftImg.png')
ArrowRightImg = PhotoImage(file='assets/images/ArrowRightImg.png')
SignUpImg = PhotoImage(file='assets/images/SignUpImg.png')
SignInImg = PhotoImage(file='assets/images/SignInImg.png')
HomeImg = PhotoImage(file='assets/images/HomeImg.png')
HomeTextImg = PhotoImage(file='assets/images/HomeTextImg.png')
ErrorImg = PhotoImage(file='assets/images/ErrorImg.png')
AddImg = PhotoImage(file='assets/images/AddImg.png')
GenerateImg = PhotoImage(file='assets/images/GenerateImg.png')
RemoveImg = PhotoImage(file='assets/images/RemoveImg.png')
ViewImg = PhotoImage(file='assets/images/ViewImg.png')

# Defigning Variables
show = "show"
hide = "hide"
lineNum = 0
ID = 0

# Defigning Fonts
HEADING_FONT = ('Regular', 22)
LARGE_TEXT_FONT = ('Regular', 16)
MEDIUM_TEXT_FONT = ('Regular', 12)
SMALL_TEXT_FONT = ('Regular', 9)

# Defigning Colours
PRIMARY = '#FF4E5A'
TEXT = '#4E4E4E'
SECONDARY = '#1C2F37'

# Creating Data Folder
cwd = getcwd()
dir = path.join(cwd + "/assets/Data")
if not path.exists(dir):
    mkdir(dir)


# Database Management
class Database():
    def __init__(self):
        pass

    # Function To Generate Encryption/Decryption Key
    def generateKey(self, username: str, salt: bytes, password: str):
        master = password.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=500000,
        )
        key = urlsafe_b64encode(kdf.derive(master)).decode()
        self.fernet = Fernet(key)
        if not path.isfile(f"assets/Data/{username}.db"):
            with open(f"assets/Data/{username}.db", 'a'):
                pass
        self.connection = connect(f"assets/Data/{username}.db")
        self.cursor = self.connection.cursor()

    # Function To Add A User To Database
    def addUser(self, username: str, salt: bytes, password: str):
        password = self.fernet.encrypt(password.encode()).decode()
        query = '''
        CREATE TABLE userData (
            username TEXT,
            salt BLOB,
            password TEXT
        )'''
        self.cursor.execute(query)
        query = '''
        INSERT INTO userData (username, salt, password)
        VALUES (?, ?, ?)'''
        self.cursor.execute(query, (username, salt, password))
        self.connection.commit()

    # Function To Login User
    def loginUser(self, password: str):
        query = "SELECT password FROM userData"
        self.cursor.execute(query)
        masterPassword = self.cursor.fetchone()[0]
        try:
            masterPassword = self.fernet.decrypt(
                masterPassword.encode()).decode()
        except:
            return False
        if masterPassword == password:
            return True

    # Function To Check If A User Exists In Database
    def userExists(self, username: str):
        if path.isfile(f"assets/Data/{username}.db"):
            return True
        return False

    # Function To Get Salt Of A User
    def getUserSalt(self, username: str):
        connection = connect(f"assets/Data/{username}.db")
        cursor = connection.cursor()
        query = f"SELECT salt FROM userData"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        connection.close()
        return result

    # Function To Add Data To Database
    def addData(self, service: str, username: str, password: str):
        password = self.fernet.encrypt(password.encode()).decode()
        query = '''
        CREATE TABLE IF NOT EXISTS accountData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT,
            username TEXT,
            password TEXT
        )'''
        self.cursor.execute(query)
        query = '''
        INSERT INTO accountData (service, username, password)
        VALUES (?, ?, ?)'''
        self.cursor.execute(query, (service, username, password))
        self.connection.commit()

    # Function To Get Data From Database
    def getData(self, id: int, value: str):
        query = f"SELECT {value} FROM accountData WHERE id = ?"
        self.cursor.execute(query, (id,))
        result = self.cursor.fetchone()[0]
        if value == "password":
            result = self.fernet.decrypt(result.encode()).decode()
        return result

    # Function To Remove Data From Database
    def removeData(self, id: int):
        query = "DELETE FROM accountData WHERE id = ?"
        self.cursor.execute(query, (id,))
        self.connection.commit()

    # Function To Get List Of IDs
    def getID(self):
        query = "SELECT id FROM accountData"
        try:
            self.cursor.execute(query)
        except:
            return []
        return self.cursor.fetchall()


# Initializing Database
database = Database()


# Popup window
def popup(message: str):
    popupWin = Toplevel(window)
    popupWin.resizable(False, False)
    popupWin.title("AccFo")
    windowWidth = 500
    windowHeight = 75
    screenWidth = 925
    screenHeight = 500
    x = int((screenWidth/2) - (windowWidth/2)) + window.winfo_x()
    y = int((screenHeight/2) - (windowHeight/2)) + window.winfo_y()
    popupWin.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
    popupWin.configure(bg="white")
    Label(popupWin, text=message, fg=TEXT,
          bg='white', font=LARGE_TEXT_FONT).pack()
    Button(popupWin, text="OK", fg='white', bg=PRIMARY, font=LARGE_TEXT_FONT,
           border=0, cursor="hand2", command=popupWin.destroy).pack()


# Function to generate a password with given length
def genPwd(passLen: int):
    if passLen < 8:
        passLen = 8

    elif passLen > 25:
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


# Text Input Box
class TextInput():
    def __init__(self, value: str, frame: Frame, x: int, y: int):
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
    def __init__(self, value: str, frame: Frame, x: int, y: int):
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
class UserOutputButton():
    def __init__(self, value: str, frame: Frame, x: int, y: int):
        self.value = value
        self.button = Button(frame, text=self.value, font=MEDIUM_TEXT_FONT, bg="white", fg=TEXT, cursor="hand2",
                             command=self.copyText, border=0)
        self.button.place(x=x, y=y, width=281, height=29)

    def copyText(self):
        copy(self.value)
        popup("Copied!")

    def updateText(self, value: str):
        self.value = value
        self.button['text'] = self.value

    def updatePasswordText(self, value: str):
        self.value = value
        self.button['text'] = '----'


# User Output Text
class UserOutputText():
    def __init__(self, value: str, frame: Frame, x: int, y: int):
        self.value = value
        self.label = Label(frame, text=self.value,
                           font=MEDIUM_TEXT_FONT, bg="white", fg=TEXT)
        self.label.place(x=x, y=y, width=281, height=29)

    def updateText(self, value: str):
        self.value = value
        self.label['text'] = self.value

    def updatePasswordText(self, value: str):
        self.value = value
        self.label['text'] = '----'


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
        salt = urandom(16)
        if database.userExists(username.get()):
            popup(f'{username.get()} already exists!')
        else:
            database.generateKey(username.get(), salt, password.get())
            database.addUser(username.get(), salt, password.get())
            popup('Successfully signed up!')
            SignIn()

    def validate():
        count = len(filter(listdir('assets/Data'), '*.db'))
        if count == 0:
            popup("No accounts created!")
            SignUp()
        else:
            SignIn()

    Button(frame, text="Sign Up", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=logUser).place(x=614, y=350, width=160, height=34)
    Label(frame, text="Already have an account?", bg='white', fg=TEXT,
          font=SMALL_TEXT_FONT).place(x=576, y=420)
    Button(frame, text="Sign In", bg='white', fg=PRIMARY, border=0,
           cursor='hand2', font=SMALL_TEXT_FONT, command=validate).place(x=718, y=420)


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
        if database.userExists(username.get()):
            salt = database.getUserSalt(username.get())
            database.generateKey(username.get(), salt, password.get())
            if database.loginUser(password.get()):
                popup(f'Successfully logged in as {username.get()}!')
                Home()
            else:
                popup('Invalid Password!')
        else:
            popup('Invalid username!')

    Button(frame, text="Sign In", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=validate).place(x=614, y=350, width=160, height=34)
    Label(frame, text="Don't have an account?", bg='white', fg=TEXT,
          font=SMALL_TEXT_FONT).place(x=581, y=420)
    Button(frame, text="Sign Up", bg='white', fg=PRIMARY, border=0,
           cursor='hand2', font=SMALL_TEXT_FONT, command=SignUp).place(x=710, y=420)


# Home Frame
def Home():
    window.title("AccFo")
    frame = Frame(window, width=925, height=500, bg='white').place(x=0, y=0)
    Label(frame, image=HomeImg, bg="white").place(x=42, y=124)
    Label(frame, image=HomeTextImg, bg="white").place(x=348, y=444)
    Label(frame, text="AccFo", bg="white", fg=PRIMARY,
          font=HEADING_FONT).place(x=655, y=50)
    Label(frame, text="Home", bg="white", fg=PRIMARY,
          font=LARGE_TEXT_FONT).place(x=663, y=100)

    Button(frame, text="Add", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=Add).place(x=614, y=168, width=160, height=34)
    Button(frame, text="Generate", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=Generate).place(x=614, y=215, width=160, height=34)
    Button(frame, text="Remove", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=Remove).place(x=614, y=262, width=160, height=34)
    Button(frame, text="View", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=View).place(x=614, y=309, width=160, height=34)
    Button(frame, text="Quit", bg=PRIMARY, fg='white', border=0,
           cursor='hand2', font=LARGE_TEXT_FONT, command=exit).place(x=614, y=356, width=160, height=34)


# Error Frame
def Error():
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
           font=LARGE_TEXT_FONT, command=Home).place(x=614, y=367, width=160, height=34)


# Add Frame
def Add():
    window.title("AccFo - Add")
    frame = Frame(window, width=925, height=500, bg='white').place(x=0, y=0)
    Label(frame, image=AddImg, bg="white").place(x=42, y=124)
    Label(frame, text="AccFo", bg="white", fg=PRIMARY,
          font=HEADING_FONT).place(x=655, y=50)
    Label(frame, text="Add", bg="white", fg=PRIMARY,
          font=LARGE_TEXT_FONT).place(x=668, y=100)

    service = TextInput("Service Name", frame, 553, 171)
    username = TextInput("Username", frame, 553, 230)
    password = PasswordInput("Password", frame, 553, 289)

    def addData():
        database.addData(service.get(),
                         username.get(), password.get())
        popup('Successfully saved informaton!')
        Add()

    Button(frame, text="Save", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=addData).place(x=524, y=367, width=160, height=34)
    Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=Home).place(x=704, y=367, width=160, height=34)


# Generate Frame
def Generate():
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
    password = PasswordInput("Password", frame, 553, 307)

    def place():
        password.place.delete(0, "end")
        try:
            password.place.insert(0, genPwd(int(passwordLength.get())))
        except:
            popup("Invalid password length!")
            password.place.insert(0, "Password")

    def addData():
        database.addData(service.get(),
                         username.get(), password.get())
        popup('Successfully saved informaton!')
        Generate()

    Button(frame, text="Save", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=addData).place(x=524, y=367, width=160, height=34)
    Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=Home).place(x=704, y=367, width=160, height=34)
    Button(frame, text="Generate", bg=PRIMARY, fg='white', border=0, cursor='hand2',
           font=LARGE_TEXT_FONT, command=place).place(x=615, y=411, width=160, height=34)


# Remove Frame
def Remove():
    global lineNum, ID
    lineNum = 0
    info = database.getID()
    if len(info) == 0:
        Error()
    else:
        ID = info[0][0]
        window.title("AccFo - Remove")
        frame = Frame(window, width=925, height=500,
                      bg='white').place(x=0, y=0)
        Label(frame, image=RemoveImg, bg="white").place(x=42, y=124)
        Label(frame, text="AccFo", bg="white", fg=PRIMARY,
              font=HEADING_FONT).place(x=655, y=50)
        Label(frame, text="Remove", bg="white", fg=PRIMARY,
              font=LARGE_TEXT_FONT).place(x=651, y=100)

        def update():
            service.updateText(database.getData(ID, 'service'))
            username.updateText(database.getData(ID, 'username'))
            password.updatePasswordText(database.getData(ID, 'password'))

        def next():
            global lineNum, ID
            lineNum += 1
            if lineNum > (len(info) - 1):
                lineNum = (len(info) - 1)
            ID = info[lineNum][0]
            update()

        def prev():
            global lineNum, ID
            lineNum -= 1
            if lineNum < 0:
                lineNum = 0
            ID = info[lineNum][0]
            update()

        def removeData():
            database.removeData(ID)
            popup('Successfully removed information!')
            Remove()

        Button(frame, image=ArrowRightImg, bg="white",
               cursor="hand2", command=next, border=0).place(x=864, y=251)
        Button(frame, image=ArrowLeftImg, bg="white",
               cursor="hand2", command=prev, border=0).place(x=524, y=251)
        service = UserOutputText('Service Name', frame, 553, 171)
        username = UserOutputText('Username', frame, 553, 230)
        password = UserOutputText('Password', frame, 553, 289)
        update()
        Button(frame, text="Remove", bg=PRIMARY, fg='white', border=0, cursor='hand2', font=LARGE_TEXT_FONT,
               command=removeData).place(x=524, y=367, width=160, height=34)
        Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
               font=LARGE_TEXT_FONT, command=Home).place(x=704, y=367, width=160, height=34)


# View Frame
def View():
    global lineNum, ID
    lineNum = 0
    info = database.getID()
    if len(info) == 0:
        Error()
    else:
        ID = info[0][0]
        window.title("AccFo - View")
        frame = Frame(window, width=925, height=500,
                      bg='white').place(x=0, y=0)
        Label(frame, image=ViewImg, bg="white").place(x=42, y=124)
        Label(frame, text="AccFo", bg="white", fg=PRIMARY,
              font=HEADING_FONT).place(x=655, y=50)
        Label(frame, text="View", bg="white", fg=PRIMARY,
              font=LARGE_TEXT_FONT).place(x=668, y=100)

        def update():
            service.updateText(database.getData(ID, 'service'))
            username.updateText(database.getData(ID, 'username'))
            password.updatePasswordText(database.getData(ID, 'password'))

        def next():
            global lineNum, ID
            lineNum += 1
            if lineNum > (len(info) - 1):
                lineNum = (len(info) - 1)
            ID = info[lineNum][0]
            update()

        def prev():
            global lineNum, ID
            lineNum -= 1
            if lineNum < 0:
                lineNum = 0
            ID = info[lineNum][0]
            update()

        Button(frame, image=ArrowRightImg, bg="white",
               cursor="hand2", command=next, border=0).place(x=864, y=251)
        Button(frame, image=ArrowLeftImg, bg="white",
               cursor="hand2", command=prev, border=0).place(x=524, y=251)
        service = UserOutputButton('Service Name', frame, 553, 171)
        username = UserOutputButton('Username', frame, 553, 230)
        password = UserOutputButton('Password', frame, 553, 289)
        update()
        Button(frame, text="Back", bg=PRIMARY, fg='white', border=0, cursor='hand2',
               font=LARGE_TEXT_FONT, command=Home).place(x=614, y=367, width=160, height=34)


# Checking If Users Exist
count = len(filter(listdir('assets/Data'), '*.db'))
if count == 0:
    SignUp()
else:
    SignIn()

# Executing Mainloop
window.mainloop()
try:
    database.connection.close()
except:
    pass
