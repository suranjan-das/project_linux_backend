from application.workers import celery
from datetime import datetime

@celery.task()
def say_hello(name):
	print("INSIDE TASK")
	print("Hello {}".format(name))
	return "Hello {}".format(name)