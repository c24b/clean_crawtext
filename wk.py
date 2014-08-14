#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
from database import Database, TASK_MANAGER_NAME, TASK_COLL
import re
from datetime import datetime
from abc import ABCMeta, abstractmethod
#from page2 import Page
import docopt
from utils.goose import *
from datetime import datetime
from job import *
from utils import ask_yes_no

class Worker(object):
	''' main access to Job Database'''
	def __init__(self):
		'''init the project base with db and collections'''
		self.task_db = Database(TASK_MANAGER_NAME)
		self.collection =self.task_db.create_coll(TASK_COLL)
		self.doc = {	"name":None,
						"action":None,
						"start_date":None,
						"next_run":None,
						"last_run":None,
						"status":None,
						"nb_run":0,
						"msg":None,
						}

	def create_from_ui(self, user_input):
		'''mapping user input into task return job parameters'''
		job = {} 
		job['name'] = user_input['<name>']	
		
		#user interrogation
		if validate_email(job['name']) is True:
			#user_projects = self.collection.find({"user": job["name"]}):
			self.select_tasks({"user": job["name"]})
			if len(self.task_list) == 0:
				print "User %s is not registered.No projects belonging to %s have bee found" %(job["name"],job["name"])
			
			else:
				self.show_tasks({"user": job["name"]}, "user")
			sys.exit()
		#archive interrogation
		#~ elif is_valid_url(job['name']) is True:
			#~ #archive_project = self.collection.find({"url": job["name"]}):
			#~ self.select_tasks({"action": "archive", "url":job["name"]}, "action"})
			#~ if len(self.task_list) == 0:
				#~ print "Url %s is not archived." %(job["name"])
				#~ sys.exit()	
		
		#task interrogation
		else:	
			#action
			action_list = ["report", "extract", "export", "archive", "start","stop", "delete","list"]
			job['action'] = [k for k,v in user_input.items() if v is True and k in action_list]
			if len(job['action']) == 0:
				job["action"] = None
			
			#scope udpates
			scope_list = ["-u", "-r", "-q", "-k", "-s"]
			job['scope'] = [re.sub("-", "",k) for k,v in user_input.items() if v is True and k in scope_list]
			if len(job['scope']) == 0:
				job["scope"] = None
			
			#option_list 
			option_list = ['add', 'set', 'append', 'delete', 'expand']
			job['option'] = [k for k,v in user_input.items() if v is True and k in option_list]
			if len(job['option']) == 0:
				job["option"] = None
			
			#repeat
			if user_input['<month>']:
				job['repeat'] = user_input['<month>']
			else:
				job['repeat'] = "month"
			
			#additionnal data
			data_list = ['<url>', '<file>', '<query>', '<key>','<email>']
			for k,v in user_input.items():
				if v is not None and k in data_list:
					job[re.sub("<|>", "",k)] = v		
		return job
			
	def create_task(self,job, type="crawl"):
		'''create one specific task'''
		if ask_yes_no("Do you want to create a new project?"):
			job["action"] = type
			j = Job(job)
			return j.__dict__
		else: sys.exit()
		
	def update_task(self, doc):
		'''adding more info to one specific task'''
		pass
	def update_project(self, doc):
		'''adding multiple info to the project based on name '''
		pass
	def delete_project(self):
		'''delete project and archive results'''	
	def schedule_task(self, job):
		'''schedule task inserting into db'''
		self.collection.insert(job)
		return "%s on project %s has been sucessfully scheduled to be run next %s" %(job["action"], job["name"], job["repeat"])
	def schedule_project(self,job):
		'''schedule complete tasks set for one crawl inserting into db'''
		for action in ["crawl", "report", "export"]:
			job["action"] = action
			self.collection.insert(job)
		return "Project %s has been sucessfully scheduled to be run next %s" %( job["name"], job["repeat"])
		
		
	def unschedule_task(self):
		'''delete task'''
		pass
	def prioritize_task(self):
		'''action list define if the action can be done immediately or scheduled for later in case of long run cmd'''
		pass	
	def execute_task(self):
		'''run specific task'''
		pass
		
	def show_tasks(self, query, order):
		if self.task_list > 0:
			print "%s: %s"%(order.capitalize(), query[str(order)])
			for task in self.task_list:
				for k,v in task.items():
					if k == '_id':
						continue
					if v is not False or v is not None:
						print k+":", v	
		else:
			print "No task for %s"% query.value(order)
			
	def select_tasks(self, query):
		'''show tasks that match the filter with a specific order return the set of tasks'''
		self.task_list = [t for t in self.collection.find(query)]
		print len(self.task_list), "tasks stored in database :",str(TASK_MANAGER_NAME)
		if len(self.task_list) == 0:
			self.task_list = None
			return 0
		else:
			return len(self.task_list)
			 			
	def run(self, user_input):
		'''main execution from cmdline'''
		job = self.create_from_ui(user_input)
		
		#no action declared so defaut is set to crawl
		if job["action"] is None:
			self.select_tasks({"name": job["name"]})
			#no project
			if self.task_list is None:
				print "No project %s has been found." %(job["name"])
				new_job = self.create_task(job, "crawl")
				print "Defaut project will be a crawl job with name %s"%(job["name"])
				print "You will have to set a query and seeds to be executed properly"	
				return self.schedule_task(new_job)				
				#could also schedule a comple project
			else:
				#update project or task?
				#no udpate ==> show
				if job['scope'] is None:
					self.show_tasks({"name": job["name"]}, "name")
					sys.exit()
				else:
					if job["scope"] in ["r", "u"]:
						return self.update_project(self, job)
					else:
						#update sources
						return self.update_task(self,job)
						
		else:
			if job["action"] in ["start", "stop", "list", "delete"]:
				#execute immediately and don't schedule
				return self.run_task(job)
			elif job["action"] in ["export", "report", "archive"]:
				#schedule for next run
				print self.schedule_task(job)
				#and execute once
				return self.run_task(job)
			#self.select_tasks({"name": job["name"], "action": job["action"]}, "name"})	
		
