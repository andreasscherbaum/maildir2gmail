#!/usr/bin/env python

"""Upload email messages from a list of Maildir to Google Mail."""

__version__ = '0.4'

import email
import email.Header
import email.Utils
import os
import sys
import datetime
import time
import re
from pprint import pprint


class Gmail(object):
    def __init__(self, options):
        self.username = options.username
        self.password = options.password
        self.new_flag = options.new_flag
        self.folder = options.folder
        self.ignore_missing_date = options.ignore_missing_date
        self.max_size = options.max_size
        if self.folder == 'inbox':
            self.folder = 'INBOX'
        else:
            #self.folder = '[Gmail]/%s' % self.folder
            self.folder = '%s' % self.folder

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
        fileTimestamp = os.path.getctime(filename)
        if not self.ignore_missing_date:
            if not timestamp:
                log('Skipping "%s" - no date (creation time of file: %s)' % (os.path.basename(filename), datetime.datetime.fromtimestamp(fileTimestamp).strftime('%Y-%m-%d %H:%M:%S')))
                return
        else:
            timestamp = os.path.getctime(filename)

        if message.is_multipart():
            message_size = 0
            for part in message.walk():
                part_payload = part.get_payload(decode=True)
                if part_payload:
                    message_size = message_size + len(part_payload)
        else:
            message_size = len(content)

        subject = decode_header(message['subject'])        
        if message_size > self.max_size:
            log('Skipping "%s" (subject: "%s") - message too large (max. 25 MB); Size was %d bytes)' % (os.path.basename(filename), subject, len(content)))
            return

        log('Sending "%s" (%d bytes)' % (subject, message_size))
        del message

        if self.new_flag:
            self.imap.append(self.folder, '()', timestamp, content)
        else:
            self.imap.append(self.folder, '(\\Seen)', timestamp, content)
        self.mark_appended(filename)

    def check_appended(self, filename):
        return os.path.basename(filename) in self.database

    def mark_appended(self, filename):
        self.database[os.path.basename(filename)] = '1'

    @property
    def database(self):
        if self.__database is None:
            import shelve
            dbname = os.path.abspath(os.path.splitext(sys.argv[0])[0])
            self.__database = shelve.open(dbname)
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

        # verify if the specified folder exists
        f = self.__imap.status(self.folder, '(MESSAGES)')
        if (f[0] == 'OK'):
            # everything is fine, the folder exists
            pass
        elif (f[0] == 'NO'):
            # the folder does not exist
            f_p = self.folder.split('/')
            f_here = ''
            for f_c in f_p:
                if (f_here == ''):
                    f_here = f_c
                else:
                    f_here += '/' + f_c
                # check if this folder exists
                f2 = self.__imap.status(f_here, '(MESSAGES)')
                if (f2[0] == 'NO'):
                    self.__imap.create(f_here)
                    log("Create mailbox: " + f_here)
        else:
            raise Exception('Internal error quering the folder status')

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
    parser.add_option('-n', '--new', dest='new_flag', action = 'store_true',
        help='Flag all messages as UNSEEN')
    parser.add_option('--ignore-missing-date', dest='ignore_missing_date', action='store_true',
        help='Ignores messages with missing date and sets the file creation time instead')
    parser.add_option('--max-size', dest='max_size', type="int", default=25000000,
        help='Defines maximum message size [default: %default bytes]')

    options, args = parser.parse_args()

    # basic sanity check for folder name
    if (re.match(r'^[a-zA-Z0-9 \[\]\-_\/\.&]+\Z', options.folder) is None):
        raise Exception('Invalid folder name')

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

