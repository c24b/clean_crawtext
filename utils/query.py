from whoosh.qparser import MultifieldParser
from whoosh.fields import Schema, TEXT, NGRAMWORDS
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.index import create_in
import pymongo

def regexify(string):
	schema = Schema(title=TEXT, content=TEXT, tags = NGRAMWORDS, meta = TEXT)
	parser = MultifieldParser(["title", "content"], schema=schema)
	return parser.parse(string)

def query_match(shema, query, string):
	
	regex_q = regexify(query)
	ix = create_in("indexdir", schema)
	writer = ix.writer()

# MongoDB中有数据库bookmarks_cloud, 有集合bookmarks
#bookmarks_collection = pymongo.Connection().bookmarks_cloud.bookmarks

# from bookmarks_cloud.whoosh_fts import ChineseAnalyzer
# jieba已经内置了和whoosh的集成功能
#from jieba.analyse import ChineseAnalyzer
#analyzer = ChineseAnalyzer()
schema = Schema(
            nid=ID(unique=True, stored=True),
            url=ID(unique=True, stored=True),
            title=TEXT(phrase=False),
            tags=KEYWORD(lowercase=True, commas=True, scorable=True),
            note=TEXT(analyzer=analyzer),
            article=TEXT(stored=True, analyzer=analyzer)
        )

import os
from whoosh.index import create_in, open_dir
if not os.path.exists("testindexdir"):
    os.mkdir("testindexdir")
    create_in("testindexdir", schema)
ix = open_dir("testindexdir")
writer = ix.writer()
for bm in bookmarks_collection.find(timeout=False):
    writer.update_document(
            nid=str(bm['_id']),
            url=bm['url'],
            title=bm['title'],
            tags=",".join(bm['tags']),
            note=bm['note'],
            article=bm['article']
        )
writer.commit()
# 搜索
from whoosh.qparser import MultifieldParser
with ix.searcher() as searcher:
    query = MultifieldParser(["url", "title", "tags", "note", "article"], ix.schema).parse("Python")
    results = searcher.search(query)
    print(len(results))
    print(results[0])
    keywords = [keyword for keyword, score in results.key_terms("article", docs=10, numterms=5)]
    print(keywords)

