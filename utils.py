import re

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
            print("bogo couldn't split %s %s" % (spamh, message))
    return False


def spammy_spamc(message):
    spamh = message["x-spam-flag"]
    if spamh is not None:
        try:
            if spamh == "YES":
                # spam!
                return True
        except ValueError:
            print("spamc header error %s: %s" % (spamh, message))
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


def file(src, dst, message, key):

    # ignore any message that is a tickler message
    if 'x-tickler' in message: return

    # notify, but only if from a VIP

    # extract addr from string in fmt "Joe P. Quinn <joe@quinn.com>"
    from_header = message.get('from', '')
    from_match  = re.search("[^ <]+@.[^ >]+", from_header)

    if from_match:
        from_addr = from_match.group(0)
        if from_addr in VIPs.keys():
            notify(message)

    else:
        print "bad from address:", from_addr

    # file away, no matter whether from VIP or not
    print("mv %s/%s -> %s" % (maildirname(src), message.get("subject", ''), maildirname(dst)))
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
    print("marked as read", message)
    message.add_flag('S') # ('S'een)


def uniq(seq):
    seen        = set()
    seen_add    = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
