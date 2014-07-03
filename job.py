import re
from validate_email import validate_email
from datetime import datetime
from utils import yes_no
from database import *

class Job(object):
	#__metaclass__ = ABCMeta
	def __init__(self, user_input):
		#initializing job
		self.action = None
		self.user = None
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
			
			if self.action is None:
				self.action = "show"
	
	def create_from_ui(self):
		'''defaut values from user input'''
		for k, v in self.__dict__.items():
			if k in ["report", "extract", "export", "delete", "archive", "crawl"]:
				if v is True:
					self.action = k
					self.start_date = datetime.today()
					self.update = False
						
				
			elif k in ["q", "s", "k", "u", "r"]:
				if v is True:
					#print "updating parameter '%s' in project '%s'"%(k, user_input["<name>"])
					self.update = True
					self.action = "update"
					self.scope = k		
					
			elif k in ["monthly", "weekly", "daily"]:
				if v is not None or False:
					self.frequency = v
				else:
					self.frequency = "monthly"
			else:
				pass
		

	def create_from_database(self):
		'''doc.action = crawl ==> CrawlJob(doc)'''
		try:
			return globals()[(self.action).capitalize()+"Job"](self.__dict__) 
		except KeyError:
			return NotImplementedError
	
				
	def __repr__(self):
		'''print Job properties'''
		return self.__dict__	
			    
		
	def run(self):
		print "running Job..."
		pass
				
class CreateJob(Job):
	def __init__(self, doc): 
		#self.date = datetime.now()
		
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
		print "updating"
		print self.scope
		pass	
		
class CrawlJob(Job):
	def __init__(self, doc): 
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		self.db = Database(self.name)
		self.db.create_colls()	
	
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
			print e
			self.status_code = -1
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
			self.db.sources.insert({"url":url, "origin":"bing","date":[datetime.today()]}, upsert=False)
		else:
			self.db.sources.update({"url":url,"$push": {"date":datetime.today()}}, upsert=True)
		return self.db.sources.find_one({"url": url})
		
	def collect_sources(self):
		''' Method to add new seed to sources and send them to queue if sourcing is deactivate'''
		if self.file is not None:
			self.get_local()
		if self.query is not None and self.key is not None:
			self.get_bing()
		#~ if self.expand is True:
			#~ self.expand()
		return self
		
	def send_seeds_to_queue(self):
		#here we could filter out problematic urls
		for url in self.db.sources.distinct("url"):
			self.db.queue.insert({"url":url})
		return self
		
	def activate(self):
		try:
			#if self.sourcing is False:
			self.collect_sources()
		except AttributeError:
			pass
		return self.send_seeds_to_queue()
		
	def run(self):
		print "Running crawler..."
		self.activate()
		start = datetime.now()
		while self.db.queue.count > 0:
			for url in self.db.queue.distinct("url"):
				page = Page(url)
				if page.logs["status"] is False:
					self.db.logs.insert(page.logs)
				else:
					page.extract("article")
					print page.title 
					
				#~ print page.status
					#print page.canonical_link
				# else:
				# 	self.db.logs.insert(article.bad_status())
				self.db.queue.remove({"url": url})
				if self.db.queue.count() == 0:
					break
			
			if self.db.queue.count() == 0:		
				break
		
		end = datetime.now()
		elapsed = end - start
		print "crawl finished in %s" %(elapsed)
		print self.db.stats()
		return 
	
class ReportJob(Job):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		self.db = Database(self.name)
		
	def run(self):
		print "Report:"
		filename = "Report_%s_%d" %(self.name, self.date)
		with open( 'a') as f:
			f.write((self.db.stats()).encode('utf-8'))
		print "Successfully generated report for %s" %self.name 	
		return self	
		
class ExtractJob(Job):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		pass
		
class ExportJob(Job):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		pass
class RunJob(Job):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		pass
class UpdateJob(Job):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		pass
class DeleteJob(Job):
	def __init__(self, doc):
		self.date = datetime.now()
		for k, v in doc.items():
			setattr(self,k,v) 	
		pass
