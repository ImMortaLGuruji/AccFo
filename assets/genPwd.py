import random
import array


def genPwd(passLen):
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
