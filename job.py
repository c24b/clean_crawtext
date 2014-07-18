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
	def __init__(self, user_input):
		#normalizing between DB and docopt
		for k,v in user_input.items():
			k = re.sub("<|>|-|--", "", k)
			if k not in ["task_db", "coll", "job", "collection"]:
				setattr(self,k,v)
			
		#configuring job	
		if self.name is not None and self.user is None:
			if validate_email(self.name) is True:
				self.user = self.name
				self.name = None

	def create_from_ui(self):
		'''defaut values from user input'''
		self.update = None
		self.action = None
		for k, v in self.__dict__.items():
			if k in ["report", "extract", "export", "archive"]:
				self.action = k
				self.start_date = datetime.today()
				
			elif k == "u" and self.__dict__['user'] is not None:
				#option for the all bunch of project
				self.update = "all"
				
			elif k in ["q", "s", "k"] and v is True:
				#option for the defaut crawl project
				#print "adding parameter '%s' for crawl project '%s'"%(k, self.name)
				self.update = "crawl"
			elif k in ["monthly", "weekly", "daily"]:
				self.freq = k
				self.update = "all"
				
			else:			
				continue
		return self
		
		
			
		

	def create_from_database(self):
		'''doc.action = crawl ==> CrawlJob(doc)'''
		try:
			return globals()[(self.action).capitalize()+"Job"](self.__dict__) 
		except KeyError:
			print self.action, "has not been implemented Yet"			
			raise NotImplementedError

	def run(self):
		#self.action = "crawl"
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
			return False
	
	def expand(self):
		'''Expand sources url adding results urls collected from previous crawl'''
		for url in self.db.results.distinct("url"):
			if url not in self.db.sources.find({"url": url}):
				self.insert_url(url, origin="automatic")
		return True
				
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
			return False
		
	def send_seeds_to_queue(self):
		#here we could filter out problematic urls
		for url in self.db.sources.distinct("url"):
			self.db.queue.insert({"url":url})
		return self
		
	def activate(self):
		self.ex
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
		

