#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 noexpandtab

import os
import rpm
from report import Report
from rpmpackage import RPMPackage
from rpminfo import RPMInfo
from colors import Colors as c

class RPMRepManager:

	def __init__(self, base, version, arch, repo, fake, cleanup, unsigned, verbose, report, force_delete, wipe_repo):
		if not '/' in base[-1:]:
			base += '/'
		if not '/' in repo[-1:]:
			repo += '/'

		self.__link_relative = '../../../'
		self.__www		= 'www/'
		self.__base		= base
		self.__version	= version
		self.__arch		= arch
		self.__repo		= base + self.__www + version + '-' + arch + '/' + repo
		self.__rpmdir	= base + version + '/'
		self.__fake_run			= True if fake else False
		self.__take_unsigned	= True if unsigned else False
		self.__cleanup			= True if cleanup else False
		self.__verbose			= True if verbose else False
		self.__report			= True if report else False
		self.__force_delete		= True if force_delete else False
		self.__wipe_repo		= True if wipe_repo else False

		self.__report_link = Report("link", "linked", self.__verbose, True)
		self.__report_cleanup = Report("cleanup", "removed symlink", self.__verbose, True)
		self.__report_other = Report("other_rpms", "moved", self.__verbose, True)
		self.__report_deldup = Report("deldup", "delete old", self.__verbose, True)

	"""
	Clean repo by deleting all symlinks.
	Doesn't rebuild repo database.
	"""
	def clean_repo(self):
		repo = self.__repo
		os.chdir(repo) # if not done, relative symlinks will never be valid.
	
		for file in os.listdir(repo):
			try:
				if not '.rpm' in file[-4:]:
					raise Exception()
				if not os.path.islink(repo + file):
					raise Exception(repo + file + " is not a symlink")
				o_rpm = RPMPackage(repo + file)
				if self.__wipe_repo:
					self.__report_cleanup.add_action(file)
					if not self.__fake_run:
						os.remove(repo + file)
				elif not (self.__take_unsigned or o_rpm.is_signed()):
					self.__report_cleanup.add_action(file)
					if not self.__fake_run:
						os.remove(repo + file)
			except OSError:
				self.__report_cleanup.add_action(file)
				if not self.__fake_run:
					os.remove(repo + file)
			except:
				pass
	
	def move_other_rpms(self):
		dir = self.__rpmdir + 'other_rpms/'
		list = os.listdir(dir)

		for file in list:
			if RPMInfo.isa_rpm(dir + file):
				o_rpm = RPMPackage(dir + file)
				dest = self.__rpmdir + o_rpm.get("arch") + '/' + file
				if not self.__fake_run:
					os.rename(dir + file, dest)
					os.symlink(dest, dir + file)
				self.__report_other.add_action(dir + file)

	def list_rpms(self, dirs):
		rpms = []
		for dir in dirs:
			if dir[-1:] != '/':
				dir += '/'

			list = os.listdir(dir)
			for file in list:
				if RPMInfo.isa_rpm(dir + file):
					rpms.append(RPMPackage(dir + file))

		return rpms

	def sort_signed(self, rpms):
		signed = []
		unsigned = []

		for o_rpm in rpms:
			if o_rpm.is_signed():
				signed.append(o_rpm)
			else:
				unsigned.append(o_rpm)

		return signed, unsigned

	def __get_del_list(self, l_rpms, h_rpms):
		rpm_del_list = []
		for k in h_rpms:
			if len(h_rpms[k]) > 1:
				o_rpm = h_rpms[k][0]
				o_rpm_del = None
				print(" * " + k)
				for i in h_rpms[k][1:]:
					r = o_rpm.is_latest(i)
					if r == 0:
						o_rpm_del = o_rpm
						o_rpm = i
					elif r == 1:
						o_rpm_del = i
					else:
						print("\t" + c.BLUE + " + what to do with " + i.get("bname") + " ?" + c.NC)
						o_rpm_del = None

					if o_rpm_del != None:
						print("\t" + c.RED + " + will delete " + o_rpm_del.get("bname")  + " signed: " + str(o_rpm_del.is_signed()) + c.NC)
						l_rpms.remove(o_rpm_del)
						rpm_del_list.append(o_rpm_del)

				print("\t" + c.GREEN + " + take " + o_rpm.get("bname") + " signed: " + str(o_rpm.is_signed()) + c.NC)
		return l_rpms, rpm_del_list

	def delete_duplicates(self, l_rpms):
		h_rpms = {}
		for o_rpm in l_rpms:
			if not o_rpm.is_signed() or self.__force_delete:
				try:
					h_rpms[o_rpm.get("name")].append(o_rpm)
				except:
					h_rpms[o_rpm.get("name")] = [o_rpm]

		l_rpms, rpm_del_list = self.__get_del_list(l_rpms, h_rpms)
		for i in rpm_del_list:
			self.__report_deldup.add_action(i.get("bname") + " (signed: " + str(i.is_signed()) + ")")
			if not self.__fake_run:
				os.remove(i.get("fname"))

		return l_rpms

	def populate_repo(self, rpms):
		os.chdir(self.__repo)

		for f_rpm in rpms:
			name = f_rpm.get("bname")
			arch = f_rpm.get("arch")
			src = self.__link_relative + self.__version + '/' + arch + '/' + name
			if not os.path.exists(name):
				if not self.__fake_run:
					os.symlink(src, name)
				self.__report_link.add_action(name)
	
	def build_repo(self):
		os.chdir(self.__repo)
		if not self.__fake_run:
			os.system('createrepo .')

	def run(self):
		# 1. Move other_rpms to rpm/version/pkg_arch and make a symlink
		print(c.PURPLE + 'Moving other rpms…' + c.NC)
		self.move_other_rpms()

		# 2. List all rpms in valid arch -> self.__arch and noarch
		print(c.PURPLE + 'Listing rpms…' + c.NC)
		l_rpms = self.list_rpms([self.__rpmdir + self.__arch, self.__rpmdir + 'noarch'])

		# 3. List signed and unsigned packages
		print(c.PURPLE + 'Sorting signed and unsigned rpms…' + c.NC)
		if self.__take_unsigned:
			print(c.RED + 'Taking unsigned packages' + c.NC)
		signed, unsigned = self.sort_signed(l_rpms)
		l_rpms = signed + unsigned if self.__take_unsigned else signed

		# 4. Delete duplicates unsigned packages
		if self.__cleanup:
			print(c.PURPLE + 'Deleting unsigned duplicated packages…' + c.NC)
			l_rpms = self.delete_duplicates(l_rpms)

		# 5. Clean repo before…
		print(c.PURPLE + 'Cleaning repo…' + c.NC)
		self.clean_repo()

		# 6. …making symlinks.
		print(c.PURPLE + 'Populating repo…' + c.NC)
		self.populate_repo(l_rpms)

		# 7. Then make the repo.
		self.build_repo()

		# 8. Display report if report is set.
		if not self.__verbose and self.__report:
			self.__report_cleanup.print_report()
			self.__report_link.print_report()
			self.__report_deldup.print_report()
			self.__report_other.print_report()
