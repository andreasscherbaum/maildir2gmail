#!/usr/bin/env python

"""Upload email messages from a list of Maildir to Google Mail."""

__version__ = '0.1'

import email
import email.Header
import email.Utils
import os
import sys
import time


class Gmail(object):
    def __init__(self, options):
        self.username = options.username
        self.password = options.password
        self.folder = options.folder
        if self.folder == 'inbox':
            self.folder = 'INBOX'
        else:
            self.folder = '[Gmail]/%s' % self.folder

        self.__database = None
        self.__imap = None

    def __del__(self):
        if self.__database is not None:
            try:
                self.__database.close()
            except:
                pass
            self.__database = None

        if self.__imap is not None:
            try:
                self.__imap.logout()
                self.__imap.close()
            except:
                pass
            self.__imap = None

    def append(self, filename):
        if self.check_appended(filename):
            return

        content = open(filename, 'rb').read()
        if content.endswith('\x00\x00\x00'):
            log('Skipping "%s" - corrupted' % os.path.basename(filename))
            return

        message = email.message_from_string(content)
        timestamp = parsedate(message['date'])
        if not timestamp:
            log('Skipping "%s" - no date' % os.path.basename(filename))
            return

        subject = decode_header(message['subject'])
        log('Sending "%s" (%d bytes)' % (subject, len(content)))
        del message

        self.imap.append(self.folder, '(\\Seen)', timestamp, content)
        self.mark_appended(filename)
    
    def check_appended(self, filename):
        return os.path.basename(filename) in self.database

    def mark_appended(self, filename):
        self.database[os.path.basename(filename)] = '1'

    @property
    def database(self):
        import dbhash
        if self.__database is None:
            dbname = os.path.abspath(os.path.splitext(sys.argv[0])[0] + '.db')
            self.__database = dbhash.open(dbname, 'w')
        return self.__database

    @property
    def imap(self):
        from imaplib import IMAP4_SSL
        if self.__imap is None:
            if not self.username or not self.password:
                raise Exception('Username/password not supplied') 

            self.__imap = IMAP4_SSL('imap.gmail.com')
            self.__imap.login(self.username, self.password)
            log('Connected to Gmail IMAP')
        return self.__imap


def decode_header(value):
    result = []
    for v, c in email.Header.decode_header(value):
        try:
            if c is None:
                v = v.decode()
            else:
                v = v.decode(c)
        except (UnicodeError, LookupError):
            v = v.decode('iso-8859-1')
        result.append(v)
    return u' '.join(result)


def encode_unicode(value):
    if isinstance(value, unicode):
        for codec in ['iso-8859-1', 'utf8']:
            try:
                value = value.encode(codec)
                break
            except UnicodeError:
                pass

    return value


def log(message):
    print '[%s]: %s' % (time.strftime('%H:%M:%S'), encode_unicode(message))


def main():
    from optparse import OptionParser

    parser = OptionParser(
        description=__doc__,
        usage='%prog [options] [maildirs]',
        version=__version__
    )

    parser.add_option('-f', '--folder', dest='folder', default='All Mail',
        help='Folder to store the emails. [default: %default]')
    parser.add_option('-p', '--password', dest='password',
        help='Password to log into Gmail')
    parser.add_option('-u', '--username', dest='username',
        help='Username to log into Gmail')

    options, args = parser.parse_args()

    gmail = Gmail(options)
    for dirname in args:
        for filename in os.listdir(dirname):
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                try:
                    gmail.append(filename)
                except:
                    log('Unable to send %s' % filename)
                    raise


def parsedate(value):
    if value:
        value = decode_header(value)
        value = email.Utils.parsedate_tz(value)
        if isinstance(value, tuple):
            timestamp = time.mktime(tuple(value[:9]))
            if value[9]:
                timestamp -= time.timezone + value[9]
                if time.daylight:
                    timestamp += 3600
            return time.localtime(timestamp)


if __name__ == '__main__':
    main()
