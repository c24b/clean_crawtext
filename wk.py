#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
from database import Database, TASK_MANAGER_NAME, TASK_COLL
import re
from datetime import datetime
#from abc import ABCMeta, abstractmethod

import docopt
from utils.goose import *
from datetime import datetime
#from utils import 
#from utils import ask_yes_no, validate_email, validate_url
from read_the_doc import CMD_DOC
from task import Task

class Worker(object):
	''' main access to Job Database'''
	
	def __init__(self):
		self.db = Database(TASK_MANAGER_NAME)
		self.coll = self.db.use_coll(TASK_COLL)
	
		
	def task_from_ui(self, user_input):
		'''mapping user input into task return job parameters'''
		self.task = Task(user_input)
		self.task.config()
		return self.task
			
	def task_from_db(self, query):
		self.select_tasks(query)
		
		if self.task_list is None:
			print "No task with this query"	
			return False
		else:
			self.task = Task(self.task_list[0])
			self.map_doc()
			return self.task
	def process(self, user_input):
		#creating a task
		self.task_from_ui(user_input)
		
		if self.task.action == "create_or_show":
			#create_andschedule or show a defaut crawl job if exists
			self.task.action = "crawl"
			if self.task_list is not None:
				return self.show_task()
			else:
				return self.create_task()
		elif self.task.action == "update_all":
			return self.udpate_project()
			#self.udpate_all() with self.project_data.values
		elif self.task.action == "udpate_crawl":
			self.task.action = "crawl"
			return self.udpate_task()
			#self.udpate_crawl() with self.crawl_data.values and self.option	 
		elif self.task.action == "user":
			self.show_user()
		elif self.task.action == "archive":
			#create and schedule or show a new archive job 	
			r = ArchiveTask()
			return r.run()
		elif self.task.action == "report":
			r = ReportTask()
			return r.run()
		elif self.task.action == "export":	
			r = ReportTask()
			return r.run()
			#action directly handle task with no schedule
		else:	
			if self.task.action == "start":
				return self.run_task()
				
			elif self.task.action == "stop":
				return self.stop_task()
			elif self.task.action == "delete":
				print "delete project or delete task"
				return
			elif self.task.action == "list":
				return self.list_task
			#return eval(str(self.task.action).capitalize+"()")
			#return Task.run(job["action"], job["name"])
			
	
				
				
	def create_task(self):
		'''create one specific task'''
		if ask_yes_no("Do you want to create a new project?"):
			self.schedule()
			self.run_task(3*60)
		else: sys.exit()
	
	def select_task(self, query):
		'''show tasks that match the filter with a specific order return the set of tasks'''
		self.task_list = [t for t in self.collection.find(query)]
		
		if len(self.task_list) == 0:
			self.task_list = None
			return 0
		else:
			if len(self.task_list) == 1:
				task = "task"
			else:
				task = "tasks"
			print len(self.task_list), "%s stored in %s database for %s:'%s'"%(task, str(TASK_MANAGER_NAME), str(query.keys()[0]), str(query.values()[0]))
			self.task = [n for n in self.task_list]
			return len(self.task_list)	
			
	def show_task(self):
		if self.task_list > 0:
			print "%s: %s"%(order.capitalize(), query[str(order)])
			for task in self.task_list:
				for k,v in task.items():
					if k == '_id':
						continue
					if v is not False or v is not None:
						print k+":", v	
		else:
			print "No task for %s"% self.task.name
			
	def update_task(self, doc, action="crawl", scope="s"):
		self.select_task(self, {"name":doc["name"], "action": action})
		if self.task_list == 1:
			doc = self.task[0]
			#c = CrawlJob(doc)
			#c.update_values()
			#c.set_sources()
		pass
	
	def update_project(self, doc):
		self.select_task({"name": self.task.name}, "name")
		#values = [[k, v] for k,v in doc.items() if k != "name"]
		if self.task_list is not None:
			for t in self.task_list:
				print self.project_data.keys()
				print self.project_data.values()
				for k,v in self.project_data.items():
					self.collection.update(t["_id"],{"$set":{k, v}})
			print "Succesfully updated project %s with new params" %self.project_name
		else:
			print "No project %s found."%self.project_name
		
	
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
			self.collection.remove(t)
		j = ExportJob(doc)
		log = j.run()
		db = Database(job["name"])
		db.use_coll("results")
		db.drop_database(job["name"])
		return "Project %s deleted. All data of this project has been archived in %s" %log
	def schedule_task(self):
		'''schedule task inserting into db'''
		self.task.first_run = 4*60
		self.collection.insert(self.task)
		return "%s on project %s has been sucessfully scheduled to be run next %s" %(job["action"], job["name"], job["repeat"])
	def schedule_project(self):
		'''schedule complete tasks set for one crawl inserting into db'''
		for action in ["crawl", "report", "export"]:
			self.task.action = action
			self.start_date = datetime.today()
			self.collection.insert(self.task)
		return "Project %s with crawl, report and export has been sucessfully scheduled and will be run next %s" %(self.task.name, self.task.repeat)
			
	def unschedule_task(self):
		'''delete a specific task'''
		self.select_tasks({"name":self.task.name, "action":self.task.action})
		if len(self.task_list) == 0:
				return "No project %s with task %s has been found." %(self.task.name,self.task.action)
		else:	
			self.collection.remove({"name": self.task.name, "action":self.task.action})
			#here change name to archives_db_name_date
			return "Task %s of project %s has been sucessfully deleted." 
			
		return "Task %s of project %s has been sucessfully deleted" %(self.task.action, self.task.name)
	def run_task(self, wait=3*60):
		#j = Job(self, job)
		#j.run()
		pass
	def run_project(self):
		#Crawl or Archive
		#Report
		#Export
		pass
	def run(self, user_input):
		'''main execution from cmdline'''
		job = self.task_from_ui(user_input)
		print job
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
		
