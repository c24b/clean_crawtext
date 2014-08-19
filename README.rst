.. image:: http://www.cortext.net/IMG/siteon0.png?1300195437
        :target: http://www.cortext.net

crawtext
===============================================
Crawtext is **one example of utilities we can find in the **Cortext manager** plateform.
Get a free account and discover the tools you can use for your own research
<http://manager.cortext.net/>`_here_ 


Module to crawl the web and store ressources based on your query or ressources urls using commandline

Installation
------------

To install crawtext, it is recommended to create a virtual env:
	
	$mkvirtualenv crawtext
	
	$workon crawtext

Then you can automatically install all the dependencies using pip
	
	$ pip -r requirements.txt

Using CRAWTEXT
------------

Crawtext is a simple module in command line to crawl the web given a query.
This interface offers you a full set of option to set up a project.
If you need any help on interacting with the shell command you can just type:
				$ python crawtext.py --help

CREATING A CRAWL PROJECT
----------
	python crawtext.py pesticides
    
Source
------

You can see the code `here <https://github.com/c24b/clean_crawtext>`_


TODO
----
* Activate Archive mode to crawl a website
* Build a web interface


