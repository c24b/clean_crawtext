from scheduler4 import Scheduler

if __name__ == "__main__":
	s = Scheduler()
	for n in s.get_list():
		
		try:
			#print n['name'], n['action']
			s.run_job()
		except Exception:
			continue
		#~ if n["action"] == "crawl":
			#~ s.run_job(n)
	
	
		
	
	
	
	
