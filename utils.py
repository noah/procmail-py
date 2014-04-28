from gi.repository import Notify
from os.path import dirname, basename

from config import VIPs


def spammy_bogo(message):
    spamh = message["x-bogosity"]
    if spamh is not None:
        try:
            spambool = spamh.split(',')[0]
            if spambool == "Spam":
                # spam!
                return True
        except ValueError:
            print("bogo couldn't split %s %s" % (spamh, key))
    return False


def spammy_spamc(message):
    spamh = message["x-spam-flag"]
    if spamh is not None:
        try:
            if spamh == "YES":
                # spam!
                return True
        except ValueError:
            print("spamc header error %s: %s" % (spamh, key))
    return False


def notify(message):
    if spammy_spamc(message): return
    Notify.init("new mail")
    if message.is_multipart():  msg = "%s attachments ..." % len(message.get_payload())
    else:                       msg = "%s ..." % message.get_payload(decode=True)[:100]

    try:
        n = Notify.Notification.new(
                "\n".join([
                    'From:      %s' % message.get("from", ""),
                    'To:        %s' % message.get("to", ""),
                    'Subject:   %s' % message.get("subject", "")
                ]),
                msg,
                "dialog-information")
        n.set_timeout(30000)
        n.show()
    except Exception, e:
        print(e)


def maildirname(maildir):
    return basename(dirname(maildir._paths["new"]))


def mv(src, dst, message, key):

    if message.get('from', '') in VIPs.keys():
        # reduce noise - only notify about messages from VIPs
        notify(message)
        print("mv %s/%s -> %s" % (maildirname(src), message.get("subject", ''), maildirname(dst)))

    # skip inbox messages marked for follow-up
    if not 'x-tickler' in message:
        dst.lock()
        dst.add(message)
        dst.flush()
        dst.unlock()
        src.lock()
        src.discard(key)
        src.flush()
        src.unlock()


def rm(src, key):
    print("rm %s" % key)
    src.lock()
    src.discard(key)
    src.flush()
    src.unlock()


def mark_as_read(message):
    print(type(message))
    message.add_flag('S') # ('S'een)


def uniq(seq):
    seen        = set()
    seen_add    = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
