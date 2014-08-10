#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from __future__ import print_function

import datetime
from os.path import exists
import sys
import requests
import json
import re
#from goose import Goose
from pymongo import errors as mongo_err
#from bs4 import BeautifulSoup as bs
#import beautifulsoup4 as bs
from urlparse import urlparse
from random import choice
from tld import get_tld
#~ from abpy import Filter
#~ 
#~ from article import Extractor
from scrapper import *
from utils.url import *


        
class Page(object):
	'''Page factory'''
	def __init__(self, url, query= "", output_format="defaut"):
		self.url = url
		self.query = query
		self.crawl_date = datetime.datetime.now()
		self.status = {"msg":None, "status": None, "code": None, "step": None, "url": self.url}
		#~ self.error_type = "Ok"
		#~ self.status = "Ok"
		#~ self.status_code = 0
		self.output_format = output_format
		
	def check(self):
		self.status["step"] = "check"
		self.status["status"], self.status["code"], self.status["msg"], self.status["url"] = check_url(self.url)
		self.url = self.status["url"]
		return self.status["status"]
		
	def request(self):
		'''Bool request a webpage: return boolean and update raw_html'''
		self.status["step"] = "request"
		try:
			requests.adapters.DEFAULT_RETRIES = 2
			user_agents = [u'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1', u'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2', u'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0', u'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00']
			headers = {'User-Agent': choice(user_agents),}
			proxies = {"https":"77.120.126.35:3128", "https":'88.165.134.24:3128', }
			try:
				self.req = requests.get((self.url), headers = headers,allow_redirects=True, proxies=None, timeout=5)
				
				try:
					self.raw_html = self.req.text
					self.status["status"] = True
					self.status["code"] = 200
					
				except Exception, e:
					self.status["msg"] = "Request answer was not understood %s" %e
					self.status["code"] = 400
					self.status["status"] = False
					
			except Exception, e:
				self.status["msg"] = "Request answer was not understood %s" %e
				self.status["code"] = 400
				self.status["status"] = False
				
		except requests.exceptions.MissingSchema:
			self.status["msg"] = "Incorrect url - Missing sheme for : %s" %self.url
			self.status["code"] = 406
			self.status["status"] = False
			
		except Exception as e:
			self.status["msg"] = "Another wired exception: %s %s" %(e, e.args)
			self.status["code"] = 204
			self.status["status"] = False
		return self.status["status"]
		
	def control(self):
		'''Bool control the result if text/html or if content available'''
		self.status["step"] = "control"
		#Content-type is not html 
		try:
			self.req.headers['content-type']
			if 'text/html' not in self.req.headers['content-type']:
				self.status["msg"]="Content type is not TEXT/HTML"
				self.status["code"] = 404
				self.status["status"] = False
				
			#Error on ressource or on server
			elif self.req.status_code in range(400,520):
				self.status["code"] = self.req.status_code
				self.status["msg"]="Request error on connexion no ressources or not able to reach server"
				self.status["status"] = False
				
			#Redirect
			#~ elif len(self.req.history) > 0 | self.req.status_code in range(300,320): 
				#~ self.error_type="Redirection"
				#~ self.bad_status()
				#~ return False
			else:
				self.status["status"] = True
		#Headers problems		
		except Exception:
			self.status["msg"]="Request headers were not found"
			self.status["code"] = 403
			self.status["status"] = False
		return self.status["status"]	
	
			
	def extract(self, type="article"):
		'''Dict extract content and info of webpage return boolean and self.info'''	
		self.status["step"] = "extract %s" %type
		try:
			self.content = Extractor.run(type, self.url, self.raw_html)
			self.status["status"] = True
		
		except Exception as e:
			self.status["msg"]="Extraction error %s" %e
			self.status["code"] = -2
			self.status["status"] = False
	
		return self.status["status"]	
	
	def filter(self, query= None, content= None):
		if query is None:
			query = self.query
		if content is None
			content = self.content
		chunks = StringSplitter(" |-|\.|OR|or")
		s_content = chunks.split(content.lower)
		
		
							
	def is_relevant(self):
		'''Bool Decide if page is relevant and match the correct query. Reformat the query properly: supports AND, OR and space'''
		if self.query is not None:
			self.query = re.sub('-', ' ', self.query) 
			if 'OR' in self.query:
				for each in self.query.split('OR'):
					query4re = each.lower().replace(' ', '.*')
					if re.search(query4re, self.article, re.IGNORECASE) or re.search(query4re, self.url, re.IGNORECASE):
						self.status = True
						self.error_code = 0
						self.error_type = None
						return True

			elif 'AND' in self.query:
				query4re = self.query.lower().replace(' AND ', '.*').replace(' ', '.*')
				return bool(re.search(query4re, self.article, re.IGNORECASE) or re.search(query4re, self.url, re.IGNORECASE))
			#here add NOT operator
			else:
				query4re = self.query.lower().replace(' ', '.*')
				return bool(re.search(query4re, self.article, re.IGNORECASE) or re.search(query4re, self.url, re.IGNORECASE))
	
	def filter(self):
		if self.is_relevant():
			self.status = True
		else:
			self.error_type = "Not relevant"
			self.status_code = -1
			self.status = False
		return self.status	
						 	
	def bad_status(self):
		'''create a msg_log {"url":self.url, "error_code": self.req.status_code, "error_type": self.error_type, "status": False,"date": self.crawl_date}'''			
		return {"url":self.url, "query": self.query, "error_code": self.status_code, "type": self.error_type, "status": False, "date":[self.crawl_date]}
		
	def clean_url(self, url):
		''' utility to normalize url and discard unwanted extension : return a url or None'''
		#ref tld: http://mxr.mozilla.org/mozilla-central/source/netwerk/dns/effective_tld_names.dat?raw=1
		#if url in ["#"]:
		#	print url
		if url == self.url:
			return None
		elif url not in [ "#","/", None, "\n", "",] or url not in 'javascript':
			self.netloc = urlparse(self.url).netloc
			uid = urlparse(url)
			#if next_url is relative take previous url netloc
			if uid.netloc == "":
				if len(uid.path) <=1:
					return None			
				elif (uid.path[0] != "/" and self.netloc[-1] != "/"):
					clean_url = "http://"+self.netloc+"/"+uid.path
				else:
					clean_url = "http://"+self.netloc+uid.path
			else:
				clean_url = url
			return clean_url
		else:
			return None
				
	def crawl(self):		
		if self.check():
			if self.request():
				if self.control():
					if self.extract():
						print self.__dict__
		else:
			print self.bad_status()
