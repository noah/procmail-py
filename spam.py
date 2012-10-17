import os
import shutil
from subprocess import Popen

from config import BASEDIR

# WARNING:
#
# emails which contain words in badwords.txt will be summarily deleted!
#
# format is one bad word per line, all lowercase
blacklisted = [w.strip() for w in open(os.path.join(BASEDIR, 'badwords.txt')).readlines()]



def bogofilter(mail):
    print("processing %s" % mail)
    # run spam filtering on all new mails in the INBOX
    # annotate the mail headers
    failure = True
    backup  = ".".join([mail, "bak"])
    with open(mail, 'r') as f:
        # run bogofilter
        #  create a temporary file
        with open(backup, 'w') as bak:
            # run the mail through bogofilter
            bogo = Popen(["bogofilter", "-u", "-e", "-p"], stdin=f, stdout=bak)
            failure = bogo.wait() != 0
    if failure: print("error:  bogofilter failed on %s" % mail)
    else:       shutil.move(backup, mail)
