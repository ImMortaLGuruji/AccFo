def add(fernet):
    serviceName = input("Service Name: ")
    username = input("Username: ")
    password = input("Password: ")

    with open('assets/passwords.txt', 'a') as file:
        file.write(serviceName + "\:-:/" + username + "\:-:/" +
                   fernet.encrypt(password.encode()).decode() + "\n")
