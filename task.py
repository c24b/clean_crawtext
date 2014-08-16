#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from database import Database, TASK_COLL, TASK_MANAGER_NAME
from read_the_doc import CMD_DOC
from docopt import docopt
from utils import validate_email, validate_url
import re
class Task(object):
	'''A simple Task'''
	DB = Database(TASK_MANAGER_NAME)
	COLL = DB.use_coll(TASK_COLL)
	ACTION_LIST = ["report", "extract", "export", "archive", "start","stop", "delete","list"]
	SCOPE_LIST = ["-u", "-r", "-q", "-k", "-s"]
	OPTION_lIST	= ['add', 'set', 'append', 'delete', 'expand']
	DATA_C_LIST = ['<url>', '<file>', '<query>', '<key>']
	DATA_U_LIST = ['<email>', '<month>']
	DATA_A_LIST = ['<format>']
	
	def __init__(self):
		'''Une tache est d'abord définie par le nom du projet et son type'''
		#defaut params
		self.name = None
		self.action = "unset"
		self.msg ="created"
		self.repeat = "month"
		self.user = "4barbes@gmail.com"
		self.status = True
		
		#schedule params
		self.run = False
		self.scheduled = True
		self.start_date = datetime.today()
		#self.first_run = self.start_date.replace(self.start_day.minute+3)
		self.nb_run = 0
		
		
		
	
	
	def parse_input(self, user_input):
		self.name = user_input['<name>']
		#run immediately
		self.first_run = 1
		#no schedule
		self.scheduled = False
		
		if validate_email(self.name) is True:
			self.action = "show_user"
			self.user = self.name
			return self
			
		elif validate_url(self.name) is True:
			self.action = "archive"
			self.url = self.name
			self.scheduled = True
			try:
				self.format = 	user_input['<format>']
			except KeyError:
				self.format = "defaut"
				return self	
		elif user_input["archive"] is True:
			self.action = 'archive'
			self.url = user_input['<url>']
			self.name = self.url
			self.scheduled = True
			try:
				self.format = 	user_input['<format>']
			except KeyError:
				self.format = "defaut"
				return self
		else:
			self.action = "create_or_show"		
			for k,v in user_input.items():
				if v is True and k in self.ACTION_LIST:
					self.action = k
					return self
				elif v is True and k in self.SCOPE_LIST:
					self.scope = re.sub("-", "", k)
					self.action = "udpate"
					
				elif v is True and k in self.OPTION_lIST:
					self.option = k
					
					
				elif v is not None and k in self.DATA_C_LIST:
					setattr(self, re.sub("<|>", "", k), v)
					self.action = "update_crawl"
					self.scheduled = True
				elif v is not None and k in self.DATA_C_LIST:
					setattr(self, re.sub("<|>", "", k), v)
					
					self.action = "update_all"
				else:
					continue
			
			return self		
				
		
	@property
	def last_run(self):
		self.last_run = datetime.today()
		return self.last_run
	
	def map_doc(self, data):
		for k,v in data.items():
			if v is not None:
				setattr(self, k, v)
			elif v is True:
				setattr(self, k, v)
			else: continue
					
				
	def update(self, data):
		self.next_run = self.next_run(self.repeat, self.start_date)
		pass
	
	def __get_key__(input, filter):
		for k,v in input.items():
			if k in filter.items():
				if v is True:
					yield k
	def __get_value__(input, filter):
		for k,v in input.items():
			if k in filter.items():
				if v is True:
					yield v
	
	@property
	def next_run(self, repeat = None):
		if repeat is not None:
			self.repeat = repeat
		
		if self.repeat == "day":
			return self.creation_date.replace(day=start_job.day+1)
		elif self.repeat == "week":			
			return self.creation_date.replace(day=start_job.day+7)
			
		elif self.repeat == "month":
			return self.creation_date.replace(month=start_job.month+1)
			
		elif self.repeat == "year":
			return self.creation_date.replace(year=start_job.year+1)
		else:
			return self.creation_date
	
	@property	
	def last_run(self):
		'''udpate run date'''
		self.last_run = datetime.today()
		return self.last_run
	def __str__(self):
		return "%s"%(str(self.__dict__))
			
	def run():
		#static Factory
		#task.run()
		log = Job.run()
		self.msg = log
		self.last_run()
		return self
		
class CrawlTask(Task):
	pass

class ArchiveTask(Task):
	def udpate(self, doc):
		self.format = "defaut"
		self.url = doc.name
		self.name = doc.name
		self.action = doc.action
		self.repeat = None
		self.map_doc(doc)
		
		
	def run(self):
		print self.name
		print "Archiving %s" %self.url
		return True
				
if __name__ == "__main__":
	user_input = docopt(CMD_DOC)
	t = Task(user_input)
	t.config()
	print t
