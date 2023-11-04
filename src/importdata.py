#!/usr/bin/env python

from functions import check_internet_connection, write_result_csv
from dotenv import dotenv_values
import requests
import json
import logging

# logging any error or any exception to a log file
logging.basicConfig(filename='../log/redcap_connector.log', encoding='utf-8', format="%(asctime)s - %(message)s\n",
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


def import_records(record):
    # try:
    # load the .env values
    config = dotenv_values("../.env")

    # read the file import_json file
    with open(record) as jf:
        import_record = json.load(jf)

    data = json.dumps(import_record)

    fields = {
        'token': config['API_TOKEN'],
        'content': 'record',
        'action': 'import',
        'format': 'json',
        'type': 'flat',
        'data': data,
        'returnContent': 'count',  # ids
        'returnFormat': 'json'
    }

    # check for internet is available or REDCap server is online(available)
    if check_internet_connection("https://redcap-testing.bibbox.bnitm.de/"):
        # import records into the REDCap database
        r = requests.post(config['API_URL'], data=fields)
        print(f'HTTP Status: {str(r.status_code)}')
        count = r.json()['count']
        print(f"{count} records were imported successfully!!!")
        # write the data to csv file(s)
        write_result_csv(data)
    else:
        # write the data to csv file(s) if there is no internet connection
        write_result_csv(data)

    # when record successful imported write it to csv(import_data_[date&time])
    # or json file(imported_fbc_data.json). use function for both.
    # write_result_csv(data)

# except IOError:
#    print("There's an error importing data.")
# except Exception as error:
#    logging.exception(f"Unexpected Error Occurred: {error: }")


# stop logging
logging.shutdown()

if __name__ == '__main__':
    import_records("../data/import_data.json")
