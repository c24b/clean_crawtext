#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
from database import Database, TASK_MANAGER_NAME, TASK_COLL
import re
from datetime import datetime
#from abc import ABCMeta, abstractmethod

import docopt
from utils.goose import *
from datetime import date, datetime

#from utils import 
#from utils import ask_yes_no, validate_email, validate_url
from read_the_doc import CMD_DOC
from task import *
from utils import *

class Worker(object):
	''' main access to Job Database'''
	DB = Database(TASK_MANAGER_NAME)
	COLL = DB.use_coll(TASK_COLL)
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
		self.user = "4barbes@gmail.com"
		self.status = True
		
		#schedule params
		self.run = False
		self.scheduled = True
		self.start_date = date.today()
		#self.first_run = self.start_date.replace(self.start_day.minute+3)
		self.nb_run = 0
		
	
		
	def task_from_ui(self, user_input):
		'''mapping user input into task return job parameters'''
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
			
	def task_from_db(self, query):
		self.select_tasks(query)
		
		if self.task_list is None:
			print "No task with this query"	
			return False
		else:
			for n in self.task_list:
				t = Task()
				t.task_from_db(n)
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
			
	def process(self, user_input):
		self.task_from_ui(user_input)
		func = getattr(self,self.action)
		func()
		#~ #self.task_from_ui(user_input)
		#~ 
		#~ if self.task.action == "create_or_show":
			#~ #create_andschedule or show a defaut crawl job if exists
			 #~ 
			#~ self.select_task({"name": self.task.name})
			#~ self.task.action = "crawl"
			#~ if self.task_list is not None:
				#~ return self.show_task()
			#~ else:
				#~ return self.create_task()
		#~ elif self.task.action == "update_all":
			#~ self.select_task({"name": self.task.name})
			#~ if self.task_list is not None:
				#~ #self.udpate_all() with self.project_data.values
				#~ return self.udpate_project()
			#~ return "No project %s found" %self.task.name
			#~ 
		#~ elif self.task.action == "udpate_crawl":
			#~ 
			#~ self.select_task({"name": self.task.name, "action": "crawl"})
			#~ if self.task_list is not None:
				#~ self.task.action = "crawl"
				#~ return self.udpate_task()
			#~ return "Project %s has no active crawl"%self.task.name
			#~ #self.udpate_crawl() with self.crawl_data.values and self.option	 
		#~ elif self.task.action == "user":
			#~ self.select_task({"user": self.task.name})
			#~ if self.task_list is not None:
				#~ return self.show_task()
			#~ return "No user %s found"%self.task.name
				#~ 
		#~ elif self.task.action == "archive":
			#~ #create and schedule or show a new archive job
			#~ self.task.format = "defaut"
			#~ self.task.url = self.task.name
			#~ self.task.name = self.task.name
			#~ 
			#~ self.select_task({"name": self.task.name, "action":self.task.action})
			#~ if self.task_list is not None:
				#~ return self.show_task()
			#~ else:
				#~ return self.create_task()
			#~ 
		#~ elif self.task.action == "report":
			#~ r = ReportTask()
			#~ return r.run()
		#~ elif self.task.action == "export":	
			#~ r = ReportTask()
			#~ return r.run()
			#~ #action directly handle task with no schedule
		#~ else:	
			#~ if self.task.action == "start":
				#~ return self.run_task()
				#~ 
			#~ elif self.task.action == "stop":
				#~ return self.stop_task()
			#~ elif self.task.action == "delete":
				#~ print "delete project or delete task"
				#~ return
			#~ elif self.task.action == "list":
				#~ return self.list_task
			#~ #return eval(str(self.task.action).capitalize+"()")
			#~ #return Task.run(job["action"], job["name"])
			
	
				
				
	def create_task(self):
		'''create one specific task'''
		if ask_yes_no("Do you want to create a new project?"):
			del self.task.raw_data
			self.schedule_task()
			self.run_task()
			return "Sucessfully created '%s' task for project '%s'."%(self.task.action,self.task.name)
		else: sys.exit()
	
	def select_task(self, query):
		'''show tasks that match the filter with a specific order return the set of tasks'''
		self.task_list = [t for t in self.COLL.find(query)]
		
		if len(self.task_list) == 0:
			self.task_list = None
			return 0
		else:
			if len(self.task_list) == 1:
				task = "task"
			else:
				task = "tasks"
			print "\n", len(self.task_list), "%s stored in %s database for %s:'%s'"%(task, str(TASK_MANAGER_NAME), str(query.keys()[0]), str(query.values()[0]))
			return len(self.task_list)	
			
	def show_task(self):
		if self.task_list > 0:
			#print "%s: %s"%(order.capitalize(), query[str(order)])
			
			print "\n"
			print self.task.name.upper()
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
			print "No task for %s"% self.task.name
			
	def update_task(self, doc, action="crawl", scope="s"):
		self.select_task(self, {"name":self.task.name, "action": self.task.action})
		if self.task_list is not None:
			for k, v in self.task.items:
				print k,v
			print self.task.scope
			#c = CrawlJob(doc)
			#c.update_values()
			#c.set_sources()
		else:
			print "No task %s found for project %s" %(self.action, self.name)
	
	def update_project(self, doc):
		self.select_task({"name": self.task.name}, "name")
		#values = [[k, v] for k,v in doc.items() if k != "name"]
		for t in self.task_list:				
			print self.project_data.keys()
			print self.project_data.values()
			for k,v in self.project_data.items():
				print k,v
				self.task[k] = v
				#self.COLL.update(t["_id"],{"$set":{k, v}})
		#~ if self.task_list is not None:
			#~ for t in self.task_list:
				#~ print self.project_data.keys()
				#~ print self.project_data.values()
				#~ for k,v in self.project_data.items():
					#~ self.COLL.update(t["_id"],{"$set":{k, v}})
			#~ print "Succesfully updated project %s with new params" %self.project_name
		#~ else:
			#~ print "No project %s found."%self.project_name
			#~ self.task.action = "crawl"
			#~ 
			#~ self.create_task()
			#~ #self.update_task()
	
	def refresh_task(self, name, action="crawl"):
		'''after a run update the last_run and set nb_run how to log msg?'''
		pass	
	def delete_project(self, doc):
		'''delete project and archive results'''
		#Results and logs are saved in the database of the project.\nTo see stats type:\n\t python crawtext.py %s report\nTo have direct acess to database, type:\n\t mongo %s\n\t>db.results.find()\n\t>db.logs.find()\n\t>db.sources.find()" %(job['name'], job['action'])
		self.select_tasks({"name":job["name"]}, "name")
		if self.task_list is None:
			return "No project %s found. Project can't be deleted" %job["name"]
		for t in self.task_list:
			self.COLL.remove(t)
		j = ExportJob(doc)
		log = j.run()
		db = Database(job["name"])
		db.use_coll("results")
		db.drop_database(job["name"])
		return "Project %s deleted. All data of this project has been archived in %s" %log
	def schedule_task(self):
		'''schedule task inserting into db'''
		self.task.first_run = 4*60
		self.COLL.insert(self.task.__dict__)
		return "%s on project %s has been sucessfully scheduled to be run next %s" %(self.task.action, self.task.name, self.task.repeat)
	def schedule_project(self):
		'''schedule complete tasks set for one crawl inserting into db'''
		for action in ["crawl", "report", "export"]:
			self.task.action = action
			self.start_date = datetime.today()
			self.COLL.insert(self.task)
		return "Project %s with crawl, report and export has been sucessfully scheduled and will be run next %s" %(self.task.name, self.task.repeat)
			
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
	
	def run_task(self, wait=3*60):
		#j = Job(self, job)
		#j.run()
		return "Current %s  for project %s will be running in 3 minutes.\n An email will be sent when job is finished"%(self.task.action, self.task.name)
		
	def run_project(self):
		#Crawl or Archive
		#Report
		#Export
		pass
	
