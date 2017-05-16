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
BASE_URL_SUMMARIES = config.get("Waka", "baseUrlDurations")
START_DATE = str(datetime.strptime(config.get("Waka", "startDate"), "%Y-%m-%d").date())

def prepare_request_header(api_key_in_bytes):
    b64_api_key = base64.b64encode(api_key_in_bytes).decode("utf-8")
    headers = {'content-type': 'application/json', 'Authorization': 'Basic ' + b64_api_key}
    return headers

def get_summaries_from_waka(date, header):
    req_url = BASE_URL_SUMMARIES + date + "&end=" +  datetime.now().strftime("%Y-%m-%d")
    response = requests.get(req_url, headers=header)
    return response.json()

#def write_data_to_dataframe(df)
#    response_summaries_json = get_summaries_from_waka(START_DATE, prepare_request_header(str.encode(API_KEY)))

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
