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
	
	def __init__(self, user_input):
		'''Une tache est d'abord définie par le nom du project et son type'''
		self.name = user_input['<name>']
		self.action = "unset"
		#self.start_date = datetime.today()
		self.first_run = 180
		self.raw_data = user_input
		#first_run = start_day.replace(start_day.minute+3)
		#eq to wait 180 sec
		self.nb_run = 0
		self.status = None
		self.msg ="just created"
	
	
	
	def parse_input(self, input):
		self.crawl_data = {}
		self.action = None
		self.scope = ""
		self.project_data = {}
		for k,v in input.items():
			if v is True and k in self.ACTION_LIST:
				self.action = k
				return self.action
			elif v is True and k in self.SCOPE_LIST:
				self.scope = re.sub("-", "", k)
				
			elif v is True and k in self.OPTION_lIST:
				self.option = k
				
			elif v is not None and k in self.DATA_C_LIST:
				self.crawl_data[str(re.sub("<|>", "", k))] = v 
				self.action = "update_crawl"
			elif v is not None and k in self.DATA_C_LIST:
				self.project_data[str(re.sub("<|>", "", k))] = v
				self.action = "update_all"
		return self.action		
			
	@property	
	def start_date(self):
		return datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S')
		
	@property
	def last_run(self):
		self.last_run = datetime.today()
		return self.last_run
	
	
	def config(self):
		if validate_email(self.name) is True:
			self.action = "user"
			self.first_run = 0
		elif validate_url(self.name) is True:
			self.action = "archive"
		elif self.action == "unset":
			self.action = self.parse_input(self.raw_data)
			if self.action is None:
				self.action = "create_or_show"
		else:
			self.action = self.action
		del self.raw_data 
		return self
	
	def map_doc(self):
		print self.raw_data
				
				
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
		
if __name__ == "__main__":
	user_input = docopt(CMD_DOC)
	t = Task(user_input)
	t.config()
	print t
