#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wk import Worker
from database import Database, TASK_COLL, TASK_MANAGER_NAME
from datetime import datetime
from threading import Timer
from multiprocessing import Pool
from job import *

def refresh_task(next_run, repeat):
	'''after a run update the last_run and set nb_run how to log msg?'''
	last_run = next_run
	
	if repeat == "week":
		next_run = last_run.replace(day = self.last_run.day+7)
	else:
		last_value = getattr(last_run, repeat)
		
		if repeat == "day":
			next_run = last_run.replace(day=last_value+1)
			
		if repeat == "month":
			next_run = last_run.replace(month=last_value+1)
		elif repeat == "year":
			next_run = last_run.replace(year=last_value+1)
	return last_run, next_run
	
def run_or_die(task):
	today = datetime.today()
	if task["next_run"] is None:
		return False
		
	if task["repeat"] == "hour":
		if task["next_run"].hour == today.hour: 
			return True
		
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
	db = Database(TASK_MANAGER_NAME)
	db.job = db.use_coll(TASK_COLL)
	
	if run_or_die(task) is True:
		class_action = task["action"].capitalize()
		j = class_action(task["name"])
		j.run_job()
		last_run, next_run = refresh_task(task['next_run'], task['repeat'])	
		db.job.update({"_id":task["_id"]}, {"$inc": {"nb_run": 1}})
		if j is False:
			db.job.update({"_id":task["_id"]}, {"$set":{"status":j.status})
			db.job.update({"_id":task["_id"]}, {"$set":{"next_run":None})
		else:
			db.job.update({"_id":task["_id"]}, {"$set":{"last_run":last_run,"next_run":next_run,})
		return True	
	else:
		return False
def scheduler():
	db = Database(TASK_MANAGER_NAME)
	db.job = db.use_coll(TASK_COLL)
	for n in db.job.find():
		print run_task(n)
	#~ tasks = db.job.find()
	#~ pool = Pool(6)
	#~ pool.map(run_task, tasks)	
	#~ pool.close()
	#~ return pool.join()
    
def main():
	#~ x=datetime.today()
	#~ y=x.replace(day=x.day, hour=23, minute=42, second=10, microsecond=0)
	#~ delta_t=y-x
	#~ secs=delta_t.seconds+1
	t = Timer(1, scheduler)
	t.start()
	
if __name__ == "__main__":
	main()

