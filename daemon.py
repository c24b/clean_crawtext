import threading
from database import *
#http://code.activestate.com/recipes/65222-run-a-task-every-few-seconds/
class TaskThread(threading.Thread):
    """Thread that executes a task every N seconds"""
    
    def __init__(self):
		threading.Thread.__init__(self)
		self._finished = threading.Event()
		self._interval = 15.0
		db = Database(TASK_MANAGER_NAME)
		db.jobs = db.use_coll(TASK_COLL)
		self.tasks = db.jobs.find()
    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval
    
    def shutdown(self):
        """Stop this thread"""
        self._finished.set()
    
    def run(self):
        while 1:
            if self._finished.isSet(): return
            self.task()
            
            # sleep for interval or until shutdown
            self._finished.wait(self._interval)
    
    def task(self):
		print "run"
        
        

class printTaskThread(TaskThread):
        def task(self):
			for n in self.tasks:
				print n
            
if __name__ == '__main__':
	tt = printTaskThread()
	tt.setInterval(3)
	print 'starting'
	tt.start()
	print 'started, wait now'
	import time
	time.sleep(7)
	print 'killing the thread'
	tt.shutdown()
	print 'killed and done'
