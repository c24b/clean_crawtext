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

from copy import deepcopy
from parsers import Parser
from cleaners import StandardDocumentCleaner
from extractors import StandardContentExtractor
from formatters import StandardOutputFormatter

unwanted_extensions = ['css','js','gif','asp', 'GIF','jpeg','JPEG','jpg','JPG','pdf','PDF','ico','ICO','png','PNG','dtd','DTD', 'mp4', 'mp3', 'mov', 'zip','bz2', 'gz', ]	
adblock = Filter(file('./ressources/easylist.txt'))
class Article(object):
	'''Article'''
	def __init__(self):
		# title of the article
		self.title = None

		# stores the lovely, pure text from the article,
		# stripped of html, formatting, etc...
		# just raw text with paragraphs separated by newlines.
		# This is probably what you want to use.
		self.cleaned_text = u""

		# meta description field in HTML source
		self.meta_description = u""

		# meta lang field in HTML source
		self.meta_lang = u""

		# meta favicon field in HTML source
		self.meta_favicon = u""

		# meta keywords field in the HTML source
		self.meta_keywords = u""

		# The canonical link of this article if found in the meta data
		self.canonical_link = u""

		# holds the domain of this article we're parsing
		self.domain = u""

		# holds the top Element we think
		# is a candidate for the main body of the article
		self.top_node = None

		# holds a set of tags that may have
		# been in the artcle, these are not meta keywords
		self.tags = set()

		# stores the final URL that we're going to try
		# and fetch content against, this would be expanded if any
		self.final_url = u""

		# stores the MD5 hash of the url
		# to use for various identification tasks
		self.link_hash = ""

		# stores the RAW HTML
		# straight from the network connection
		self.raw_html = u""

		# the lxml Document object
		self.doc = None

		# this is the original JSoup document that contains
		# a pure object from the original HTML without any cleaning
		# options done on it
		self.raw_doc = None

		# Sometimes useful to try and know when
		# the publish date of an article was
		self.publish_date = None

		# A property bucket for consumers of goose to store custom data extractions.
		self.additional_data = {}
		self.links = None
		self.outlinks = None
		self.backlinks = None
		self.start_date = datetime.datetime.today()
        
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
		'''Bool: check the format of the next url compared to curr url'''
		if self.url is None or len(self.url) <= 1 or self.url == "\n":
			self.error_type = "Url is empty"
			self.status = False
			self.status_code = 406
		elif (( self.url.split('.')[-1] in unwanted_extensions ) and ( len( adblock.match(self.url) ) > 0 ) ):
			self.error_type="Url has not a proprer extension or page is an advertissement"
			self.status = False
			self.status_code = 406
		else:
			self.scheme = urlparse(self.url).scheme
			if self.scheme == "":
				self.url = "http://"+self.url
			self.status = True
			self.status_code = 200
		return self.status
		
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
	
	def get_article(self):		
		#init parser here defaut parser
		self.parser = Parser()
		self.extractor = StandardContentExtractor(self.article,self.parser, target_language="en", stopwords_class="en")			
		# init the document cleaner
		self.cleaner = StandardDocumentCleaner(self.article, self.parser)
		# init the output formatter
		self.formatter = StandardOutputFormatter(self.article,self.parser, stopwords_class="en")

		#then
		doc = self.parser.fromstring(self.raw_html)
		self.article.final_url = self.url
		self.article.raw_html = self.raw_html
		self.article.doc = doc
		self.article.raw_doc = deepcopy(doc)
		# TODO
		# self.article.publish_date = config.publishDateExtractor.extract(doc)
		# self.article.additional_data = config.get_additionaldata_extractor.extract(doc)
		self.article.title = self.extractor.get_title()
		self.article.meta_lang = self.extractor.get_meta_lang()
		self.article.meta_favicon = self.extractor.get_favicon()
		self.article.meta_description = self.extractor.get_meta_description()
		self.article.meta_keywords = self.extractor.get_meta_keywords()
		self.article.canonical_link = self.extractor.get_canonical_link()
		self.article.domain = self.extractor.get_domain()
		self.article.tags = self.extractor.extract_tags()

		# before we do any calcs on the body itself let's clean up the document
		self.article.doc = self.cleaner.clean()

		# big stuff
		self.article.top_node = self.extractor.calculate_best_node()

		# if we have a top node
		# let's process it
		if self.article.top_node is not None:
            # post cleanup
			self.article.top_node = self.extractor.post_cleanup()

			# clean_text
			self.article.cleaned_text = self.formatter.get_formatted_text()
        # return the article
		return self.article
			
	def extract(self):
		'''Dict extract content and info of webpage return boolean and self.info'''	
		#try:
		
		self.url = self.clean_url(self.url)
		self.article = Article()
		self.get_article()
		print ">>>", self.article.cleaned_text
		#~ self.article = bs(self.src).text
		#~ self.title = bs(self.src).title.text
		#~ 
		#~ self.target_urls = set()
		#~ #if self.filter() is True:
		#~ for e in bs(self.raw_html).find_all('a', {'href': True}):
			#~ #print e.attrs['href']
			#~ print e.attrs['href']
			#~ if e.attrs['href'] is not None or e.attrs['href'] != "":
				#~ target_url = self.clean_url(url=e.attrs['href'])
				#~ if target_url is not None:
					#~ self.target_urls.append(target_url)
			#~ 
		#~ self.info = {	
					#~ "source_url":self.url,
					#~ "query": self.query,
					#~ "source_domain": get_tld(self.url),
					#~ "target_urls": list(self.target_urls),
					#~ "target_domains": [get_tld(n) for n in self.outlinks],
					#~ "texte": self.article,
					#~ "title": self.title,
					#~ "html": self.raw_html,
					#~ #"meta_description":bs(self.article.meta_description).text,
					#~ "date": [self.crawl_date]
					#~ }
		self.status = True		
		'''		
		except Exception, e:
			print e
			self.error_type = str(e)
			self.status_code = -2
			self.status = False
		'''
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
