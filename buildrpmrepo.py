#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab
"""

http://projet.beastie.eu/?p=pyrpm-manage.git;a=summary

How to use ?

/home/rpmuser/rpm   <-- base dir

Where we have RPMs:
base
    RHEL6			<-- version
        noarch		<-- unvalid version/arch
        i686		<-- valid version/arch
        x86_64		<-- valid version/arch
        other_rpms	<-- for rpms from « outside », arch automaticaly discovered

Where we have repositories:

base
    www/RHEL6-x86_64/RPMS.racdevel			<-- repository's root/name

Have a look in __init__, for __www and __link_relative in rpmrepmanager.py

Use example for previous tree:
./buildrpmrepo.py --base /home/rpmuser/rpm/ --version RHEL6 --arch x86_64 --repo RPMS.racdevel --real --unsigned
"""

import optparse
from repomanager.rpm.repo import RPMRepManager
from repomanager.common.colors import Colors as c

def main():
    parser = RPMRepManager.MakeNeededOptions()
    (options, args) = parser.parse_args()
    if not options.base:
        parser.error('No base given')
    if not options.version:
        parser.error('No version given')
    if not options.arch:
        parser.error('No arch given')
    if not options.repo:
        parser.error('No repo directory given')

    if options.real and options.fake:
        parser.error('Real or fake ? Are U real ?')
    elif not (options.real or options.fake):
        parser.error('No real or fake mode given')

    if options.force_delete and not options.cleanup:
        parser.error('Cannot force deletion if you dont want to --cleanup')
    if options.wipe_all_old and not options.force_delete:
        parser.error('Cannot wipe all old if not --force-delete')
    
    if options.verbose and options.report:
        parser.error('Cannot be verbose and make report.')

    print("=> Working on repo " + options.repo + " for " + options.version + " on arch " + options.arch)
    print("=> Options: ")

    if options.cleanup and not options.nocleanup:
        print("   * Cleanup old packages")
    if options.unsigned:
        print("   * Take unsigned packages")

    if options.force_delete:
        print("   * Force deletion of old signed packages")

    if options.wipe_repo:
        print("   * Wipe repository before linking")
    else:
        print("   * Keep valid symlinks")

    if options.wipe_all_old:
        print("   * Delete all old packages even if signed")
    else:
        print("   * Keep latest signed and unsigned packages")

    if options.fake:
        print("   * Fake mode")
    else:
        print("   * Real mode")

    if options.report:
        print("   * Print report at the end")

    if options.verbose:
        print("   * Verbose mode")

    rep = RPMRepManager(options)
    rep.run()
    
    if options.fake:
        print(c.RED + "\t\t==> RAN FAKE MODE, NO ACTION PERFORMED. <==" + c.NC)

if __name__ == '__main__':
    main()
