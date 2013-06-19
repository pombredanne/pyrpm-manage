#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
from report import Report
from rpmpackage import RPMPackage
from rpminfo import RPMInfo
from colors import Colors as c

class RPMRepManager:
    """
    Manage RPM repository.
    """
    def __init__(self, base, version, arch, repo, fake, cleanup, unsigned, verbose, report, force_delete, wipe_repo, keep_all_latest):
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
        self.__keep_all_latest  = True if keep_all_latest else False

        self.__report_link = Report("link", "linked", self.__verbose, True)
        self.__report_cleanup = Report("cleanup", "removed symlink", self.__verbose, True)
        self.__report_other = Report("other_rpms", "moved", self.__verbose, True)
        self.__report_deldup = Report("deldup", "delete old", self.__verbose, True)

    def remove(self, f_file):
        if not self.__fake_run:
            os.remove(f_file)

    def symlink(self, src, dest):
        if not self.__fake_run:
            os.symlink(src, dest)
    def rename(self, src, dest):
        if not self.__fake_run:
            os.rename(src, dest)

    def clean_repo(self):
        """
        Clean repo by deleting all symlinks.
        Doesn't rebuild repo database.
        """
        repo = self.__repo
        os.chdir(repo) # if not done, relative symlinks will never be valid.
    
        for f_rpm in os.listdir(repo):
            ff_rpm = repo + f_rpm
            try:
                if not '.rpm' in f_rpm[-4:]:
                    raise Exception()
                if not os.path.islink(ff_rpm):
                    raise Exception(ff_rpm + " is not a symlink")

                o_rpm = RPMPackage(ff_rpm)
                if self.__wipe_repo:
                    self.__report_cleanup.add_action(f_rpm)
                    self.remove(ff_rpm)
                elif not (self.__take_unsigned or o_rpm.get("signed")):
                    self.__report_cleanup.add_action(f_rpm)
                    self.remove(ff_rpm)
            except OSError:
                self.__report_cleanup.add_action(f_rpm)
                self.remove(ff_rpm)
            except:
                pass
    
    def move_other_rpms(self):
        """
        Move RPMs from elsewhere to the right
        arch subdirectory and make a symlink to.

        NEVER touch these symlinks. The script don't
        care of them but it will be useful to remove
        them if not needed.
        """
        dir_ = self.__rpmdir + 'other_rpms/'
        list_f = os.listdir(dir_)

        for f_rpm in list_f:
            ff_rpm = dir_ + f_rpm
            if RPMInfo.isa_rpm(ff_rpm):
                o_rpm = RPMPackage(ff_rpm)
                dest = self.__rpmdir + o_rpm.get("arch") + '/' + f_rpm
                self.rename(ff_rpm, dest)
                self.symlink(dest, ff_rpm)
                self.__report_other.add_action(ff_rpm)

    @staticmethod
    def list_rpms(dirs):
        """
        Get a list of RPM packages in dirs.
        """
        rpms = []
        for dir_ in dirs:
            list_f = os.listdir(dir_)
            for f_rpm in list_f:
                ff_rpm = dir_ + '/' + f_rpm
                if RPMInfo.isa_rpm(ff_rpm):
                    rpms.append(RPMPackage(ff_rpm))

        return rpms

    @staticmethod
    def sort_signed(rpms):
        """
        Give a list of signed packages and unsigned ones.
        """
        signed = []
        unsigned = []

        for o_rpm in rpms:
            if o_rpm.get("signed"):
                signed.append(o_rpm)
            else:
                unsigned.append(o_rpm)

        return signed, unsigned

    @staticmethod
    def __get_del_list(l_rpms, h_rpms):
        """
        Make the list of RPMS to delete.
        """
        rpm_del_list = []
        o_rpm_del = None
        o_rpms_signed = []
        o_rpms_unsigned = []
        h_rpms_ = dict((k, v) for k, v in h_rpms.iteritems() if len(v) > 1)

        for k, v in h_rpms_.items():
            for i in v:
                if i.get('signed'):
                    o_rpms_signed.append(i)
                else:
                    o_rpms_unsigned.append(i)

            print("\n * " + k)

            vv = [o_rpms_signed, o_rpms_unsigned] if self.__keep_all_latest else [o_rpms_signed + o_rpms_unsigned]
            for v in vv:
                o_rpm = v[0]
                for i in v[1:]:
                    res = o_rpm.is_latest(i)
                    if res == -1:
                        print("\t" + c.BLUE + " + what to do with " + i.get("bname")
                                + " ?" + c.NC)
                        o_rpm_del = None
                    elif not res:
                        o_rpm_del = o_rpm
                        o_rpm = i
                    elif res:
                        o_rpm_del = i

                    if o_rpm_del:
                        print("\t" + c.RED + " + delete " + o_rpm_del.get("bname")
                                + " signed: " + str(o_rpm_del.get("signed")) + c.NC)
                        l_rpms.remove(o_rpm_del)
                        rpm_del_list.append(o_rpm_del)

                print("\t" + c.GREEN + " +   take " + o_rpm.get("bname")
                     + " signed: " + str(o_rpm.get("signed")) + c.NC)

        return l_rpms, rpm_del_list

    def delete_duplicates(self, l_rpms):
        """
        Remove old packages following conditions signed and force_delete.
        """
        h_rpms = {}
        for o_rpm in l_rpms:
            if self.__force_delete or not o_rpm.get("signed"):
                try:
                    h_rpms[o_rpm.get("name")].append(o_rpm)
                except KeyError:
                    h_rpms[o_rpm.get("name")] = [o_rpm]

        l_rpms, rpm_del_list = RPMRepManager.__get_del_list(l_rpms, h_rpms)
        for i in rpm_del_list:
            self.__report_deldup.add_action(i.get("bname") +
                    " (signed: " + str(i.get("signed")) + ")")
            self.remove(i.get("fname"))

        return l_rpms

    def populate_repo(self, rpms):
        """
        Make symlinks to RPMs in repository.
        """
        os.chdir(self.__repo)

        for f_rpm in rpms:
            name = f_rpm.get("bname")
            arch = f_rpm.get("arch")
            src = self.__link_relative + self.__version + '/' + arch + '/' + name

            if not os.path.exists(name):
                self.__report_link.add_action(name)
                self.symlink(src, name)
    
    def build_repo(self):
        """
        Build repository.
        """
        os.chdir(self.__repo)
        if not self.__fake_run:
            os.system('createrepo --update .')

    def run(self):
        """
        Run everything.
        """
        # 1. Move other_rpms to rpm/version/pkg_arch and make a symlink
        Report.inline_print('1/6 Moving other rpms…')
        self.move_other_rpms()

        # 2. List all rpms in valid arch -> self.__arch and noarch
        Report.inline_print('2/6 Listing rpms…')
        arch_l = [self.__rpmdir + self.__arch, self.__rpmdir + 'noarch']
        l_rpms = RPMRepManager.list_rpms(arch_l)

        # 3. List signed and unsigned packages
        u_str = ' '
        if self.__take_unsigned:
            u_str = ' and unsigned '
        Report.inline_print('3/6 Sorting signed' + u_str + 'rpms…')
        signed, unsigned = RPMRepManager.sort_signed(l_rpms)
        l_rpms = signed + unsigned if self.__take_unsigned else signed

        # 4. Delete duplicates unsigned packages
        if self.__cleanup:
            Report.inline_print('4/6 Deleting duplicated packages…')
            l_rpms = self.delete_duplicates(l_rpms)

        # 5. Clean repo before…
        Report.inline_print('5/6 Cleaning repo…')
        self.clean_repo()

        # 6. …making symlinks.
        Report.inline_print('6/6 Populating repo…')
        self.populate_repo(l_rpms)

        # 7. Then make the repo.
        Report.newline()
        self.build_repo()

        # 8. Display report if report is set.
        if not self.__verbose and self.__report:
            Report.newline()
            self.__report_deldup.print_report()
            self.__report_cleanup.print_report()
            self.__report_link.print_report()
            self.__report_other.print_report()
