#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 noexpandtab

import sys

class Report:
    __inline_print_len = 0
    __inline_print_len_new = 0
    def __init__(self, subject, action, verbose, sort):
        self.__subject = subject
        self.__action = action
        self.__verbose = verbose
        self.__sort = sort
        self.__report = {
                "subject" : subject,
                "action"  : action,
                "timeline": []
                }

    def __print_action(self, action):
        print(str(action[0]) + " + " + self.__report["action"] + ' : ' + action[1])


    def add_action(self, msg):
        action = ['', msg]
        if self.__verbose:
            self.__print_action(action)
        self.__report["timeline"].append(action)
    
    def print_report(self):
        timeline = None
        if self.__sort and not self.__verbose:
            timeline = sorted(self.__report["timeline"])
        else:
            timeline = self.__report["timeline"]

        for action in timeline:
            self.__print_action(action)

    @staticmethod
    def inline_print(msg):
        Report.__inline_print_len_new = len(msg)
        spaces = 0
        if Report.__inline_print_len > Report.__inline_print_len_new:
            spaces = Report.__inline_print_len - len(msg)
        sys.stdout.write('\r' + msg + ' ' * spaces)
        sys.stdout.flush()
        Report.__inline_print_len = Report.__inline_print_len_new

