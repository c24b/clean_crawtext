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



class CrawlJob(object):
	def __init__(self, job): 
		self.option = None
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
			self.status = True
		except Exception as e:
			self.status_code = -2
			self.error_type = "Error fetching results from BING API.\nError is : \"%s\".\nCheck your API key then check your credentials: number of calls may not exceed 5000req/month" %e.args
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
			print "Automatically expanding sources from last results"
			self.expand()
		if self.file is not None:
			print "Getting seeds from file %s" %self.file
			self.get_local(self.file)
		else:
			print "Getting seeds from file is deactivated. No file with seeds url has been foud. Please set up a file with url if you want to add multiple urls."
			
		if self.query is not None:
			print "Getting seeds from Bing results on search %s" %self.query
			if self.key is not None:
				self.get_bing(self.key, self.query)
			else:
				print "Search seeds is deactivated. No credential for search in Bing have been foud. Please set up a api key if you want to activate search."
			return True
		else:
			return False	
			
		
	def send_seeds_to_queue(self):
		#here we could filter out problematic urls
		for url in self.db.sources.distinct("url"):
			self.db.queue.insert({"url":url})
		return True
		
			
	def run(self):
		if self.query is None:
			return "Unable to start crawl: no query has been set."
		seeds = self.collect_sources()
		if self.db.sources.count() == 0:
			return "Unable to start crawl: no seeds have been set."
		else:
			self.send_seeds_to_queue()
		
		print "running crawl on %i sources with query '%s'" %(len(self.db.sources.distinct("url")), self.query)
		start = datetime.now()
		while self.db.queue.count > 0:	
			for url in self.db.queue.distinct("url"):
				if url != "":
					page = Page(url, self.query)
					if page.check() and page.request() and page.control():
						content = page.extract("article")
						if content is not False:
							print content
						else:
							print False
						#~ outlinks, outlinks_err = page.get_outlinks()
						#~ if len(outlinks_err) > 0:
							#~ self.db.logs.insert(outlinks_err)
						#~ self.db.queue.insert(outlinks)
						#~ print self.db.queue.count()
							#~ for l in logs:
								#~ print l
						#~ for url in page.outlinks:
							#~ outlink = {"status": "", "status_code": "", "error_type": "", "url": ""}
							#~ url = from_rel_to_absolute_url(url,page.url)
							#~ outlink["status"], outlink["status_code"], outlink["error_type"], outlink["url"] = check_url(url)
							#~ outlink["url"]
					#~ 
				#~ 
				#~ if page.status is False:
					#~ self.db.logs.insert(page.bad_status())
				#~ else:
					#~ print page.__dict__
					#~ self.db.results.insert(page.info)
						#~ 
				self.db.queue.remove({"url": url})
				#~ if self.db.queue.count() == 0:
					#~ break
			#~ 
				if self.db.queue.count() == 0:		
					break
			if self.db.queue.count() == 0:		
					break
					
		return "Crawl done succesfully"
			#~ end = datetime.now()
			#~ elapsed = end - start
			#~ print "Crawl done sucessfully:\n-%i results\n-%i non pertinents urls \n-%i errors. \nElapsed time %s" %(len([n for n in self.db.results.find()]), len([n for n in self.db.logs.find()]), len([n for n in self.db.logs.find({"error_code":"-1"})]),elapsed)
			#~ print "To export results, logs, sources:\n python crawtext.py export %s" %self.name
			
			
	
	
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
		return "Successfully generated report for %s\nReport name is %s and stored in current directory" %(self.name, filename)
		
		
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
		print "Exporting data from", self.name
		
		for n in ['sources', 'results', 'logs']:
			c = "mongoexport -d %s -c %s --jsonArray -o Export_%s_%s.json"%(self.name,n, self.name, n)	
			print "- exporting %s" %(n)
			subprocess.call(c.split(" "), stdout=open(os.devnull, 'wb'))
		return "Sucessfully exported data project %s in json file" %self.name
		#subprocess.call(['zip', +zipf+".zip", s.local_filename])
		#print "Exporting %s" %self.name
		
		
		

