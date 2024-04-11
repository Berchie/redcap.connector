import os
import sys
from dotenv import dotenv_values, load_dotenv
import requests
import json
from loguru import logger
from redcapconnector.config.log_config import handlers

# setting up the logging
logger.configure(
    handlers=handlers,
)

# load .env variables
dotenv_path = os.path.abspath(f"{os.environ['HOME']}/.env")
if os.path.abspath(f"{os.environ['HOME']}/.env"):
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise logger.exception('Could not found the application environment variables!')


def redcap_event(event, project_id):
    api_token = None
    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        if project_id == 'M19':
            api_token = os.environ['M19_API_TOKEN']
        elif project_id == 'P21':
            api_token = os.environ['P21_API_TOKEN']

        data = {
            'token': api_token,
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
        logger.error(f"Connection Error to REDCap database. Check your internet connection: {cr}")
    except Exception as e:
        logger.exception(f"Exception Occurred: {e}")


def redcap_mbc_record_id(study_id):
    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        data = {
            'token': os.environ['API_TOKEN'],
            'content': 'record',
            'action': 'export',
            'format': 'json',
            'type': 'flat',
            'csvDelimiter': '',
            'records': study_id,
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
        logger.debug(f"Connection Error to REDCap database. Check your internet connection: {cr}")
    except Exception as error:
        logger.exception(f"Connection Error Occurred: {error}")


def get_events():
    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        # env_config = dotenv_values("../.env")

        api_token = os.environ['LAB_API_TOKEN']

        data = {
            'token': api_token,
            'content': 'event',
            'format': 'json',
            'arms': '',  # change the key:value ('arms':'') to pull all events in the database (arms[0]:'2')
            'returnFormat': 'json'
        }
        r = requests.post(os.environ['LAB_API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(json.dumps(r.json(), indent=2))

        events = json.loads(json.dumps(r.json()))

        return events

    except ConnectionError as cr:
        logger.error(f"Connection Error to REDCap database. Check your internet connection: {cr}")
    except Exception as e:
        logger.exception(f"Exception Occurred: {e}")


def get_redcap_arms():
    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        # env_config = dotenv_values("../.env")

        api_token = os.environ['LAB_API_TOKEN']

        data = {
            'token': api_token,
            'content': 'arm',
            'format': 'json',
            'returnFormat': 'json'
        }
        r = requests.post(os.environ['LAB_API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(json.dumps(r.json(), indent=2))

        arms = json.loads(json.dumps(r.json()))

        return arms

    except ConnectionError as cr:
        logger.error(f"Connection Error to REDCap database. Check your internet connection: {cr}")
    except Exception as e:
        logger.exception(f"Exception Occurred: {e}")


if __name__ == '__main__':
    # redcap_event("T6", 'M19')
    # redcap_mbc_record_id("M19-20001-T0")
    data1 = get_events()
    data2 = get_redcap_arms()

    print(json.dumps(data1, indent=4))
    print(data2)
