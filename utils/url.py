"""
This module contains general purpose URL functions not found in the standard
library.

Some of the functions that used to be imported from this module have been moved
to the w3lib.url module. Always import those from there instead.
"""
import posixpath
from six.moves.urllib.parse import ParseResult, urlunparse, urldefrag, urlparse
import urllib
import cgi

# scrapy.utils.url was moved to w3lib.url and import * ensures this move doesn't break old code
from w3lib.url import *
from utils.encoding import unicode_to_str
from abpy import Filter

#adblocklist of unwanted domain
#adblock = Filter(file('/home/c24b/projets/CRAWTEXT/V2.04/utils/easylist.txt'))
#IGNORED_DOMAINS = adblock.get_list()

# common scheme that are not followed if they occur in links
#IGNORED_PROTOCOL = ['ftp', 'sftp', 'mailto', 'magnet', 'javascript']
ACCEPTED_PROTOCOL = ['http', 'https']

# common file extensions that are not followed if they occur in links
IGNORED_EXTENSIONS = [

    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg','gif', 'ico', 'svg',

    # audio
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

    # video
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
    'm4a',

    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'doc', 'docx', 'odt', 'ods', 'odg', 'odp',
	
	#compressed doc
	'zip', 'rar', 'gz', 'bz2', 'torrent', 'tar',
	 
    # other
    'css', 'pdf', 'exe', 'bin', 'rss','dtd', 'asp', 'js', 'torrent',
]
IGNORED_DOMAINS = Filter(file('./utils/easylist.txt'))

def check_url(url):
	'''Bool: check the format of the curr url'''
	if url is None or len(url) <= 1 or url == "\n":
		error_type = "Url is empty"
		status = False
		status_code = 406
		
	elif url_has_any_extension(url, IGNORED_EXTENSIONS) is True :
		error_type="Url has not a supported extension (PDF, ZIP, etc...)"
		status = False
		status_code = 406.1
		
	elif url_is_from_any_domain(url, IGNORED_DOMAINS) is True:
		error_type="Url refers to an advertissement listed in Adblock"
		status = False
		status_code = 406.2
		
	else:
		scheme = urlparse(url).scheme
		if scheme == "" or scheme is None:
			url = "http://"+url
			status = True
			status_code = 200
			error_type = None
			
		elif scheme not in ACCEPTED_PROTOCOL:
			error_type="Protocol is not http or https"
			status = False
			status_code = 406.2	
		else:
			status = True
			status_code = 200
			error_type = None
	return (status, status_code, error_type)
			

def url_has_any_protocol(url, protocols):
	"""Return True if the url belongs to any of the given protocol"""
	scheme = parse_url(url).scheme.lower()
	if scheme:
		return any(((scheme == d.scheme()) for d in protocols))		
	else:
		return False
    
def url_is_from_any_domain(url, domains):
    """Return True if the url belongs to any of the given domains"""
    if len( domains.match(url) ) > 0:
		return True
    else:
        return False


def url_is_from_spider(url, spider):
    """Return True if the url belongs to the given spider"""
    return url_is_from_any_domain(url,
        [spider.name] + list(getattr(spider, 'allowed_domains', [])))

def url_has_any_protocol(url, protocols):
	print protocols
	return (parse_url(url).scheme).lower() in protocols
	
def url_has_any_extension(url, extensions):
	return posixpath.splitext(parse_url(url).netloc)[1].lower() in extensions


def relative_url(url):
	if urlparse(url).netloc is None:
		return True
	if urlparse(url).path == "/" or urlparse(url).path == "../":
		return True
	else:
		return False
			
def from_rel_to_absolute_url(url,root_url):
	scheme, netloc, path, params, query, fragment = urlparse(url)
	if relative_url(url):
		scheme = urlparse(root_url).scheme
		netloc = urlparse(root_url).netloc
	print netloc
	return urlunparse((scheme, netloc.lower(), path, params, query, fragment))	

def check_scheme(url):
	scheme = urlparse(url).scheme
	print scheme
	if scheme in ["mailto", "ftp", "magnet"]:
		return False
	
		
		
def canonicalize_url(url,keep_blank_values=True, keep_fragments=False,
        encoding=None):
	"""Canonicalize the given url by applying the following procedures:

	- sort query arguments, first by key, then by value
	- percent encode paths and query arguments. non-ASCII characters are
	  percent-encoded using UTF-8 (RFC-3986)
	- normalize all spaces (in query arguments) '+' (plus symbol)
	- normalize percent encodings case (%2f -> %2F)
	- remove query arguments with blank values (unless keep_blank_values is True)
	- remove fragments (unless keep_fragments is True)

	The url passed can be a str or unicode, while the url returned is always a
	str.

	For examples see the tests in tests/test_utils_url.py
	"""
	scheme, netloc, path, params, query, fragment = parse_url(url)
		
	keyvals = cgi.parse_qsl(query, keep_blank_values)
	keyvals.sort()
	query = urllib.urlencode(keyvals)
	path = safe_url_string(_unquotepath(path)) or '/'
	fragment = '' if not keep_fragments else fragment
	return urlunparse((scheme, netloc.lower(), path, params, query, fragment))


def _unquotepath(path):
    for reserved in ('2f', '2F', '3f', '3F'):
        path = path.replace('%' + reserved, '%25' + reserved.upper())
    return urllib.unquote(path)


def parse_url(url, encoding=None):
    """Return urlparsed url from the given argument (which could be an already
    parsed url)
    """
    return url if isinstance(url, ParseResult) else \
        urlparse(unicode_to_str(url, encoding))

def escape_js(url):
	pass
			
def escape_ajax(url):
    """
    Return the crawleable url according to:
    http://code.google.com/web/ajaxcrawling/docs/getting-started.html

    >>> escape_ajax("www.example.com/ajax.html#!key=value")
    'www.example.com/ajax.html?_escaped_fragment_=key%3Dvalue'
    >>> escape_ajax("www.example.com/ajax.html?k1=v1&k2=v2#!key=value")
    'www.example.com/ajax.html?k1=v1&k2=v2&_escaped_fragment_=key%3Dvalue'
    >>> escape_ajax("www.example.com/ajax.html?#!key=value")
    'www.example.com/ajax.html?_escaped_fragment_=key%3Dvalue'
    >>> escape_ajax("www.example.com/ajax.html#!")
    'www.example.com/ajax.html?_escaped_fragment_='

    URLs that are not "AJAX crawlable" (according to Google) returned as-is:

    >>> escape_ajax("www.example.com/ajax.html#key=value")
    'www.example.com/ajax.html#key=value'
    >>> escape_ajax("www.example.com/ajax.html#")
    'www.example.com/ajax.html#'
    >>> escape_ajax("www.example.com/ajax.html")
    'www.example.com/ajax.html'
    """
    defrag, frag = urldefrag(url)
    if not frag.startswith('!'):
        if url not in ["#"]:
			return url
    return add_or_replace_parameter(defrag, '_escaped_fragment_', frag[1:])
