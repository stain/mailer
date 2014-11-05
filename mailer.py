#!/usr/bin/env python2.5

import email
import email.utils
import time
import re

import smtplib
smtp = smtplib.SMTP("smtp.gmail.com", 587) 
smtp.starttls()
smtp.login("stian@mygrid.org.uk", "*********")


def send_email(to, counter):
    text = open("email.txt").read()
    text = text.replace("d3", "%02x" % counter)
    msg = email.message_from_string(text)
    msg["To"] = to
    to_email = re.split("[<>]", to)[1]
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-Id"] = email.utils.make_msgid("taverna")
    smtp.sendmail("stian@mygrid.org.uk", to, msg.as_string())

def mass_mailer():
    counter = 240
#    all = open("addresses.txt")
    all = open("test-addresses.txt")
    for recipient in all:
        recipient = recipient.strip()
        counter += 1
        print recipient,
        try:
            send_email(recipient, counter)
            print "%02x" % counter 
        except Exception, ex:
            print repr(ex)
        time.sleep(1)

if __name__ == "__main__":
    mass_mailer()

