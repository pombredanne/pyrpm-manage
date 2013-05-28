#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
import sys
import optparse
from rpmrepmanager import RPMRepManager

def main():
    parser = optparse.OptionParser()
    parser.add_option('--base', dest='base', help='base dir for everything')
    parser.add_option('--version', dest='version', help='version of distro')
    parser.add_option('--arch', dest='arch', help='architecture')
    parser.add_option('--oneline', action='store_true', help='display in one line, to use directly with rpmsign for example')
    (options, args) = parser.parse_args()

    if not options.base:
        parser.error('No base given')
    if not options.version:
        parser.error('No version given')
    if not options.arch:
        parser.error('No arch given')

    rep = RPMRepManager(
            options.base,
            options.version,
            options.arch,
            "",
            False,
            False,
            True,
            True,
            False,
            False,
            False
            )
    list = []
    for arch in [options.arch, 'noarch']:
        list += rep.list_rpms([options.base + '/' + options.version + '/' + arch])
    signed, unsigned = rep.sort_signed(list)
    for u in unsigned:
        if options.oneline:
            sys.stdout.write(u.get("fname") + ' ')
        else:
            sys.stdout.write(u.get("fname") + '\n')
    sys.stdout.flush()

if __name__ == '__main__':
    main()
