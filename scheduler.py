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
from job import CrawlJob

class Scheduler(object):
	''' main access to Job Database'''
	def __init__(self):
		'''init the project base with db and collections'''
		self.task_db = Database(TASK_MANAGER_NAME)
		self.collection =self.task_db.create_coll(TASK_COLL)			
	
	def create_from_ui(self, user_input):
		'''user_input info to job properties'''
		job = {}
		job['name'] = user_input['<name>']	
		job['user'] = None
		
		if validate_email(job['name']) is True:
			job['user'] = job['name']
			
		action_list = ["report", "extract", "export", "archive", "start", "delete"]
		job['action'] = [k for k,v in user_input.items() if v is True and k in action_list]
		
		scope_list = ["-u", "-r", "-q", "-k", "-s"]
		job['scope'] = [re.sub("-", "",k) for k,v in user_input.items() if v is True and k in scope_list]
		
		option_list = ['add', 'set', 'append', 'delete', 'expand']
		job['option'] = [k for k,v in user_input.items() if v is True and k in option_list]
		
		job['repeat'] = user_input['<monthly>']
		
		data_list = ['<url>', '<file>', '<query>', '<key>','<email>']
		for k,v in user_input.items():
			if v is not None and k in data_list:
				job[re.sub("<|>", "",k)] = v
		job['data'] = [[re.sub("<|>", "",k),v] for k,v in user_input.items() if v is not None and k in data_list]
		#job['data_v = [v for k,v in user_input.items() if v is True and k in option_list]
		return job
		
	def create_or_show(self, job):
		'''show user or show project if project doesn't exists create a new one with defaut params'''
		del job['scope']
		del job['option']
		del job['repeat']
		del job['data']
		if job['user'] is not None and job['name'] is None:
			del job['name']
			has_user = self.get_one({"user": job['user']})
			if has_user is None:
				return "No user '%s' registered." %job['user']
			else:
				#print has_user
				return self.show({"user":job['user']}, "name")
		else:
			del job['user']
			has_job = self.get_one({"name": job['name']})
			if has_job is None:
				job['action'] = "crawl"
				job['start_date'] = datetime.today()
				self.collection.insert(job)
				return "Project %s has been successfully created and scheduled!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'],job['name'])			
			else:
				#print has_job
				return self.show({"name":job['name']}, "action")
	
	def update_all(self, job):
		'''updating every job of the project'''
		ex_jobs = self.get_list({"name": job['name']})
		#update user ownernship
		if job['scope'] == "u":
			job['user'] = job['email']
			del job['email']
			del job['scope']
			
			#if no project with user declared
			if ex_jobs is None:
				print "No project '%s' found.\n" 
				#Creating a new project with defaut user '%s'" %(job['name'], job['user'])
				#print self.get_list({"name": job['name']})
				job['action'] = "crawl"
				job['start_date'] = datetime.now()
				self.collection.insert(job)
				return "A default crawl job for project %s has been successfully created with user %s and scheduled!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'],job['user'], job['name'])
				
			else:
				#Raise pymongo.errors.OperationFailure: database error: Unsupported projection option: $exists
				#ex_jobs = self.collection.find({"name": job.name}, {"user":{"$exists": False}})
				for doc in ex_jobs:
					self.collection.update({"_id": doc['_id']}, {"$set":{"user": job['user']}})
					#self.collection.update({"_id": doc['_id']}, {"date":{"$push": datetime.today}})
				return "Every job of the project '%s' are now belonging to %s."%(job['name'], job['user'])
			
			
		else:#job['scope'] == "r"
			
			if ex_jobs is None:
				print "No project '%s' found.\n Creating a new project that will be repeated '%s'" %(job['name'], job['repeat'])
				#print self.get_list({"name": job['name']})
				del job['scope']
				del job['option']
				del job['data']
				job['action'] = "crawl"
				job['start_date'] = datetime.now()
				
				self.collection.insert(job)
				return "Project %s has been successfully created and scheduled %s!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'], job['repeat'], job['name'])
			else:
				#print job.items()	
				for doc in ex_jobs:
					self.collection.update({"_id": doc['_id']}, {"$set":{"repeat":job['repeat']}})
					#self.collection.update({"_id": doc['_id']}, {"date":{"$push": datetime.today}})	
				return "Every job of the project '%s' will be executed %s."%(job['name'], job['repeat'])
			
	def update_sources(self, job):
		print "update crawl_job sources"
		if job['option'] == "set":
			print job['file']
			#self.collection.update({"_id": has_job['_id']}, {"$set":{"file": job.file}, "$set":{"option":[]}})
		elif job['option'] == "append":
			print "sources.db add file urls to sources"
			print job['file']
			#self.collection.update({"_id": has_job['_id']}, {"$set":{"file": job.file},"$push":{"option": job['option']}})
		elif job['option'] == "extend":
			print "sources.db add results to sources"
			#make results automatically being inserted in sources at the beginning
			#self.collection.update({"_id": has_job['_id']},"$push":{"option": job['option']}})
		elif job['option'] == "add":
			print "sources.db add url"
			print job['url']
		else:
			#job['option'] == delete
			if job.url is not None:
				print job['url']
				print "sources.db delete url	"
			else:
				print "sources.db drop	"
	def update_crawl(self, job):
		job['action'] = "crawl"
		job['start_date'] = datetime.today() 
		has_job = self.get_one({"name": job['name'], "action": job['action']})
		if job['scope'] == "q":
			print "update crawl_job query"
			if has_job is None:
				del job['repeat']
				del job['user']
				del job['scope']
				del job['data']
				del job['option']
				print "No project '%s' found.\n" %job['name']
				#print job
				self.collection.insert(job)
				return "A default crawl job for project %s has been successfully created with query \"%s\" and scheduled!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'],job['query'], job['name'])
			else:	
				self.collection.update({"_id": has_job['_id']}, {"$set":{"query": job['query']}})
				return "Sucessfully added query \"%s\" for crawl job in project '%s'\nA crawl job needs a query and seeds (Bing API key or/and a set of urls) to be active.\n\n See crawtext.py --help on how to activate the crawl adding seeds" %(job['query'], job['name'])
			#update crawl_job query
		elif job['scope'] == "k":
			
			if has_job is None:
				del job['repeat']
				del job['user']
				del job['scope']
				del job['data']
				del job['option']
				print "No project '%s' found.\n" %job['name']
				#print job
				self.collection.insert(job)
				return "A default crawl job for project '%s' has been successfully created and scheduled with key \"%s\" \n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'],job['key'], job['name'])
			else:
				if job['option'] == "append":
					
					self.collection.update({"_id": has_job['_id']}, {"$set":{"key": job['key']}})
					#make first search and push it to sources adding a special method from CrawlJob search seeds
					c = CrawlJob(job)
					try:
						if c.get_bing(key = job['key'], query = has_job['query']) is True:
							return "Seeds from search successfully added to sources of crawl project '%s'" % job['name']
						else:
							return c.error_type
					except KeyError:
						return "Unable to search new seeds beacause no query has been set.\nTo set a query to your crawl project '%s' type:\n python crawtext.py %s -q \"your awesome query\"" %(job['name'], job['name'])
				else:		
					#job.option == "set":	
					self.collection.update({"_id": has_job['_id']}, {"$set":{"key": job['key']}})
					#"$push":{"update_sources":datetime.today()}
					return "Sucessfully added key \"%s\" for crawl job in project '%s'\nA crawl job needs a query and seeds to be active.\n\nSee crawtext.py --help on how to activate the crawl adding a query" %(job['key'], job['name'])
				
				
				
		else:#job.scope == "s"
			return self.udpate_sources(job)
					
	def schedule(self, user_input):
		job = self.create_from_ui(user_input)
		
		#schedule		
		if len(job['action']) == 1:
			job['action'], = job['action']
			job['start_date'] = datetime.now()
			del job['scope']
			del job['repeat']
			del job['data']
			del job['option']
			self.collection.insert(job)
			return "Sucessfully scheduled %s on %s" %(job['action'], job['name'])
		#udpate
		elif len(job['scope']) == 1:
			
			job['scope'], = job['scope']
			#update every project
			if job['scope'] in ['u', 'r']:
				del job['scope']
				del job['repeat']
				del job['data']
				return self.update_all(job)
				 
			#udpate crawl
			else:
				del job['scope']
				del job['repeat']
				del job['data']
				job['option'], = job['option']
				return self.update_crawl(job)
		#create or show
		else:
			return self.create_or_show(job)
			

	def delete(self, project_name):
		'''Delete existing project'''
		job_list = self.get_list(project_name)
		if job_list is not None:
			#one by one
			#~ for n in job_list:
				#~ self.collection.remove(n)
			self.collection.drop(project_name)
			print "All the tasks of the project '%s' have been sucessfully deleted !"%project_name
			return True
		else:
			print "No existing project '%s' with active tasks found"%project_name
			return False
			
	def get_one(self, project_name):
		'''get one job'''
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
				return None
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
				
				for k,v in job.items():
					if k == ['_id']:
						continue
					if v is not False or v is not None:
						print k, v
				print "====================="		
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
