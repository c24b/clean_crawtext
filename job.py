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
		
class CrawlJob(object):
	def __init__(self, job): 
		for k,v in job.items():
			setattr(self, k, v)
			
		self.date = datetime.now()
		#required properties
		self.db = Database(self.name)
		#~ self.sources = self.db.create_coll('sources')
		#~ self.results = self.db.create_coll('results')
		#~ self.logs = self.db.create_coll('logs')
		#~ self.queue = self.db.create_coll('queue')
		self.db.create_colls(['sources', 'results', 'logs', 'queue'])	
		
	
	def get_bing(self, key="", query=""):
		''' Method to extract results from BING API (Limited to 5000 req/month) automatically sent to sources DB ''' 
		try:
			r = requests.get(
					'https://api.datamarket.azure.com/Bing/Search/v1/Web', 
					params={
						'$format' : 'json',
						'$top' : 100,
						'Query' : '\'%s\'' % query,
					},
					auth=(key, key)
					)
			for e in r.json()['d']['results']:
				self.insert_url(e["Url"],origin="bing")
			return True
		except Exception as e:
			self.status_code = -2
			self.error_type = "Error fetching results from BING API.\nError is : \"%s\".\nCheck your API key then check your credentials: number of calls may not exceed 5000req/month" %e.args
			self.db.logs.insert({"status_code":self.status_code,"error_type": self.error_type, "key":key, "query": query})
			return False

	def get_local(self, afile = ""):
		''' Method to extract url list from text file'''
		try:
			for url in open(afile).readlines():
				url = re.sub("\n", "", url)
				self.insert_url(url, origin=afile)
			return True
		except Exception:
			self.status_code = -2
			self.error_type = "Error fetching results from file: %s.\nFile doesn't not exists or has a wrong name.\nPlease set up a correct filename:\n\t crawtext.py %s -s append your_sources_file.txt" %(self.filename, self.name)
			self.db.logs.insert({"status_code":self.status_code,"error_type": self.error_type, "file": afile})
			return False
	
	def extend(self):
		'''Expand sources url adding results urls collected from previous crawl'''
		for url in self.db.results.distinct("url"):
			if url not in self.db.sources.find({"url": url}):
				self.insert_url(url, "automatic")
		return
				
	def insert_url(self, url, origin="default"):
		if url not in self.db.sources.find({"url": url}):
			return self.db.sources.insert({"url":url, "origin":origin,"date":[datetime.today()]})
		else:
			return self.db.sources.update({"url":url,"origin":origin, "$push": {"date":datetime.today()}})
		
	
	def delete_url(self, url):
		if self.db.sources.find_one({"url": url}) is not None:
			self.db.sources.remove({"url":url})
			return "'%s' has been deleted from seeds" %url
		else:
			return "url %s was not in sources. Check url format" %url
		
			
	def delete(self):
		self.db.sources.drop()
		return 'Every single seed has been deleted. No way back!'		
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
	
class ReportJob(object):
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
		
class ArchiveJob(object):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		pass
	def run(self):
		print "Archiving %s" %self.url
		
class ExportJob(object):
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
		

