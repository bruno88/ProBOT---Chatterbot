#!/usr/bin/python
# coding: utf-8

import smtplib
import os

def sendMailOnError(errorMsg):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()

    # For Safety, password was stored on Environment Variables with:
    # export SMTP_EMAIL="this is a secret email"
	# export SMTP_PWD="this is a secret password"
    server.login(os.environ['SMTP_EMAIL'], os.environ['SMTP_PWD'])

    aux = "Ocorreu um erro no uso do chatterbot!\n "
    aux += "Mensagem de erro: {errorMsg}\n".format(errorMsg=errorMsg)

    msg = "\r\n".join([
    "From: brunoclemente88@gmail.com",
    "To: brunoclemente88@gmail.com",
    "Subject: O chatterbot fechou irregularmente!",
    aux])

    server.sendmail("brunoclemente88@gmail.com", "brunoclemente88@gmail.com", msg)
    print 'E-Mail enviado com sucesso!'
    server.quit()
