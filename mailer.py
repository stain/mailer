#!/usr/bin/env python

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
    if not config().has_section("email"):
        config().add_section("email")
    config().set("email", "sender", DUMMY_USER)
    config().set("email", "from", "Dummy User")

_smtp = None
def smtp():
    global _smtp
    if _smtp is not None:
        return _smtp
    if config().get("smtp", "username") == DUMMY_USER:
        print >>sys.stderr, "You need to configure 'smtp' settings in", _configpath()
        sys.exit(1)
    if config().get("email", "sender") == DUMMY_USER:
        print >>sys.stderr, "You need to configure 'email' settings in", _configpath()
        sys.exit(1)
    _smtp = smtplib.SMTP(config().get("smtp", "host"), config().getint("smtp", "port"))
    if (config().getboolean("smtp", "tls")):
        _smtp.starttls()
    if (config().has_option("smtp", "username")):    
        _smtp.login(config().get("smtp", "username"), config().get("smtp", "password"))
    return _smtp

def send_email(email_filename, to, counter):
    text = open(email_filename).read()
    text = text.replace("--counter--", "%02x" % counter)
    msg = email.message_from_string(text)
    msg["To"] = to
    to_email = re.split("[<>]", to)[1]
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-Id"] = email.utils.make_msgid("mailer.py")
    smtp().sendmail("stian@mygrid.org.uk", to, msg.as_string())

def mass_mailer(email_filename, addresses_filename):
    all = open(addresses_filename)
    counter = 0
    for recipient in all:
        recipient = recipient.strip()
        counter += 1
        print recipient,
        try:
            send_email(email_filename, recipient, counter)
            print "%02x" % counter 
        except Exception, ex:
            print repr(ex)
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage:", sys.argv[0], "email.txt", "addresses.txt"
        print ""
        print "Where email.txt is the RC822 formatted email (with headers)"
        print "and addresses.txt is a list of addresses to email, in the form"
        print ""
        print "First Last <email@example.com>"
        print ""
        sys.exit(1)

    mass_mailer(sys.argv[1], sys.argv[2])

