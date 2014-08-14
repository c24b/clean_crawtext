class Task(object):
	def __init__(self,data=data, type):
		'''creating a defaut job conforme à son type'''
	def udpate():
		pass
	@property
	def next_run(repeat, start_date):	
		start_job = start_date
		if repeat == "day":
			return start_job.replace(day=start_job.day+1)
		elif repeat == "week":			
			return start_job.replace(day=start_job.day+7)
			
		elif repeat == "month":
			
			return start_job.replace(month=start_job.month+1)
			
		elif repeat == "year":
			return start_job.replace(year=start_job.year+1)
		else:
			return start_job
	@propery	
		def last_run()
			'''udpate run date'''
			pass
	def run():
		#static Factory
		task.run()
		pass
