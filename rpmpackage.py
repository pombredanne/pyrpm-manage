#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
import re
import rpm
from rpminfo import RPMInfo

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

    @staticmethod
    def __complex_version(my_version, his_version):
        """
        If simple version test failed, try with char
        by char comparition.
        """
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

    def is_latest(self, o_rpmpackage):
        """
        @return:
            -2 : impossible to determine
            -1 : same version but differe by arch
             0 : not the latest
             1 : is the latest
        """
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
        except ValueError:
            pass

        # COMPLEX VERSION
        try:
            res = RPMPackage.__complex_version(my_version, his_version)
            if res != None:
                return res
        except ValueError:
            pass

        # RELEASE
        try:
            m_tr = float(my_truerelease)
            h_tr = float(his_truerelease)
            if m_tr > h_tr:
                return 1
            elif m_tr < h_tr:
                return 0
        except ValueError:
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
        except ValueError:
            pass

        # ARCH
        if my_arch != his_arch:
            return -1

        # ?!?
        return -2

