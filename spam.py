import shutil
from subprocess import Popen

blacklisted = [
        "viagra",
        "payday loan",
        "tramadol",
        "beats by dre",
        "transvaginal mesh",
        "ugg boots",
        "louis vuitton",
        "anti aging",
        "abilify",
        "amitryptyline",
        "insanityworkout",
        #
        ]


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
