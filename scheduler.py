import daemon # install python-daemon from pypi

import sys
import sched
import time
from datetime import datetime as dt
import datetime
from worker import Worker
from job import *
from database import Database

def run_crawtext():
	w = Worker()
	for task in w.collection.find():
		
		job = w.create_from_database(task)
		print job["repeat"]
		
	#~ db = Database(TASK_MANAGER_NAME)
	#~ collection = db.use_coll(TASK_COLL)
	#~ project_list = db.collection.find({"action":{"$or":["crawl", "archives"]})
	#~ for n in project_list:
		#~ print n
	return 
	#~ for n in project_list:
		#~ j = Job(n)
		#~ j2 = j.create_from_database()
		#~ #try:
		#~ print j2.		
		#~ return j2.run()
	#~ print "Running"
	#~ w = Worker()
	#~ return w.run_job()
	
	
def now_str():
    """Return hh:mm:ss string representation of the current time."""
    t = dt.now().time()
    return t.strftime("%H:%M:%S")


def main():
	def do_something_again(message):
		print 'RUNNING:', now_str(), message
		# Do whatever you need to do here
		run_crawtext()
		# then re-register task for same time tomorrow
		t = dt.combine(dt.now() + datetime.timedelta(days=1), daily_time)
		scheduler.enterabs(time.mktime(t.timetuple()), 1, do_something_again, ('Running again',))

	# Build a scheduler object that will look at absolute times
	scheduler = sched.scheduler(time.time, time.sleep)
	print 'START:', now_str()
	# Put task for today at 7am on queue. Executes immediately if past 7am
	now = dt.now()
	next_day = now
	day =  now.day
	next_day = now.replace(day=day+7)

	daily_time = datetime.time(next_day)
	first_time = dt.combine(now, daily_time)
	# time, priority, callable, *args
	scheduler.enterabs(time.mktime(first_time.timetuple()), 1,
					   do_something_again, ('Run the first time',))
	scheduler.run()

if __name__ == '__main__':
    main()
    #if "-f" in sys.argv:
    #    main()
    #else:
    #    with daemon.DaemonContext():
    #        main()
