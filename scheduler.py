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
		j = Job(user_input)
		j.create_from_ui()
		
		if j.start is True:
			if j.name is not None:
				return self.run_job(j.name)
			else:
				return self.run_job()
		elif j.delete is True:
			return self.delete(j.name)	
		elif j.update is not None:
			print "Updating"
			if j.update == "all":
				print "All"
				job_list = [n for n in self.collection.find({"name":j.name})]
				if len(job_list) == 0:
					return self.create(j.__dict__)
				elif j.user is not None:
					for n in job_list:	
						self.collection.update({"_id":n["_id"]}, {"$set":{"user":j.user}}, upsert=False)
					print "User '%s' will be the owner of every jobs of the project '%s'" %(j.user, j.name)
					return sys.exit()
					
				elif j.freq is not None:
					print j.freq
					for n in self.collection.find({"name":j.name}):
						self.collection.update({"_id":n["_id"]}, {"$set":{"frequency":j.freq}}, upsert=False)
					print "Every task of project %s will be run on a %s basis"%(j.name, j.freq)
					return sys.exit()
			else:
				print "Crawl"
				scheduled_job = self.get_one({"name":j.name, "action": "crawl"})
				if scheduled_job is not None:
					print self.update(j.__dict__)
					return sys.exit()
				else:
					j.action = "crawl"
					print self.create(j.__dict__)
					return sys.exit()
		
		elif j.action is not None:
			print "Running", j.action
			print self.create(j.__dict__)
			return sys.exit()
		
		elif j.name is not None and self.get_one(j.name) is None:			
			print self.create(j.__dict__)
			return sys.exit()
			
		elif j.user is not None:
			self.show_by(j, by="user")
			return sys.exit()
		else:
			self.show(j.name)
			return sys.exit()
			#j.create()	
		
	def create(self, project_dict):				
		 project_dict["action"] = "crawl"
		 project_dict["start_date"] = datetime.now()
		 self.collection.insert(project_dict)
		 return "Project %s has been successfully created and scheduled!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(project_dict['name'],project_dict['name'])			
		 
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
