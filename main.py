import json
import requests
from dotenv import dotenv_values

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
r = requests.post('https://redcap-testing.bibbox.bnitm.de/api/',data=data_e)
print('HTTP Status: ' + str(r.status_code))
#print(json.dumps(r.json(),indent=2))


