#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import time
from glob import iglob
import mailbox

# procmail-py - Email content and spam filtering
# MIT License
# © 2012 Noah K. Tilton <noahktilton@gmail.com>

from config import BASE_MAILDIR, MY_DOMAINS, addresses, mark_read
from spam import spamc, blacklisted
from utils import file, spammy_spamc, mark_as_read, uniq

INBOXDIR            = os.path.join(BASE_MAILDIR, "INBOX")
maildirs_on_disk    = [os.path.basename(dir) for dir in iglob(os.path.join(BASE_MAILDIR, "*"))]
maildirs_in_file    = addresses.values() # <- some of these may not exist
maildirs            = uniq(maildirs_on_disk + maildirs_in_file)
mailboxes           = dict((d, mailbox.Maildir(os.path.join(BASE_MAILDIR, d), create=True)) for d in maildirs)


# N.B.: the order of the following filters matters.  note the return
# statements.  this short-circuiting is desirable, but has to be done
# carefully to avoid double-booking mails.
def filter(args):
    try:
        key, message = args

        # BLACKLISTED WORDS/PHRASES
        if not message.is_multipart():
            # Can't run blacklist logic against multipart messages
            # because random phrases such as "gucci" may show up in
            # base64-encoded strings ... and I'm too lazy to write a
            # better loop here.  Derp.
            flat_msg = message.as_string()
            for badword in blacklisted:
                if badword in flat_msg:
                    print("badword: %s (%s)" % (badword, message["subject"]))
                    mark_as_read(message)
                    file(INBOX, mailboxes["Junk"], message, key)
                    return

        # SPAM?
        if spammy_spamc(message):
            mark_as_read(message)
            file(INBOX, mailboxes["Junk"], message, key)
            return

        # MARK-AS-READ?
        for header, string in mark_read.items():
            if string in message[header]:
                # http://docs.python.org/library/mailbox.html#mailbox.MaildirMessage
                mark_as_read(message)

        # MAILING LIST?
        for list_header in [message["delivered-to"], message["reply-to"], message["list-id"]]:
            if list_header is not None:
                try:
                    list_id, remainder = list_header.split("@")
                    remainder = remainder.strip()
                    # only allow mailinglist delivery to MY_DOMAINS
                    if remainder not in MY_DOMAINS: return
                    destination = None
                    if list_id not in mailboxes.keys():
                        # maildir doesn't exist: create it.
                        mailbox.Maildir(os.path.join(BASE_MAILDIR, list_id), create=True)
                        destination = list_id
                    else:
                        destination = mailboxes[list_id]
                    file(INBOX, destination, message, key)
                    return
                except ValueError:
                    print("couldn't split %s %s %s" % (list_header, key,
                          message["subject"]))

        # WHITELISTED SENDER?
        # FIXME - this should be a regex, not an 'in' check
        for addr in addresses.keys():
            if addr in message["from"].lower():
                file(INBOX, mailboxes[addresses[addr]], message, key)
                return
    except Exception, e:
        print("error", e)

if __name__ == '__main__':
    INBOX       = mailbox.Maildir(INBOXDIR, factory=None)
    #numprocs    = (min((cpu_count() + 2), len(INBOX)))
    #if numprocs < 1: sys.exit()
    #get_pool    = lambda: Pool(processes=numprocs)

    for email in iglob(os.path.join(INBOXDIR, "new", "*")):
        if time.time() - os.stat(email).st_mtime < 90:
            spamc(email)

    for email in INBOX.iteritems():
        filter(email)

    [box.close() for name, box in mailboxes.items()]
