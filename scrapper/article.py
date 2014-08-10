# -*- coding: utf-8 -*-
from copy import deepcopy
from parsers import Parser
from cleaners import StandardDocumentCleaner
from formatters import StandardOutputFormatter
from extractors import StandardContentExtractor
import datetime
class Extractor(object):
	'''Generic Extractor'''	
	def __init__(self):
		self.url = url
		self.lang = lang
		# title of the article
		self.title = None
		#text
		self.cleaned_text = u""
		# meta
		self.meta_description = u""
		self.meta_lang = u""
		self.meta_favicon = u""
		self.meta_keywords = u""
		#link and domain
		self.canonical_link = u""
		self.domain = u""
		# cleaned text
		self.top_node = None
		self.tags = set()
		self.final_url = url
		self.raw_html = raw_html
		# the lxml Document object
		self.parser = Parser()
		self.raw_doc = None
		self.publish_date = None
		self.additional_data = {}
		self.links = None
		self.outlinks = None
		self.backlinks = None
		self.inlinks = None
		self.start_date = datetime.datetime.today()
	@staticmethod
	def run(type, url, raw_html):
		if type == "article":
			content = Article(url, raw_html)
		elif type == "defaut":
			content = WebPage()
		else:
			raise NotImplementedError	
		#init parser here defaut parser
		
		return content.get()
		


class Article(Extractor):
	'''Article'''
	def __init__(self, url, raw_html, lang = "en"):
		self.url = url
		self.lang = lang
		# title of the article
		self.title = None
		#text
		self.cleaned_text = u""
		# meta
		self.meta_description = u""
		self.meta_lang = u""
		self.meta_favicon = u""
		self.meta_keywords = u""
		#link and domain
		self.canonical_link = u""
		self.domain = u""
		# cleaned text
		self.top_node = None
		self.tags = set()
		self.final_url = url
		self.raw_html = raw_html
		# the lxml Document object
		self.parser = Parser()
		self.raw_doc = None
		self.publish_date = None
		self.additional_data = {}
		self.links = None
		self.outlinks = None
		self.backlinks = None
		self.inlinks = None
		self.start_date = datetime.datetime.today()
	
	def get(self):
		
		self.doc = self.parser.fromstring(self.raw_html)
		#init extractor method
		extractor = StandardContentExtractor(self,"en")	
		# init the document cleaner
		cleaner = StandardDocumentCleaner(self)
		# init the output formatter
		formatter = StandardOutputFormatter(self, stopwords_class="en")
	
		# instanciation
		
		
		#url and raw_html
		
		#doc
		#self.doc = doc
		self.raw_doc = deepcopy(self.raw_html)
		
		self.title = extractor.get_title()
		#meta
		self.meta_lang = extractor.get_meta_lang()
		self.meta_favicon = extractor.get_favicon()
		self.meta_description = extractor.get_meta_description()
		self.meta_keywords = extractor.get_meta_keywords()
		
		#domain and url
		self.canonical_link = extractor.get_canonical_link()
		self.domain = extractor.get_domain()
		#~ 
		#~ #tag
		self.tags = extractor.extract_tags()
		#~ #text
		self.doc = cleaner.clean()
		
		self.top_node = extractor.calculate_best_node()
		if self.top_node is not None:
			# post cleanup
			self.top_node = extractor.post_cleanup()
		# clean_text
		self.cleaned_text = formatter.get_formatted_text()
		self.links = extractor.get_links()
		self.outlinks, self.outlinks_err = extractor.get_outlinks(self.links)
		self.inlinks, self.inlinks_err = extractor.get_outlinks(self.links)
		# TODO
		# self.article.publish_date = self.extractor.get_pub_date(doc)
		# self.article.additional_data = self.extractor.more(doc)
		
		return self
	'''
	def run(self):
		# TODO
		# self.article.publish_date = config.publishDateExtractor.extract(doc)
		# self.article.additional_data = config.get_additionaldata_extractor.extract(doc)
		self.title = self.extractor.get_title()
		self.meta_lang = self.extractor.get_meta_lang()
		self.meta_favicon = self.extractor.get_favicon()
		self.meta_description = self.extractor.get_meta_description()
		self.meta_keywords = self.extractor.get_meta_keywords()
		self.canonical_link = self.extractor.get_canonical_link()
		self.domain = self.extractor.get_domain()
		self.tags = self.extractor.extract_tags()

		# before we do any calcs on the body itself let's clean up the document
		self.doc = self.cleaner.clean()

		# big stuff
		self.top_node = self.extractor.calculate_best_node()
		# if we have a top node
		# let's process it
		if self.top_node is not None:
            # post cleanup
			self.top_node = self.extractor.post_cleanup()

			# clean_text
			self.cleaned_text = self.formatter.get_formatted_text()
        # return the article
		self.links = self.extractor.get_links()
		self.outlinks_err, self.outlinks = self.extractor.get_outlinks()
		delattr(self, parser)
		delattr(self, extractor)
		return self
	'''
