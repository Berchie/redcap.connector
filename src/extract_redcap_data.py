##!/usr/bin/env python

from dotenv import dotenv_values
import requests
import json
import logging

# logging any error or any exception to a log file
logging.basicConfig(filename='../log/redcap_connector.log', encoding='utf-8', format="%(asctime)s - %(message)s\n",
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


def redcap_event(event):
    try:
        # load the .env values
        config = dotenv_values("../.env")

        data = {
            'token': config['API_TOKEN'],
            'content': 'event',
            'format': 'json',
            'arms[0]': '2',  # change the key:value ('arms':'') to pull all events in the database
            'returnFormat': 'json'
        }
        r = requests.post(config['API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(json.dumps(r.json(), indent=2))

        events = json.loads(json.dumps(r.json()))

        for x in events:
            if x["event_name"] == event:
                event_name = x['unique_event_name']
                # print(f'redcap_event_name: {event_name}')
                return event_name

    except Exception as error:
        logging.exception(f"Unexpected Error Occurred: {error: }")


def redcap_mbc_record_id(studyID):
    try:
        # load the .env values
        config = dotenv_values("../.env")

        data = {
            'token': config['API_TOKEN'],
            'content': 'record',
            'action': 'export',
            'format': 'json',
            'type': 'flat',
            'csvDelimiter': '',
            'records': studyID,
            'fields': '',
            'forms': '',
            'events': '',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json',
            # 'filterLogic': 'ch_subbarcode = M19-20213-T0'
        }
        r = requests.post(config['API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(json.dumps(r.json(), indent=2))

        return r.json()[0]['m_subbarcode']

    except Exception as error:
        logging.exception(f"Unexpected Error Occurred: {error: }")


# stop logging
logging.shutdown()
