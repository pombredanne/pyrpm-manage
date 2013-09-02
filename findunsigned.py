#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
import sys
import optparse
from rpmrepmanager import RPMRepManager

def main():
    options, args, parser = RPMRepManager.parse_options()
    if not options.base:
        parser.error('No base given')
    if not options.version:
        parser.error('No version given')
    if not options.arch:
        parser.error('No arch given')

    rep = RPMRepManager(options)
    rpmlist = []
    for arch in [options.arch, 'noarch']:
        rpmlist += rep.list_rpms([options.base + '/' + options.version + '/' + arch])
    signed, unsigned = rep.sort_signed(rpmlist)
    for u in unsigned:
        sys.stdout.write(u.get("fname") + '\n')
    sys.stdout.flush()

if __name__ == '__main__':
    main()
