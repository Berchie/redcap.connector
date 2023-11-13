#!/usr/bin/env python

from functions import check_internet_connection, write_result_csv
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


def import_records(record):
    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        # read the file import_json file
        with open(record) as jf:
            import_record = json.load(jf)

        data = json.dumps(import_record)

        fields = {
            'token': env_config['API_TOKEN'],
            'content': 'record',
            'action': 'import',
            'format': 'json',
            'type': 'flat',
            'data': data,
            'returnContent': 'count',  # count #ids
            'returnFormat': 'json'
        }

        # check for internet is available or REDCap server is online(available)
        if check_internet_connection("https://redcap-testing.bibbox.bnitm.de/"):
            # import records into the REDCap database
            r = requests.post(env_config['API_URL'], data=fields)
            print(f'HTTP Status: {str(r.status_code)}')
            count = r.json()
            logging.info(f"{count.get('count', 0)} record(s) were imported successfully!!!")
            # logging.info(f"{len(count)} record(s) were imported successfully!!!")
            # write the data to csv file(s)
            write_result_csv(data)
        else:
            # write the data to csv file(s) if there is no internet connection
            write_result_csv(data)

        # when record successful imported write it to csv(import_data_[date&time])
        # or json file(imported_fbc_data.json). use function for both.
        # write_result_csv(data)

    except IOError as ioerror:
        logger.error(f"There's an error importing data. {ioerror}", exc_info=True)
    except Exception as error:
        logging.exception(f"Exception Occurred. {error}", exc_info=True)


# stop logging
logging.shutdown()

if __name__ == '__main__':
    import_records("../data/import_data.json")
