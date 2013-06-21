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
    parser.add_option('--repo', dest='repo', default="", help='repository for symlinks to rpm')
    parser.add_option('--fake', action='store_true', default=True, help='run fake remake')
    parser.add_option('--real', action='store_true', default=False, help='run real remake')
    parser.add_option('--unsigned', action='store_true', default=True, help='link unsigned packages')
    parser.add_option('--verbose', action='store_true', default=False, help='if an action is performed, say it')
    parser.add_option('--report', action='store_true', default=True, help='like verbose but makes a report of all actions')
    parser.add_option('--cleanup', action='store_true', default=True, help='clean old versions/release of a package. dont touch signed packages unless --force-delete')
    parser.add_option('--force-delete', action='store_true', default=False, help='force deletion of old packages, event if signed. use with CAUTION.')
    parser.add_option('--wipe-repo', action='store_true', default=False, help='wipe repository instead of just remake missing/invalid symlinks to RPM')
    parser.add_option('--wipe-all-old', action='store_true', default=False, help='default is to keep both latest unsigned and signed package. This option forces to delete all old packages. useful with --force-delete')
    (options, args) = parser.parse_args()
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
