#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 noexpandtab

import datetime

class Report:
	def __init__(self, subject, action, verbose, sorted):
		self.__subject = subject
		self.__action = action
		self.__verbose = verbose
		self.__sorted = sorted
		self.__report = {
				"subject" : subject,
				"action"  : action,
				"timeline": []
				}

	def __print_action(self, a):
		print(str(a[0]) + " + " + self.__report["action"] + ' : ' + a[1])


	def add_action(self, msg):
		a = ['', msg]
		if self.__verbose:
			self.__print_action(a)
		self.__report["timeline"].append(a)
	
	def print_report(self):
		timeline = None
		if self.__sorted and not self.__verbose:
			timeline = sorted(self.__report["timeline"])
		else:
			timeline = self.__report["timeline"]

		for a in timeline:
			self.__print_action(a)

