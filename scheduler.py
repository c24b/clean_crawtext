#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from database import Database, TASK_MANAGER_NAME, TASK_COLL
import re
from datetime import datetime
from job import Job
#from page2 import Page
from validate_email import validate_email
from utils import yes_no


class Scheduler(object):
	''' main access to Job Database'''
	def __init__(self):
		'''init the project base with db and collections'''
		self.task_db = Database(TASK_MANAGER_NAME)
		self.collection =self.task_db.create_coll(TASK_COLL)			
			
	def schedule(self, user_input):
		'''Schedule a new job from user_input (crawtext.py)'''
		j = Job(user_input)
		if j.delete is True:
			self.delete(j.name)
			return
		elif j.name is not None:
			j.create_from_ui()	
			if j.update is False:
				# selecting user
				if j.user is not None and j.name is None:
					#find user
					#if user
					if self.get_one({"user":j["user"]}) is not None:
						#show every projects of the user
						print "Project owned by %s"%j["user"] 
						self.show_by(j,"user")
						return True
					#no user :error_msg
					else:
						print "User:%s is not already registered" %j["user"]
						print "To register you as user %s:\n1/Create a new project:\n\tpython crawtext.py yournewproject\n2/Set Ownership to the project:\n\tpython crawtext.py yournewproject -u %s" %(j["user"],j["user"])
						return False
				#selecting project
				elif j.name is not None:
					#verify
					if j.name in ["crawl", "delete", "archive", "report", "export"]:
						print "**Project Name** can't be 'crawl', 'archive', 'report', 'export' or 'delete'"
						print "\t*To generate a report:\n\t\tcrawtext report pesticides"
						print "\t*To create an export :\n\t\tcrawtext export pesticides"
						print "\t*To delete a projet :\n\t\tcrawtext delete pesticides"
						print "\t*To archive a website :\n\t\tcrawtext archive www.lemonde.fr"
						return False
					#create
					elif self.get_one({"name":j.name}) is None:							
						print "No existing project found!"
						return j.create()
					#show
					else:
						print "Jobs of the project %s"%j.name
						#self.show(j.name)
						self.show_by(j.__dict__, "name")
						return True
			#update
			elif j.udpate is True:
				#find existing project
				existing = self.get_one({"name":j.name, "action": crawl})
				print "Update existing project"
				#	j.update()
			#Job.create_from_database()
			#j2.run()
			#j['action'] is not None:
			#create job
		#delete
		else:
			return
				
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
			print "***\tProject %s: %s\t***" %(str(by), str(doc[by]))
			for job in project_list:
				for k, v in job.items():
					if v is False or v is None:
						continue
					if k not in ['_id', by, '_key']:
						print "\t-", k,'\t', v
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
		
