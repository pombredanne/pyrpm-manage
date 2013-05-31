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

    def clean_repo(self):
        """
        Clean repo by deleting all symlinks.
        Doesn't rebuild repo database.
        """
        repo = self.__repo
        os.chdir(repo) # if not done, relative symlinks will never be valid.
    
        for f_rpm in os.listdir(repo):
            try:
                if not '.rpm' in f_rpm[-4:]:
                    raise Exception()
                if not os.path.islink(repo + f_rpm):
                    raise Exception(repo + f_rpm + " is not a symlink")

                o_rpm = RPMPackage(repo + f_rpm)
                if self.__wipe_repo:
                    self.__report_cleanup.add_action(f_rpm)
                    if not self.__fake_run:
                        os.remove(repo + f_rpm)
                elif not (self.__take_unsigned or o_rpm.is_signed()):
                    self.__report_cleanup.add_action(f_rpm)
                    if not self.__fake_run:
                        os.remove(repo + f_rpm)
            except OSError:
                self.__report_cleanup.add_action(f_rpm)
                if not self.__fake_run:
                    os.remove(repo + f_rpm)
            except:
                pass
    
    def move_other_rpms(self):
        """
        Move RPMs from elsewhere to the right
        arch subdirectory and make a symlink to.

        NEVER touch these symlinks.
        """
        dir_ = self.__rpmdir + 'other_rpms/'
        list_f = os.listdir(dir_)

        for f_rpm in list_f:
            if RPMInfo.isa_rpm(dir_ + f_rpm):
                o_rpm = RPMPackage(dir_ + f_rpm)
                dest = self.__rpmdir + o_rpm.get("arch") + '/' + f_rpm
                if not self.__fake_run:
                    os.rename(dir_ + f_rpm, dest)
                    os.symlink(dest, dir_ + f_rpm)
                self.__report_other.add_action(dir_ + f_rpm)

    @staticmethod
    def list_rpms(dirs):
        """
        Get a list of RPM packages in dirs.
        """
        rpms = []
        for dir_ in dirs:
            if dir_[-1:] != '/':
                dir_ += '/'

            list_f = os.listdir(dir_)
            for f_rpm in list_f:
                if RPMInfo.isa_rpm(dir_ + f_rpm):
                    rpms.append(RPMPackage(dir_ + f_rpm))

        return rpms

    @staticmethod
    def sort_signed(rpms):
        """
        Give a list of signed packages and unsigned ones.
        """
        signed = []
        unsigned = []

        for o_rpm in rpms:
            if o_rpm.is_signed():
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
        for k in h_rpms:
            if len(h_rpms[k]) > 1:
                o_rpm = h_rpms[k][0]
                o_rpm_del = None
                print(" * " + k)
                for i in h_rpms[k][1:]:
                    res = o_rpm.is_latest(i)
                    if res == 0:
                        o_rpm_del = o_rpm
                        o_rpm = i
                    elif res == 1:
                        o_rpm_del = i
                    else:
                        print("\t" + c.BLUE + " + what to do with " + i.get("bname") + " ?" + c.NC)
                        o_rpm_del = None

                    if o_rpm_del != None:
                        print("\t" + c.RED + " + will delete " + o_rpm_del.get("bname")	 + " signed: " + str(o_rpm_del.is_signed()) + c.NC)
                        l_rpms.remove(o_rpm_del)
                        rpm_del_list.append(o_rpm_del)

                print("\t" + c.GREEN + " + take " + o_rpm.get("bname") + " signed: " + str(o_rpm.is_signed()) + c.NC)
        return l_rpms, rpm_del_list

    def delete_duplicates(self, l_rpms):
        """
        Remove old packages following conditions signed and force_delete.
        """
        h_rpms = {}
        for o_rpm in l_rpms:
            if self.__force_delete or not o_rpm.is_signed():
                try:
                    h_rpms[o_rpm.get("name")].append(o_rpm)
                except KeyError:
                    h_rpms[o_rpm.get("name")] = [o_rpm]

        l_rpms, rpm_del_list = RPMRepManager.__get_del_list(l_rpms, h_rpms)
        for i in rpm_del_list:
            self.__report_deldup.add_action(i.get("bname") + " (signed: " + str(i.is_signed()) + ")")
            if not self.__fake_run:
                os.remove(i.get("fname"))

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
                if not self.__fake_run:
                    os.symlink(src, name)
                self.__report_link.add_action(name)
    
    def build_repo(self):
        """
        Build repository.
        """
        os.chdir(self.__repo)
        if not self.__fake_run:
            os.system('createrepo .')

    def run(self):
        """
        Run everything.
        """
        # 1. Move other_rpms to rpm/version/pkg_arch and make a symlink
        Report.inline_print(c.GREEN + 'Moving other rpms…' + c.NC)
        self.move_other_rpms()

        # 2. List all rpms in valid arch -> self.__arch and noarch
        Report.inline_print(c.GREEN + 'Listing rpms…' + c.NC)
        l_rpms = RPMRepManager.list_rpms([self.__rpmdir + self.__arch, self.__rpmdir + 'noarch'])

        # 3. List signed and unsigned packages
        u_str = ' '
        if self.__take_unsigned:
            u_str = ' and unsigned '
        Report.inline_print(c.GREEN + 'Sorting signed' + u_str + 'rpms…' + c.NC)
        signed, unsigned = RPMRepManager.sort_signed(l_rpms)
        l_rpms = signed + unsigned if self.__take_unsigned else signed

        # 4. Delete duplicates unsigned packages
        if self.__cleanup:
            Report.inline_print(c.GREEN + 'Deleting duplicated packages…' + c.NC)
            l_rpms = self.delete_duplicates(l_rpms)

        # 5. Clean repo before…
        Report.inline_print(c.GREEN + 'Cleaning repo…' + c.NC)
        self.clean_repo()

        # 6. …making symlinks.
        Report.inline_print(c.GREEN + 'Populating repo…' + c.NC)
        self.populate_repo(l_rpms)

        # 7. Then make the repo.
        Report.newline()
        self.build_repo()

        # 8. Display report if report is set.
        if not self.__verbose and self.__report:
            Report.newline()
            self.__report_cleanup.print_report()
            self.__report_link.print_report()
            self.__report_deldup.print_report()
            self.__report_other.print_report()
