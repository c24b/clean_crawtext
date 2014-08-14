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
	
	def create_from_ui(self, user_input):
		'''user_input info to job properties'''
		if user_input["list"] is True:
			if user_input["archives"] is True:
				print "Archives Project: "
				for doc in self.collection.find({"action":"archive"}):
					print "\t-", doc["name"], doc["start_date"]
			else:
				print "Crawl Project: "
				for doc in self.collection.find({"action":"crawl"}):
					try:
						print "\t-", doc["name"], doc["start_date"]
					except KeyError:
						print "\n\t-", doc
						
			sys.exit()			
			
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
		
		job['repeat'] = user_input['<month>']
		
		data_list = ['<url>', '<file>', '<query>', '<key>','<email>']
		for k,v in user_input.items():
			if v is not None and k in data_list:
				job[re.sub("<|>", "",k)] = v
		#job['data'] = [[re.sub("<|>", "",k),v] for k,v in user_input.items() if v is not None and k in data_list]
		#job['data_v = [v for k,v in user_input.items() if v is True and k in option_list]
		return job
		
	def create_or_show(self, job):
		'''show user or show project if project doesn't exists create a new one with defaut params
		return True for show and False for create'''
		action_list = ["report", "extract", "export", "archive", "start", "delete"]
		
		del job['scope']
		del job['option']
		if job['user'] is not None and job['name'] is None:
			del job['name']
			has_user = self.get_one({"user": job['user']})
			if has_user is None:
				print "No user '%s' registered." %job['user']
				return True
			else:
				#print has_user
				print self.show({"user":job['user']}, "name")
				return True
		else:
			del job['user']
			has_job = self.get_one({"name": job['name']})
			if has_job is None:
				if job["name"] not in action_list:
					print "No project '%s' has been found." %job["name"]
					if ask_yes_no("Do you want to create a new project?"):
						new_job = {}
						new_job["name"] = job["name"]
						new_job['action'] = "crawl"
						new_job['start_date'] = datetime.now()
						new_job["repeat"] = "month"
						new_job["wait"], new_job["next_run"] = self.config_next_run(new_job)
						self.collection.insert(new_job)
						print "Sucessfully scheduled a crawl job for project :'%s'\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'], job['name'])
						return False
					else:
						return True
				else:
					print "Project can be named '%s' :(  \nBut you can choose a different name! "%("' or '".join(action_list))
					return True
					
			else:
				#print has_job
				return self.show({"name":job['name']}, "name")
	
	def config_next_run(self,job):	
		next_run = None
		start_job = job["start_date"]
		if job["repeat"] == "day":
			next_run = start_job.replace(day=start_job.day+1)
		elif job["repeat"] == "week":
			
			next_run = start_job.replace(day=start_job.day+7)
			
		elif job["repeat"] == "month":
			
			next_run = start_job.replace(month=start_job.month+1)
			
		elif job["repeat"] == "year":
			
			next_run = start_job.replace(year=start_job.year+1)
		else:
			next_run = start_job
		return next_run
			
	def update_all(self, job):
		'''updating every job of the project'''
		ex_jobs = self.get_list({"name": job['name']})
		#update user ownernship
		
		if job['scope'] == "u":
			job['user'] = job['email']
			#if no project with user declared
			if ex_jobs is None:
				print "No project '%s' found.\n"  %job["name"]
				#Creating a new project with defaut user '%s'" %(job['name'], job['user'])
				#print self.get_list({"name": job['name']})
				if ask_yes_no("Do you want to create a new project?"):
					new_job = {}
					new_job["user"] = job['user']
					new_job["name"] = job["name"]
					new_job['action'] = "crawl"
					new_job['start_date'] = datetime.now()
					new_job["repeat"] = "month"
					new_job["next_run"] = self.config_next_run
					self.collection.insert(new_job)
					return "Sucessfully scheduled a crawl job for project :'%s' with owner '%s'\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'],job['user'], job['name'])
				else:
					sys.exit()
			else:
				#Raise pymongo.errors.OperationFailure: database error: Unsupported projection option: $exists
				#ex_jobs = self.collection.find({"name": job.name}, {"user":{"$exists": False}})
				for doc in ex_jobs:
					self.collection.update({"_id": doc['_id']}, {"$set":{"user": job['user']}})
					#self.collection.update({"_id": doc['_id']}, {"date":{"$push": datetime.today}})
				return "Every job of the project '%s' are now belonging to %s."%(job['name'], job['user'])
			
			
		else:#job['scope'] == "r"
			
			if ex_jobs is None:
				print "No project '%s' found.\n" %(job['name'])
				#print self.get_list({"name": job['name']})
				if ask_yes_no("Do you want to create a new project?"):
					new_job = {}
					new_job["repeat"] = job['repeat']
					new_job["name"] = job["name"]
					new_job['action'] = "crawl"
					new_job['start_date'] = datetime.now()
					new_job["repeat"] = "month"
					new_job["wait"], new_job["next_run"] = self.config_next_run(new_job)
					self.collection.insert(new_job)
					return "Project %s has been successfully created and scheduled %s!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'], job['repeat'], job['name'])
				else:
					sys.exit()
			else:
				#print job.items()	
				for doc in ex_jobs:
					job["wait"], job["next_run"] = self.config_next_run(doc)
					self.collection.update({"_id": doc['_id']}, {"$set":{"repeat":job['repeat'], "wait": job["wait"], "next_run": job["next_run"]}})
					#self.collection.update({"_id": doc['_id']}, {"date":{"$push": datetime.today}})	
				return "Every job of project '%s' will be executed every %s."%(job['name'], job['repeat'])
	
	def set_sources(self, job):
		
		if job['option'] == "set":
			self.collection.update({"name": job['name'], 'action': 'crawl'}, {"$set":{"file": job['file']}})
			return "Sucessfully added file '%s' to configure seeds for crawl job of project '%s'"%(job['file'], job['name'])
		elif job['option'] == "append":
			c = CrawlJob(job)
			try:
				if c.get_local(job['file']) is True:
					self.collection.update({"name": job['name'], 'action': 'crawl'}, {"$set":{"file": job['file']}})
					return "Sucessfully added urls of file '%s' in sources db for crawl job of project '%s'"%(job['file'], job['name'])
				else:
					return c.error_type
			except AttributeError:
				return "No file with url found for crawl job of project. Verify that your file exists."
			#self.collection.update({"_id": has_job['_id']}, {"$set":{"file": job.file},"$push":{"option": job['option']}})
			
		elif job['option'] == "expand":
			c = CrawlJob(job)
			c.extend()
			#make results automatically being inserted in sources at the beginning
			self.collection.update({"name": job['name'], 'action': 'crawl'},{"$set":{"option": job['option']}})
			return "Sucessfully configured automatic extension of seeds for crawl job of project '%s'" %job['name']
		elif job['option'] == "add":
			c = CrawlJob(job)
			print c.insert_url(job['url'], "manual")
			return "Sucessfully inserted %s to seeds in crawl job of project '%s'" %(job['url'], job['name'])
		elif job['option'] == "delete":
			try:
				c = CrawlJob(job)
				return c.delete_url(job['url'])
			except KeyError:
				c = CrawlJob(job)
				return c.delete()
		else:
			pass
	def update_crawl(self, job):
		job['action'] = "crawl"
		job['start_date'] = datetime.today() 
		has_job = self.get_one({"name": job['name'], "action": job['action']})
		#update crawl_job query
		if job['scope'] == "q":
			if has_job is None:
				print "No project '%s' found.\n" %job['name']
				if ask_yes_no("Do you want to create a new project?"):
					new_job = {}
					new_job["query"]= job["query"]
					new_job["name"] = job["name"]
					new_job['action'] = "crawl"
					new_job['start_date'] = datetime.now()
					new_job["repeat"] = "month"
					new_job["next_run"] = self.config_next_run
					self.collection.insert(new_job)
					return "Sucessfully scheduled crawl for project '%s'.\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'], job['name'])
				else:
					sys.exit()
				
				
			else:	
				self.collection.update({"_id": has_job['_id']}, {"$set":{"query": job['query']}})
				return "Sucessfully added query \"%s\" for crawl job in project '%s." %(job['query'], job['name'])
		#update crawl_job API key
		elif job['scope'] == "k":
			if has_job is None:
				print "No project '%s' found.\n" %job['name']
				if ask_yes_no("Do you want to create a new project?"):
					new_job = {}
					new_job["query"]= job["query"]
					new_job["name"] = job["name"]
					new_job['action'] = "crawl"
					new_job['start_date'] = datetime.now()
					new_job["repeat"] = "month"
					new_job["next_run"] = self.config_next_run
					self.collection.insert(new_job)
					return "Sucessfully scheduled crawl for project '%s'.\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(job['name'], job['name'])
				else:
					sys.exit()
			else:
				if job['option'] == "append":
					#make first search and push it to sources using CrawlJob.get_bing()
					self.collection.update({"_id": has_job['_id']}, {"$set":{"key": job['key']}})
					
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
					return "Sucessfully added key \"%s\" for crawl job in project '%s'\nA crawl job needs a query and seeds to be active.\n\nSee crawtext.py --help on how to activate the crawl adding a query" %(job['key'], job['name'])			
		else:#job.scope == "s"
			return self.set_sources(job)
	
	def activate(self, job):
		#action_list = ["report", "extract", "export", "archive", "start", "delete"]
		if job['action'] == "delete":
			n = [n for n in self.collection.find({"name": job['name']})]
			if len(n) == 0:
				return "No project %s has been found. Check the name of your project" %(job['name'])
			self.collection.remove({"name": job['name']})
			#here change name to archives_db_name_date
			return "%s has been sucessfully deleted. Results and logs are saved in the database of the project.\nTo see stats type:\n\t python crawtext.py %s report\nTo have direct acess to database, type:\n\t mongo %s\n\t>db.results.find()\n\t>db.logs.find()\n\t>db.sources.find()" %(job['name'], job['name'])
		elif job['action'] == "report":
			r = ReportJob(job)
			return r.run()
		elif job['action'] == "export":
			e = ExportJob(job)
			return e.run()
		elif job['action'] == "archive":
			a = ArchiveJob(job)
			os.spawnl(os.P_NOWAIT, a.run())
			return "Archiving %s. A email will be sent when finished" %job["url"]
		elif job['action'] == "start":
			has_job = self.collection.find_one({"name": job['name'], "action":"crawl"})
			if has_job is not None:
				c = CrawlJob(has_job)
				#return c.run()
				os.spawnl(os.P_NOWAIT, c.run())
				return "Crawling %s. An email will be sent when finished" %job["name"]
			else:
				return "Job project not properly configured.\n Type python crawtext.py %s to see parameters" %self.name
		else:
			self.collection.insert(job)
			return "Sucessfully scheduled %s on %s" %(job['action'], job['name'])
	
	def schedule(self, user_input):
		job = self.create_from_ui(user_input)
		
		#activate
		if len(job['action']) == 1 and len(job['scope']) == 0:
			job['action'], = job['action']
			job['start_date'] = datetime.now()
			job["next_run"] = self.config_next_run(job)
			del job['scope']
			del job['repeat']
			del job['option']
			self.activate(job)
		#udpate
		elif len(job['scope']) == 1:
			
			job['scope'], = job['scope']
			#update every project
			if job['scope'] in ['u', 'r']:
				del job['option']
				return self.update_all(job)
				 
			#udpate crawl
			else:
				
				try:
					job['option'], = job['option']
				except ValueError:
					del job['option']
				return self.update_crawl(job)
		#create or show
		else:
			if self.create_or_show(job) is False:
				self.activate(job)
			return 
			
		
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
				return project_list
			else:
				return None
		elif type(project_name) == str:
			project_list = [n for n in self.collection.find({"name":project_name})]
			if len(project_list)> 0:
				return project_list
		else:
			return None
	
	def show(self, values, by=None):
		project_list = self.get_list(values)
		if project_list is not None:
			#print "******\t%s : %s    ******" %(by, values.values()[0])
			for i,job in enumerate(project_list):
				i = i+1
				db = Database(job["name"])
				queue = db.use_coll("queue").distinct("url")
				sources = db.use_coll("sources").distinct("url")
				results = db.use_coll("results").distinct("url")
				logs_err = db.use_coll("logs").distinct("url")
				logs = [n for n in db.use_coll("logs").find({"code":"-1"}).distinct("url")]
				print "\n %s) Project: %s"%(str(i),job["name"].upper())
				print "----------------------"
				for k,v in job.items():
					if k == '_id':
						continue
					if v is not False or v is not None:
						print k+":", v
				if job["action"] == "crawl":
					print "nb de seeds:",len(sources),"urls"
					print "nb de resultats:",len(results),"articles"
					print "nb d'erreurs:",len(logs_err),"urls"	
					print "dont",len(logs),"pages non pertinentes"
					print "nb d'urls à traiter:",len(queue),"urls"	
				print "----------------------"
				
			return "" 			
		
	'''
	def run_job(self, job_name=None):
		Execute tasks from Job Database
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
	'''
