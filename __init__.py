#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Crawtext.
Description:
A simple crawler in command line.

Usage:
	crawtext.py archive [ -f (default|wiki|forum) ] <url>
	crawtext.py <name>
	crawtext.py <user>
	crawtext.py report <name> 
	crawtext.py export <name> 
	crawtext.py delete <name>
	crawtext.py <name> -u <email>
	crawtext.py <name> -q <query>
	crawtext.py <name> -k set <key>
	crawtext.py <name> -k append [<key>]
	crawtext.py <name> -s set <file>
	crawtext.py <name> -s add <url>
	crawtext.py <name> -s append <file>
	crawtext.py <name> -s expand
	crawtext.py <name> -s delete [<url>]
	crawtext.py <name> -s delete					
	crawtext.py <name> -r <month>
	crawtext.py start <name>
	crawtext.py list projects
	crawtext.py list archives
	crawtext.py (-h | --help)
  	crawtext.py --version
  	
Options:
	Projets:
	# Pour consulter un projet : 	crawtext.py pesticides
	# Pour consulter vos projets :	crawtext.py vous@cortext.net
	# Pour obtenir un rapport : 	crawtext.py report pesticides
	# Pour obtenir un export : 		crawtext.py export pesticides
	# Pour supprimer un projet : 	crawtext.py delete pesticides
	Proprietaire:
	# pour définir le propriétaire du project: crawtext pesticides -u vous@cortext.net
	Requête:
	# pour définir la requête: crawtext pesticides -q "pesticides AND DDT"
	Sources:
	# pour définir les sources d'après un fichier :	crawtext.py pesticides -s set sources.txt	
	# pour ajouter des sources d'après un fichier :	crawtext.py pesticides -s append sources.txt
	# pour ajouter une nouvelle url : 				crawtext.py pesticides -s add www.latribune.fr
	# pour définir les sources d'après Bing :		crawtext.py pesticides -k set 12237675647
	# pour ajouter des sources d'après Bing :		crawtext.py pesticides -k append 12237675647
	# pour ajouter des sources automatiquement :	crawtext.py pesticides -s expand
	# pour supprimer une source :					crawtext.py pesticides -s delete www.latribune.fr
	# pour supprimer toutes les sources :			crawtext.py pesticides -s delete
	Récurrence
	# pour définir la récurrence :                	crawtext.py pesticides -r (monthly|weekly|daily)
	Executer un projet								crawtext.py run pesticides
	
'''

__all__ = ['crawtext', 'manager','database', "scrapper", "dispatcher"]
import os, sys

CRAWTEXT = "crawtext"
CRAWTEXT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))


import __future__
from docopt import docopt
from worker import Worker

 

if __name__== "__main__":
	
	try:		
		w = Worker()
		print w.run(docopt(__doc__))
	except KeyboardInterrupt:
		sys.exit()
