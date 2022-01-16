from cryptography.fernet import Fernet
from assets.setKey import setKey
from assets.add import add
from assets.gen import gen
from assets.view import view

fernet = Fernet(setKey())

running = True
while running:
    mode = input("What would you like to do (add/gen/view/quit)? ").lower()
    if mode == "add":
        add(fernet)
    elif mode == "gen":
        gen(fernet)
    elif mode == "view":
        view(fernet)
    elif mode == "quit":
        running = False
    else:
        print("Invalid mode")
