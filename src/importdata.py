import os
import re
import sys
from pathlib import Path
from time import localtime, strftime
from src.functions import check_internet_connection, write_result_csv
from dotenv import dotenv_values
import requests
import json
import logging.config
import yaml
import csv
from src.sendemail import email_notification


# add the path of the new different folder (the folder from where we want to import the modules)
sys.path.insert(0, './src')

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open(f'{os.path.abspath(".")}/config_log.yaml', 'r') as f:
    yaml_config = yaml.safe_load(f.read())
    logging.config.dictConfig(yaml_config)

logger = logging.getLogger(__name__)


# writing the imported results to CSV file
def result_csv():
    csv_file = f'{os.path.abspath(".")}/data/csv/haematology.csv'

    # open or read the json file
    with open(f'{os.path.abspath(".")}/data/import_data.json') as json_file:
        json_results = json.load(json_file)

    # open the csv file
    if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
        data_file = open(csv_file, 'a', newline='')
    else:
        data_file = open(csv_file, 'w', newline='')

    # create the csv writer object
    csv_writer = csv.writer(data_file)

    # Counter variable used for writing
    # headers to the CSV file
    # if the CSV file exist and not empty set the counter to 1 to write the rows
    if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
        counter = 1
    else:
        counter = 0

    for result in json_results:

        if counter == 0:
            # Writing headers of CSV file
            header = result.keys()
            csv_writer.writerow(header)
            counter += 1

        # writing data of the CSV file
        csv_writer.writerow(result.values())


# convert json data to CSV file for the daily run
def json_csv():
    csv_file = f'{os.path.abspath(".")}/data/daily_result/{strftime("%Y%m%d", localtime())}_haematology.csv'

    # open or read the json file
    with open(f'{os.path.abspath(".")}/data/import_data.json') as json_file:
        json_results = json.load(json_file)

    # open the csv file
    if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
        data_file = open(csv_file, 'a', newline='')
    else:
        data_file = open(csv_file, 'w', newline='')

    # create the csv writer object
    csv_writer = csv.writer(data_file)

    # Counter variable used for writing
    # headers to the CSV file
    # if the CSV file exist and not empty set the counter to 1 to write the rows
    if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
        counter = 1
    else:
        counter = 0

    for result in json_results:

        if counter == 0:
            # Writing headers of CSV file
            header = result.keys()
            csv_writer.writerow(header)
            counter += 1

        # writing data of the CSV file
        csv_writer.writerow(result.values())


def data_import(project_id):

    # m19_csv_file = 'import_m19_data.csv'
    # p21_csv_file = 'import_p21_data.csv'
    # record = f'{os.path.abspath("..")}/data/import_data.json'
    record = './data/import_data.json'

    try:
        # load the .env values
        env_config = dotenv_values(f"{os.path.abspath('.')}/.env")

        # read the file import_json file
        if os.path.getsize(record) != 0:
            with open(record) as jf:
                import_record = json.load(jf)

            data = json.dumps(import_record)

            # API TOKEN for the REDCap database
            api_token = env_config['LAB_API_TOKEN']

            fields = {
                'token': api_token,
                'content': 'record',
                'action': 'import',
                'format': 'json',  # json csv
                'type': 'flat',
                'overwriteBehavior': 'normal',  # overwrite normal
                'data': data,
                'returnContent': 'ids',  # count #ids
                'returnFormat': 'json'
            }

            # with click.progressbar(label='Importing data into the REDCap database', length=100, fill_char=u'█', empty_char='', width=100) as import_data_bar:
            # check for internet is available or REDCap server is online(available)
            if check_internet_connection("https://redcap.bibbox.bnitm.de/"):
                # import records into the REDCap database
                r = requests.post(env_config['LAB_API_URL'], data=fields)
                # print(f'HTTP Status: {str(r.status_code)}')
                res = r.json()

                count = len(res)

                if r.status_code == 200:
                    logging.info(f"{count} of {project_id} record(s) were imported successfully!!!")

                    import_success_msg = f"{count} of {project_id} record(s) were imported successfully!"
                    sample_ids = res

                    # email notification
                    email_notification(import_success_msg, sample_ids)

                    # convert json to CSV
                    json_csv()

                    # write the import data to CSV file
                    result_csv()

                else:
                    error_msg = re.sub(r"[\\{}]", "", r.text)
                    print(f'HTTP Status:{r.status_code} - {error_msg}')

        else:
            print(f'No {project_id} data to import.')
            # click.echo(f'No {project_id} data to import.')

        # when record successful imported write it to csv(import_data_[date&time])
        # or json file(imported_fbc_data.json). use function for both.
        # write_result_csv(data)

    except IOError as ioerror:
        logger.error(f"There's an error importing data. {ioerror}", exc_info=True)
    except Exception as error:
        logging.exception(f"Exception Occurred. {error}", exc_info=True)


# stop logging
# logging.shutdown()

if __name__ == '__main__':
    data_import('M19')
