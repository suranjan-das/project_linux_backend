from application.jobs.workers import celery
from datetime import datetime
from celery.schedules import crontab
import csv
import time
from application.data.database import db
from application.data.models import *

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(10.0, show_curr_time.s(), name='add every 10 seconds')
    sender.add_periodic_task(10.0, get_user_last_reviewed_time.s(), name='add every 10 seconds')

@celery.task()
def get_user_last_reviewed_time():
    now = datetime.now()
    users = User.query.all()
    for user in users:
        user_decks = user.decks
        for deck in user_decks:
            date_reviewed = deck.time_created
            delta = now - date_reviewed
            days_last_reviewed = delta.days
    return "Hello"

@celery.task()
def show_curr_time():
	print("START")
	now = datetime.now()
	print("now =", now)
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	print("date and time =", dt_string)
	return dt_string

@celery.task
def export_data_to_csv(data):
    print("starting exporting job")
    # name of csv file 
    filename = "application/mydata.csv"
    # writing to csv file 
    with open(filename, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile)

        # writing the fields 
        # csvwriter.writerow(["d_id", "deck_name", "deck_info", "time_created", "score"])
            
        # writing the data rows
        for i in range(len(data[0])):
            csvwriter.writerow(["d_id", "deck_name", "deck_info", "time_created", "score"])
            id, name, info, time_stamp, score = data[0][i]["d_id"], data[0][i]["deck_name"], data[0][i]["deck_info"], data[0][i]["time_created"], data[0][i]["score"]
            csvwriter.writerow([id, name, info, time_stamp, score])
            csvwriter.writerow(["c_id", "front", "back", "score"])
            for j in range(len(data[1][i])):
                c_id, c_front, c_back, c_score = data[1][i][j]["c_id"], data[1][i][j]["front"], data[1][i][j]["back"], data[1][i][j]["score"]
                csvwriter.writerow([c_id, c_front, c_back, c_score])
    print("exporting completed successfully")
    return "all done"