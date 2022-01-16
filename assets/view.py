def view(fernet):
    with open('assets/passwords.txt', 'r') as file:
        for line in file.readlines():
            data = line.rstrip()
            service, username, passw = data.split("\:-:/")
            print("\nService name:", service, "\nUsername:", username, "\nPassword:",
                  fernet.decrypt(passw.encode()).decode() + "\n")
