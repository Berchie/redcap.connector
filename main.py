import datetime
import getpass
import pathlib
import time
import json
import csv
import os
import socket

import requests
from dotenv import dotenv_values
from urllib.request import urlopen as url
from urllib.error import *
import configparser
import pandas as pd
import re

# from src.functions import read_json


# conf = dotenv_values(".env")
#
# # Opening JSON file
# f = open("config/redcap_variables.json", "r")
# # returns JSON object as a dictionary
# data_json = json.loads(f.read())
# print(data_json["M19_FBC_FV"]['WBC'])
# # closing file
# f.close()
#
# data = {
#     'token': '74C2BA424ADDED80148990A8946E53BA',
#     'content': 'event',
#     'format': 'json',
#     'arms[0]': '2',
#     'returnFormat': 'json'
# }
# r = requests.post('https://redcap-testing.bibbox.bnitm.de/api/', data=data)
# print('HTTP Status: ' + str(r.status_code))
# print(json.dumps(r.json(), indent=2))
# events = json.loads(json.dumps(r.json()))
# for x in events:
#     if x["event_name"] == 'T7':
#         event_name = x['unique_event_name']
#         print(f'redcap_event_name: {event_name}')
#
# print(f'redcap_event_name: {event_name}')
#
# data_e = {
#     'token': '74C2BA424ADDED80148990A8946E53BA',
#     'content': 'record',
#     'action': 'export',
#     'format': 'json',
#     'type': 'flat',
#     'csvDelimiter': '',
#     'records[0]': 'M19-20213-T0--1',
#     'fields': '',
#     'forms': '',
#     'events': '',
#     'rawOrLabel': 'raw',
#     'rawOrLabelHeaders': 'raw',
#     'exportCheckboxLabel': 'false',
#     'exportSurveyFields': 'false',
#     'exportDataAccessGroups': 'false',
#     'returnFormat': 'json'
# }
# r = requests.post('https://redcap-testing.bibbox.bnitm.de/api/', data=data_e)
# print('HTTP Status: ' + str(r.status_code))
# # print(json.dumps(r.json(),indent=2))
#
# # check if
# try:
#     redcap_server = url('https://redcap-testing.bibbox.bnitm.de')
#
# except HTTPError as e:
#     print("HTTP error", e)
# except URLError as e:
#     print("Opps! REDCap server not found!", e)
# else:
#     print("Yeah! REDCap server is online")
#
# try:
#     respond = requests.head('https://redcap-testing.bibbox.bnitm.de')
#     if respond.status_code == 200:
#         print("Yeah! REDCap server is online")
#     else:
#         print("Opps! REDCap server not found!")
# except requests.ConnectionError as e:
#     print(e)
#
# # check for internet connection
# try:
#     pass
#     # connect to a URL
#     url("https://www.google.com/", timeout=5)
#     print('SUCCESS: Internet connection is available')
# except ConnectionError as error:
#     print("FAIL: Internet connection is not available")
#
# try:
#     with open(csv_file, 'a', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
#         # writer.writeheader()
#
#         for i in dict_data:
#             writer.writerow(i)
# except IOError:
#     print("I/O error")


config = configparser.ConfigParser()
config.read("config/db_config.conf")
config.sections()
# with open("config/db_config.conf", "r") as file:
#     db_api_token = file.read()

print(config['API_TOKENS']['P21'])

# obj = pd.read_json('data/import_data.json', orient='records', precise_float=True)
obj = pd.read_csv('data/20231220_mbc_t6_t12_lab_result.csv')
print(obj)

if os.path.exists('importdata.csv') and os.path.getsize('importdata.csv') > 0:
    obj.to_csv('importdata.csv', index=False, header=False, mode='a')
else:
    obj.to_csv('importdata.csv', index=False)

# successfulCount = 0
# noImportCount = 0
# with open('log/redcap_connector.log') as log_file:
#     statement = log_file.readlines()
#     print(statement)
#     # todayDate = datetime.date.today().strftime('%d-%m-%Y')
#     todayDate = datetime.date(2023, 12, 14).strftime('%d-%m-%Y')
#     for line in statement:
#         line_split = line.split()
#         if line_split[0] == todayDate and 'INFO:' in line_split:
#             print(line)
#
#             if line_split[4].isnumeric() and int(line_split[4]) > 0 and 'record(s) were imported successfully!!!' in line:
#                 successfulCount += 1
#             elif line_split[4].isalpha() and 'No data to import' in line:
#                 noImportCount += 1
#
#         elif line_split[0] == todayDate and 'ERROR:' in line_split:
#             print('other log messages')
#             print('__________________________')
#             print(line)
#
# print(f'Importation of records into REDCap database was successfully done {successfulCount} time(s)')
# print(f'No importation happened {noImportCount} time(s)')
# print(datetime.date.today().strftime('%d-%m-%Y'))

# send text message or email to lims admin or system alert to the admin
if os.path.exists('importdata.csv'):
    print('File exist')

print(os.getlogin())
print(getpass.getuser())
print(os.uname())
print(os.path.exists('importdata.csv'))
print(os.path.getmtime('importdata.csv'))
print(datetime.date.fromtimestamp(os.path.getctime('importdata.csv')))
for (root, dirs, file) in os.walk('./data', topdown=True):
    print(root)
    print(dirs)
    for f in file:
        print(f'{root}/{f}')
    print('-------------------------------')
print(datetime.date.today() - datetime.timedelta(days=15))

statement = 'No M19 lab records was found!'
print(re.findall('No|lab|records|was|found', statement, flags=re.IGNORECASE))
