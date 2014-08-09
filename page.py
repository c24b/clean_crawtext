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
from bs4 import BeautifulSoup as bs
#import beautifulsoup4 as bs
from urlparse import urlparse
from random import choice
from tld import get_tld
from abpy import Filter

from extractors import Article
from utils.url import *


        
class Page(object):
	'''Page factory'''
	def __init__(self, url, query= ""):
		self.url = url
		self.query = query
		self.crawl_date = datetime.datetime.now()
		self.error_type = "Ok"
		self.status = "Ok"
		self.status_code = 0
		
	def check(self):
		self.status, self.status_code, self.error_type, self.final_url = check_url(self.url)
		return self.status
		'''Bool: check the format of the curr url'''
		'''
		if self.url is None or len(self.url) <= 1 or self.url == "\n":
			self.error_type = "Url is empty"
			self.status = False
			self.status_code = 406
			return self.status
		elif url_has_any_extension(self.url, IGNORED_EXTENSIONS) is True :
			self.error_type="Url has not a supported extension (PDF, ZIP, etc...)"
			self.status = False
			self.status_code = 406.1
			return self.status
		elif url_is_from_any_domain(self.url, IGNORED_DOMAINS) is True:
			self.error_type="Url refers to an advertissement listed in Adblock"
			self.status = False
			self.status_code = 406.2
			return self.status
		else:
			self.scheme = urlparse(self.url).scheme
			if self.scheme == "" or self.scheme is None:
				self.url = "http://"+self.url
				self.status = True
				self.status_code = 200
				return self.status
				
			elif self.scheme not in ACCEPTED_PROTOCOL:
				self.error_type="Protocol is not http or https"
				self.status = False
				self.status_code = 406.2
				return self.status
			
			else:
				self.status = True
				self.status_code = 200
				
				return self.status
		'''
	def request(self):
		'''Bool request a webpage: return boolean and update raw_html'''
		try:
			requests.adapters.DEFAULT_RETRIES = 2
			user_agents = [u'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1', u'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2', u'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0', u'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00']
			headers = {'User-Agent': choice(user_agents),}
			proxies = {"https":"77.120.126.35:3128", "https":'88.165.134.24:3128', }
			try:
				self.req = requests.get((self.url), headers = headers,allow_redirects=True, proxies=None, timeout=5)
				
				try:
					self.raw_html = self.req.text
					self.status = True
					self.status = 200
					
				except Exception, e:
					self.error_type = "Request answer was not understood %s" %e
					self.status_code = 400
					self.status = False
					
			except Exception, e:
				#print "Error requesting the url", e
				self.error_type = "Request answer was not understood %s" %e
				self.status_code = 400
				self.status = False
				
		except requests.exceptions.MissingSchema:
			self.error_type = "Incorrect url - Missing sheme for : %s" %self.url
			self.status_code = 406
			self.status = False
			
		except Exception as e:
			self.error_type = "Another wired exception: %s %s" %(e, e.args)
			self.status_code = 204
			self.status = False
		return self.status
		
	def control(self):
		'''Bool control the result if text/html or if content available'''
		#Content-type is not html 
		try:
			self.req.headers['content-type']
			if 'text/html' not in self.req.headers['content-type']:
				self.error_type="Content type is not TEXT/HTML"
				self.status_code = 404
				self.status = False
				
			#Error on ressource or on server
			elif self.req.status_code in range(400,520):
				self.status_code = self.req.status_code
				self.error_type="Request error on connexion no ressources or not able to reach server"
				self.status = False
				
			#Redirect
			#~ elif len(self.req.history) > 0 | self.req.status_code in range(300,320): 
				#~ self.error_type="Redirection"
				#~ self.bad_status()
				#~ return False
			else:
				self.status = True
		#Headers problems		
		except Exception:
			self.error_type="Request headers were not found"
			self.status_code = 403
			self.status = False
		return self.status	
	
			
	def extract(self, format="article"):
		'''Dict extract content and info of webpage return boolean and self.info'''	
		if format == "article":
			
			try:	
				#self.url = self.clean_url(self.url)
				#self.content = 
				
				#~ self.outlinks = self.article.outlinks
				#~ self.outlinks_err = self.article.outlinks_err
				self.status = True
				return Article(self.url, self.raw_html)
			except Exception, e:
				self.error_type = "Error in extracting article :"+str(e)
				self.status_code = -2
				self.status = False
				return self.status
	
	
		
						
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
