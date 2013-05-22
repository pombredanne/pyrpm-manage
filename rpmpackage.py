#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 noexpandtab

import os
import re
import rpm
from rpminfo import RPMInfo

re_true_release = re.compile(r'^([0-9]?[\.]{0,1}[0-9]+)([\._\-a-z0-9]*)$', re.I)

class RPMPackage:
	def __init__(self, f_rpm):
		self.__infos			= {}
		self.__infos["fname"]	= f_rpm
		self.__infos["bname"]	= os.path.basename(f_rpm)
		self.__infos["name"]	= self.get_info(rpm.RPMTAG_NAME)
		self.__infos["version"]	= self.get_info(rpm.RPMTAG_VERSION)
		self.__infos["epoch"]	= self.get_info(rpm.RPMTAG_EPOCH)
		self.__infos["arch"]	= self.get_info(rpm.RPMTAG_ARCH)
		match = re_true_release.match(self.get_info(rpm.RPMTAG_RELEASE))
		self.__infos["release"]	= match.group(1)
		try:
			self.__infos["extrarelease"] = match.group(2)
		except:
			self.__infos["extrarelease"] = ''

	"""
	Retrieve cached datas about package.
	"""
	def get(self, tag):
		try:
			return self.__infos[tag]
		except:
			return None

	def get_info(self, tag):
		return RPMInfo.get_info(self.get("fname"), tag)

	def is_signed(self):
		gpg = self.get_info(rpm.RPMTAG_SIGGPG)
		pgp = self.get_info(rpm.RPMTAG_SIGPGP)

		if gpg or pgp:
			return True
		return False

	"""
	@return:
		-2 : differe by arch
		-1 : impossible to determine
		 0 : not the latest
		 1 : is the latest
	"""
	def is_latest(self, o_rpmpackage):
		catastrophe	= 0
		my_version		= self.get("version")
		my_truerelease	= self.get("release")
		my_epoch		= self.get("epoch")
		my_arch			= self.get("arch")
		his_version		= o_rpmpackage.get("version")
		his_truerelease	= o_rpmpackage.get("release")
		his_epoch		= o_rpmpackage.get("epoch")
		his_arch		= o_rpmpackage.get("arch")

		try:
			m_v = float(my_version)
			h_v = float(his_version)
			if m_v > h_v:
				return 1
			elif m_v < h_v:
				return 0
		except:
			m_v = 0
			h_v = 0
		try:
			m_tr = float(my_truerelease)
			h_tr = float(his_truerelease)
			if m_tr > h_tr:
				return 1
			elif m_tr < h_tr:
				return 0
		except:
			m_tr = 0
			h_tr = 0
		try:
			m_e = float(my_epoch)
			h_e = float(his_epoch)
			if m_e > h_e and m_tr == h_tr:
				return 1
			elif m_e < h_e and m_tr == h_tr:
				return 0
		except:
			m_e = 0
			h_e = 0

		if my_arch != his_arch:
			return -2
		else:				# impossible to determine which is the latest
			return -1

