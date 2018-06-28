#!/usr/bin/python
# coding: utf-8

import aiml
import prologHandler
import textHandler
import emailHandler
import scholar
import os
import socket
import datetime
import sys


### VARIABLES ###
printed = False
filesVerified = False
SERVER = "irc.freenode.net"
CHANNEL = "#testebruno"
BOTNICK = "chatterbot_pc"
GREETINGS = ' :Olá, seja bem vindo! Sou um robô de conversação (chatterbot) e estou pronto para conversar ! Do que vamos falar hoje ?'

### METHODS AND FUNCTIONS ###
def doPreProcessing(k, userName, input):
    # If the new input is Data to be stored
    if (textHandler.typeOfInput(input) == 'certeza' or textHandler.typeOfInput(input) == 'duvida'):
        analyzeDataToStore(k, userName, input)

def doPostProcessing(k, userName, brainOutput):
    executeMethod(k, userName, brainOutput)

def analyzeDataToStore(k, userName, input):
    qtd = prologHandler.isAlreadySaved(userName, textHandler.clearInput(input))
    # Only saves if the new data wasn't already on the Prolog base
    if qtd == 0:
        prologHandler.saveOnProlog(userName, k.getBotPredicate("topic"), textHandler.typeOfInput(input), textHandler.clearInput(input))
    # If it is already on Prolog, Update it's description
    elif qtd > 0:
        resolvePrologCollision(userName, textHandler.typeOfInput(input), textHandler.clearInput(input))

def resolvePrologCollision(userName, description, input):
    global printed

    savedDescription = prologHandler.getDescriptionOfDataSaved(userName, input)
    if (description == savedDescription):
        printed = True
        output = "Você já digitou esta afirmação! O que mais podemos falar sobre esse assunto?"
        ircsock.send("PRIVMSG "+ CHANNEL +" :"+ output+"\n")
        textHandler.writeLog(BOTNICK,output)
    else:
        printed = True
        output = "Antes esta era uma {savedDescription}, mas agora você disse que é uma {description}. ".format(savedDescription=savedDescription,description=description)
        output = output + 'Estou atualizando o que sei sobre isto! O que mais podemos falar sobre esse assunto?'
        prologHandler.swapDescription(userName, savedDescription, description, input)
        ircsock.send("PRIVMSG "+ CHANNEL +" :"+ output+"\n")
        textHandler.writeLog(BOTNICK,output)

def executeMethod(k, userName, brainOutput):
    global printed
    output = ''

    if (brainOutput.find("listCertezas()") <> -1):
        printStoredData(k, userName, 'element', 'TOPICLESS', 'certeza')
    elif (brainOutput.find("listCertezas(") <> -1):
        printStoredData(k, userName, 'element', brainOutput[len("listCertezas("):-1], 'certeza')
    elif (brainOutput.find("listDuvidas()") <> -1):
        printStoredData(k, userName, 'element', 'TOPICLESS', 'duvida')
    elif (brainOutput.find("listDuvidas(") <> -1):
        printStoredData(k, userName, 'element', brainOutput[len("listDuvidas("):-1], 'duvida')
    elif (brainOutput.find("setTopic(") <> -1):
        printed = True
        k.setBotPredicate("topic",brainOutput[len("setTopic("):-1])
        output = "Ok, então falaremos sobre {topic}, por hora. O que você quer falar sobre este assunto?".format(topic=k.getBotPredicate("topic"))
        ircsock.send("PRIVMSG "+ CHANNEL +" :"+ output+"\n")
        textHandler.writeLog(BOTNICK,output)
    elif (brainOutput.find("getTopic()") <> -1):
        printed = True
        output = "Estamos falando sobre {topic}. O que você quer falar sobre este assunto?".format(topic=k.getBotPredicate("topic"))
        ircsock.send("PRIVMSG "+ CHANNEL +" :"+ output+"\n")
        textHandler.writeLog(BOTNICK,output)
    elif (brainOutput.find("getArticle(") <> -1):
        printed = True

        subject = brainOutput[len("getArticle("):-1]
        year = datetime.date.today().year - 10

        article = os.popen('python scholar.py -c 1 --after {year} --no-citations -A "{subject}" "" '.format(year=year, subject=textHandler.removeAccents(subject))).read()
        output = 'Estou te passando um artigo sobre {subject} encontrado no Google Acadêmico, a leitura pode lhe ser útil!\n\n{article}'.format(subject=subject, article=article)

        for line in output.splitlines():
            line = line.strip('\n\r')

            if (line is not None and line <> ''):
                ircsock.send("PRIVMSG "+ CHANNEL +" :"+ line+"\n")

        textHandler.writeLog(BOTNICK,output)

def printStoredData(kernel, userName, typeOf, topic, description):
    global printed
    if (brainOutput.find("listCertezas(") <> -1):
        printed = True
        prologOutput = prologHandler.loadFromProlog(userName, topic, description)
    elif (brainOutput.find("listDuvidas(") <> -1):
        printed = True
        prologOutput = prologHandler.loadFromProlog(userName, topic, description)
    elif (brainOutput.find("getTopic()") <> -1):
        printed = True
        k.setBotPredicate("topic",brainOutput[len("getTopic("):-1])
        prologOutput = prologOutput.replace('getTopic()', kernel.getBotPredicate())

    if (printed):
        ircsock.send("PRIVMSG "+ CHANNEL +" :"+ prologOutput+"\n")
        textHandler.writeLog(BOTNICK, prologOutput)

def ping():
	ircsock.send("PONG :pingis\r\n")

####################################################################################################################
if (__name__ == '__main__'):
    try:
        #Verify Required Files
        textHandler.verifyRequiredFiles()

        k = aiml.Kernel()
        k.learn("questionador.aiml") # Learn from AIML File

        # mannually insert channel name, if needed
        newChannelName = raw_input("CHANNEL: ")
        if (newChannelName != ''):
            CHANNEL = newChannelName

        # IRC Connection
        ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ircsock.connect((SERVER, 6667))
        ircsock.send("NICK %s \r\n" % (BOTNICK))
        ircsock.send("USER %s %s %s :Ssssh\r\n" % (BOTNICK,BOTNICK,BOTNICK))

        ircsock.send("JOIN "+ CHANNEL +"\r\n")
        prologHandler.reloadPrologFile()

        #Confirms connection on Terminal
        print "\n### CONNECTION ESTABILISHED ### \n\nServer Name: {server} \nChannel name: {channel}\n\n###############################".format(server=SERVER, channel = CHANNEL)


        # Main Loop of the Chatterbot
        while True:
            IRCInput = ircsock.recv(2048) # receive data from the server
            IRCInput = IRCInput.strip('\n\r') # removing unnecessary linebreaks

            # chatterbot logged, player joins : greets on JOIN confirmations
            if IRCInput.find(' JOIN ') != -1 :
                ircsock.send("PRIVMSG "+ CHANNEL + GREETINGS + "\r\n")
                textHandler.writeLog(BOTNICK, GREETINGS[2:])
                prologHandler.reloadPrologFile()

            # only user messages
            if IRCInput.find(' PRIVMSG ') != -1 :
                userName = textHandler.getDataFromIRCInput(IRCInput, 'userName')
                userInput = textHandler.getDataFromIRCInput(IRCInput, 'msg')

                textHandler.writeLog(userName,userInput)

                #Pre-processing
                doPreProcessing(k, userName, userInput)

                # If data wasn't printed on Pre-Processing, keep going
                if not printed:
                    #Get response from AIML file
                    brainOutput = k.respond(userInput)

                    #post-processing
                    doPostProcessing(k, userName, brainOutput)

                    # if the answer wasn't displayed during a method execution, do it now
                    if not printed:
                        ircsock.send("PRIVMSG "+ CHANNEL +" :"+ brainOutput+"\n")
                        textHandler.writeLog(BOTNICK, brainOutput)

                # Always resets the Global Variable to False
                printed = False

            # Check for Ping, answer
            if IRCInput.find("PING :") != -1:
        		ping()
    except:
        print "Unexpected error:", sys.exc_info()
        emailHandler.sendMailOnError(sys.exc_info())
