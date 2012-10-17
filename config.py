import os

BASE_MAILDIR    = "/some/maildir/base"
BASEDIR         = os.path.dirname(__file__)

addresses = {
            # email (partial OK)        # folder
            # lower-case only!
            # target                    # destination
            "noah@someaddr.com"         : "move-to-this-file"
            }

mark_read = {
            "from"                      : "noaht@blah.com",
            "subject"                   : "daily backup report",
            }
