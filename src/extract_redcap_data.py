##!/usr/bin/env python

from dotenv import dotenv_values
import requests
import json
import logging.config
import yaml

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open('../config_log.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def redcap_event(event):
    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        data = {
            'token': env_config['API_TOKEN'],
            'content': 'event',
            'format': 'json',
            'arms': '',  # change the key:value ('arms':'') to pull all events in the database (arms[0]:'2')
            'returnFormat': 'json'
        }
        r = requests.post(env_config['API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(json.dumps(r.json(), indent=2))

        events = json.loads(json.dumps(r.json()))

        for x in events:
            if x["event_name"] == event:
                event_name = x['unique_event_name']
                # print(f'redcap_event_name: {event_name}')
                return event_name
    except ConnectionError as cr:
        logger.error("Connection Error to REDCap database. Check your internet connection", exc_info=True)
    except Exception as e:
        logger.error("Exception Occurred", exc_info=True)


def redcap_mbc_record_id(studyID):
    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        data = {
            'token': env_config['API_TOKEN'],
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
        r = requests.post(env_config['API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(json.dumps(r.json(), indent=2))

        return r.json()[0]['m_subbarcode']

    except ConnectionError as cr:
        print("Connection Error to REDCap database. Check your internet connection")
        logging.debug(f"Connection Error to REDCap database. Check your internet connection: {cr}", exc_info=True)
    except Exception as error:
        logging.error(f"Connection Error Occurred", exc_info=True)


# stop logging
logging.shutdown()

if __name__ == '__main__':
    redcap_event("T6")
    redcap_mbc_record_id("M19-20001-T0")
