#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os, sys
from validate_email import validate_email
from datetime import datetime
from utils import yes_no
from database import *
import requests
from page import Page
import sys
from multiprocessing import Pool
import subprocess
from utils.url import *

from query import Query
		
class Job(object):
	def __init__(self, doc):
		self.action = doc["action"]
		self.user = None
		self.name = doc["name"]
		self.start_date = datetime.now()
		self.repeat = "month"
		self.nb_run = 0
		self.last_run = None
		self.next_run = self.config_next_run(self.start_date, self.repeat)
		for k,v in doc.iteritems():
			setattr(self, k,v)
		#~ self.db = Database(doc["name"])
		#~ self.coll = self.db.create_colls("results", "log", "queue")
		
	def update(self, values):
		for k, v in values.iteritems():
			if k == "repeat":
				self.repeat = v
				self.next_run = self.config_next_run(self.start_date, self.repeat)
			set(self, k, v)
		return self
				
	def config_next_run(self, start_day, repeat):
		next_run = None
		start_job = start_day
		if repeat == "day":
			next_run = start_job.replace(day=start_job.day+1)
		elif repeat == "week":
			next_run = start_job.replace(day=start_job.day+7)
			
		elif repeat == "month":
			next_run = start_job.replace(month=start_job.month+1)
			
		elif repeat == "year":
			next_run = start_job.replace(year=start_job.month+1)
		else:
			pass
		return next_run
		
	@staticmethod
	def run(job):
		db = Database(TASK_MANAGER_NAME)
		collection = db.use_coll(TASK_COLL)
		if job["action"] == "archive":
			c = ArchiveJob(job)
			os.spawnl(os.P_NOWAIT, c.run())
			return "Archiving %s. An email will be sent when finished" %job["url"]
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
			has_job = collection.find_one({"name": job['name'], "action":"crawl"})
			if has_job is not None:
				c = CrawlJob(has_job)
				#return c.run()
				os.spawnl(os.P_NOWAIT, c.run())
				return "Crawling %s. An email will be sent when finished" %job["name"]
			else:
				return False
		elif job["action"] == "crawl":
			has_job = collection.find_one({"name": job['name'], "action":"crawl"})
			if has_job is not None:
				c = CrawlJob(has_job)
				#return c.run()
				os.spawnl(os.P_NOWAIT, c.run())
				return "Crawling %s. An email will be sent when finished" %job["name"]
			else:
				
				return False	
		elif job['action'] == "delete":
			c = DeleteJob(job)
			if c.run() is True:
				return "%s has been sucessfully unscheduled and deleted.\n Results and logs are saved in an archivesdatabase of the project.\nTo have direct acess to archived database, type:\n\t mongo %s\n\t>db.results.find()\n\t>db.logs.find()\n\t>db.sources.find()" %(job['name'], c.new_name)
			else:
				return "Error while deleting project"
		else:
			return "Job project not properly configured.\n Type python crawtext.py %s to see parameters" %job["name"]

class DeleteJob(object):
	def __init__(self, job): 
		self.name = job["name"]
		self.db_task = Database(TASK_MANAGER_NAME)
		self.t_collection = self.db_task.use_coll(TASK_COLL)
		self.job = job
		self.db_data = Database(job["name"])
		self.client = self.db_data.client
		
	def run(self):
		n = [n for n in self.t_collection.find({"name": self.job['name']})]
		if len(n) == 0:
			print "No project %s has been found. Check the name of your project" %(self.job['name'])
			return False
		else:
			self.t_collection.remove({"name": self.job['name']})
			print "Unscheduling task"
			old_name = str(self.job["name"])
			date = datetime.today()
			self.new_name = "__%s_ARCHIVES__%s-%s-%s"%(old_name, date.year, date.month, date.day)
			try:
				print self.client.copy_database(old_name,self.new_name, 'localhost')
				print "Renaming projects database %s into %s" %(old_name, self.new_name)
			except Exception as e:
				print "e"
			print self.client.drop_database(old_name)
			print "Deleting projects database %s ." %old_name
		return True

			 
class CrawlJob(object):
	def __init__(self, job): 
		self.option = None
		self.file  = None
		self.key = None
		self.query = None
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
		
	def update_seeds(self, data):
		pass
		
	def get_bing(self, key=None, query=None):
		''' Method to extract results from BING API (Limited to 5000 req/month) automatically sent to sources DB ''' 
		if query is None:
			query = self.query
		if key is None:
			key = self.key
					
		try:
			#https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%27web%2Bnews%27&Query=%27ebola%27
			r = requests.get(
					'https://api.datamarket.azure.com/Bing/Search/v1/Web', 
					params={
						'$format' : 'json',
						'$top' : 100,
						'Query' : '\'%s\'' %query,
					},
					auth=(key, key)
					)
			r.raise_for_status()
			i = 0
			for e in r.json()['d']['results']:
				i = i+1
				self.insert_url(e["Url"],origin="bing")
			self.seeds_nb = i
			self.status = True
			
		except Exception as e:
			self.status_code = r.status_code
			self.error_type = "Error fetching results from BING API. %s" %e.args
			self.db.logs.insert({"status_code":self.status_code,"error_type": self.error_type, "key":key, "query": query})
			self.status = False
		return self.status
		
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
		return 'Every single seed has been deleted. No way back!...Unless you configure seeds again.\nType python crawtext.py --h for options'		
		
	def collect_sources(self):
		''' Method to add new seed to sources and send them to queue if sourcing is deactivate'''
		
		if self.option == "expand":
			#print "Automatically expanding sources from last results"
			self.extend()
		if self.file is not None:
			print "Getting seeds from file %s" %self.file
			self.get_local(self.file)
		else:
			#print "Getting seeds from file is deactivated. No file with seeds url has been foud. Please set up a file with url if you want to add multiple urls."			
			if self.query is not None:
				#print "Getting seeds from Bing results on search %s" %self.query
				if self.key is not None:
					self.get_bing(self.key, self.query)
				else:
					print "Search seeds is deactivated. No credential for search in Bing have been foud. Please set up a api key if you want to activate search."
				return True
			else:
				return False	
			
	def send_seeds_to_queue(self):
		for url in self.db.sources.distinct("url"):
			if url not in self.db.logs.find({"url": url}):
				self.db.queue.insert({"url":url})
		return True
				
	def run(self):
		if self.query is None:
			print "Unable to start crawl: no query has been set."
			return False 
		else:
			query = Query(self.query)
			
		seeds = self.collect_sources()
		if self.db.sources.count() == 0:
			print "Unable to start crawl: no seeds have been set."
			return False
		else:
			self.send_seeds_to_queue()
		
		start = datetime.now()
		if self.db.queue.count == 0:
			print "Error while sending urls into queue: queue is empty"
			return False
			
		else:
			print "running crawl on %i sources with query '%s'" %(len(self.db.sources.distinct("url")), self.query)
				
			while self.db.queue.count > 0:	
				for url in self.db.queue.distinct("url"):
					if url != "":
						page = Page(url)
						if page.check() and page.request() and page.control():
							article = page.extract("article")
							if article.status is True:
								if article.is_relevant(query):
									
									self.db.results.insert(article.repr())
									if article.outlinks is not None and len(article.outlinks) > 0:
										self.db.queue.insert(article.outlinks)
							else:
								self.db.logs.insert(article.logs)
						else:
							self.db.logs.insert(page.status)	
					self.db.queue.remove({"url": url})
					
					if self.db.queue.count() == 0:		
						break
				if self.db.queue.count() == 0:		
						break
			end = datetime.now()
			elapsed = end - start
			print "Crawl done sucessfully in %s s" %str(datetime.timedelta(seconds=elapsed))
			print "To export results, logs, sources:\n python crawtext.py export %s" %self.name 
			return True
			
			
			
	
	
class ReportJob(object):
	def __init__(self, doc):
		
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		self.db = Database(self.name)
		
	def run(self):
		print "Report for crawl results of %s" %self.name
		filename = "Report_%s_%d-%d-%d-%d:%d.txt" %(self.name, self.date.year, self.date.month, self.date.day,self.date.hour, self.date.minute)
		with open(filename, 'a') as f:
			f.write((self.db.stats()).encode('utf-8'))
		print "Successfully generated report for %s\nReport name is %s and stored in current directory" %(self.name, filename)
		return True
		
		
class ArchiveJob(object):
	def run(self):
		print "Archiving %s" %self.url
		return True

class ExportJob(object):
	#~ def __init__(self, doc):
		#~ self.date = datetime.now()
		#~ for k, v in doc.items():
			#~ setattr(self,k,v) 	
	def run(self):
		print "Exporting data from", self.name
		
		for n in ['sources', 'results', 'logs']:
			c = "mongoexport -d %s -c %s --jsonArray -o Export_%s_%s.json"%(self.name,n, self.name, n)	
			print "- exporting %s" %(n)
			subprocess.call(c.split(" "), stdout=open(os.devnull, 'wb'))
			print "Sucessfully exported data project %s in json file" %self.name
		#subprocess.call(['zip', +zipf+".zip", s.local_filename])
		#print "Exporting %s" %self.name
		return True
		
		
		
		

