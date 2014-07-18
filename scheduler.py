#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from database import Database, TASK_MANAGER_NAME, TASK_COLL
import re
from datetime import datetime
from abc import ABCMeta, abstractmethod
#from page2 import Page
import docopt
from utils import *
from datetime import datetime
from job import Job

class Scheduler(object):
	''' main access to Job Database'''
	def __init__(self):
		'''init the project base with db and collections'''
		self.task_db = Database(TASK_MANAGER_NAME)
		self.collection =self.task_db.create_coll(TASK_COLL)			
			
	def schedule(self, user_input):
		#j = Job(user_input)
		#j.create_from_ui()
		job = self.create_from_ui(user_input)
		if job['name'] is not None:
			ex_job = self.get_one(job['name'])
			if ex_job is None:
				self.create()
			if job['type'] != 'crawl':
				sel	
			if job['action'] == "create":
				pass
			elif job['action'] == "update":
				pass
			#find existing
		else:
			pass	
	def create_from_ui(self, user_input):
		job_type = ["start", "delete", "report", "export", "archive"]
		
		job = {}
		#cleaning input
		for k, v in user_input.items():
			if v is None or v is False:
				del user_input[k]
			else:
				job[re.sub("<|>|-|--", "", k)] = v
		
		#checking if simple user or project
		if validate_email(job['name']) is True:
			job['user'] = job['name']
			job['name'] = None
		else:
			job['user'] = None
				
		job['type'] = [k for k in job.keys() if k in job_type]
		
			
		if len(job['type']) == 0:
			job['type'] = "crawl"
			crawl_params = ["q", "s", "k"]
			crawl_params_i = ["query", "sources", "key"]
			crawl_values = ["query", "url", "file", "key"]
			crawl_options = ["set", "append", "extend", "extend", "delete"]
			
			if "r" in job.keys():
				frequency = ["monthly", "weekly", "daily"]
				#updating frequency of the call
				job['scope'] = "frequency"
				job['data'] = ('frequency','r', [k for k in frequency if k in job.keys()][0])
				job['option'] = ""
				job['type'] = "project"
				job['action'] = "update"
				
			elif "user" in job.keys():
				#updating owner of the project
				job['scope'] = "user"
				job['data'] = ("user", "u", job['user'])
				job['type'] = "project"
				job['option'] = ""
				job['action'] = "update"
			else:
				#updating crawl project with additionnal values
				job['scope_n'] = [k for k in crawl_params if k in job.keys()]
				job['scope'] = [k for k in crawl_params_i if k[0] in job['scope_n']]
				job['data'] = [k for k in job.keys() if k in crawl_values]
				job['option'] = [k for k in job.keys() if k in crawl_options]
				job['data'] = zip(job['scope'], job['scope_n'], job['data'])[0]
				print job['data']
				if len(job['data']) <= 0:
					job['action'] = "create"
					
				else:
					job['action'] = "update"
		else:
			if job['name'] in job_type.items():
				print "Error"
				return None
			else:
				job['action'] = "create"
				job['option'] = ""
		
		return {"name": job['name'], "type": job['type'], "action": job['action'], "option": job['option'], "data": job['data']}
		#return job_params
			
	def other():	
		'''
		if user_input['start'] is True:
			if user_input['name'] is not None:
				return self.run_job(user_input['name'])
			else:
				return self.run_job()
		elif user_input['delete is True:
			return self.delete(user_input['name)	
		elif user_input['update is not None:
			if user_input['update == "all":
				job_list = [n for n in self.collection.find({"name":user_input['name})]
				if len(job_list) == 0:
					return self.create(user_input['__dict__())
				elif user_input['user is not None:
					for n in job_list:	
						self.collection.update({"_id":n["_id"]}, {"$set":{"user":user_input['user}}, upsert=False)
					print "User '%s' will be the owner of every jobs of the project '%s'" %(user_input['user, user_input['name)
					return sys.exit()
					
				elif user_input['freq'] is not None:
					for n in self.collection.find({"name":user_input['name}):
						self.collection.update({"_id":n["_id"]}, {"$set":{"frequency":user_input['freq}}, upsert=False)
					print "Every task of project %s will be run on a %s basis"%(user_input['name, user_input['freq)
					return sys.exit()
			else:
				print "Crawl"
				scheduled_job = self.get_one({"name":user_input['name, "action": "crawl"})
				if scheduled_job is not None:
					print self.update()
					return sys.exit()
				else:
					user_input['action'] = "crawl"
					self.action = 
					print self.create()
					return sys.exit()
		
		elif user_input['action'] is not None:
			print "Running", user_input['action']
			self.action = user_input['action']
			print self.create_from_database()
			return sys.exit()
		
		elif user_input['name'] is not None:			
			existing_job = self.get_one(user_input['name'])
			if existing_job is None:
				print self.create()
			else:
				self.show(user_input['name'])
			
			return sys.exit()
			
		elif user_input['user'] is not None:
			self.show_by(j, by="user")
			return sys.exit()
		else:
			self.show(user_input['name'])
			'''
		return sys.exit()
			#user_input['create()	
		
	def create(self, project_dict):				
		 project_dict["action"] = "crawl"
		 project_dict["start_date"] = datetime.now()
		 for k, v in project_dict.items():
			 if v is None or v is False:
				 del project_dict[k]
		 
		 self.collection.insert(project_dict)
		 return "Project %s has been successfully created and scheduled!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(project_dict['name'],project_dict['name'])			
	
	def update(self, job):
		
		if job['q']:
			self.collection.update({"_id":project_dict["_id"]}, {"$set":{"query":job["query"]}}, upsert=False)
			print "Setting up query '%s' for the crawl project %s" %(j.query, j.name)
			return sys.exit()
		else:
			crawl_job = crawl_job.get_from_database()
			crawl_job = Job(scheduled_job)
			#access to crawl job database
			#crawl_job = crawl_job.get_from_database()
				# if j.scope == "s":
				# 	print new_job.sources.count()		
	def delete(self, project_name):
		'''Delete existing project'''
		job_list = self.get_list(project_name)
		if job_list is not None:
			for n in job_list:
				self.collection.remove(n)
			print "All the tasks of the project '%s' have been sucessfully deleted !"%project_name
			#print self.collection.drop(project_name)
			return True
		else:
			
			print "No existing project '%s' with active tasks found"%project_name
			return False
			
	def get_one(self, project_name):
		if project_name is None:
			return None
		elif type(project_name) == dict:
			return self.collection.find_one(project_name)
		elif type(project_name) == str:
			if validate_email(project_name) is True:
				return self.collection.find_one({"email":project_name})
			else:	
				return self.collection.find_one({"name":project_name})
		else:
			return None
	
	def get_list(self, project_name=None):
		'''get all the current job'''		
		
		if project_name is None:
			return [n for n in self.collection.find()]
		elif type(project_name) == dict:
			project_list = [n for n in self.collection.find(project_name)]
			if len(project_list)> 0:
				#print "*** Project %s: %s ****" %(project_name.keys(), project_name.values())
				return project_list
			else:
				return  None
		elif type(project_name) == str:
			project_list = [n for n in self.collection.find({"name":project_name})]
			if len(project_list)> 0:
				#print "*** Project %s: %s ****" %(project_name.keys(), project_name.values())
				return project_list
		else:
			return None
	
	def show(self, name):
		project_list = self.get_list({"name": name})
		if project_list is not None:
			print "******\tProject : %s    ******" %(name)
			for job in project_list:
				if job["action"] == "crawl":
					print "action:", job["action"]
				for k,v in job.items():
					if v is not False or v is not None:
						print k, v
					else:
						pass
				
			return "*******************************************" 			
		
	def show_by(self, doc , by="name"):
		project_list = self.get_list({str(by): doc[str(by)]})
		if project_list is not None:
			print "******\tProject %s: %s    ******" %(str(by), str(doc[by]))
			for job in project_list:
				print job["action"]
				for k, v in job.items():
					if k not in ['_id']:
						if v is not False or v is not None:
							print "*\t-", k,'\t', v
			return "*******************************************"
		

	def run_job(self, job_name=None):
		'''Execute tasks from Job Database'''
		if job_name is None:
			project_list = self.get_list()
			for n in project_list:
				j = Job(n)
				j2 = j.create_from_database()
				#try:
				return j2.run()
				#except NotImplementedError:
				#	pass
		else:
			project_list = self.get_list({"name":job_name})
			for n in project_list:
				j = Job(n)
				j2 = j.create_from_database()
				#try:
				return j2.run()
				#except NotImplementedError:
				#	pass
