import json
import csv
import os
import socket

import requests
from dotenv import dotenv_values
from urllib.request import urlopen as url
from urllib.error import *
#from src.functions import read_json


conf = dotenv_values(".env")

# Opening JSON file
f = open("config/redcap_variables.json", "r")
# returns JSON object as a dictionary
data_json = json.loads(f.read())
print(data_json["M19_FBC_FV"]['WBC'])
# closing file
f.close()

data = {
    'token': '74C2BA424ADDED80148990A8946E53BA',
    'content': 'event',
    'format': 'json',
    'arms[0]': '2',
    'returnFormat': 'json'
}
r = requests.post('https://redcap-testing.bibbox.bnitm.de/api/', data=data)
print('HTTP Status: ' + str(r.status_code))
print(json.dumps(r.json(), indent=2))
events = json.loads(json.dumps(r.json()))
for x in events:
    if x["event_name"] == 'T7':
        event_name = x['unique_event_name']
        print(f'redcap_event_name: {event_name}')

print(f'redcap_event_name: {event_name}')

data_e = {
    'token': '74C2BA424ADDED80148990A8946E53BA',
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'records[0]': 'M19-20213-T0--1',
    'fields': '',
    'forms': '',
    'events': '',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}
r = requests.post('https://redcap-testing.bibbox.bnitm.de/api/', data=data_e)
print('HTTP Status: ' + str(r.status_code))
# print(json.dumps(r.json(),indent=2))

# check if
try:
    redcap_server = url('https://redcap-testing.bibbox.bnitm.de')

except HTTPError as e:
    print("HTTP error", e)
except URLError as e:
    print("Opps! REDCap server not found!", e)
else:
    print("Yeah! REDCap server is online")

try:
    respond = requests.head('https://redcap-testing.bibbox.bnitm.de')
    if respond.status_code == 200:
        print("Yeah! REDCap server is online")
    else:
        print("Opps! REDCap server not found!")
except requests.ConnectionError as e:
    print(e)

# check for internet connection
try:
    pass
    # connect to a URL
    url("https://www.google.com/", timeout=5)
    print('SUCCESS: Internet connection is available')
except ConnectionError as error:
    print("FAIL: Internet connection is not available")

# write dict to csv
csv_columns = ['No', 'Name', 'Country']
dict_data = [
    {'No': 1, 'Name': 'Kelvin', 'Country': 'USA'},
    {'No': 2, 'Name': 'Kwame', 'Country': 'Ghana'},
    {'No': 3, 'Name': 'Wibke', 'Country': 'Germany'},
    {'No': 4, 'Name': 'Smith', 'Country': 'UK'},
    {'No': 5, 'Name': 'Berchie', 'Country': 'Ghana'}
]
csv_file = "names.csv"

try:
    with open(csv_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        # writer.writeheader()

        for i in dict_data:
            writer.writerow(i)
except IOError:
    print("I/O error")


def check_internet_connection():
    remote_server = "www.google.com"
    port = 80
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((remote_server, port))
        return True
    except socket.error:
        return False
    finally:
        sock.close()


data = [
    {'No': 1, 'Name': 'Kelvin', 'Country': 'USA'},
    {'No': 2, 'Name': 'Kwame', 'Country': 'Ghana'},
    {'No': 3, 'Name': 'Wibke', 'Country': 'Germany'},
    {'No': 4, 'Name': 'Smith', 'Country': 'UK'},
    {'No': 5, 'Name': 'Berchie', 'Country': 'Ghana'}
]
print(data[0].keys())

print(os.getcwd())
