import os
 
from whoosh.fields import Schema, ID, KEYWORD, TEXT
from whoosh.index import create_in
from whoosh.query import Term
 
#from pymongo import Connection
from database import Database
from bson.objectid import ObjectId
class Search(object):
	def __init__(self): 
	 
		# Set index, we index title and content as texts and tags as keywords.
		# We store inside index only titles and ids.
		self.schema = Schema(title=TEXT(stored=True), content=TEXT,
						nid=ID(stored=True))
		 
		# Create index dir if it does not exists.
		if not os.path.exists("indexd"):
			os.mkdir("indexd")
		 
		# Initialize index
		self.index = create_in("index", self.schema)
 
# Initiate db connection
#~ db = Database('pesticides22')
#~ db.create_coll("results")
#~ results = db.results
#~ connection = Connection('localhost', 27017)
#~ db = connection["cozy-home"]
#~ posts = db.posts
 
	
	def fill(self, doc):
	# Fill index with posts from DB
		self.writer = self.index.writer()
		self.writer.update_document(title=doc["title"],
							   content=doc["article"])

		self.writer.commit()
	
	def search(self, term, scope="content"):
		# Search inside index for post containing "test", then it displays
		# results.
		with self.index.searcher() as searcher:
			result = searcher.search(Term(term, scope))[0]
			return result
		#~ #post = posts.find_one(ObjectId(result["nid"]))
		#~ print result["title"]
		#~ print post["content"]


if __name__ == '__main__':
	s = Search()
	doc = {"title": u"Digital humanities", "article": u"Digital humanity"}
	s.fill(doc)
	s.search(u"digital")
	#w_query = query_parser("digital AND humanities")
	#~ print w_query
	#~ self.db = Database("dh")
	#~ self.db.create_colls(['sources', 'results', 'logs', 'queue'])	
	
