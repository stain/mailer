# mailer.py

Mass-mailer, reading two text files containing email text and
email addresses. Tested with Gmail.

Author: Stian Soiland-Reyes <stian@soiland-reyes.com>
http://orcid.org/0000-0001-9842-9718

Source code: https://github.com/stain/mailer


This is not intended for spam purposes, as it:

a) Is too slow for very large volumes
b) Uses your regular SMTP service
c) Does not support HTML emails or forged From addresses


## License: GPL 3

(c) 2009-2014 University of Manchester

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

See [LICENSE.txt](LICENSE.txt) or https://www.gnu.org/licenses/gpl-3.0.html for details.



## Usage

    stain@biggie-mint ~/src/mailer $ python mailer.py 
    Usage: mailer.py email.txt addresses.txt

    Where email.txt is the RC822 formatted email (with headers)
    and addresses.txt is a list of addresses to email, in the form

    First Last <email@example.com>



    stain@biggie-mint ~/src/mailer $ ./mailer.py email.txt test-addresses.txt 
    John Doe <johndoe@example.com> 01
    Stian Soiland-Reyes <stian@soiland-reyes.com> 02

### email.txt

The first argument should be the name of a file containing an RFC822 valid 
message, including header lines (minimum `Subject`). Example (from [email.txt](email.txt)):

    Subject: Example email 

    You are receiving this email because you registered to be kept informed
    about our news. If this is no longer the case, feel free to reply to
    this email, and we'll remove you from our subscription list.

    -- 
    John Doe
    example.com
    --counter--

The `From`, `Date` and `To` headers are added automatically.

The email file MUST be in UTF-8 encoding and should not contain HTML (unless
you also modify `Content-Type`). It is good practice to include a signature
after `-- `.


### addresses.txt

The list of addresses to email, line by line.

Example (from [test-addresses.txt](test-addresses.txt)):

  John Doe <johndoe@example.com>
  <alice.bob@example.net>

The name is importan,t as it will be used in the `To` header.

### Serial numbers

If your email message file contains the string ``--counter--``, it will be
replaced with the counter returned when running the script. This is a
hexadecimal number starting from 01, e.g. 01, 02, ...,
09, 0a, 0b, 0c, 0d, 0e, 0f, 10, 11, etc.


## Configuration

On first run, `~/.mailer` is created, and must be configured with the 
smtp details:

    [smtp]
    host = smtp.gmail.com
    port = 587
    tls = True
    username = nobody@gmail.com
    password = WrongPassword

    [email]
    sender = nobody@gmail.com
    from = Dummy User


### [smtp]

The `[smtp]` section defines how to connect to the SMTP server for sending emails. The 
defaults should work with Google by changing `username` and `password`. You might need to use
Google's [application passwords](https://security.google.com/settings/security/apppasswords)
for this feature.


To configure against a different server, also modify `host` and `port`. Note that 
most other authenticated SMTP servers require a plain username with
`@example.com`.

For a classic local SMTP server that does not require TLS or username/password, remove
`username` and `password` and use simply:

    [smtp]
    host = smtp.example.com
    port = 25
    tls = False

### [email]

This section configures defaults for the outgoing email. The `sender` email
address should be one that is accepted by the outgoing email server, typically
for Gmail this is the same as your username.

# Feedback

For any improvements or issues, please use either the 
[Github issues](https://github.com/stain/mailer/issues)
or [Github pull requests](https://github.com/stain/mailer/pulls)


