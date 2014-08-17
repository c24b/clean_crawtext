#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
from database import *
import re
from datetime import datetime as dt
from job import *
#from abc import ABCMeta, abstractmethod

import docopt
from utils.goose import *


#from utils import 
#from utils import ask_yes_no, validate_email, validate_url
from read_the_doc import CMD_DOC
from utils import *

class Worker(object):
	''' main access to Job Database'''
	DB = Database(TASK_MANAGER_NAME)
	COLL = DB.use_coll(TASK_COLL)
	#values for docopt and YAML?
	ACTION_LIST = ["report", "extract", "export", "archive", "start","stop", "delete","list"]
	SCOPE_LIST = ["-u", "-r", "-q", "-k", "-s"]
	OPTION_lIST	= ['add', 'set', 'append', 'delete', 'expand']
	DATA_C_LIST = ['<url>', '<file>', '<query>', '<key>']
	DATA_U_LIST = ['<email>', '<month>']
	DATA_A_LIST = ['<format>']
	
	
	def __init__(self):
		#defaut params
		self.name = None
		self.action = "unset"
		self.msg ="created"
		self.repeat = "month"
		self.user = "constance@cortext.net"
		self.status = True
		
		#schedule params
		self.run = False
		self.scheduled = True
		self.start_date = dt.now()
		#self.first_run = self.start_date.replace(self.start_day.minute+3)
		self.nb_run = 0
			
	def task_from_ui(self, user_input):
		'''mapping user input into task return job parameters'''
		self.name = user_input['<name>']
		#run immediately
		self.first_run = 1
		#no schedule
		self.scheduled = False
		self.value = None
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
					if user_input["-s"] is False:
						self.action = k
		
					else:
						self.action = "update_sources"
						self.option = k
						
				elif v is True and k in self.SCOPE_LIST:
					self.scope = re.sub("-", "", k)
					
				elif v is True and k in self.OPTION_lIST:
					self.option = k
					self.action = "update_sources"
					self.value = None
					
				elif v is not None and k in self.DATA_C_LIST:
					k = re.sub("<|>", "", k)
					setattr(self, k, v)
					self.action = "update_crawl"
					self.scheduled = True
					self.value = k
				elif v is not None and k in self.DATA_U_LIST:
					k = re.sub("<|>", "", k)
					setattr(self, k, v)
					self.value = k
					self.action = "update_project"
				else:
					continue
			
			return self
			
	def task_from_db(self, query):
		self.select_tasks(query)
		
		if self.task_list is None:
			print "No task with this query"	
			return False
		else:
			for k,v  in self.task.items():
				setattr(self, k, v)
				
			return True
		
	def show_user(self):
		
		user_data = [n for n in self.COLL.find({"user": self.user})]
		if len(user_data) == 0:
			print "No user %s registered" %self.user
			return False
		else:
			print "Project owned by:",self.user, "\n"
			for i, n in enumerate(user_data):
				i = i+1
				print "%s) %s job for '%s'"%(str(i), n["action"], n["name"])
			return True
	
	def create_or_show(self):
		if self.action == "create_or_show":
			#defaut action to create is a crawl
			self.action = "crawl"
			
		self.select_tasks({"name": self.name, "action":self.action})
		if self.task is None:
			print "Task not found."
			self.create_task()
		else:
			self.show_task()		
			
	def create_task(self):
		'''create one specific task'''
		if ask_yes_no("Do you want to create a new project?"):
			print self.__dict__
			self.schedule_task()
			self.run_task()
			return "Sucessfully created '%s' task for project '%s'."%(self.task.action,self.task.name)
		else: sys.exit()
	
	def select_task(self, query):
		self.task = self.COLL.find_one(query)
		return self.task
		
	def select_tasks(self, query):
		'''show tasks that match the filter with a specific order return the set of tasks'''
		self.task_list = list(self.COLL.find(query))
		
		self.task = None
		if len(self.task_list) == 0:
			self.task_list = None
			return None
		else:
			if len(self.task_list) == 1:
				self.task = self.task_list[0]
				task = "task"
				
			else:
				task = "tasks"
			print "\n", len(self.task_list), "%s stored in %s database for %s:'%s'"%(task, str(TASK_MANAGER_NAME), str(query.keys()[0]), str(query.values()[0]))
			return len(self.task_list)	
			
	def show_task(self):
		if self.task_list is not None:
			#print "%s: %s"%(order.capitalize(), query[str(order)])
			print "\n"
			print self.name.upper()
			print "____________________\n"
			for task in self.task_list:
				print "> ", task["action"],":\n"
				print "  parameters"
				print "--------------"
				for k,v in task.items():
					if k == '_id' or k =="action" or k == "name":
						continue
					if v is not False or v is not None:
						print k+":", v
				print "--------------"
			return "____________________"
		else:
			print "No task for project %s"% self.name
			
	def update_crawl(self):
		self.action = "crawl"
		self.select_task({"name": self.name, "action": self.action})
		if self.task is None:
			print "No active crawl has been found for project %s" %self.name
			self.create_task()
		else:
			
			if self.scope == "q":
				self.COLL.update({"_id":self.task["_id"]}, {"$set":{"query": self.query}})
				return "Sucessfully updated query to : %s on crawl job of project %s" %(self.query, self.name)
			elif self.scope == "k":
				self.COLL.update({"_id":self.task["_id"]},{"$set":{"key": self.key}})
				print "Sucessfully added a new BING API KEY to crawl job of project %s"%(self.name)
				if self.option == "append":
					c = CrawlJob(self.task)
					try:
						if c.get_bing() is True:
							return "%s seeds from search successfully added to sources of crawl project '%s'" %(c.nb_seeds, self.name)
						else:
							return c.status["msg"]
					except KeyError:
						return "Unable to search new seeds beacause no query has been set.\nTo set a query to your crawl project '%s' type:\n python crawtext.py %s -q \"your awesome query\"" %(self.name, self.name)
				
			else:
				return self.update_sources()	
				
	def update_sources(self):
		self.select_task({"name":self.name, "action": "crawl"})
		c = CrawlJob(self.task)
		#delete 
		if self.option == "delete":
			#all
			if self.value is None:
				return c.delete()
			#url
			else:
				self.url = check_url(self.url)[-1]
				return c.delete_url(self.url)
		#expand
		elif self.option == "expand":
			self.COLL.update({"_id":self.task["_id"]},{"$set":{"option": self.option}})
			print "Successfully added option expand for crawl project %s"% self.name
			return c.expand()
			
		else:
			#set
			self.COLL.update({"_id":self.task["_id"]},{"$set":{self.value: getattr(self, self.value)}})
			print "Sucessfully added a new %s \"%s\" to crawl job of project %s"%(self.value, getattr(self, self.value), self.name)		
			if self.option == "set":
				return
			#append
			else:	
				return c.get_local()
				
	def update_project(self):
		self.select_task({"name": self.task.name})
		#values = [[k, v] for k,v in doc.items() if k != "name"]
		if self.task_list is None:
			print "No project%s found" %self.name
			return self.create_task()
		else:
			for n in self.task_list:
				#~ print n["name"], n["_id"]
				#~ print self.data, getattr(self, str(self.value))
				print self.COLL.update(n["id"],{"$set":{self.data: getattr(self, self.value)}})	
			return "Succesfully updated the entire project %s with new params %s" %(self.name, self.value)
		
	def refresh_task(self, name, action="crawl"):
		'''after a run update the last_run and set nb_run how to log msg?'''
		pass	
	
	
	def schedule_task(self):
		'''schedule task inserting into db'''
		self.first_run = 4*60
		self.COLL.insert(self.task.__dict__)
		return "%s on project %s has been sucessfully scheduled to be run next %s" %(self.task.action, self.task.name, self.task.repeat)
		
	def schedule_project(self):
		'''schedule complete tasks set for one crawl inserting into db'''
		for action in ["crawl", "report", "export"]:
			w = Worker()
			w.action = action
			self.COLL.insert(w.__dict__)
		return "Project %s with crawl, report and export has been sucessfully scheduled and will be run next %s" %(self.name, self.repeat)
			
	def unschedule_task(self):
		'''delete a specific task'''
		self.select_tasks({"name":self.task.name, "action":self.task.action})
		if len(self.task_list) == 0:
				return "No project %s with task %s has been found." %(self.task.name,self.task.action)
		else:	
			self.COLL.remove({"name": self.task.name, "action":self.task.action})
			#here change name to archives_db_name_date
			return "Task %s of project %s has been sucessfully deleted." 
			
		return "Task %s of project %s has been sucessfully deleted" %(self.task.action, self.task.name)
	
	def archive(self):
		self.repeat = None
		self.next_run = self.start_date.replace(self.start_date.minute, self.start_date.minute+3)
		self.COLL.insert(self.__dict__)
		return "Sucessfully scheduled Archive job for %s Next run will be executed in 3 minutes" %self.url
	
	def delete(self):
		'''delete project and archive results'''
		self.select_task({"name":self.name, "action":"crawl"})
		if self.task is None:
			return "No active crawl job found for %s" %self.name
		else:
			self.COLL.remove({"name":self.name})
			self.select_tasks({"name":self.name})
			if self.task_list is not None:
				print "Before deleting project :\n****Archiving*****" 
				e = ExportJob(self.name)
				e.run()
				db = Database(self.name)
				
				db.client.drop_database(self.name)
			return "Project %s sucessfully deleted." %self.name
	
	
	def start(self):
		self.select_task({"name":self.name, "action":"crawl"})
		if self.task is None:
			return "No active crawl job found for %s" %self.name
		else:
			e = CrawlJob(self.task)
			return e.run()
	def stop(self):
		self.select_task({"name":self.name, "action":"crawl"})
		if self.task is None:
			return "No active crawl job found for %s" %self.name
		else:
			e = CrawlJob(self.task)
			return e.stop()		
			
	def report(self):
		e = ReportJob(self.name)
		return e.run()
	
	def export(self):
		self.select_task({"name":self.name, "action":"crawl"})
		if self.task is None:
			print "No active crawl job found for %s" %self.name
		else:	
			e = ExportJob(self.name)
			return e.run()
		
	def process(self, user_input):
		self.task_from_ui(user_input)
		func = getattr(self,self.action)
		return func()
		
				
class ArchiveJob(Worker):
	def run(self):
		print "Archiving %s" %self.url
		
