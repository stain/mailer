#!/usr/bin/env python2.5

from ConfigParser import ConfigParser
import email
import email.utils
import getpass
import os
import re
import smtplib
import sys
import time

DUMMY_USER="nobody@gmail.com"

def _configpath():
    configpath = os.path.expanduser("~/.mailer")
    if not os.path.exists(configpath):
        open(configpath, "w").close()
        os.chmod(configpath, 0600)
    return configpath

_config = None
def config():
    global _config
    if _config is not None:
        return _config
    _config = ConfigParser()
    _config.read(_configpath())
    if not _config.has_section("smtp"):
        template_config()
        save_config()
    return _config

def save_config():
    fp = open(_configpath(), "w")
    try:
        config().write(fp)
    finally:
        fp.close()

def template_config():
    if not config().has_section("smtp"):
        config().add_section("smtp")
    config().set("smtp", "host", "smtp.gmail.com")    
    config().set("smtp", "port", 587)    
    config().set("smtp", "tls", True)
    config().set("smtp", "username", DUMMY_USER)
    config().set("smtp", "password", "WrongPassword")

if config().get("smtp", "username") == DUMMY_USER:
    print >>sys.stderr, "You need to configure smtp settings in", _configpath()
    sys.exit(1)


smtp = smtplib.SMTP(config().get("smtp", "host"), config().getint("smtp", "port"))

if (config().getboolean("smtp", "tls")):
    smtp.starttls()
if (config().has_option("smtp", "username")):    
    smtp.login(config().get("smtp", "username"), config().get("smtp", "password"))


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

