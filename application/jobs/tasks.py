from application.jobs.workers import celery
from datetime import datetime
from celery.schedules import crontab
import csv
import time
from application.data.database import db
from application.data.models import *
import requests
import json
from application.utils import email_util

GCHAT_WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAAAF_kfYyI/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=3CepxdOylc6dAUO_MOCF1RN38fjMoOnxgcwThXqwj68%3D"

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(1060.0, get_user_last_reviewed_time.s(), name='notify in gchat')
    pass

@celery.on_after_finalize.connect
def setup_email_report_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute="*"), send_mail_to_user.s(), name='report in email')

@celery.task
def send_mail_to_user():
    print("sending mail to users")
    users = User.query.all()
    user_group = []
    if users:
        user_deck_data = []
        for user in users:
            user_deck_data = prepare_user_monthly_report(user.email)
            user_group.append({"name":user.username, "email":user.email, "decks": user_deck_data})
    if user_group:
        for usg in user_group:
            email_util.send_welcome_message(data=usg)

@celery.task()
def get_user_last_reviewed_time(email):
    now = datetime.now()
    users = User.query.all()
    for user in users:
        user_decks = user.decks
        for deck in user_decks:
            date_reviewed = deck.time_created
            delta = now - date_reviewed
            days_last_reviewed = delta.days
            if days_last_reviewed >= 1:
                # send gchat reminder
                send_gchat_reminder(GCHAT_WEBHOOK_URL, "You have not reviewed anything in the last day!!")
    return "reminder sent to user successfully"

def prepare_user_monthly_report(email):
    now = datetime.now()
    user = User.query.filter(User.email == email).first()
    deck_data = []
    if user:
        user_decks = user.decks
        if user_decks:
            for deck in user_decks:
                date_reviewed = deck.time_created
                delta = now - date_reviewed
                days_last_reviewed = delta.days
                if delta.days <= 31:
                    deck_data.append({"deck_name": deck.deck_name, "deck_info": deck.deck_info,
                        "time_viewed": deck.time_created.strftime("%m/%d/%Y"), "score": deck.score})
    return deck_data


def send_gchat_reminder(url, message):
    try:
        print(message)
        requests.post(url, data=json.dumps({"text" : message}))
    except Exception as e:
        return "something went wrong"

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