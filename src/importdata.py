#!/usr/bin/env python
import os
import re
import pandas as pd
from functions import check_internet_connection, write_result_csv
from dotenv import dotenv_values
import requests
# import json
import logging.config
import yaml

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open('../config_log.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def import_records(record, project):
    m19_csv = 'import_m19_data.csv'
    p21_csv = 'import_p21_data.csv'

    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        # read the file import_json file
        # with open(record) as jf:
        #     import_record = json.load(jf)
        #
        # data = json.dumps(import_record)

        if os.path.getsize(record) != 0:
            # convert json data to csv object
            # use the read the csv object or file to be imported into REDCap database
            df_obj = pd.read_json(record, orient='records', precise_float=True)
            if project == 'M19':
                df_obj.to_csv(f'../data/{m19_csv}', index=False)

                with open(f'../data/{m19_csv}') as csv_file:
                    data = csv_file.read()

            else:
                df_obj.to_csv(f'../data/{p21_csv}', index=False)

                with open(f'../data/{p21_csv}') as csv_file:
                    data = csv_file.read()

            # with open('../data/import_data.csv') as csv_file:
            #     data = csv_file.read()

            if project == 'M19':
                api_token = env_config['M19_API_TOKEN']
            else:
                api_token = env_config['P21_API_TOKEN']

            fields = {
                'token': api_token,
                'content': 'record',
                'action': 'import',
                'format': 'csv',  # json csv
                'type': 'flat',
                'overwriteBehavior': 'overwrite',  # overwrite normal
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
                if r.status_code == 200:
                    logging.info(f"{count.get('count', 0)} record(s) were imported successfully!!!")
                    print(count)
                else:
                    count = re.sub(r"[\\{}]", "", r.text)
                    logger.error(f'HTTP Status:{r.status_code} - {count}')

                # delete the import_data.csv file
                if project == 'M19':
                    if os.path.exists(f'../data/{m19_csv}'):  # check if the file exist before deleting it
                        os.remove(f'../data/{m19_csv}')
                else:
                    if os.path.exists(f'../data/{p21_csv}'):
                        os.remove(f'../data/{p21_csv}')

                # write the data to csv file(s)
                write_result_csv(record, project)
            else:
                # write the data to csv file(s) if there is no internet connection
                write_result_csv(record, project)
        else:
            logger.info('No data to import.')

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
    import_records("../data/import_data.json", 'P21')
