#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from validate_email import validate_email
from datetime import datetime
from utils import yes_no
from database import *
import requests
from page import Page
import sys

class Job(object):
	#__metaclass__ = ABCMeta
	def __init__(self):
		pass
	
	def create_from_ui(self, user_input):
		'''user_input info to job properties'''
		self.name = user_input['<name>']	
		self.user = None
		if validate_email(self.name) is True:
			self.user = self.name
		
		action_list = ["report", "extract", "export", "archive", "start", "delete"]
		self.action = [k for k,v in user_input.items() if v is True and k in action_list]
		
		scope_list = ["-u", "-r", "-q", "-k", "-s"]
		self.scope = [re.sub("-", "",k) for k,v in user_input.items() if v is True and k in scope_list]
		
		option_list = ['add', 'set', 'append', 'delete', 'expand']
		self.option = [k for k,v in user_input.items() if v is True and k in option_list]
		
		freq_list = ['<monthly>', '<weekly>', '<daily>']
		self.freq = [re.sub("<|>", "",k) for k,v in user_input.items() if v is True and k in freq_list]
		
		data_list = ['<url>', '<file>', '<query>', '<key>','<email>']
		for k,v in user_input.items():
			if v is not None and k in data_list:
				setattr(self, k,v)
		self.data = [[re.sub("<|>", "",k),v] for k,v in user_input.items() if v is not None and k in data_list]
		#self.data_v = [v for k,v in user_input.items() if v is True and k in option_list]
		return self
	
	def dispatch(self):
		#schedule
		if len(self.action) == 1:
			self.action, = self.action
		#udpate
		elif len(self.scope) == 1:
			self.scope, = self.scope
		#create or show
		else:
			self.create_or_show()		
	'''
	def create_from_ui(self):
	'''	
		#'''defaut values from user input'''
	
		#main action
		
		
		#update all
		
		
		#update crawl
	'''
		scope_crawl = ["q", "s", "k"]
		crawl_scope = [k for k in self.__dict__.keys() if k in scope_crawl]
		c_option = ['add', 'set', 'append', 'delete', 'expand']
		option = [k for k in self.__dict__.keys() if k in c_option]
		
		
		#values to insert from user_input
		data = ['name', 'url', 'file', 'query', 'key','email', 'user']
		#user_input_values = action_list+scope_all+scope_crawl+data
		#~ for k,v in self.__dict__.items():
			#~ if k not in data:
				#~ del self.__dict__[k]
			
			
					
		if len(job_action) != 0:
			
			self.start_date = datetime.today()
			return self
		
		elif len(scope_all) != 0:
			self.update = 'all'
			self.action = None
			self.scope = scope_all[0]
			self.value = value_all[0]
			self.date = datetime.now()
			return self
			
		elif len(scope_crawl) != 0:
			self.update = 'crawl'
			self.action = None
			self.scope = scope_crawl[0]
			self.option = option_crawl[0]
			self.date = datetime.now()
			
			 
		else:
			self.action = None
			self.update = None
			return self
	'''	
		

	def create_from_database(self):
		'''doc.action = crawl ==> CrawlJob(doc)'''
		try:
			return globals()[(self.action).capitalize()+"Job"](self.__dict__) 
		except KeyError:
			print self.action, "has not been implemented Yet"			
			#raise NotImplementedError
			return NotImplementedError
					
class CreateJob(Job):
	def __init__(self, doc): 
		self.start_date = datetime.now()
		
		for k, v in doc.items():
			if v is not None or False:
				setattr(self,k,v)
		self.action = "crawl"
		self.status = "inactive"
		self.active = False
		
	def run(self):
		new = yes_no("Do you want to create a new CRAWL project?")
		if new == 1:		
			task_db = Database(TASK_MANAGER_NAME)
			coll = task_db.create_coll(TASK_COLL)
			coll.insert(self.__dict__)
			print "Project %s has been successfully created and scheduled!\n\t1/To see default parameters of the project:\n\tpython crawtext.py %s\n\t2/To add more parameters see help and options \n\tpython crawtext.py --help" %(self.name,self.name)
			return True
			
class UpdateJob(Job):
	def __init__(self, doc): 
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
	
	def run(self):
		print self.scope
		pass	
		
class CrawlJob(Job):
	def __init__(self, doc): 
		self.date = datetime.now()
		#required properties
		self.query = None
		self.key = None
		self.file = None
		self.expand = None
		for k, v in doc.items():
			setattr(self,k,v) 	
		self.db = Database(self.name)
		self.sources = self.db.create_coll('sources')
		self.results = self.db.create_coll('results')
		self.logs = self.db.create_coll('logs')
		self.queue = self.db.create_coll('queue')
		self.filename = None
		for k, v in doc.items():
			setattr(self,k,v) 	
		self.db = Database(self.name)
		self.db.create_colls()	
		
		#properties
		#pour définir les sources d'après un fichier :	crawtext pesticides -s set sources.txt	
	# pour ajouter des sources d'après un fichier :	crawtext pesticides -s append sources.txt
	# pour définir les sources d'après Bing :		crawtext pesticides -k set 12237675647
	# pour ajouter des sources d'après Bing :		crawtext pesticides -k append 12237675647
	# pour ajouter des sources automatiquement :	crawtext pesticides -s expand
	# pour supprimer une source :					crawtext pesticides -s delete www.latribune.fr
	#pour ajouter une nouvelle sources				crawtext pesticides -s add www.latribune.fr
	# pour supprimer toutes les sources :			crawtext pesticides -s delete
	#Récurrence
	# pour définir la récurrence :                	crawtext pesticides -r monthly|weekly|daily

	def get_bing(self):
		''' Method to extract results from BING API (Limited to 5000 req/month). ''' 
		try:
			r = requests.get(
					'https://api.datamarket.azure.com/Bing/Search/v1/Web', 
					params={
						'$format' : 'json',
						'$top' : 100,
						'Query' : '\'%s\'' % self.query,
					},
					auth=(self.key, self.key)
					)
			for e in r.json()['d']['results']:
				self.insert_url(e["Url"],origin="bing")
			return True
		except Exception as e:
			print "Bing exception", e
			self.status_code = -2
			self.error_type = "Error fetching results from BING API.\nError is : (%s).\n>>>>Check your credentials: number of calls may not exceed 5000req/month" %e.args
			return False

	def get_local(self):
		''' Method to extract url list from text file'''
		try:
			for url in open(self.file).readlines():
				url = re.sub("\n", "", url)
				self.insert_url(url, origin=self.file)
			return True
		except Exception:


			self.status_code = -2
			self.error_type = "Error fetching results from file: %s.\nFile doesn't not exists or has a wrong name.\nPlease set up a correct filename:\n\t crawtext.py %s -s append your_sources_file.txt" %(self.filename, self.name)
			self.status = False



			self.status_code = -1
			self.error_type = "Error fetching results from file: %s.\n>>> Check if file exists" %self.file
			print self.error_type

			return False
	
	def expand(self):
		'''Expand sources url adding results urls collected from previous crawl'''
		for url in self.db.results.distinct("url"):
			if url not in self.db.sources.find({"url": url}):
				self.insert_url(url, origin="expand")
		return
				
	def insert_url(self, url, origin="default"):
		if url not in self.db.sources.find({"url": url}):
			self.db.sources.insert({"url":url, "origin":"bing","date":[datetime.today()]}, upsert=True)
		else:
			self.db.sources.update({"url":url,"origin":origin, "$push": {"date":datetime.today()}}, upsert=False)
		return self.db.sources.find_one({"url": url})
	
	def delete_url(self, url, origin="default"):
		if url not in self.db.sources.find({"url": url}):
				print "url %s was not in sources. Check url format" %url
		else:
			self.db.sources.remove({"url":url})
		return
			
	def collect_sources(self):
		''' Method to add new seed to sources and send them to queue if sourcing is deactivate'''


		try:
			if self.file is not None:
				print "Getting local urls"
				self.get_local()
			if self.key is not None:
				print "Searching on Bing"
				self.get_bing()
			return self
			
		except Exception as e:
			print ">>>> collecting source error:", e



		if self.query is not None:
			if self.filename is not None:
				print self.filename
				self.get_local()
			if self.key is not None:
				print self.key
				self.get_bing()
			#~ if self.expand is True:
				#~ self.expand()
		else:




			return False
		
	def send_seeds_to_queue(self):
		#here we could filter out problematic urls
		for url in self.db.sources.distinct("url"):
			self.db.queue.insert({"url":url})
		return self
		
	def activate(self):
		if self.query is None:
			print "No query search has been configured for crawl project\nPlease provide a query expression:\tcrawtext.py %s -q \"your_query_expression\""	
			return False
		else:
			if len(self.db.sources.distinct("url")) <= 0:
				if self.file is None and self.key is None:
					print "No sources have been configured for crawl project\n Please provide or a list of url using a file\nA\)To define sources to crawl using a file:\tcrawtext.py %s -s set your_sources_file.txt\nB\)To define sources to crawl using search option adding a Bing API key crawtext %s -k set your_api_key" %(self.name, self.name)
					return False	
				else:
					self.collect_sources()
			self.send_seeds_to_queue()
			return True
	
			
	def run(self):
		print "running crawl on %i sources with query '%s'" %(self.db.sources.count(), self.query)
		if self.activate():
			start = datetime.now()
			while self.db.queue.count > 0:
				for url in self.db.queue.distinct("url"):
					page = Page(url, self.query)
					if page.status is False:
						self.db.logs.insert(page.bad_status())
					else:
						print page.__dict__
						self.db.results.insert(page.info)
						
					self.db.queue.remove({"url": url})
					if self.db.queue.count() == 0:
						break
			
				if self.db.queue.count() == 0:		
					break
			print "Crawl done succesfully"
			end = datetime.now()
			elapsed = end - start
			print "Crawl done sucessfully:\n-%i results\n-%i non pertinents urls \n-%i errors. \nElapsed time %s" %(len([n for n in self.db.results.find()]), len([n for n in self.db.logs.find()]), len([n for n in self.db.logs.find({"error_code":"-1"})]),elapsed)
			print "To export results, logs, sources:\n python crawtext.py export %s" %self.name
		else:
			pass
			
		

		if self.query is not None:
			if self.filename is not None or self.key is not None:
				self.collect_sources()
				return self.send_seeds_to_queue()
			else:
				print "No sources have been configured for crawl project\n Please provide or a list of url using a file\nA\)To define sources to crawl using a file:\tcrawtext.py %s -s set your_sources_file.txt\nB\)To define sources to crawl using search option adding a Bing API key crawtext %s -k set your_api_key" %(self.name, self.name)
		else:
			print "No query search has been configured for crawl project\nPlease provide a query expression:\tcrawtext.py %s -q \"your_query_expression\""
			
	def run(self):
		if self.f is True or self.q is True:
			self.activate()
		else:
			if self.query is not None:
				if self.filename is not None or self.key is not None:
					self.collect_sources()
					return self.send_seeds_to_queue()
				else:
					print "No sources have been configured for crawl project\n Please provide or a list of url using a file\nA\)To define sources to crawl using a file:\tcrawtext.py %s -s set your_sources_file.txt\nB\)To define sources to crawl using search option adding a Bing API key crawtext %s -k set your_api_key" %(self.name, self.name)
			else:
				print "No query search has been configured for crawl project\nPlease provide a query expression:\tcrawtext.py %s -q \"your_query_expression\""
			
	def run(self):
		if self.f is True or self.q is True:
			self.activate()
		else:

			print "Crawler has 2 required values: a Query and a sources collection (created by giving urls, or search API key"
		#~ self.activate()

		#~ start = datetime.now()
		#~ while self.db.queue.count > 0:
			#~ for url in self.db.queue.distinct("url"):
				#~ page = Page(url)
				#~ if page.logs["status"] is False:
					#~ self.db.logs.insert(page.logs)
				#~ else:
					#~ page.extract("article")
					#~ print page.title 
					#~ 
				#print page.status
					#~ #print page.canonical_link
				#~ # else:
				#~ # 	self.db.logs.insert(article.bad_status())
				#~ self.db.queue.remove({"url": url})
				#~ if self.db.queue.count() == 0:
					#~ break
			#~ 
			#~ if self.db.queue.count() == 0:		
				#~ break
		#~ 
		
		return self
	
class ReportJob(Job):
	def __init__(self, doc):
		print "Report Job"
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		self.db = Database(self.name)
		
	def run(self):
		print "Report for %s" %self.name
		filename = "Report_%s_%d-%d-%d-%d:%d.txt" %(self.name, self.date.year, self.date.month, self.date.day,self.date.hour, self.date.minute)
		with open(filename, 'a') as f:
			f.write((self.db.stats()).encode('utf-8'))
		print "Successfully generated report for %s" %self.name 	
		return self	
		
class ArchiveJob(Job):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		pass
	def run(self):
		print "Archiving %s" %self.url
		
class ExportJob(Job):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
	def run(self):
		print "Exporting %s" %self.name
		
		
#~ class RunJob(Job):
	#~ def __init__(self, doc):
		#~ self.date = datetime.now()
		#~ for k, v in doc.items():
			#~ setattr(self,k,v) 	
		

