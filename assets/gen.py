from assets.genPwd import genPwd


def gen(fernet):
    serviceName = input("Service Name: ")
    username = input("Username: ")
    password = genPwd(int(input("Password length: ")))

    with open('assets/passwords.txt', 'a') as file:
        file.write(serviceName + "\:-:/" + username + "\:-:/" +
                   fernet.encrypt(password.encode()).decode() + "\n")

    print("Generated password: " + password)
