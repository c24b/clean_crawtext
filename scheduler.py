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
		job = Job(user_input)
		job.create_from_ui()
		
		
		#create_or_show
		if job.action is None and job.update is None:
			has_job = self.get_one({"name": job.name})
			if has_job is None:
				job.action = "crawl"
				self.create(job.__dict__)
			else:
				#print has_job
				self.show(job.name)
		#run job
		elif job.action is not None:
			print "Scheduling job : %s" %job.action
			print job.__dict__
			#job.create_from_database()
			#job.run()
		elif job.update is not None:
			print job.update
			if job.update == "all":
				print "updating EVERY job with given params"
				#set ownership
				if job.u is True:
					ex_jobs = self.get_list({"user": job.user, "name": job.name})
					if ex_jobs is None:
						ex_jobs = self.get_list({"name": job.name})
						for doc in ex_jobs:
							self.collection.update({"_id": doc['_id']}, {"$set":{"user": job.user}})
						print "All jobs of project %s are sucessfully owned by %s"%(job.name, job.user)
					else:
						#Raise pymongo.errors.OperationFailure: database error: Unsupported projection option: $exists
						#ex_jobs = self.collection.find({"name": job.name}, {"user":{"$exists": False}})
						ex_jobs = self.collection.find({"name": job.name})
						for doc in ex_jobs:
							self.collection.update({"_id": doc['_id']}, {"$set":{"user": job.user}})
						print "Sucessfull updated every job of project %s to be owned by %s. Erase other users"%(job.name, job.user)
					print "Job owned by %s" %(job.user)
					print self.show({"name":job.name})
					
				#set frequency
				else:
					print job.freq
					#update project_name frequency
			elif job.update == "crawl":
				print "Updating crawl project"
				has_job = self.get_one({"name": job.name, "action": "crawl"})
				if has_job is None:
					self.create(job.__dict__)
				else:
					print "updating parameters"
					if job.value == "q":
						print "update crawl_job query"
						print job.query
						#update crawl_job query
					elif job.value == "k":
						print "update crawl_job Key"
						print job.key
						#update crawl_job Key
					else:
						print "update crawl_job sources"
						#udpate crawl_job sources
			else:
				#no update
				pass
		elif job.user is not None:
			has_user = self.get_one({"user": job.user})
			if has_user is None:
				print "No project found with user %s" %job.user
			else:
				print "***Project owned by user: %s***" %job.user
				self.show({"user": job.user})
						
	def create(self, project_dict):				
		project_dict["action"] = "crawl"
		project_dict["start_date"] = datetime.now()
		for k, v in project_dict.items():
			 if v is None or v is False:
				 del project_dict[k]
		self.collection.insert(project_dict)
		print "Project %s has been successfully created and scheduled!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(project_dict['name'],project_dict['name'])			
		return
		
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
