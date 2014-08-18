#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wk import Worker
from database import Database, TASK_COLL, TASK_MANAGER_NAME
from datetime import datetime
from threading import Timer
from multiprocessing import Pool
from job import Job

def run_or_die(task):
	today = datetime.today()
	print today.second
	if task["repeat"] == "hour":
		if task["next_run"].hour == today.hour: return True
		
	elif task["repeat"] == "day" or task["repeat"] == "week":
		if task["next_run"].day == today.day: 
			return True
	elif task["repeat"] == "month":
		if task["next_run"].month == today.month and task["next_run"].day == today.day: 
			return True
	elif task["repeat"] == "year":
		if task["next_run"].year == today.year and task["next_run"].month == today.month and task["next_run"].day == today.day: 
			return True
		
	else:
		return False		

def run_task(task):
	print task
	if run_or_die(task) is True:
		
		db.job.update(task["_id"], {"$set":{"last_run_at":datetime.today(), "exec_time": t.elapsed, "status": status, "msg": t.logs}, "$inc": {"nb_run": 1}})
		
		return True	
	else:
		return False
def scheduler():
	db = Database(TASK_MANAGER_NAME)
	db.jobs = db.use_coll(TASK_COLL)
	tasks = db.jobs.find()
	pool = Pool(6)
	pool.map(run_task, tasks)	
	pool.close()
	return pool.join()
    
def main():
	#~ x=datetime.today()
	#~ y=x.replace(day=x.day, hour=23, minute=42, second=10, microsecond=0)
	#~ delta_t=y-x
	#~ secs=delta_t.seconds+1
	t = Timer(1, scheduler)
	t.start()
	
if __name__ == "__main__":
	main()
