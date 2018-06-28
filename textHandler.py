#!/usr/bin/python
# coding: utf-8

import os
import unicodedata
import time

def writeLog(usr,input):
    with open(getLogFileName(), "a") as log:
        currentTime = time.strftime("%H:%M:%S")
        currentDate = time.strftime("%d/%m/%Y")
        log.write("[{currentTime} - {currentDate}] {usr}> {resposta} \n".format(currentTime=currentTime, currentDate=currentDate, usr=usr, resposta=input))

def writePrologFile(prologLine):
    with open(getPrologFileName(), "a") as plFile:
        plFile.write("{prologLine} \n".format(prologLine=prologLine))

def removeAccents(s):
    letras_acentuadas = ['á','é','í','ó','ú','à','è','ì','ò','ù','ã','ẽ','ĩ','õ','ũ','â','ê','î','ô','û','ü','ç']
    letras_nao_acentuadas = ['a','e','i','o','u','a','e','i','o','u','a','e','i','o','u','a','e','i','o','u','u','c']
    for idx in range(0, len(letras_acentuadas)):
        s = s.replace(letras_acentuadas[idx], letras_nao_acentuadas[idx])

    return s

def getDataFromIRCInput(IRCInput, dataType):
    if dataType == 'userName':
        return IRCInput.split('!')[0][1:]
    if dataType == 'channel':
        return IRCInput.split(' PRIVMSG ')[-1].split(' :')[0]
    if dataType == 'msg':
        return IRCInput.split(' PRIVMSG ')[-1].split(':')[1]

def getDirectoryPath(dirName):
    RESOURCES_PATH = os.path.dirname(os.path.abspath(__file__))
    RESOURCES_PATH = RESOURCES_PATH + '/resources/'
    return RESOURCES_PATH

def getLogFileName():
    RESOURCES_PATH = getDirectoryPath('resources')
    return "{RESOURCES_PATH}log.txt".format(RESOURCES_PATH=RESOURCES_PATH)

def getPrologFileName():
    RESOURCES_PATH = getDirectoryPath('resources')
    return "{RESOURCES_PATH}/logic.pl".format(RESOURCES_PATH=RESOURCES_PATH)

def verifyRequiredFiles():
    # Verify AIML Files
    verifyAIMLFile('questionador.aiml')

    # Verify LOG Files
    LOG_FILE = getLogFileName()
    if os.path.isfile(LOG_FILE) == False:
        open(LOG_FILE, 'w+')

    # Verify PROLOG Files
    PROLOG_FILE = getPrologFileName()
    if os.path.isfile(PROLOG_FILE) == False:
        open(PROLOG_FILE, 'w+')

def verifyAIMLFile(fileName):
    if os.path.isfile(fileName) == False:
        print "ERRO: Arquivo 'questionador.aiml' não encontrado."
        exit()

def typeOfInput (input):
    if (any([input.find("sei que") <> -1,input.find("validei que") <> -1,input.find("constatei que") <> -1])):
        return 'certeza'
    elif (any([input.find("acho que") <> -1,input.find("ouvi que") <> -1])):
        return 'duvida'

def clearInput(input):
    startPos = 0
    certeza1, certeza2, certeza3 = 'sei que ', 'validei que ', 'constatei que '
    duvida1, duvida2 = 'acho que ', 'ouvi que '

    if (typeOfInput(input) == 'certeza'):
        if (input.find(certeza1) != -1):
            startPos = input.find(certeza1) + len(certeza1)
        if (input.find(certeza2) != -1):
            startPos = input.find(certeza2) + len(certeza2)
        if (input.find(certeza3) != -1):
            startPos = input.find(certeza3) + len(certeza3)

    elif (typeOfInput(input) == 'duvida'):
        if (input.find(duvida1) != -1):
            startPos = input.find(duvida1) + len(duvida1)
        if (input.find(duvida2) != -1):
            startPos = input.find(duvida2) + len(duvida2)

    return input[startPos:]

def numberOfRelatedWords(text1,text2):
    qtd = 0
    for word in text1.split():
        for word2 in text2.split():
            if (word == word2):
                qtd+=1
    return qtd

def getNumberOfWords(text):
    qtd=0
    for word in text.split():
        qtd+=1
    print qtd

def removeLineFromPrologFile(lineNumber):
    #filename = os.getcwd()+'/resources/logic.pl'
    filename = getPrologFileName()

    #puts all lines in a list
    with open(filename,"r") as prologFile:
        lines = list(prologFile)

    #delete regarding element
    del lines[lineNumber - 1]

    #rewrite the file from list:
    with open(filename,"w") as prologFile:
        for n in lines:
            prologFile.write(n)
