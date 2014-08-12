import os

from database import Database
from whoosh.qparser import MultifieldParser
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.index import create_in, open_dir
schema = Schema(
				nid=ID(unique=True, stored=True),
				url=ID(unique=True, stored=True),
				title=TEXT(phrase=False),
				tags=KEYWORD(lowercase=True, commas=True, scorable=True),
				article=TEXT(stored=True)
			)
			
def query_parser(query):
	
	parser = MultifieldParser(["url", "title", "tags", "article", "meta_description"], schema=schema)
	w_query = parser.parse(query)
	return w_query
	
def parse(doc, query):
	if not os.path.exists("index"):
		os.mkdir("index")
		create_in("index", schema)
	ix = open_dir("index")
	writer = ix.writer()
	writer.update_document(
		nid = str(doc["_id"]),
		url=doc['url'],
        title=doc['title'],
        tags=",".join(doc['meta_keywords']),    
        article=doc['article'],
        meta_description = doc['meta_description']
        )
	writer.commit()
	results = searcher.search(query)
	print(len(results))
	print(results[0])
	keywords = [keyword for keyword, score in results.key_terms("article", docs=10, numterms=5)]
	print(keywords)

'''if __name__ == '__main__':
	w_query = query_parser("digital AND humanities")
	print w_query
	self.db = Database("dh")
	self.db.create_colls(['sources', 'results', 'logs', 'queue'])	
	'''
