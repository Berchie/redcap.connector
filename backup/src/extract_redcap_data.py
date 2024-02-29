import os
from dotenv import dotenv_values
import requests
import json
import logging.config
import yaml

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open(f'{os.path.abspath(os.curdir)}/config_log.yaml', 'r') as f:
#with open('../config_log.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def redcap_event(event, project_id):
    api_token = None
    try:
        # load the .env values
        env_config = dotenv_values(f"{os.path.abspath(os.curdir)}/.env")

        if project_id == 'M19':
            api_token = env_config['M19_API_TOKEN']
        elif project_id == 'P21':
            api_token = env_config['P21_API_TOKEN']

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
        logger.error(f"Exception Occurred: {e}")


def redcap_mbc_record_id(studyID):
    try:
        # load the .env values
        env_config = dotenv_values(f"{os.path.abspath(os.curdir)}/.env")

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
        logging.debug(f"Connection Error to REDCap database. Check your internet connection: {cr}")
    except Exception as error:
        logging.error(f"Connection Error Occurred: {error}")


def getEvents():
    try:
        # load the .env values
        env_config = dotenv_values(f"{os.path.abspath(os.curdir)}/.env")

        # env_config = dotenv_values("../.env")

        api_token = env_config['LAB_API_TOKEN']

        data = {
            'token': api_token,
            'content': 'event',
            'format': 'json',
            'arms': '',  # change the key:value ('arms':'') to pull all events in the database (arms[0]:'2')
            'returnFormat': 'json'
        }
        r = requests.post(env_config['LAB_API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(json.dumps(r.json(), indent=2))

        events = json.loads(json.dumps(r.json()))

        return events

    except ConnectionError as cr:
        logger.error(f"Connection Error to REDCap database. Check your internet connection: {cr}")
    except Exception as e:
        logger.error(f"Exception Occurred: {e}")


def getRedcapArms():
    try:
        # load the .env values
        env_config = dotenv_values(f"{os.path.abspath(os.curdir)}/.env")

        # env_config = dotenv_values("../.env")

        api_token = env_config['LAB_API_TOKEN']

        data = {
            'token': api_token,
            'content': 'arm',
            'format': 'json',
            'returnFormat': 'json'
        }
        r = requests.post(env_config['LAB_API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(json.dumps(r.json(), indent=2))

        arms = json.loads(json.dumps(r.json()))

        return arms

    except ConnectionError as cr:
        logger.error(f"Connection Error to REDCap database. Check your internet connection: {cr}")
    except Exception as e:
        logger.error(f"Exception Occurred: {e}")


# stop logging
logging.shutdown()

if __name__ == '__main__':
    # redcap_event("T6", 'M19')
    # redcap_mbc_record_id("M19-20001-T0")
    data1 = getEvents()
    data2 = getRedcapArms()

    print(json.dumps(data1, indent=4))
    print(data2)
