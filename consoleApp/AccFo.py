from cryptography.fernet import Fernet
import os
import random
import array

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


def genPwd(passLen):
    if passLen <= 7:
        passLen = 8
        print("Password length set to:", passLen)

    elif passLen >= 26:
        passLen = 25
        print("Password length set to:", passLen)

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


def add():
    serviceName = input("Service Name: ")
    username = input("Username: ")
    password = input("Password: ")

    with open('data/passwords.txt', 'a') as file:
        file.write(serviceName + "\:-:/" + username + "\:-:/" +
                   fernet.encrypt(password.encode()).decode() + "\n")


def gen():
    serviceName = input("Service Name: ")
    username = input("Username: ")
    passLen = int(input("Password length(8 - 25): "))
    password = genPwd(passLen)

    with open('data/passwords.txt', 'a') as file:
        file.write(serviceName + "\:-:/" + username + "\:-:/" +
                   fernet.encrypt(password.encode()).decode() + "\n")

    print("Generated password: " + password)


def remove():
    info = []
    with open("data/passwords.txt", 'r') as file:
        info = file.readlines()

    if len(info) <= 0:
        print("You have not saved anything yet!\n")

    else:
        lineNum = int(
            input("Which account info would you like to delete: "))
        data = []
        with open("data/passwords.txt", 'r') as file:
            data = file.readlines()

        if lineNum > len(data) or lineNum <= 0:
            print("Invalid number\n")
        else:
            with open("data/passwords.txt", 'w') as file:
                for number, line in enumerate(data):
                    if number not in [lineNum - 1]:
                        file.write(line)

            print("successfully removed!\n")


def view():
    info = []
    with open("data/passwords.txt", 'r') as file:
        info = file.readlines()

    if len(info) <= 0:
        print("You have not saved anything yet!\n")

    else:
        with open('data/passwords.txt', 'r') as file:
            for line in file.readlines():
                data = line.rstrip()
                service, username, passw = data.split("\:-:/")
                print("\nService name:", service, "\nUsername:", username, "\nPassword:",
                      fernet.decrypt(passw.encode()).decode() + "\n")


running = True
while running:
    mode = input("What would you like to do (add/gen/rmv/view/quit)? ").lower()
    if mode == "add":
        add()
    elif mode == "gen":
        gen()
    elif mode == "rmv":
        remove()
    elif mode == "view":
        view()
    elif mode == "quit":
        running = False
    else:
        print("Invalid mode")
