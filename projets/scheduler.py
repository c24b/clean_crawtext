#!/usr/bin/env python
# -*- coding: utf-8 -*-
from worker import Worker
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
		if task["next_run"].day == today.day: return True
		return True
	elif task["repeat"] == "month":
		if task["next_run"].month == today.month and task["next_run"].day == today.day: 
			return True
		return False
	elif task["repeat"] == "year":
		if task["next_run"].year == today.year and task["next_run"].month == today.month and task["next_run"].day == today.day: return True
		return False
	else:
		return False		

def run_task(task):
	if run_or_die(task) is True:
		t = Job()
		status = t.run(task)
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
	x=datetime.today()
	y=x.replace(day=x.day, hour=x.hour, minute=x.minute+2, second=00, microsecond=0)
	delta_t=y-x
	secs=delta_t.seconds+1
	t = Timer(secs, scheduler)
	t.start()
	
if __name__ == "__main__":
	main()
