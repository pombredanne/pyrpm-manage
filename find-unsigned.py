#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 noexpandtab
"""
Copyright (c) 2013, Florent Peterschmitt <florent@peterschmitt.fr>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import os
import sys
import re
import optparse
import rpm
from report import Report
from repmanager import RepManager

def main():
	parser = optparse.OptionParser()
	parser.add_option('--base', dest='base', help='base dir for everything')
	parser.add_option('--version', dest='version', help='version of distro')
	parser.add_option('--arch', dest='arch', help='architecture')
	parser.add_option('--oneline', action='store_true', help='display in one line, for use directly with rpmsign for example')
	(options, args) = parser.parse_args()

	if not options.base:
		parser.error('No base given')
	if not options.version:
		parser.error('No version given')
	if not options.arch:
		parser.error('No arch given')

	rep = RepManager(
			options.base,
			options.version,
			options.arch,
			"",
			False,
			False,
			True,
			True,
			False
			)
	list = []
	for a in [options.arch, 'noarch']:
		list += rep.list_rpms([options.base + '/' + options.version + '/' + a])
	signed, unsigned = rep.sort_signed(list)
	for u in unsigned:
		if options.oneline:
			sys.stdout.write(u + ' ')
		else:
			sys.stdout.write(u + '\n')
	sys.stdout.flush()

if __name__ == '__main__':
	main()
