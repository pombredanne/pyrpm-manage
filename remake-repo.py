#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 noexpandtab
"""

http://projet.beastie.eu/?p=rpm-manage.git;a=summary

How to use ?

/home/rpmuser/rpm											<-- base dir

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

Have a look in __init__, for __www and __link_relative

Use example for previous tree:
./remake-repo.py --base /home/rpmuser/rpm/ --version RHEL6 --arch x86_64 --repo RPMS.racdevel --real --unsigned
"""

import optparse
from rpmrepmanager import RPMRepManager
from colors import Colors as c

def main():
	parser = optparse.OptionParser()
	parser.add_option('--base', dest='base', help='base dir for everything')
	parser.add_option('--version', dest='version', help='version of distro')
	parser.add_option('--arch', dest='arch', help='architecture')
	parser.add_option('--repo', dest='repo', help='repository for symlinks to rpm')
	parser.add_option('--fake', action='store_true', help='run fake remake')
	parser.add_option('--real', action='store_true', help='run real remake')
	parser.add_option('--unsigned', action='store_true', help='link unsigned packages')
	parser.add_option('--verbose', action='store_true', help='if an action is performed, say it')
	parser.add_option('--report', action='store_true', help='like verbose but makes a report of all actions')
	parser.add_option('--cleanup', action='store_true', help='clean old versions/release of a package. dont touch signed packages unless --force-delete')
	parser.add_option('--force-delete', action='store_true', help='force deletion of old packages, event if signed. use with CAUTION.')
	parser.add_option('--wipe-repo', action='store_true', help='wipe repository instead of just remake missing/invalid symlinks to RPM')
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
	
	if options.verbose and options.report:
		parser.error('Cannot be verbose and make report.')

	rep = RPMRepManager(
			options.base,
			options.version,
			options.arch,
			options.repo,
			options.fake,
			options.cleanup,
			options.unsigned,
			options.verbose,
			options.report,
			options.force_delete,
			options.wipe_repo
			)
	rep.run()
	
	if options.fake:
		print(c.RED + "\t\t==> RAN FAKE MODE, NO ACTION PERFORMED. <==" + c.NC)

if __name__ == '__main__':
	main()
