#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
import re
import rpm
from rpminfo import RPMInfo
from distutils.version import LooseVersion

RE_TRUE_RELEASE = re.compile(r'^([0-9]?[\.]{0,1}[0-9]+)([\._\-a-z0-9]*)$', re.I)

class RPMPackage:
    """
    Make object for RPM package and get infos about.
    """
    def __init__(self, f_rpm):
        self.__infos    = {}
        self.update_cache(f_rpm)
    
    def update_cache(self, f_rpm):
        """
        Update/initialize cached datas of RPM [f_rpm]
        """
        self.__infos["fname"]	= f_rpm
        self.__infos["bname"]	= os.path.basename(f_rpm)
        self.__infos["name"]	= self.get_info(rpm.RPMTAG_NAME, None)
        self.__infos["version"]	= self.get_info(rpm.RPMTAG_VERSION, None)
        self.__infos["epoch"]	= self.get_info(rpm.RPMTAG_EPOCH, None)
        self.__infos["arch"]	= self.get_info(rpm.RPMTAG_ARCH, None)
        match = RE_TRUE_RELEASE.match(self.get_info(rpm.RPMTAG_RELEASE, None))
        self.__infos["release"]	= match.group(1)
        try:
            self.__infos["extrarelease"] = match.group(2)
        except KeyError:
            self.__infos["extrarelease"] = ''

    def get(self, tag):
        """
        Retrieve cached data about package.
        """
        try:
            return self.__infos[tag]
        except KeyError:
            pass

        return self.get_info(tag, None)

    def get_info(self, tag, cache_name):
        """
        Can make a [cache_name] key entry in cached datas.
        Custom cached datas cannot be updated via update_cache.
        """
        info = RPMInfo.get_info(self.get("fname"), tag)
        if cache_name != None:
            self.__infos[cache_name] = info
        return info

    def is_signed(self):
        """
        Check if package is GPG or PGP signed.
        """
        gpg = self.get_info(rpm.RPMTAG_SIGGPG, None)
        pgp = self.get_info(rpm.RPMTAG_SIGPGP, None)

        if gpg or pgp:
            return True
        return False


    def is_latest(self, o_rpmpackage):
        myv_s = self.get('version') + '-' + self.get('release') + '-' + self.get('epoch')
        ov_s = o_rpmpackage.get('version') + '-' + o_rpmpackage.get('release') + '-' + self.get('epoch')
        if LooseVersion(myv_s) == LooseVersion(ov_s) and self.get('arch') != o_rpmpackage.get('arch'):
            return -1
        return LooseVersion(myv_s) > LooseVersion(ov_s)
