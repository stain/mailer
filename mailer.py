#!/usr/bin/env python

"""
Mass-emailer, reading an email text file and a list of email addresses.
(c) 2009-2015 University of Manchester

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Author: Stian Soiland-Reyes <stian@soiland-reyes.com>
http://orcid.org/0000-0001-9842-9718

https://github.com/stain/mailer


On first run, ~/.mailer is created, and must be configured with the
smtp details.

Tested with smtp.gmail.com.
"""


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
        sys.exit(2)
    if config().get("email", "sender") == DUMMY_USER:
        print >>sys.stderr, "You need to configure 'email' settings in", _configpath()
        sys.exit(3)
    _smtp = smtplib.SMTP(config().get("smtp", "host"), config().getint("smtp", "port"))
    if (config().getboolean("smtp", "tls")):
        _smtp.starttls()
    if (config().has_option("smtp", "username")):
        _smtp.login(config().get("smtp", "username"), config().get("smtp", "password"))
    return _smtp

def send_email(email_filename, to, counter, cc=None):
    text = open(email_filename).read()
    if "John Doe" in text:
        print >>sys.stderr, "You need to edit", email_filename
        sys.exit(4)

    ## template to insert a tracking counter that is
    ## unique per email, e.g. into the Subject field
    ## or signature. Note that the counter starttls
    ## from 00 for each execution.
    text = text.replace("--counter--", "%02x" % counter)
    if cc:
        ## template to insert the name of the first CC-ed person
        ## into message, e.g. the recommending "friend"
        first_cc = cc[0].split("<")[0].strip()
        text = text.replace("--friend--", first_cc)
    else:
        ## some kind of fallback
        text = text.replace("--friend--", "someone")

    msg = email.message_from_string(text)

    # Set standard headers if not already read from
    # file
    msg["MIME-Version"]= "1.0"
    if not msg["Content-Type"]:
        msg["Content-Type"] = "text/plain; charset=UTF-8"

    sender_email = config().get("email", "sender")
    sender_from = config().get("email", "from")
    msg["Sender"] = sender_email
    if not msg["From"]:
        msg["From"] = "%s <%s>" % (sender_from, sender_email)
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-Id"] = email.utils.make_msgid("mailer.py")
    msg["To"] = to
    if (cc):
        msg["Cc"] = ", ".join(cc)
    #to_email = re.split("[<>]", to)[1]
    #print to_email
    ## sendmail seems to parse "Blah Blah <>" format?

    recipients = [to]
    if cc:
        recipients += cc
    smtp().sendmail(sender_email, recipients, msg.as_string())

def mass_mailer(email_filename, addresses_filename):
    all = open(addresses_filename)
    counter = 0
    for recipient in all:
        recipient = recipient.strip()
        if "johndoe@example.com" in recipient:
            print >>sys.stderr, "You need to edit", email_filename
            sys.exit(5)
        cc = []
        if ("\t") in recipient:
            # A line with CC
            fields = recipient.split("\t")
            recipient = fields[0]
            cc = fields[1:]
        if recipient.count("<") > 1:
            print "FAILED: More than one email address on line - use \\t (tab character)"
            return
        counter += 1
        sent = False
        try:
            while not sent:
                try:
                    send_email(email_filename, recipient, counter, cc)
                    print recipient,
                    print "%02x" % counter
                    for also in cc:
                        print "      Cc:", also
                    sent = True
                except smtplib.SMTPServerDisconnected, ex:
                    print recipient,
                    print repr(ex)
                    print "Reconnecting in 60 seconds"
                    _smtp = None
                    time.sleep(60)
        except Exception, ex:
            print recipient,
            print repr(ex)
        time.sleep(1)

if __name__ == "__main__":
    config()
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
