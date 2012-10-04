#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
from glob import iglob
import mailbox
from multiprocessing import cpu_count, Pool

# procmail-py - Email content and spam filtering
# MIT License
# © 2012 Noah K. Tilton <noahktilton@gmail.com>

from config import BASEDIR, addresses, mark_read
from spam import bogofilter, blacklisted
from utils import mv, rm

INBOXDIR    = os.path.join(BASEDIR, "INBOX")
mailboxes   = dict((name, mailbox.Maildir(os.path.join(BASEDIR, name))) for name in [os.path.basename(dir) for dir in iglob(os.path.join(BASEDIR, "*"))])


# N.B.: the order of the following filters matters.  note the return
# statements.  this short-circuiting is desirable, but has to be done
# carefully to avoid double-booking mails.
def filter(args):
    key, message = args

    # BLACKLISTED WORDS/PHRASES
    flat_msg = ' '.join(str(message).split("\n"))
    for badword in blacklisted:
        if badword in flat_msg:
            print("badword: %s (%s)" % (badword, message["subject"]))
            rm(INBOX, key)
            return

    # SPAM?
    spamh = message["x-bogosity"]
    if spamh is not None:
        try:
            spambool = spamh.split(',')[0]
            if spambool == "Spam":
                # spam!
                mv(INBOX, mailboxes["Junk"], message, key)
                return
        except ValueError:
            print("bogo couldn't split %s %s" % (spamh, key))

    # MARK-AS-READ?
    for header, string in mark_read.items():
        if string in message[header]:
            # http://docs.python.org/library/mailbox.html#mailbox.MaildirMessage
            message.add_flag('S') # ('S'een)

    # MAILING LIST?
    for list_header in [message["delivered-to"], message["reply-to"], message["list-id"]]:
        if list_header is not None:
            try:
                list_id, remainder = list_header.split("@")
                if list_id in mailboxes.keys():
                    mv(INBOX, mailboxes[list_id], message, key)
                    return
            except ValueError:
                print("couldn't split %s %s %s" % (list_header, key,
                      message["subject"]))

    # WHITELISTED SENDER?
    for addr in addresses.keys():
        if addr in message["from"].lower():
            mv(INBOX, mailboxes[addresses[addr]], message, key)
            return

if __name__ == '__main__':
    INBOX       = mailbox.Maildir(INBOXDIR, factory=None)
    numprocs    = (min((cpu_count() + 2), len(INBOX)))
    if numprocs < 1: sys.exit()
    get_pool    = lambda: Pool(processes=numprocs)

    # run mail through bogofilter in parallel
    print("Running bogo ...")
    bogo_pool = get_pool()
    bogo_pool.imap(bogofilter, iglob(os.path.join(INBOXDIR, "new", "*")))
    bogo_pool.close()
    bogo_pool.join()

    print("Filtering ...")
    # filter in parallel
    filter_pool = get_pool()
    filter_pool.map(filter, INBOX.iteritems())
    filter_pool.close()
    filter_pool.join()

    [box.close() for name, box in mailboxes.items()]
