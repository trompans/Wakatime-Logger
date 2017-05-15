import requests
import base64
from datetime import timedelta, date, datetime
import pandas as pd
import os
import configparser

config = configparser.ConfigParser()
config.read('my_config.ini')

FILE_NAME = config.get("Waka", "fileName")
API_KEY = config.get("Waka", "apiKey")
BASE_URL_DURATIONS = config.get("Waka", "baseUrlDurations")
BASE_URL_HEARTBEATS = config.get("Waka", "baseUrlHeartbeats")
POST_HEARTBEAT_URL = config.get("Waka", "postHeartbeatUrl")
START_DATE = str(datetime.strptime(config.get("Waka", "startDate"), "%Y-%m-%d").date())


def prepare_request_header(api_key_in_bytes):
    b64_api_key = base64.b64encode(api_key_in_bytes).decode("utf-8")
    headers = {'content-type': 'application/json', 'Authorization': 'Basic ' + b64_api_key}
    return headers


def get_durations_from_waka(date, header):
    req_url = BASE_URL_DURATIONS + date.strftime("%Y-%m-%d")
    response = requests.get(req_url, headers=header)
    return response.json()

# Edit By Trompans :P ###########

def get_heartbeats_from_waka(date, header):
    req_url = BASE_URL_HEARTBEATS + date.strftime("%Y-%m-%d") + POST_HEARTBEAT_URL
    response = requests.get(req_url, headers=header)
    return response.json()

# Edit By Trompans :P ###########

def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def write_data_to_dataframe(df, start_date, end_date):
    last_df_index = len(df)
    if last_df_index > 0:
        start_date_str = df["date"].values[last_df_index - 1]
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        start_date = start_date + timedelta(days=1)
    for d in date_range(start_date, end_date):
        response_duration_json = get_durations_from_waka(d, prepare_request_header(str.encode(API_KEY)))
        response_heartbeat_json = get_heartbeats_from_waka(d, prepare_request_header(str.encode(API_KEY)))
        try:
            dataDuration = response_duration_json["data"]
            #data += response_heartbeat_json["data"]
            #dataHeartbeat = response_heartbeat_json["data"]
            data_dict = {}
            for duration_data in dataDuration:
                project_name = duration_data["project"]
                duration = duration_data["duration"]
                time = duration_data["time"]               
                try:
                    data_dict[project_name] += duration
                    data_dict[project_name] += time
                except KeyError:
                    data_dict[project_name] = duration
                    data_dict[project_name] = time                    
            for k, v in data_dict.items():
                new_row = [d.strftime("%Y-%m-%d"), k, v]
                df.loc[last_df_index] = new_row
                last_df_index += 1
            # Edit By Trompans :P ###########
#            for heartbeat_data in dataHeartbeat:
#                project_name = heartbeat_data["project"]
#                heartbeat = heartbeat_data["heartbeat"]
#                language = language_data["language"]
#                try:
#                    data_dict[project_name] += duration
#                except KeyError:
#                    data_dict[project_name] = duration
#            for k, v in data_dict.items():
#                new_row = [d.strftime("%Y-%m-%d"), k, v]
#                df.loc[last_df_index] = new_row
#                last_df_index += 1
            # Edit By Trompans :P ###########
        except KeyError as keyError:
            print("[*] ERROR: for {0}, key error: {1}".format(d.strftime("%Y-%m-%d"), keyError))
            print("This means that you can't see this day's records because you've exceeded the free Waka limit")
            print("Run this script at least once in a week to get all the records!")

        print("Durations saved for: {0}".format(d.strftime("%Y-%m-%d")))


def run_the_program():
    if not os.path.exists(FILE_NAME):
        print("It looks like this is the first time you run this script!")
        print("This is the start date: {0}".format(START_DATE))
        start_date = datetime.strptime(START_DATE, "%Y-%m-%d").date()
        df = pd.DataFrame(columns=["date", "project", "duration", "time"])
        write_data_to_dataframe(df, start_date, date.today())
        df.to_csv(FILE_NAME)
    else:
        df = pd.DataFrame.from_csv(FILE_NAME, header=0)
        # Here we don't need start_date because it is calculated from previous entries
        write_data_to_dataframe(df, START_DATE, date.today())
        df.to_csv(FILE_NAME)

    print("Data collection stopped!")

run_the_program()

