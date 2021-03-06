import os
import shutil
from subprocess import Popen

from config import BASEDIR

# format is one bad word per line, all lowercase
blacklisted = [w.strip() for w in open(os.path.join(BASEDIR, 'badwords.txt')).readlines()]



def spamc(mail):
    # run spam filtering on all new mails in the INBOX
    # annotate the mail headers
    failure = True
    backup  = ".".join([mail, "bak"])
    with open(mail, 'r') as f:
        # run through spamc
        #  create a temporary file
        with open(backup, 'w') as bak:
            # run the mail through spamc
            spamc = Popen(["/usr/bin/vendor_perl/spamc"], stdin=f, stdout=bak)
            failure = spamc.wait() != 0
    if failure: print("error:  spamc failed on %s" % mail)
    else:       shutil.move(backup, mail)
