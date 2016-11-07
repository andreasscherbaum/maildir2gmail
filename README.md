# maildir2gmail

Maildir 2 Gmail

## Overview and History

The _maildir2gmail.py_ script allows uploading a maildir directory into a Google Gmail account, using IMAP.

Scott Yang provides the original _maildir2gmail.py_ script on [his website](https://scott.yang.id.au/2009/01/migrate-emails-maildir-gmail.html). There is no license included, but according to a [Tweet](https://twitter.com/scottyang/status/794141870934720512) ([copy](./Twitter_2016-11-03.png)) the license is "provided as is" (public domain).

The script in this repository contains a few additional features which I found useful while migrating data, as well as additional documentation how to use it.

## Usage

```
./maildir2gmail.py [-f] [-n] -u <username> -p <password> <maildirs>
```

By default, all mails are uploaded to _All Mail_ in Gmail, following the Google concept of "never delete mails, just archive everything".
A folder can be specified using the _-f_ option.

Mails can be marked as Unseen (new) using the _n_ option.

Username and Password are required, IMAP for your mailbox must be turned on (do this in the Settings for your mailbox). In addition you have to allow [_less secure apps_](https://support.google.com/accounts/answer/6010255) in your Gmail interface.
