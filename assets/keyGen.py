from cryptography.fernet import Fernet


def keyGen():
    key = Fernet.generate_key()
    with open("assets/key.key", "wb") as keyFile:
        keyFile.write(key)
