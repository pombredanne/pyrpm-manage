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
		self.update_cache(f_rpm)
	
	def update_cache(self, f_rpm):
		self.__infos			= {}
		self.__infos["fname"]	= f_rpm
		self.__infos["bname"]	= os.path.basename(f_rpm)
		self.__infos["name"]	= self.get_info(rpm.RPMTAG_NAME, None)
		self.__infos["version"]	= self.get_info(rpm.RPMTAG_VERSION, None)
		self.__infos["epoch"]	= self.get_info(rpm.RPMTAG_EPOCH, None)
		self.__infos["arch"]	= self.get_info(rpm.RPMTAG_ARCH, None)
		match = re_true_release.match(self.get_info(rpm.RPMTAG_RELEASE, None))
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
			pass

		try:
			return self.get_info(tag, None)
		except:
			return None

	def get_info(self, tag, cache_name):
		info = RPMInfo.get_info(self.get("fname"), tag)
		if cache_name != None:
			self.__infos[cache_name] = info
		return info

	def is_signed(self):
		gpg = self.get_info(rpm.RPMTAG_SIGGPG, None)
		pgp = self.get_info(rpm.RPMTAG_SIGPGP, None)

		if gpg or pgp:
			return True
		return False

	def __complex_version(self, my_version, his_version):
		my_s_version	= my_version.split('.')
		his_s_version	= his_version.split('.')

		m_range = len(my_s_version)
		if len(his_s_version) < m_range:
			m_range = len(his_s_version)

		for i in range(m_range):
			m_v = int(my_s_version[i])
			h_v = int(his_s_version[i])
			if m_v < h_v:
				return 0
			elif m_v > h_v:
				return 1
		return None

	"""
	@return:
		-2 : impossible to determine
		-1 : same version but differe by arch
		 0 : not the latest
		 1 : is the latest
	"""
	def is_latest(self, o_rpmpackage):
		my_version		= self.get("version")
		my_truerelease	= self.get("release")
		my_epoch		= self.get("epoch")
		my_arch			= self.get("arch")
		his_version		= o_rpmpackage.get("version")
		his_truerelease	= o_rpmpackage.get("release")
		his_epoch		= o_rpmpackage.get("epoch")
		his_arch		= o_rpmpackage.get("arch")

		# VERSION
		try:
			m_v = float(my_version)
			h_v = float(his_version)
			if m_v > h_v:
				return 1
			elif m_v < h_v:
				return 0
		except:
			pass
		# COMPLEX VERSION
		try:
			r = self.__complex_version(my_version, his_version)
			if r != None:
				return r
		except:
			pass
		# RELEASE
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

		# EPOCH
		try:
			m_e = float(my_epoch)
			h_e = float(his_epoch)
			if m_tr == h_tr:
				if m_e > h_e:
					return 1
				elif m_e < h_e:
					return 0
		except:
			pass

		# ARCH
		if my_arch != his_arch:
			return -1

		# ?!?
		return -2

