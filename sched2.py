#!/usr/bin/env python
# -*- coding: utf-8 -*-
from worker import Worker
from database import Database, TASK_COLL, TASK_MANAGER_NAME
from datetime import datetime

def run_or_die(task):
	today = datetime.today()
	
	if task["repeat"] == "day" or task["repeat"] == "week":
		if task["next_run"].day == today.day:
			return True
		return False
	elif task["repeat"] == "month":
		if task["next_run"].month == today.month and task["next_run"].day == today.day:
			return True
		return False
	elif task["repeat"] == "year":
		if task["next_run"].year == today.year and task["next_run"].month == today.month and task["next_run"].day == today.day:
			return True
		return False
	else:
		return False		

def scheduler():
	db = Database(TASK_MANAGER_NAME)
	db.jobs = db.use_coll(TASK_COLL)
	for task in db.jobs.find():
		print run_or_die(task)
		
if __name__ == "__main__":
	scheduler()
