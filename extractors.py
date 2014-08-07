# -*- coding: utf-8 -*-
import re, datetime
from copy import deepcopy
from urlparse import urlparse, urljoin
from utils import StringSplitter
from utils import StringReplacement
from utils import ReplaceSequence
from utils import URLHelper, RawHelper
from utils.text import StopWords
from utils.url import *
from lxml.cssselect import CSSSelector

from copy import deepcopy
from parsers import Parser
from cleaners import StandardDocumentCleaner
from formatters import StandardOutputFormatter


MOTLEY_REPLACEMENT = StringReplacement("&#65533;", "")
ESCAPED_FRAGMENT_REPLACEMENT = StringReplacement(u"#!", u"?_escaped_fragment_=")
TITLE_REPLACEMENTS = ReplaceSequence().create(u"&raquo;").append(u"»")
PIPE_SPLITTER = StringSplitter("\\|")
DASH_SPLITTER = StringSplitter(" - ")
ARROWS_SPLITTER = StringSplitter("»")
COLON_SPLITTER = StringSplitter(":")
SPACE_SPLITTER = StringSplitter(' ')
NO_STRINGS = set()
A_REL_TAG_SELECTOR = "a[rel=tag]"
A_HREF_TAG_SELECTOR = "a[href*='/tag/'], a[href*='/tags/'], a[href*='/topic/'], a[href*='?keyword=']"
RE_LANG = r'^[A-Za-z]{2}$'

class Article(object):
	'''Article'''
	def __init__(self, url, raw_html):
		#extraction set
		#init parser here defaut parser
		
		
		self.parser = Parser()
		self.extractor = StandardContentExtractor(self,self.parser, target_language="en", stopwords_class="en")			
		# init the document cleaner
		self.cleaner = StandardDocumentCleaner(self, self.parser)
		# init the output formatter
		self.formatter = StandardOutputFormatter(self,self.parser, stopwords_class="en")
		
		

		#ARTICLE PROP
		self.url = url
		self.final_url = url
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
		self.final_url = url

		# stores the MD5 hash of the url
		# to use for various identification tasks
		self.link_hash = ""

		# stores the RAW HTML
		# straight from the network connection
		#self.raw_html = u""
		self.raw_html = raw_html
		# the lxml Document object
		self.doc = self.parser.fromstring(self.raw_html)
		
		# this is the original JSoup document that contains
		# a pure object from the original HTML without any cleaning
		# options done on it
		self.raw_doc = deepcopy(self.doc)

		# Sometimes useful to try and know when
		# the publish date of an article was
		self.publish_date = None

		# A property bucket for consumers of goose to store custom data extractions.
		self.additional_data = {}
		self.links = None
		self.outlinks = None
		self.backlinks = None
		self.start_date = datetime.datetime.today()
	
	def extract(self):
		print "extracting"
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
		self.links = self.extractor.get_outlinks()
		
		return self
		
		
class Link(object):
	def __init__(self, article, parser, target_language="en", stopwords_class="en"):
		#~ # parser
		self.parser = parser

		# article
		self.article = article

		# language
		self.language = target_language

		# stopwords class
		self.stopwords_class = stopwords_class
		#StopWords
		self.stopwords = StopWords(stopwords_class)
		
		
class ContentExtractor(object):

    def __init__(self, article, parser, target_language="en", stopwords_class="en"):
		#~ # parser
		self.parser = parser

		# article
		self.article = article

		# language
		self.language = target_language

		# stopwords class
		self.stopwords_class = stopwords_class
		#StopWords
		self.stopwords = StopWords(stopwords_class)
		
    def get_title(self):
        """\
        Fetch the article title and analyze it
        """

        title = ''
        doc = self.article.doc

        title_element = self.parser.getElementsByTag(doc, tag='title')
        # no title found
        if title_element is None or len(title_element) == 0:
            return title

        # title elem found
        title_text = self.parser.getText(title_element[0])
        used_delimeter = False

        # split title with |
        if '|' in title_text:
            title_text = self.split_title(title_text, PIPE_SPLITTER)
            used_delimeter = True

        # split title with -
        if not used_delimeter and '-' in title_text:
            title_text = self.split_title(title_text, DASH_SPLITTER)
            used_delimeter = True

        # split title with »
        if not used_delimeter and u'»' in title_text:
            title_text = self.split_title(title_text, ARROWS_SPLITTER)
            used_delimeter = True

        # split title with :
        if not used_delimeter and ':' in title_text:
            title_text = self.split_title(title_text, COLON_SPLITTER)
            used_delimeter = True

        title = MOTLEY_REPLACEMENT.replaceAll(title_text)
        return title

    def split_title(self, title, splitter):
        """\
        Split the title to best part possible
        """
        large_text_length = 0
        large_text_index = 0
        title_pieces = splitter.split(title)

        # find the largest title piece
        for i in range(len(title_pieces)):
            current = title_pieces[i]
            if len(current) > large_text_length:
                large_text_length = len(current)
                large_text_index = i

        # replace content
        title = title_pieces[large_text_index]
        return TITLE_REPLACEMENTS.replaceAll(title).strip()

    def get_favicon(self):
        """\
        Extract the favicon from a website
        http://en.wikipedia.org/wiki/Favicon
        <link rel="shortcut icon" type="image/png" href="favicon.png" />
        <link rel="icon" type="image/png" href="favicon.png" />
        """
        kwargs = {'tag': 'link', 'attr': 'rel', 'value': 'icon'}
        meta = self.parser.getElementsByTag(self.article.doc, **kwargs)
        if meta:
            favicon = self.parser.getAttribute(meta[0], 'href')
            return favicon
        return ''

    def get_meta_lang(self):
        """\
        Extract content language from meta
        """
        # we have a lang attribute in html
        attr = self.parser.getAttribute(self.article.doc, attr='lang')
        if attr is None:
            # look up for a Content-Language in meta
            items = [
                {'tag': 'meta', 'attr': 'http-equiv', 'value': 'content-language'},
                {'tag': 'meta', 'attr': 'name', 'value': 'lang'}
            ]
            for item in items:
                meta = self.parser.getElementsByTag(self.article.doc, **item)
                if meta:
                    attr = self.parser.getAttribute(meta[0], attr='content')
                    break

        if attr:
            value = attr[:2]
            if re.search(RE_LANG, value):
                return value.lower()

        return None

    def get_meta_content(self, doc, metaName):
        """\
        Extract a given meta content form document
        """
        meta = self.parser.css_select(doc, metaName)
        content = None

        if meta is not None and len(meta) > 0:
            content = self.parser.getAttribute(meta[0], 'content')

        if content:
            return content.strip()

        return ''

    def get_meta_description(self):
        """\
        if the article has meta description set in the source, use that
        """
        return self.get_meta_content(self.article.doc, "meta[name=description]")

    def get_meta_keywords(self):
        """\
        if the article has meta keywords set in the source, use that
        """
        return self.get_meta_content(self.article.doc, "meta[name=keywords]")

    def get_canonical_link(self):
        """\
        if the article has meta canonical link set in the url
        """
        if self.article.final_url:
            kwargs = {'tag': 'link', 'attr': 'rel', 'value': 'canonical'}
            meta = self.parser.getElementsByTag(self.article.doc, **kwargs)
            if meta is not None and len(meta) > 0:
                href = self.parser.getAttribute(meta[0], 'href')
                if href:
                    href = href.strip()
                    o = urlparse(href)
                    if not o.hostname:
                        z = urlparse(self.article.final_url)
                        domain = '%s://%s' % (z.scheme, z.hostname)
                        href = urljoin(domain, href)
                    return href
        return self.article.final_url

    def get_domain(self):
        if self.article.final_url:
            o = urlparse(self.article.final_url)
            return o.hostname
        return None

    def extract_tags(self):
        node = self.article.doc

        # node doesn't have chidren
        if len(list(node)) == 0:
            return NO_STRINGS

        elements = self.parser.css_select(node, A_REL_TAG_SELECTOR)
        if not elements:
            elements = self.parser.css_select(node, A_HREF_TAG_SELECTOR)
            if not elements:
                return NO_STRINGS

        tags = []
        for el in elements:
            tag = self.parser.getText(el)
            if tag:
                tags.append(tag)

        return set(tags)
    
    def get_links(self):
        node = self.article.doc
        select = CSSSelector("a")
        self.links = [ el.get('href') for el in select(node)]
        self.links = [ n for n in self.links if n is not None or n != ""]
        return set(self.links)
    
    def get_outlinks(self):
		self.get_links()
		for u in self.links:
			print u
			print validate_url(u,self.article.final_url)
		
		return set(self.outlinks) 

    def get_backlinks(self):
        self.outlinks = None
        return set(self.outlinks) 

    def calculate_best_node(self):
        doc = self.article.doc
        top_node = None
        nodes_to_check = self.nodes_to_check(doc)

        starting_boost = float(1.0)
        cnt = 0
        i = 0
        parent_nodes = []
        nodes_with_text = []

        for node in nodes_to_check:
            text_node = self.parser.getText(node)
            word_stats = self.stopwords.get_stopword_count(text_node)
            high_link_density = self.is_highlink_density(node)
            if word_stats.get_stopword_count() > 2 and not high_link_density:
                nodes_with_text.append(node)

        nodes_number = len(nodes_with_text)
        negative_scoring = 0
        bottom_negativescore_nodes = float(nodes_number) * 0.25

        for node in nodes_with_text:
            boost_score = float(0)
            # boost
            if(self.is_boostable(node)):
                if cnt >= 0:
                    boost_score = float((1.0 / starting_boost) * 50)
                    starting_boost += 1
            # nodes_number
            if nodes_number > 15:
                if (nodes_number - i) <= bottom_negativescore_nodes:
                    booster = float(bottom_negativescore_nodes - (nodes_number - i))
                    boost_score = float(-pow(booster, float(2)))
                    negscore = abs(boost_score) + negative_scoring
                    if negscore > 40:
                        boost_score = float(5)

            text_node = self.parser.getText(node)
            word_stats = self.stopwords.get_stopword_count(text_node)
            upscore = int(word_stats.get_stopword_count() + boost_score)

            # parent node
            parent_node = self.parser.getParent(node)
            self.update_score(parent_node, upscore)
            self.update_node_count(parent_node, 1)

            if parent_node not in parent_nodes:
                parent_nodes.append(parent_node)

            # parentparent node
            parent_parent_node = self.parser.getParent(parent_node)
            if parent_parent_node is not None:
                self.update_node_count(parent_parent_node, 1)
                self.update_score(parent_parent_node, upscore / 2)
                if parent_parent_node not in parent_nodes:
                    parent_nodes.append(parent_parent_node)
            cnt += 1
            i += 1

        top_node_score = 0
        for e in parent_nodes:
            score = self.get_score(e)

            if score > top_node_score:
                top_node = e
                top_node_score = score

            if top_node is None:
                top_node = e

        return top_node

    def is_boostable(self, node):
        """\
        alot of times the first paragraph might be the caption under an image
        so we'll want to make sure if we're going to boost a parent node that
        it should be connected to other paragraphs,
        at least for the first n paragraphs so we'll want to make sure that
        the next sibling is a paragraph and has at
        least some substatial weight to it
        """
        para = "p"
        steps_away = 0
        minimum_stopword_count = 5
        max_stepsaway_from_node = 3

        nodes = self.walk_siblings(node)
        for current_node in nodes:
            # p
            current_node_tag = self.parser.getTag(current_node)
            if current_node_tag == para:
                if steps_away >= max_stepsaway_from_node:
                    return False
                paraText = self.parser.getText(current_node)
                word_stats = self.stopwords.get_stopword_count(paraText)
                if word_stats.get_stopword_count() > minimum_stopword_count:
                    return True
                steps_away += 1
        return False

    def walk_siblings(self, node):
        current_sibling = self.parser.previousSibling(node)
        b = []
        while current_sibling is not None:
            b.append(current_sibling)
            previousSibling = self.parser.previousSibling(current_sibling)
            current_sibling = None if previousSibling is None else previousSibling
        return b

    def add_siblings(self, top_node):
        baselinescore_siblings_para = self.get_siblings_score(top_node)
        results = self.walk_siblings(top_node)
        for current_node in results:
            ps = self.get_siblings_content(current_node, baselinescore_siblings_para)
            for p in ps:
                top_node.insert(0, p)
        return top_node

    def get_siblings_content(self, current_sibling, baselinescore_siblings_para):
        """\
        adds any siblings that may have a decent score to this node
        """
        if current_sibling.tag == 'p' and len(self.parser.getText(current_sibling)) > 0:
            e0 = current_sibling
            if e0.tail:
                e0 = deepcopy(e0)
                e0.tail = ''
            return [e0]
        else:
            potential_paragraphs = self.parser.getElementsByTag(current_sibling, tag='p')
            if potential_paragraphs is None:
                return None
            else:
                ps = []
                for first_paragraph in potential_paragraphs:
                    text = self.parser.getText(first_paragraph)
                    if len(text) > 0:
                        word_stats = self.stopwords.get_stopword_count(text)
                        paragraph_score = word_stats.get_stopword_count()
                        sibling_baseline_score = float(.30)
                        high_link_density = self.is_highlink_density(first_paragraph)
                        score = float(baselinescore_siblings_para * sibling_baseline_score)
                        if score < paragraph_score and not high_link_density:
                            p = self.parser.createElement(tag='p', text=text, tail=None)
                            ps.append(p)
                return ps

    def get_siblings_score(self, top_node):
        """\
        we could have long articles that have tons of paragraphs
        so if we tried to calculate the base score against
        the total text score of those paragraphs it would be unfair.
        So we need to normalize the score based on the average scoring
        of the paragraphs within the top node.
        For example if our total score of 10 paragraphs was 1000
        but each had an average value of 100 then 100 should be our base.
        """
        base = 100000
        paragraphs_number = 0
        paragraphs_score = 0
        nodes_to_check = self.parser.getElementsByTag(top_node, tag='p')

        for node in nodes_to_check:
            text_node = self.parser.getText(node)
            word_stats = self.stopwords.get_stopword_count(text_node)
            high_link_density = self.is_highlink_density(node)
            if word_stats.get_stopword_count() > 2 and not high_link_density:
                paragraphs_number += 1
                paragraphs_score += word_stats.get_stopword_count()

        if paragraphs_number > 0:
            base = paragraphs_score / paragraphs_number

        return base

    def update_score(self, node, addToScore):
        """\
        adds a score to the gravityScore Attribute we put on divs
        we'll get the current score then add the score
        we're passing in to the current
        """
        current_score = 0
        score_string = self.parser.getAttribute(node, 'gravityScore')
        if score_string:
            current_score = int(score_string)

        new_score = current_score + addToScore
        self.parser.setAttribute(node, "gravityScore", str(new_score))

    def update_node_count(self, node, add_to_count):
        """\
        stores how many decent nodes are under a parent node
        """
        current_score = 0
        count_string = self.parser.getAttribute(node, 'gravityNodes')
        if count_string:
            current_score = int(count_string)

        new_score = current_score + add_to_count
        self.parser.setAttribute(node, "gravityNodes", str(new_score))

    def is_highlink_density(self, e):
        """\
        checks the density of links within a node,
        is there not much text and most of it contains linky shit?
        if so it's no good
        """
        links = self.parser.getElementsByTag(e, tag='a')
        if links is None or len(links) == 0:
            return False

        text = self.parser.getText(e)
        words = text.split(' ')
        words_number = float(len(words))
        sb = []
        for link in links:
            sb.append(self.parser.getText(link))

        linkText = ''.join(sb)
        linkWords = linkText.split(' ')
        numberOfLinkWords = float(len(linkWords))
        numberOfLinks = float(len(links))
        linkDivisor = float(numberOfLinkWords / words_number)
        score = float(linkDivisor * numberOfLinks)
        if score >= 1.0:
            return True
        return False
        # return True if score > 1.0 else False

    def get_score(self, node):
        """\
        returns the gravityScore as an integer from this node
        """
        return self.get_node_gravity_score(node) or 0

    def get_node_gravity_score(self, node):
        grvScoreString = self.parser.getAttribute(node, 'gravityScore')
        if not grvScoreString:
            return None
        return int(grvScoreString)

    def nodes_to_check(self, doc):
        """\
        returns a list of nodes we want to search
        on like paragraphs and tables
        """
        nodes_to_check = []
        for tag in ['p', 'pre', 'td']:
            items = self.parser.getElementsByTag(doc, tag=tag)
            nodes_to_check += items
        return nodes_to_check

    def is_table_and_no_para_exist(self, e):
        subParagraphs = self.parser.getElementsByTag(e, tag='p')
        for p in subParagraphs:
            txt = self.parser.getText(p)
            if len(txt) < 25:
                self.parser.remove(p)

        subParagraphs2 = self.parser.getElementsByTag(e, tag='p')
        if len(subParagraphs2) == 0 and e.tag is not "td":
            return True
        return False

    def is_nodescore_threshold_met(self, node, e):
        top_node_score = self.get_score(node)
        current_nodeScore = self.get_score(e)
        thresholdScore = float(top_node_score * .08)

        if (current_nodeScore < thresholdScore) and e.tag != 'td':
            return False
        return True

    def post_cleanup(self):
        """\
        remove any divs that looks like non-content,
        clusters of links, or paras with no gusto
        """
        targetNode = self.article.top_node
        node = self.add_siblings(targetNode)
        for e in self.parser.getChildren(node):
            e_tag = self.parser.getTag(e)
            if e_tag != 'p':
                if self.is_highlink_density(e) \
                    or self.is_table_and_no_para_exist(e) \
                    or not self.is_nodescore_threshold_met(node, e):
                    self.parser.remove(e)
        return node


class StandardContentExtractor(ContentExtractor):
    pass
