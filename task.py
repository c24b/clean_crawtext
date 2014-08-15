#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

class Task(object):
	def __init__(self,name, action = "defaut"):
		'''creating a defaut job conforme à son type'''
		self.name = name
		self.action = action
		self.nb_run = 0
		self.start_date = datetime.today()
		#for first run
		self.repeat = "minute"
		#self.next_run = self.config_next_run(self.start_date, self.repeat)
		#self.last_run = None
		self.msg = None
		self.next = self.next_run(self.repeat, self.start_date)
		
	def create(self, data):
		for k,v in iteritems():
			setattr(self, k, v)
				
	def udpate(self, data):
		pass
	@property
	def next_run(self, repeat, start_date):	
		start_job = start_date
		if repeat == "day":
			return start_job.replace(day=start_job.day+1)
		elif repeat == "week":			
			return start_job.replace(day=start_job.day+7)
			
		elif repeat == "month":
			return start_job.replace(month=start_job.month+1)
			
		elif repeat == "year":
			return start_job.replace(year=start_job.year+1)
		else:
			return start_job
	@property	
	def last_run():
		'''udpate run date'''
		pass
	def run():
		#static Factory
		task.run()
		pass
