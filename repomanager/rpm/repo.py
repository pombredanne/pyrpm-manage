#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import os
import optparse
from repomanager.common.report import Report
from repomanager.rpm.package import RPMPackage
from repomanager.rpm.info import RPMInfo
from repomanager.common.colors import Colors as c

class RPMRepManager:
    """
    Manage RPM repository.
    """
    def __init__(self, options):
        repo = options.repo
        base = options.base

        if not '/' in base[-1:]:
            base += '/'
        if not '/' in repo[-1:]:
            repo += '/'

        self.__www     = 'www/'
        self.__base    = base
        self.__version = options.version
        self.__arch    = options.arch
        self.__repo    = base + self.__www + options.version + '-' + options.arch + '/' + repo
        self.__rpmdir  = base + options.version + '/'
        self.__link_relative = '../../../'
        self.__fake_run      = True if options.fake else False
        self.__take_unsigned = True if options.unsigned else False
        self.__cleanup       = options.cleanup and not options.nocleanup
        self.__verbose       = True if options.verbose else False
        self.__report        = True if options.report else False
        self.__force_delete  = True if options.force_delete else False
        self.__wipe_repo     = True if options.wipe_repo else False
        self.__wipe_all_old  = True if options.wipe_all_old else False

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

    def __get_del_list(self, l_rpms, h_rpms):
        """
        Make the list of RPMS to delete.
        """
        rpm_del_list = []
        o_rpm_del = None
        h_rpms_ = dict((k, v) for k, v in h_rpms.iteritems() if len(v) > 1)

        for k, v in h_rpms_.items():
            o_rpms_signed = []
            o_rpms_unsigned = []
            vv = []

            if not self.__wipe_all_old:
                for i in v:
                    if i.get("signed"):
                        o_rpms_signed.append(i)
                    else:
                        o_rpms_unsigned.append(i)

                if len(o_rpms_signed) > 0:
                    vv.append(o_rpms_signed)
                vv.append(o_rpms_unsigned)
            else:
                vv = [v]

            print("\n * " + k)

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

        l_rpms, rpm_del_list = self.__get_del_list(l_rpms, h_rpms)
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
        if not self.__fake_run:
            os.chdir(self.__repo)
            os.system('createrepo --update .')

    def run(self):
        """
        Run everything.
        """

        steps = 6

        # 1. Move other_rpms to rpm/version/pkg_arch and make a symlink
        Report.inline_print('1/{0} Moving other rpms…'.format(str(steps)))
        self.move_other_rpms()

        # 2. List all rpms in valid arch -> self.__arch and noarch
        Report.inline_print('2/{0} Listing rpms…'.format(str(steps)))
        arch_l = [self.__rpmdir + self.__arch, self.__rpmdir + 'noarch']
        l_rpms = RPMRepManager.list_rpms(arch_l)

        # 3. List signed and unsigned packages
        u_str = ' '
        if self.__take_unsigned:
            u_str = ' and unsigned '
        Report.inline_print('3/{0} Sorting signed'.format(str(steps)) + u_str + 'rpms…')
        signed, unsigned = RPMRepManager.sort_signed(l_rpms)
        l_rpms = signed + unsigned if self.__take_unsigned else signed

        # 4. Delete duplicates unsigned packages
        if self.__cleanup:
            Report.inline_print('4/{0} Deleting duplicated packages…'.format(str(steps)))
            l_rpms = self.delete_duplicates(l_rpms)

        # 5. Clean repo before…
        Report.inline_print('5/{0} Cleaning repo…'.format(str(steps)))
        self.clean_repo()

        # 6. …making symlinks.
        Report.inline_print('6/{0} Populating repo…'.format(str(steps)))
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

    @staticmethod
    def MakeNeededOptions():
        parser = optparse.OptionParser()
        parser.add_option('--base', dest='base',
                help='base dir for everything')
        parser.add_option('--version', dest='version',
                help='version of distro')
        parser.add_option('--arch', dest='arch',
                help='architecture', default='noarch')

        parser.add_option('--repo', dest='repo',
                default="",
                help='name of the repository under base/www/version-arch/')

        parser.add_option('--fake', action='store_true',
                help='run in fake mode, no action performed. this is default mode.')

        parser.add_option('--real', action='store_true',
                help='run in real mode')

        parser.add_option('--unsigned', action='store_true',
                help='build repository with unsigned packages. default to signed only')

        parser.add_option('--verbose', action='store_true',
                help='if an action is performed, say it immediately')

        parser.add_option('--report', action='store_true',
                default=True,
                help='like verbose but makes a report of all actions at the end. this is default')

        parser.add_option('--cleanup', action='store_true',
                default=True,
                help='clean old versions/release of a package. dont touch signed packages unless --force-delete. this is default')

        parser.add_option('--no-cleanup', dest='nocleanup',
                action='store_true')

        parser.add_option('--force-delete', action='store_true',
                help='force deletion of old packages only, event if signed (but old)')

        parser.add_option('--wipe-repo', action='store_true',
                help='wipe repository instead of just remake missing/invalid symlinks to RPM')

        parser.add_option('--wipe-all-old', action='store_true',
                help='default is to keep both latest unsigned and signed package. this option forces to *really* delete *all old* packages. useful only with --force-delete')
        return parser
