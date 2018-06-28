#!/usr/bin/python
# coding: utf-8

import os
import pyswip
import textHandler
import time

### element structure
# element(userName, currentDate, currentTime, topic, description, input)

p = pyswip.Prolog()

def reloadPrologFile():
    # Open files, retract each line and add it subsequently.
    # This loads all lines from 'logic.pl' and ensures that there is no repetition
    with open(textHandler.getPrologFileName()) as prologFile:
        for line in prologFile:
            line = line.rstrip('\n')
            result = list(p.query('retract({line}),fail'.format(line=line)))
            p.assertz(line.rstrip('\n'))

def swapDescription(userName, savedDescription, newDescription, input):
    #swaps on 'logic.pl'
    lineNumber, line = getLineWithInput(input)
    #removes the line
    textHandler.removeLineFromPrologFile(lineNumber)

    #alters the line
    listFromLine = list(line.split(','))

    savedDate = listFromLine[1]
    savedTime = listFromLine[2]
    currentTime = "'{time}'".format(time = time.strftime("%H:%M:%S"))
    currentDate = "'{date}'".format(date = time.strftime("%d/%m/%Y"))

    line = line.replace(savedDescription,newDescription)
    line = line.replace(savedDate,currentDate)
    line = line.replace(savedDate,currentDate)
    line = line.replace(savedTime,currentTime)

    #write new line on the end of the file
    with open(textHandler.getPrologFileName(), "a") as prologFile:
        prologFile.write(line)

    #swaps on Prolog memory
    try:
        queryStr = 'element(\'{userName}\',W,X,Y,Z,\'{input}\')'.format(userName=userName,input=input)

        currentTime = "{time}".format(time = time.strftime("%H:%M:%S"))
        currentDate = "{date}".format(date = time.strftime("%d/%m/%Y"))

        for row in list(p.query(queryStr)):
            #saves the old register
            oldPrologInput = 'element(\'{userName}\',\'{currentDate}\',\'{currentTime}\',\'{topic}\',\'{description}\',\'{input}\')'.format(userName=userName,
                                                                                                                                        currentDate=row['W'],
                                                                                                                                        currentTime=row['X'],
                                                                                                                                        topic=row['Y'],
                                                                                                                                        description=row['Z'],
                                                                                                                                        input=input)
            #formats the new register
            newPrologInput = 'element(\'{userName}\',\'{currentDate}\',\'{currentTime}\',\'{topic}\',\'{description}\',\'{input}\')'.format(userName=userName,
                                                                                                                                        currentDate=currentDate,
                                                                                                                                        currentTime=currentTime,
                                                                                                                                        topic=row['Y'],
                                                                                                                                        description=newDescription,
                                                                                                                                        input=input)
            #retract old register
            result = list(p.query('retract({line}),fail'.format(line=oldPrologInput)))
            #assert new register
            p.assertz(newPrologInput)

    except pyswip.prolog.PrologError:
        print 'PrologError on swapDescription'

def getLineWithInput(input):
    filename = textHandler.getPrologFileName()
    lineNumber = 0
    with open(filename) as prologFile:
        for line in prologFile:
            lineNumber += 1
            if line.find(input) <> -1:
                return lineNumber, line

    return 0,''


def saveOnProlog(userName, topic, description, input):
    if not topic:
        topic='TOPICLESS'

    currentTime = time.strftime("%H:%M:%S")
    currentDate = time.strftime("%d/%m/%Y")

    prologInput = 'element(\'{userName}\',\'{currentDate}\',\'{currentTime}\',\'{topic}\',\'{description}\',\'{input}\')'.format(userName=userName,
                                                                                                                                    currentDate=currentDate,
                                                                                                                                    currentTime=currentTime,
                                                                                                                                    topic=topic,
                                                                                                                                    description=description,
                                                                                                                                    input=input)
    textHandler.writePrologFile(prologInput)
    p.assertz(prologInput)

def loadFromProlog(userName, topic, description):
    try:
        if topic == 'TOPICLESS':
            queryStr = 'element(\'{userName}\',W,Z,V,\'{description}\',Y)'.format(userName=userName,description=description)
            fmt_output = ''
            for row in list(p.query(queryStr)):
                fmt_output += ', \"{row}\"'.format(row=row.values()[0])
            return 'Você me disse que suas {description} são: {result}'.format(description=description, result=str(fmt_output[2:]),topic=topic)
        else:
            queryStr = 'element(\'{userName}\',W,Z,\'{topic}\',\'{description}\',Y)'.format(userName=userName,description=description, topic=topic)
            fmt_output = ''
            for row in list(p.query(queryStr)):
                fmt_output += ', \"{row}\"'.format(row=row.values()[0])
            return 'Você me disse que suas {description} sobre {topic} são: {result}'.format(description=description, topic=topic, result=str(fmt_output[2:]))
    except pyswip.prolog.PrologError:
        return 'Ainda não tenho informações para te dar uma resposta. Podemos conversar mais sobre o assunto?'

def isAlreadySaved(userName, input):
    qtd = 0
    try:
        queryStr = 'element(\'{userName}\',W,X,Z,Y,\'{input}\')'.format(userName=userName,input=input)
        for row in list(p.query(queryStr)):
            qtd += 1

        return qtd
    except pyswip.prolog.PrologError:
        # Prolog sempre dá erro caso a query não tenha retorno, portanto retorna 0, ao invés de erro
        # TODO: Achar um tratamento melhor, senão ele vai mascarar erros
        return 0

def getDescriptionOfDataSaved(userName, input):
    qtd = 0
    try:
        queryStr = 'element(\'{userName}\',_,_,_,Y,\'{input}\')'.format(userName=userName, input=input)
        for row in list(p.query(queryStr)):
            return row.values()[0]
    except pyswip.prolog.PrologError:
        print 'Prolog Error on getDescriptionOfDataSaved'
        return 0
