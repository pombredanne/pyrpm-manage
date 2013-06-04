#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
import rpm

class RPMInfo:
    """
    Retrieve informations from RPM package.
    """
    @staticmethod
    def isa_rpm(f_rpm):
        """
        Ugly method to tell if it's a real RPM file.
        """
        if os.path.isfile(f_rpm) and '.rpm' in f_rpm[-4:] and not os.path.islink(f_rpm):
            return True
        return False

    @staticmethod
    def get_headers(f_rpm):
        """
        Give info of file [f_rpm] and tags [[rpm.TAG*]]
        """
        transaction = rpm.ts()
        fdno = os.open(f_rpm, os.O_RDONLY)

        res = {}
        headers = None

        try:
            headers = transaction.hdrFromFdno(fdno)
        except:
            os.close(fdno)
            try:
                rpm.delSign(f_rpm)
            except:
                os.system('rpmsign --delsign ' + f_rpm + ' 2>/dev/null')
            fdno = os.open(f_rpm, os.O_RDONLY)
            headers = transaction.hdrFromFdno(fdno)
        finally:
            return headers
            os.close(fdno)

