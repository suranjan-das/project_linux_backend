from application.jobs.workers import celery
from datetime import datetime
import csv
import time

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