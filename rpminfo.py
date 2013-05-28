#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
import rpm

class RPMInfo:
    def __init__():
        pass

    @staticmethod
    def isa_rpm(f_rpm):
        if os.path.isfile(f_rpm) and '.rpm' in f_rpm[-4:] and not os.path.islink(f_rpm):
            return True
        return False

    @staticmethod
    def get_info(f_rpm, tag):
        transaction = rpm.ts()
        fdno = os.open(f_rpm, os.O_RDONLY)

        res = None
        hdr = None

        try:
            hdr = transaction.hdrFromFdno(fdno)
        except:
            try:
                rpm.delSign(f_rpm)
            except:
                os.system('rpmsign --delsign ' + f_rpm + ' 2>/dev/null')
            fdno = os.open(f_rpm, os.O_RDONLY)
            hdr = transaction.hdrFromFdno(fdno)
        finally:
            try:
                res = hdr[tag]
                os.close(fdno)
            except:
                pass

        return res

