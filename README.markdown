# About

http://blog.tilton.co/2012-10-04-my-email-setup-mutt-and-procmail-py.html


# Installation

Copy config.py.example to config.py.  Copy \*.json.example files to .json.

# Mutt integration

A macro for adding FROM addresses to the VIP or non-VIP address list:

    macro index,pager @ "<pipe-message>/path/to/procmail-py/add.py<return>" "add TO/CCs to procmail config"

`add.py` uses some `stdin` magic, and may not work on Windows.

A macro for running the Procmail-Py filters (on-demand):

    macro index,pager F "<enter-command>unset wait_key<enter><pipe-entry>/path/to/procmail-py/main.py<enter><enter-command>set wait_key<enter><sync-mailbox>"

# Cron

If not using awesome window manager can drop the environment variables:

    DISPLAY=$DISPLAY DBUS_SESSION_BUS_ADDRESS="$(grep -zi DBUS /proc/$(pgrep awesome)/environ | sed -r -e 's/^DBUS_SESSION_BUS_ADDRESS=//')" python2 /path/to/procmail-py/main.py >> ~/logs/mail.log 2>&1 
