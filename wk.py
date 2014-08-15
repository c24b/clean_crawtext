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
	_db = Database(TASK_MANAGER_NAME)
	_coll = self._db.use_coll(TASK_COLL)
	
	def __init__(self):
		'''init the project base with db and collections'''
		pass
		
	def task_from_ui(self, user_input):
		'''mapping user input into task return job parameters'''
		self.task = Task(user_input)
		t.config()
		return self.task
	
	def task_from_db(self):
		self.task = Task({"name": name})
		self.map_doc()
		
	def process(self):
		 
						
		if validate_email(t.name) is True:
		#if validate_email(job['name']) is True:
			#user interrogation
			#user_projects = self.collection.find({"user": job["name"]}):
			self.select_tasks({"user": t.name})
			#self.select_tasks({"user": job["name"]})
			if len(self.task_list) == 0:
				print "User %s is not registered.No projects belonging to %s have bee found" %(job["name"],job["name"])
			else:
				self.show_tasks({"user": t.name}, "user")
				#self.show_tasks({"user": job["name"]}, "user")
			sys.exit()
		elif validate_url(t.name) is True:
			t.action = "archive"
		#elif is_valid_url(job['name']) is True:
			#archive interrogation
			#archive_project = self.collection.find({"url": job["name"]}):
			self.select_tasks({"action": t.action, "url":t.name})
			#self.select_tasks({"action": "archive", "url":job["name"]}, "action"})
			if self.task_list is None:
				print "Site %s is not archived.\nTo archive a new site type: python crawtext.py archive %s" %(t.name, t.name)
				#print "Site %s is not archived.\nTo archive a new site type: python crawtext.py archive %s" %(job["name"], job["name"])
				sys.exit()	
			else:
				t.update(user_input)
				print t.__dict__
				self.schedule_task(t)
				#self.create_task(job, "archive")
		#task interrogation
		else:	
			#action
			action_list = ["report", "extract", "export", "archive", "start","stop", "delete","list"]
			job['action'] = [k for k,v in user_input.items() if v is True and k in action_list]
			#crawl config
			if len(job['action']) == 0:
				scope_list = ["-u", "-r", "-q", "-k", "-s"]
				job["udpate"] = [re.sub("-", "",k) for k,v in user_input.items() if v is True and k in scope_list]
				if len(job["update"]) == 0:
					#no udpate
					#create or show
					self.select_tasks(self,{"action":crawl, "name": job["name"]})
					if self.task_list is None:
						new_job = self.create_task(job, "crawl")
						#job["next_run"] = +2minutes
						return self.schedule_task(new_job)
						
				elif scope in scope_list[0:1]:
					print "Udpating",scope
					for k,v in user_input.items():
						if k in ["email", "month"]:
							if v is not None or v != "":
								job[k] = v
					return self.update_project(job["name"], job)
				else:
					print "Update crawl" 
					job["scope"] = [re.sub("-", "",k) for k,v in user_input.items() if v is True and k in scope_list[2:]]
					option_list = ['add', 'set', 'append', 'delete', 'expand']
					job['option'] = [k for k,v in user_input.items() if v is True and k in option_list]
					if len(job['option']) == 0:
						if self.task_list is not None:
							return self.show_tasks({"action":crawl, "name": job["name"]}, "name")
						else:
							return "No project %s with active crawl found" %job["name"]
					else:		
						data_list = ['<url>', '<file>', '<query>', '<key>']
						for k,v in user_input.items():
							if v is not None and k in data_list:
								job[re.sub("<|>", "",k)] = v
						self.update_task(job, crawl, scope)		
						
			elif job["action"] == "archive":
				job["format"] = format
				job["url"] = url
				job["name"] = url
				job["start_date"] = datetime.today
				#job["next_run"] = +2minutes
				return self.schedule_task(job)
			else:
				#execute immediately the task without scheduling it
				return Task.run(job["action"], job["name"])
			
	
	def task_from_db(self, query):
		self.select_tasks(query)
		if self.task_list is not None:
			return [Task(t.name, t.action) for t in self.task_list]
		else:
			print "No task with this query"	
				
				
	def create_task(self,job, type="crawl"):
		'''create one specific task'''
		if ask_yes_no("Do you want to create a new project?"):
			job["action"] = type
			j = Job(job)
			return j.__dict__
		else: sys.exit()
	
	def select_tasks(self, query):
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
			
	def update_task(self, doc, action="crawl", scope="s"):
		self.select_task(self, {"name":doc["name"], "action": action})
		if self.task_list == 1:
			doc = self.task[0]
			#c = CrawlJob(doc)
			#c.update_values()
			#c.set_sources()
		pass
	
	def update_project(self, doc):
		self.project_name = doc["name"]
		del doc["name"]
		del doc["action"]
		self.select_task({"name": doc["name"]}, "name")
		#values = [[k, v] for k,v in doc.items() if k != "name"]
		if self.task_list is not None:
			for t in self.task_list:
				for k,v in doc.items():
					if v is not None or v is not False:
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
	def unschedule_task(self, job):
		'''delete a specific task'''
		self.select_tasks({"name":job["name"], "action":job["action"]})
		if len(self.task_list) == 0:
				return "No project %s with task %s has been found." %(job['name'], job["action"])
		else:	
			self.collection.remove({"name": job['name'], "action":job["action"]})
			#here change name to archives_db_name_date
			return "Task %s of project %s has been sucessfully deleted." 
			
		return "Task %s of project %s has been sucessfully deleted" %(job["action"], job["name"], job["repeat"])
	def execute_task(self):
		#j = Job(self, job)
		#j.run()
		pass
	def execute_project(self):
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
		
