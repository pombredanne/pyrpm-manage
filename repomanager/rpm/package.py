#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
import re
import rpm
from repomanager.rpm.info import RPMInfo
from distutils.version import LooseVersion

RE_TRUE_RELEASE = re.compile(r'^([0-9]?[\.]{0,1}[0-9]+)([\._\-a-z0-9]*)$', re.I)

class RPMPackage:
    """
    Make object for RPM package and get infos about.
    """
    def __init__(self, f_rpm):
        self.__infos    = {}
        self.make_cache(f_rpm)
    
    def update_cache(self):
        self.__make_cache(self.get("fname"))

    def make_cache(self, f_rpm):
        """
        Update/initialize cached datas of RPM [f_rpm]
        """
        self.__infos["fname"]	= f_rpm
        self.__infos["bname"]	= os.path.basename(f_rpm)
        self.__infos["headers"] = RPMInfo.get_headers(f_rpm)
        self.get_info(rpm.RPMTAG_NAME, "name")
        self.get_info(rpm.RPMTAG_VERSION, "version")
        self.get_info(rpm.RPMTAG_RELEASE, "fullrelease")
        self.get_info(rpm.RPMTAG_EPOCH, "epoch")
        self.get_info(rpm.RPMTAG_ARCH, "arch")
        self.get_info(rpm.RPMTAG_SIGPGP, "pgp")
        self.get_info(rpm.RPMTAG_SIGGPG, "gpg")
        self.__infos["signed"] = False
        if self.get("pgp") or self.get("gpg"):
            self.__infos["signed"] = True

        match = RE_TRUE_RELEASE.match(self.get("fullrelease"))
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

    def get_info(self, rpmtag, cache_name):
        """
        Can make a [cache_name] key entry in cached datas.
        Custom cached datas cannot be updated via update_cache.

        Tag must be rpm.RPMTAG
        """
        info = self.__infos["headers"][rpmtag]
        if cache_name:
            self.__infos[cache_name] = info
        return info

    def is_latest(self, o_rpm):
        myv_s = self.get('version') + '-' + self.get('release')
        ov_s = o_rpm.get('version') + '-' + o_rpm.get('release')
        try:
            myv_s += '-' + self.get('epoch')
            ov_s +=  '-' + o_rpm.get('epoch')
        except TypeError:
            pass

        if LooseVersion(myv_s) == LooseVersion(ov_s) and self.get('arch') != o_rpm.get('arch'):
            return -1
        return LooseVersion(myv_s) > LooseVersion(ov_s)
