
test = [
#create crawl name
'python crawtext.py new_project'
#show crawl name	
'python crawtext.py new_project'
#show archive url
'python crawtext.py www.lemonde.fr'
#create archive url
'python crawtext.py archive www.lemonde.fr'
#show user
'python crawtext.py 4barbes@gmail.com'
#udpate	crawl query
'python crawtext.py new_project -q "ebola"'
#udpate	project user
'python crawtext.py new_project -u me@cortext.net'
#udpate crawl source url
'python crawtext.py new_project -s add www.lemonde.fr'
#udpate crawl key
'python crawtext.py new_project -k "123347Z3"'
#udpate crawl option
'python crawtext.py new_project -s extend'
#udpate project repeat
'python crawtext.py new_project -r day'
#start project 
'python crawtext.py start new_project'
#delete crawl source url
'python crawtext.py new_project -s delete www.lemonde'
#udpate crawl source url
'python crawtext.py new_project -s add www.lemonde'
#unschedule project 
'python crawtext.py stop new_project'
#delete project
'python crawtext.py delete new_project'
#list project
'python crawtext.py list projects'
#list archives
'python crawtext.py list archives'


action_list = (	1: "create",
				2: "show",
				3: "update",
				4: "run",
				5: "schedule",
				6: "unschedule",
				7: "delete",
				8: "list",
				9: "stop",
				10:"start",
			)
value_list = ( 	1:"name",
				2: "mail",
				3:'url',
				4: 'query',
				5: "sources",
				6: "key",
				7: 'repeat',
			)
		
scope_list = (	1: "project",
				2: "crawl",
				3: "archive",
			)
				
					
