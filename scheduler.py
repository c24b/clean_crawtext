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
from job import Job

class Scheduler(object):
	''' main access to Job Database'''
	def __init__(self):
		'''init the project base with db and collections'''
		self.task_db = Database(TASK_MANAGER_NAME)
		self.collection =self.task_db.create_coll(TASK_COLL)			
			
	def schedule(self, user_input):
		'''Schedule a new job from user_input (crawtext.py)'''
		j = Job(user_input)
		j.create_from_ui()
		if j.start is True:
			if j.name is not None:
				self.run_job(j.name)
			else:
				self.run_job()
		
		elif j.action == "show":
			if j.user is not None:
				if self.get_one({"user":j.user}) is not None:
					print "Project owned by '%s'"%j.user
					self.show_by(j,"user")
				
				else:
					#error_msg
					print "User:%s is not already registered" %j.user
					print "To register you as user %s:\n1/Create a new project:\n\tpython crawtext.py yournewproject\n2/Set Ownership to the project:\n\tpython crawtext.py yournewproject -u %s" %(j.user,j.user)
		

			elif j.name is not None:
				if validate_url(j.name):
					print "Archives of the website %s"%j.name
					self.show_by(j.__dict__, "name")
					
				elif j.name in ["crawl", "delete", "archive", "report", "export", "extract"]:
					print "**Project Name** can't be 'crawl', 'archive', 'report', 'extract','export' or 'delete'"
					print "\t*To generate a report:\n\t\tcrawtext.py report pesticides"
					print "\t*To create an export :\n\t\tcrawtext.py export pesticides"
					print "\t*To delete a projet :\n\t\tcrawtext.py delete pesticides"
					print "\t*To archive a website :\n\t\tcrawtext.py archive www.lemonde.fr"
					
				elif self.get_one({"name":j.name}) is None:
					print "No existing project found!"
					j.action ="create"
					try:
						new_job = Job(j.__dict__)
						new_job = new_job.create_from_database()
						new_job.run()
					except KeyboardInterrupt:
						sys.exit()
				else:
					print "Jobs of the project '%s'"%j.name
					self.show_by(j.__dict__, "name")
					#print "To activate crawl, you need to configure the 2 required options:\n\t- A query\n\t- A list of url to crawl OR a search API Key\n To see how to add parameters to the current job: crawtext.py --help" 
		elif j.action == "manage":
		#updating every job of the project
			job_list = [n for n in self.collection.find({"name":j.name})]
			if len(job_list) == 0:
				print "No project '%s' found!\nTo create a new project:\n\tpython crawtext.py %s" %(j.name,j.name)
				sys.exit()
			if j.scope == "u":
				for n in job_list:
					
					self.collection.update({"_id":n["_id"]}, {"$set":{"user":j.user}}, upsert=False)
				print "User '%s' will be the owner of every jobs of the project '%s'" %(j.user, j.name)
			elif j.scope == "r":
				print "Configuring frequency of call for every projects"
				
				for n in self.collection.find({"name":j.name}):
					self.collection.update({"_id":n["_id"]}, {"$set":{"frequency":j.frequency}}, upsert=False)
		#managing existing crawljob
		elif j.action == "manage":
			try:
				scheduled_job = self.collection.find_all({"name":j.name})
				for n in scheduled_job:
					print n
			except IndexError:
				print "No existing crawl project '%s' to update" %j.name
				sys.exit()
				
		elif j.action == "update":	
		
			try:
				scheduled_job = self.collection.find_one({"name":j.name, "action":'crawl'})
			except IndexError:
				print "No existing crawl project '%s' to update" %j.name
				sys.exit()

			crawl_job = Job(scheduled_job)
			#access to crawl job database
			crawl_job = crawl_job.get_from_database()
				# if j.scope == "s":
				# 	print new_job.sources.count()	
			#query 
			if j.scope == "q":
				self.collection.update({"_id":j._id}, {"$set":{"query":j.query}}, upsert=False)
				print "Setting up query '%s' for the crawl project %s" %(j.query, j.name)
				# key api for search
			elif j.scope == "k":
				print "Configuring seeds with search on BING"
				if j.append is True:
					if crawl_job.query is not None:
				 		if j.key is not None:
				 			crawl_job.key = j.key
				 			print "Directly collect seeds url from results search on Bing on query and sending it for next crawl'%s'"%j.query
							print crawl_job.sources.count()
							crawl_job.get_bing()
							print crawl_job.sources.count()
				 		else:
				 			print "No API key found!\n 1/Create a new api search key going to '%s" %("https://datamarket.azure.com/dataset/5BA839F1-12CE-4CCE-BF57-A49D98D29A44")
				 			print "2/Configure your project add this new key to your crawl project:"
				 			print "\tpython crawtext.py %s -k set yourapikey" %j.name
				 			sys.exit()
				 	else:
				 		print "No query found! To set up a query for the crawl project '%s'"%j.name
				# 		print "\tpython crawtext.py %s -q youquery" %j.name
				# 		sys.exit()
			
			elif j.scope == "s":
				if j.set is True:
					print j.url
					if validate_url(j.url):
						print "Adding your new seed url '%s'" %j.url
						if j.url is not None:
							if url not in crawl_job.sources.distinct("url"):
								crawl_job.insert_url(j.url,origin="manual")
								print "adding url %s to sources" %j.url
					else:
						"Your new seed url '%s'is invalid. Please check format." %j.url
				elif j.append is True:
					if j.file is not None:
						crawl_job.file = j.file
						print "Configuring seeds from file '%s'" %j.file
						crawl_job.get_local()
						print "Sucessfully added each url of the file '%s' in the sources of the crawl job of '%s'." %(j.file, j.name)
						self.collection.update({"_id":j._id}, {"$set":{"file":j.file}}, upsert=False)
						print "Sources urls will be verified for each crawljob and updated with the date of crawl."
				elif j.expand is True:
					if crawl_job.results.count() > 0:
						crawl_job.expand()
						print "Results url has been automatically added to sources"
					else:
						print "No results found, expanded mode will be run for next crawl"
						self.collection.update({"_id":j._id}, {"$set":{"expanded":true}}, upsert=False)	

				elif j.delete is True:
					if j.url is not None:
						if crawl_job.sources.find_one({"url":j.url}) is not None:
							crawl_job.sources.remove({"url": j.url})
							#removing url also from current exec?
							#queue.remove({"url":j["url"]})
							print "deleting url %s from sources of the project %s" %(j.url, j.name)
						else:
							print "Url %s was not in sources" %j.url
					else:
						print crawl_job.sources.drop()
				else:
					pass				
			# #Updating status if required elements are set
			# project_db = Database(j.name)
			# sources = project_db.create_coll('sources')	
			# for n in self.collection.find({"name":j.name}):
			# 	try:
			# 		if n['query'] is not None and n['key'] is not None:
			# 			self.collection.update({"_id":n["_id"]}, {"$set":{"status":"active"}}, upsert=False)
			# 		elif n['query'] is not None and n['filename'] is not None:
			# 			self.collection.update({"_id":n["_id"]}, {"$set":{"status":"active"}}, upsert=False)
			# 		elif sources.count() >= 0:
			# 			self.collection.update({"_id":n["_id"]}, {"$set":{"status":"active"}}, upsert=False)
			# 		else:
			# 			pass
			# 	except KeyError:
			# 		pass
			
		elif j.action == "archive":
			j.name = j.url
			_id = self.collection.find_one({"name":j.name, "action":j.action})
			
			if _id is None:
				self.collection.insert(j.__dict__)
				print "Job %s sucessfully scheduled on %s"%(j.action, j.name)
			else:
				print "Website %s has been already archived" %j.name
				self.show_by(j.__dict__, "name")
		elif j.action == "delete":
			if j.s is True:
				project_db = Database(j.name)
				sources = project_db.create_coll('sources')
				queue = project_db.create_coll('queue')
				if j.url is not None:
					if sources.find_one({"url":j.url}) is not None:
						sources.remove({"url": j.url})
						queue.remove({"url":j["url"]})
						print "deleting url %s from sources of the project %s" %(j.url, j.name)
					else:
						print "Url %s was not in sources" %j.url
				else:
					for n in sources.find():
						if sources.find_one({"url":j.url}) is not None:
							sources.remove({"url":n["url"]})
							queue.remove({"url":n["url"]})
					print "Cleaning up url sources for project %s" %(j.name)
			else:	
				self.delete(j.__dict__)
			return sys.exit()
		else:
			existing_crawl_job = self.collection.find_one({"name":j.name, "action":"crawl"})
			j.initial_action = j.action
			if existing_crawl_job is None:
				print "No existing crawl job has be previously scheduled: %s on %s will produce now results as long as you have no crawl project properly configured"%(j.action, j.name)
				j.action ="create"
				try:
					new_job = Job(j.__dict__)
					new_job = new_job.create_from_database()
					new_job.run()
				except KeyboardInterrupt:
					sys.exit()
									
			existing_job = self.collection.find_one({"name":j.name, "action":j.action})
			j.action = j.initial_action
			if existing_job is not None:
				#print existing_job
				print "Job %s already exists on %s"%(j.action, j.name)
				#self.collection.update({"id":existing_job["_id"]}, j.__dict__, False)
				#print "Updating %s job on %s"%(j.action, j.name)
				
			else:
				self.collection.insert(j.__dict__)
				print "Job %s sucessfully scheduled on %s"%(j.action, j.name)
		return sys.exit()	
					
					
	def delete(self, job):
		'''Delete existing project'''
		job_list = self.get_list({"name":job["name"]})
		if job_list is not False:
			for n in job_list:
				self.collection.remove(n)
				
				
			print "All the tasks of the project '%s' have been sucessfully deleted !"%job['name']
			return True
		else:
			print "No existing project '%s' with active tasks found" %job['name']
			return False
			
	def get_one(self, project_name):
		if project_name is None:
			return None
		elif type(project_name) == dict:
			return self.collection.find_one(project_name)
		elif type(project_name) == str:
			if validate_email(project_name) is True:
				return self.collection.find_one({"email":job_name})
			else:	
				return self.collection.find_one({"name":job_name})
		else:
			return None
	
	def get_list(self, project_name=None):
		'''get all the current job'''		
		
		if project_name is None:
			return [n for n in self.collection.find()]
		if type(project_name) == dict:
			project_list = [n for n in self.collection.find(project_name)]
			if len(project_list)> 0:
				#print "*** Project %s: %s ****" %(project_name.keys(), project_name.values())
				return project_list
			else:
				return  False
		else:
			return False
	
	def show_by(self, doc , by="name"):
		project_list = self.get_list({str(by): doc[str(by)]})
		if project_list is not False:
			print "******\tProject %s: %s    ******" %(str(by), str(doc[by]))
			for job in project_list:
				print job["action"]
				for k, v in job.items():
					if v is False or v is None:
						continue
					if k not in ['_id', by, '_key', "initial_action"]:
						print "*\t-", k,'\t', v
			print "*******************************************"
			return project_list
		else:
			return False

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
