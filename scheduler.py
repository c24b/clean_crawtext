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
	def create_or_show(self, job):
		#create_or_show
		has_job = self.get_one({"name": job.name})
		if has_job is None:
			job.action = "crawl"
			return self.create(job.__dict__)
		else:
			#print has_job
			return self.show({"name":job.name}, "action")
	
	def update_all(self, job):
		if job.scope == "u":
			ex_jobs = self.get_list({"user": job.user, "name": job.name})
			if ex_jobs is None:
				ex_jobs = self.get_list({"name": job.name})
				for doc in ex_jobs:
					self.collection.update({"_id": doc['_id']}, {"$set":{"user": job.user}})
					#self.collection.update({"_id": doc['_id']}, {"date":{"$push": datetime.today}})	
				print "All jobs of project %s are sucessfully owned by %s"%(job.name, job.user)
			else:
				#Raise pymongo.errors.OperationFailure: database error: Unsupported projection option: $exists
				#ex_jobs = self.collection.find({"name": job.name}, {"user":{"$exists": False}})
				ex_jobs = self.collection.find({"name": job.name})
				for doc in ex_jobs:
					self.collection.update({"_id": doc['_id']}, {"$set":{"user": job.user}})
					#self.collection.update({"_id": doc['_id']}, {"date":{"$push": datetime.today}})
				print "Every job of the project '%s' are now belonging to %s."%(job.name, job.user)
			
			return self.show({"user":job.user}, "name")
		else:
			ex_jobs = self.collection.find({"name": job.name})
			for doc in ex_jobs:
				self.collection.update({"_id": doc['_id']}, {"$set":{"repeat":job.value}})
				#self.collection.update({"_id": doc['_id']}, {"date":{"$push": datetime.today}})	
			print "Every job of the project '%s' will be run %s."%(job.name, job.value)
			return 	
	def update_sources(self, job):
		print "update crawl_job sources"
		if job.option == "set":
			print job.file
			#self.collection.update({"_id": has_job['_id']}, {"$set":{"file": job.file}, "$set":{"option":[]}})
		elif job.option == "append":
			print "sources.db add file urls to sources"
			print job.file
			#self.collection.update({"_id": has_job['_id']}, {"$set":{"file": job.file},"$push":{"option": job.option}})
		elif job.option == "extend":
			print "sources.db add results to sources"
			#make results automatically being inserted in sources at the beginning
			#self.collection.update({"_id": has_job['_id']},"$push":{"option": job.option}})
		elif job.option == "add":
			print "sources.db add url"
			print job.url
		else:
			#job.option == delete
			if job.url is not None:
				print job.url
				print "sources.db delete url	"
			else:
				print "sources.db drop	"
	def update_crawl(self, job):
		if job.scope == "q":
			print "update crawl_job query"
			self.collection.update({"_id": has_job['_id']}, {"$set":{"query": job.query}})
			#update crawl_job query
		elif job.scope == "k":
			print "update crawl_job Key"
			if job.option == "set":
				return self.collection.update({"_id": has_job['_id']}, {"$set":{"key": job.key}})
				#self.collection.update({"_id": has_job['_id']}, {"$set":{"option": []}})
			#update crawl_job Key
			else:
			# job.option == "append":
				#make first search and push it to sources
				#self.collection.update({"_id": has_job['_id']}, {"$set":{"key": job.key}})
				return self.collection.update({"_id": has_job['_id']}, {"$set":{"key": job.key},"$push":{"option": job.option}})			
		else:#job.scope == "s"
			return self.udpate_sources(job)
					
	def update_job(job):
		if job.update == "all":
			return self.update_all(job)
					
		else:#job.update == "crawl":
			has_job = self.get_one({"name": job.name, "action": "crawl"})
			if has_job is None:
				return self.create(job.__dict__)
			else:
				self.update_crawl(job)
				return self.collection.update({"_id": has_job['_id']}, {"date":{"$push": datetime.today}})						
	
	def schedule(self, user_input):
		job = Job()
		job = job.create_from_ui(user_input)
		print job.__dict__
		#~ if job.name is not None:
			#~ print job.name, job.action,  job.udpate
			#~ if job.delete is True:
				#~ print self.collection.drop(job.name)
				#~ print "Sucessfully deleted project '%s'" %(job.name) 
			#~ else:
				#~ print job.action		
				#~ if job.action is not None:
				#~ #run job
					#~ self.collection.insert(job.__dict__)
					#~ print "Sucessfully scheduled %s on project '%s'" %(job.action, job.name) 
			#create_or_show
			#elif job.action is None and job.update is None:
			#	pass
				#self.create_or_show(job)
			#udpate job
			#else: #elif job.update is not None:
			#	self.udpate(job)
		#show user		
		#else:
		#elif job.user is not None:
		#	has_user = self.get_one({"user": job.user})
		#	if has_user is None:
		#		print "No project found with user %s" %job.user
				
		#	else:
		#		print self.show({"user": job.user})
		#	return 	
						
	def create(self, project_dict):				
		project_dict["action"] = "crawl"
		project_dict["start_date"] = datetime.now()
		for k, v in project_dict.items():
			 if v is None or v is False:
				 del project_dict[k]
		self.collection.insert(project_dict)
		print "Project %s has been successfully created and scheduled!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(project_dict['name'],project_dict['name'])			
		return
		
	
	def delete(self, project_name):
		'''Delete existing project'''
		job_list = self.get_list(project_name)
		if job_list is not None:
			#~ for n in job_list:
				#~ self.collection.remove(n)
			#~ print "All the tasks of the project '%s' have been sucessfully deleted !"%project_name
			self.collection.drop(project_name)
			print "All the tasks of the project '%s' have been sucessfully deleted !"%project_name
			return True
		else:
			print "No existing project '%s' with active tasks found"%project_name
			return False
			
	def get_one(self, project_name):
		if project_name is None:
			return None
		elif type(project_name) == dict:
			return self.collection.find_one(project_name)
		else:
		#elif type(project_name) == str:
			if validate_email(project_name) is True:
				return self.collection.find_one({"email":project_name})
			elif validate_url(project_name) is True:
				return self.collection.find_one({"name":project_name, "action": "archive"})
			else:	
				return self.collection.find_one({"name":project_name})
		
	
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
	
	def show(self, values, by=None):
		project_list = self.get_list(values)
		if project_list is not None:
			print "******\t%s : %s    ******" %(by, values.values()[0])
			for job in project_list:
				print "*******"
				for k,v in job.items():
					if v is not False or v is not None:
						print k, v
				
				
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
