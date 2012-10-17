from gi.repository import Notify
from os.path import dirname, basename


def notify(message):
    Notify.init("new mail")
    if message.is_multipart():  msg = "%s attachments ..." % len(message.get_payload())
    else:                       msg = "%s ..." % message.get_payload()[:100]
    n = Notify.Notification.new("\n".join([message.get("from", ""), message.get("subject", "")]),
                                msg,
                                "dialog-information")
    n.set_timeout(0)
    n.show()


def maildirname(maildir):
    return basename(dirname(maildir._paths["new"]))


def mv(src, dst, message, key):
    print("mv %s/%s -> %s" % (maildirname(src), message.get("subject", ''), maildirname(dst)))
    notify(message)
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
