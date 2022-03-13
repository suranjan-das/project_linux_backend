from application.workers import celery
from datetime import datetime

@celery.task()
def say_hello(name):
	print("INSIDE TASK")
	print("Hello {}".format(name))
	return "Hello {}".format(name)

@celery.task()
def show_curr_time():
	print("START")
	now = datetime.now()
	print("now =", now)
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	print("date and time =", dt_string)
	return dt_string