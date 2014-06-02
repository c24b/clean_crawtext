#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
from pymongo import errors

class Database(object):
	'''Database creation''' 
	def __init__(self, database_name):
		self.db_name = database_name
		self.client = MongoClient('mongodb://localhost,localhost:27017')
		self.db = self.client[self.db_name]
		#self.results = self.db['results']
		#self.queue = self.db['queue'] 
		#self.log = self.db['log']
		#self.sources = self.db['sources']
		#self.jobs = self.db['jobs']
		#self.db.x = self.db[x]
		
	def __repr__(self, database_name):	
		print "Using database: %s" %self.client[database_name]
		return self.client[database_name]
	def __getitem__(self, item):
		return self.db[str(item)].find_one()

	def use_db(self, name):
		return self.client[str(name)]

	def show_dbs(self):
		return self.client.database_names()
	
	def show_coll(self):
		print "using collection %s in DB : %s" %(self.name, self.db_name)
		return self.name

		#return self.db.collection_names()
	def show_coll_items(self, coll_name):
		return [n for n in self.db[str(coll_name)].find()]	
	
	def create_tables(self):
		self.results = self.db['results']
		self.queue = self.db['queue'] 
		self.log = self.db['log']
		self.sources = self.db['sources']
		print "Creating coll",  [n for n in self.db.collection_names()]
		return [n for n in self.db.collection_names()]
	
	def create_table(self, name):
		self.name= self.db[name]
		print "coll : %s has been created in db:%s " %(self.name, self.db_name)
		return self.name
	
	def drop(self, type, name):
		if type == "collection":
			return self.db[str(name)].drop()
		elif type == "database":
			return self.client.drop_database(str(name))
		else:
			print "Unknown Type"
			return False
	def drop_all_dbs():
		'''be carefull'''
		for n in self.show_dbs():
			self.use_db(n)
			self.drop("database", n)

	def stats(self):
		'''Output the current stats of database in Terminal'''
		title = "===STATS===\n"
		name ="Stored results in Mongo Database: %s \n" %(self.name)
		res = "\t-Nombre de resultats dans la base: %d\n" % (self.db.results.count())
		sources = "\t-Nombre de sources: %d\n" % len(self.db.sources.distinct('url')) 
		url = "\t-urls en cours de traitement: %d\n" % (self.db.queue.count())
		url2 = "\t-urls traitees: %d\n" % (self.db.results.count()+ self.db.log.count())
		url3 = "\t-urls erronées: %d\n" % (self.db.log.count())
		size = "\t-Size of the database %s: %d MB\n" % (self.name, (self.db.command('dbStats', 1024)['storageSize'])/1024/1024.)
		result = [title, name, res, sources, url, url2, size]
		return "".join(result)
	
	def report(self):
		''' Output the currents of database for Email Report'''
		res = "<li>Nombre de resultats dans la base: %d</li>" % (self.db.results.count())
		sources = "<li>Nombre de sources: %d</li>" % len(self.db.sources.distinct('url')) 
		url = "<li>urls en cours de traitement: %d\n</li>" % (self.db.queue.count())
		url2 = "<li>urls traitees: %d</li>" % (self.db.results.count()+ self.db.log.count())
		size = "<li>Size of the database %s: %d MB</li>" % (self.name, (self.db.command('dbStats', 1024)['storageSize'])/1024/1024.)
		result = [res, sources, url, url2, size]
		return "".join(result)
	