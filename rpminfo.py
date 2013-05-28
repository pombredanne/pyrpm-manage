#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 noexpandtab

import os
import rpm

class RPMInfo:
    @staticmethod
    def isa_rpm(f_rpm):
        if os.path.isfile(f_rpm) and '.rpm' in f_rpm[-4:] and not os.path.islink(f_rpm):
            return True
        return False

    @staticmethod
    def get_info(f_rpm, tag):
        ts = rpm.ts()
        fdno = os.open(f_rpm, os.O_RDONLY)

        res = None
        hdr = None

        try:
            hdr = ts.hdrFromFdno(fdno)
        except:
            try:
                rpm.delSign(f_rpm)
            except:
                os.system('rpmsign --delsign ' + f_rpm + ' 2>/dev/null')
            fdno = os.open(self.get("fname"), os.O_RDONLY)
            hdr = ts.hdrFromFdno(fdno)
        finally:
            try:
                res = hdr[tag]
                os.close(fdno)
            except:
                pass

        return res

