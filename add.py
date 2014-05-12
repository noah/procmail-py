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
        if addr in non_VIPs.keys()  or addr in VIPs.keys():
            print "{} is already added".format( addr )
            continue
        else:
            user, domain = addr.split('@')
            response = raw_input("{} -> {} [Enter/folder name/X] ".format(addr,
                user)).strip()
            if response == "":
                folder = user
            elif response.lower() == "x":
                break
            else:
                folder = response
            response    = raw_input("{} is VIP [y/N]?".format(addr)).strip()
            vip         = response.lower() in ['y']
            vd          = {True:'VIP', False:'Non-VIP'}
            response    = raw_input("{} -> {} ({}) [Y/n]".format(addr, folder,
                                        vd[vip])).strip()
            if response.lower() in ['', 'y']:

                # do it.
                print "{} -> {} {}".format(addr, folder, vd[vip])
                fmap = {True: VIPS_FILE, False: ADDRESS_FILE}
                if vip:
                    VIPs.update({addr:folder})
                    with open(fmap[vip], 'w') as f:
                          json.dump(VIPs, f)
                else:
                    non_VIPs.update({addr:folder})
                    with open(fmap[vip], 'w') as f:
                          json.dump(non_VIPs, f)
                print "Added."
            else:
                print "Abort."; break
