#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Crawtext.

Usage:
	crawtext.py <project> crawl <query> [--email=<email>]
	crawtext.py <project> discover <query> [--file=<filename> | --key=<bing_api_key> | --file=<filename> --key=<bing_api_key>] [-v]
	crawtext.py <project> restart 
	crawtext.py <project> stop
	crawtext.py <project> report [--email=<email>]
	crawtext.py (-h | --help)
  	crawtext.py --version

Options:
	crawl launch a crawl on a specific query using the existing source database
	discover launch a crawl on a specific query using a textfile AND/OR a search query on Bing
	restart restart the current process
	stop clean the current process
	report send a email with the data stored in the specified project database 
	--file Complete path of the sourcefile.
	--key  Bing API Key for SearchNY.
	--mail one or more emails separated by a coma
	-h --help Show usage and Options.
	--version Show versions.  
'''

__all__ = ['crawtext']

import __future__
import datetime

import sys
from docopt import docopt
from database import Database
from page import Page
from crawtext_options import Discovery, Sourcing
from report import Report, send_report
from pymongo import errors as mongo_err

def crawler(docopt_args):
	start = datetime.datetime.now()
	db_name = docopt_args['<project>']
	query = docopt_args['<query>']
	'''the main consumer from queue insert into results or log'''
	db = Database(db_name)
	db.create_tables()
	schedule(send_report, docopt_args)
	while db.queue.count > 0:

		print "beginning crawl"
		print "Nombre de sources dans la base", db.sources.count()
		print "Nombre d'url à traiter", len(db.queue.distinct("url"))
		for url in db.queue.distinct("url"):
			if url not in db.results.find({"url":url}):
				p = Page(url, query)
				
				if p.check() and p.request() and p.control() and p.extract():
					#print "Links", p.outlinks
					db.results.insert(p.info)
					if p.outlinks is not None:
						try:
							for n_url in p.outlinks:
								if n_url not in db.queue.find({"url":n_url}) or n_url not in db.results.find({"url":n_url}) or n_url not in db.log.find({"url":n_url}):
									next_p = Page(n_url, query)
									if next_p.clean_url(p.url) is not None:
										db.queue.insert({"url":n_url})
						except mongo_err:
							db.log.insert(({"url":url, "error_type": "pymongo error inserting outlinks", "status":False}))
				elif p.error_type != 0:
					''' if the page is not relevant do not store in db'''
					db.log.insert(p.bad_status())
				else:
					continue

			db.queue.remove({"url": url})
			# print "En traitement", self.db.queue.count()
			# print "Resultats", self.db.results.count()
			# print "Erreur", self.db.log.count()
			if db.queue.count() == 0:
				print db.stats()
				#unschedule(send_report, docopt_args)
				break
			
		if db.queue.count() == 0:
			print db.stats()
			unschedule(send_report, docopt_args)
			break
		

	end = datetime.datetime.now()
	elapsed = end - start
	print "crawl finished, %i results and %i sources are stored in Mongo Database: %s in %s" %(db.results.count(),db.sources.count(),db_name, elapsed)
	return 

def crawtext(docopt_args):
	''' main crawtext run by command line option '''
	if docopt_args['discover'] is True:
		print "Running discovery mode ..."
		if docopt_args['<query>'] is not None:
			Discovery(db_name=docopt_args['<project>'],query=docopt_args['<query>'], path=docopt_args['--file'], api_key=docopt_args['--key'])
			Sourcing(db_name=docopt_args['<project>'])
			crawler(docopt_args)
			self.db.queue.drop()
			return "Discovery completed"
		else:
			print "Discovery mode needs a query to search. Please check your arguments and try again"
			print docopt_args['help']
			return False
		#crawler(docopt_args)
		# if docopt_args['--repeat']:
		# 	schedule(crawler, docopt_args)
		# 	return sys.exit()
	elif docopt_args['crawl'] is True:
		s = Sourcing(db_name=docopt_args['<project>'])
		crawler(docopt_args)
		return "Sourcing completed"
		#crawler(docopt_args)
		# if docopt_args['--repeat']:
			# schedule(crawler, docopt_args)
			# return sys.exit()
	elif docopt_args['stop']:
		db = Database(docopt_args['<project>'])
		db.queue.drop()
		# unschedule(docopt_args)
		print ">>>Current queue is now empty. Process is stopped"
		print db.stats()
		return
	elif docopt_args['restart']:
		'''Option restart restarting the current queue without adding to sources'''
		db = Database(docopt_args['<project>'])
		
		if db.queue.count() <=0:
			print ">>>No data in current queue. Process can't be restarted. Please use crawl or discovery mode"
			print db.stats()
			return
		else:
			print ">>>Restarting..."
			crawler(docopt_args)
		#schedule(crawler, docopt_args)
		return 
	elif docopt_args['report']:
		Report(docopt_args)
		return
	else:
		print "No command supplied, please check command line usage and options."
		return sys.exit() 

if __name__ == "__main__":
	crawtext(docopt(__doc__))
	sys.exit()

