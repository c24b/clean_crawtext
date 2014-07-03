#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from database import Database, TASK_MANAGER_NAME, TASK_COLL
import re
from datetime import datetime
from abc import ABCMeta, abstractmethod
#from page2 import Page
from validate_email import validate_email
import docopt
from utils import yes_no
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
		
		if j.action == "show":
			if j.user is not None:
				if self.get_one({"user":j.user}) is not None:
					print "Project owned by %s"%j.user
					self.show_by(j,"user")
					return True
				else:
					#error_msg
					print "User:%s is not already registered" %j.user
					print "To register you as user %s:\n1/Create a new project:\n\tpython crawtext.py yournewproject\n2/Set Ownership to the project:\n\tpython crawtext.py yournewproject -u %s" %(j.user,j.user)
					return False
			elif j.name is not None:
				if j.name in ["crawl", "delete", "archive", "report", "export"]:
					print "**Project Name** can't be 'crawl', 'archive', 'report', 'export' or 'delete'"
					print "\t*To generate a report:\n\t\tcrawtext.py report pesticides"
					print "\t*To create an export :\n\t\tcrawtext.py export pesticides"
					print "\t*To delete a projet :\n\t\tcrawtext.py delete pesticides"
					print "\t*To archive a website :\n\t\tcrawtext.py archive www.lemonde.fr"
					return False
				elif self.get_one({"name":j.name}) is None:
					print "No existing project found!"
					
					j.action ="create"
					new_job = j.__dict__
					new_job = Job(new_job)
					new_job = new_job.create_from_database()
					new_job.run()
					return True
				else:
					print "Jobs of the project %s"%j.name
					self.show_by(j.__dict__, "name")
					print "To activate crawl, you need to configure the 2 required options:\n\t- A query\n\t- A list of url to crawl OR a search API Key\n To see how to add parameters to the current job: crawtext.py --help" 
					return True	
					
		if j.action == "update":
			if j.scope == "u":
				for n in self.collection.find({"name":j.name}):
					print n["_id"]
					self.collection.update({"_id":n["_id"]}, {"$set":{"user":j.user}}, upsert=False)
				print "User %s will be the owner of the project %s" %(j.user, j.name)
			elif j.scope == "q":
				print "Setting up query %s for the crawl project %s" %(j.query, j.name)
				j._id = self.collection.find({"name":j.name, "action":"crawl"})[0]['_id']
				self.collection.update({"_id":j._id}, {"$set":{"user":j.user}}, upsert=False)
				
			elif j.scope == "s":
				print "Configuring sources"
				pass
				#~ j._id = self.collection.find({"name":j.name, "action":"crawl"})[0]['_id']
				#~ self.collection.update({"_id":j._id}, {"$set":{"sources":j.user}}, upsert=False)
				
			elif j.scope == "k":
				print "Configuring search API"
				j._id = self.collection.find({"name":j.name, "action":"crawl"})[0]['_id']
				self.collection.update({"_id":j._id}, {"$set":{"key":j.key}}, upsert=False)
				
			elif j.scope == "r":
				print "Configuring frequency of call for every projects"
				for n in self.collection.find({"name":j.name}):
					self.collection.update({"_id":n["_id"]}, {"$set":{"frequency":j.frequency}}, upsert=False)
			else:
				pass
		# selecting user
		'''
		if j['user'] is not None and j['name'] is None:
			#find user
			#if user
			if self.get_one({"user":j["user"]}) is not None:
				#show every projects of the user
				print "Project owned by %s"%j["user"] 
				self.show_by(j,"user")
				return True
			
		#selecting project
		elif j["name"] is not None and j['update'] is False:
				#verifying that name is correct
				if j['name'] in ["crawl", "delete", "archive", "report", "export"]:
					print "**Project Name** can't be 'crawl', 'archive', 'report', 'export' or 'delete'"
					print "\t*To generate a report:\n\t\tcrawtext report pesticides"
					print "\t*To create an export :\n\t\tcrawtext export pesticides"
					print "\t*To delete a projet :\n\t\tcrawtext delete pesticides"
					print "\t*To archive a website :\n\t\tcrawtext archive www.lemonde.fr"
					return False
				#project doesn't exist: create new one
				elif self.get_one({"name":j['name']}) is None:							
					print "No existing project found!"
					j['action'] = "create"
					j2 = Job.create_from_database(j)
					j2.run()
					return True
				#project exist: show
				else:
					print "Jobs of the project %s"%j["name"] 
					self.show_by(j, "name")
					return True
		
		else:
			if j["update"] is True:
				print "Update existing project"
				j2 = Job.create_from_database(j)
				j2.run()
			#j['action'] is not None:
			#create job
		'''	
		
	def delete(self, job_name):
		'''Delete existing project'''
		job_list = self.get_list(job_name)
		if job_list is not False:
			for n in job_list:
				self.collection.remove(n)
				print "Sucessfully deleted task:", n['name']
				
			print "All the tasks of the project %s have been sucessfully deleted !"%job_name['name']
			return True
		else:
			print "No existing project %s with active tasks found" %job_name['name']
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
			return False
			#return [n["project"] for n in self.collection.distinct("name")]
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
				for k, v in job.items():
					if v is False or v is None:
						continue
					if k not in ['_id', by, '_key']:
						print "*\t-", k,'\t', v
			print "*******************************************"
			return project_list
		else:
			return False
		
	def run_job(self, job_name=None):
		'''Execute tasks from Job Database'''
		if job_name is not None:
			doc = self.get_one(job_name)		
			j = Job.create_from_database(doc)
			print "Running %s on %s" %(j.name, j.action)
			return j.run()
		else:
			docs = self.get_list()
			for doc in docs:
				j = Job.create_from_database(doc)
				print "Running %s on %s" %(j.name, j.action)
				j.run()
			return "All jobs done !"
		
