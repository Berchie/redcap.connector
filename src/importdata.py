#!/usr/bin/ python

from dotenv import dotenv_values
import requests
import json, logging

# logging any error or any exception to a log file
logging.basicConfig(filename='../log/logfile.log', encoding='utf-8', format="%(asctime)s - %(message)s\n",
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


def import_records(record):
    try:
        # load the .env values
        config = dotenv_values("../.env")

        data = json.dumps(record)

        fields = {
            'token': config['API_TOKEN'],
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'data': data
        }

        r = requests.post(config['API_URL'], data=fields)
        print(f'HTTP Status: {str(r.status_code)}')
        print(r.text)

        # when record successful imported write it to csv(import_data_[date&time])
        # or json file(imported_fbc_data.json). use function for both.
    except Exception as error:
        logging.exception(f"Unexpected Error Occurred: {error: }")


# stop logging
logging.shutdown()
