import os.path as path
from assets.keyGen import keyGen


def setKey():
    if path.isfile("assets/key.key") == False:
        keyGen()
    with open("assets/key.key", "r") as keyFile:
        key = keyFile.read()
    return key
