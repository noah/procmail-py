#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import shutil
import json
from email.parser import HeaderParser
from email.utils import getaddresses

# procmail-py - Email content and spam filtering
# MIT License
# © 2014 Noah K. Tilton <code@tilton.co>

# add.py - programmatically add email addresses to the procmail configuration
# intended to be called from a MUA binding

from config import non_VIPs, VIPs, ADDRESS_FILE, VIPS_FILE


def confirm(msg):
    return raw_input("{} [Y/n] ".format(msg)).strip().lower() in ['y', '']

if __name__ == '__main__':


    # backup json
    [shutil.copyfile(f, f + ".bak") for f in [ADDRESS_FILE, VIPS_FILE] ]

    message = HeaderParser().parse(sys.stdin, headersonly=True)
    ffroms  = message.get_all('from', [])
    #ccs     = message.get_all('cc', [])
    #addrs   = getaddresses(ffroms + ccs)
    addrs   = getaddresses(ffroms)

    # reset STDIN handle
    sys.stdin = open("/dev/tty")

    for name, addr in addrs:
        addr = addr.lower()
        try:
            _ = VIPs[addr]
            print ("key exists: {} -> @vip".format( addr ))
            continue
        except KeyError:
            pass

        try:
            dst = non_VIPs[addr]
            print ("key exists: {} -> {}".format( addr, dst ))
            continue
        except KeyError:
            pass

        user, domain = addr.split('@')

        # prompt for VIP status

        fmap        = {True: VIPS_FILE, False: ADDRESS_FILE}
        vd          = {True:'VIP', False:'Non-VIP'}
        is_vip      = raw_input("{} is VIP [y/N]? ".format(addr)).strip().lower() in ['y']

        if is_vip:
            folder_name = "@vip"
            VIPs.update({addr:folder_name})
            if confirm("{} -> {} ({})".format(addr, folder_name, vd[is_vip])):
                with open(fmap[is_vip], 'w') as f:
                    json.dump(VIPs, f)
        else:
            folder_name = raw_input("{} -> {} [Enter/folder name/X] ".format(addr, user)).strip().lower()
            if folder_name == "":
                folder_name = user
            elif folder_name == "x":
                break
            else:
                if confirm("{} -> {} ({})".format(addr, folder_name, vd[is_vip])):
                    non_VIPs.update({addr:folder_name})
                    with open(fmap[is_vip], 'w') as f:
                        json.dump(non_VIPs, f)
