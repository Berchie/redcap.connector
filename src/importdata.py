#!/usr/bin/env python
import datetime
import os
import re
from pathlib import Path
import pandas as pd
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


def to_csv_file():
    DATA_DIR = './data'
    MBC_TVISIT_CSV_DIR = './data/csv/mbc_tvisit_labresult.csv'
    MBC_FVISIT_CSV_DIR = './data/csv/mbc_fevervisit_labresult.csv'
    PEDVAC_CSV_DIR = './data/csv/pedvac_labresult.csv'
    CHECK_DATE = datetime.date.today()
    CHECK_FILE_DATE_STRING = datetime.date.today().strftime('%Y%m%d')

    # list items in the data dir
    for item in Path(DATA_DIR).iterdir():
        # print(item)
        if item.is_file() and item.name.split('.')[-1] == 'csv':
            if CHECK_DATE == datetime.date.fromtimestamp(item.lstat().st_atime):
                print(f'file: {item.name}\n\tdate:{datetime.datetime.fromtimestamp(item.lstat().st_atime)}')  # strftime("%Y%m%d")
                if item.name.split('_')[0] == CHECK_FILE_DATE_STRING and item.name.split('_')[1] == 'mbc':
                    # print(item.name.split('_'))
                    # print(item)
                    if 'mbc_t612visit_labresult.csv' in item.name:
                        df_tv = pd.read_csv(item)
                        if os.path.exists(MBC_TVISIT_CSV_DIR) and os.path.getsize(MBC_TVISIT_CSV_DIR) > 0:
                            df_tv.to_csv(MBC_TVISIT_CSV_DIR, index=False, header=False, mode='a')
                        else:
                            df_tv.to_csv(MBC_TVISIT_CSV_DIR, index=False)
                    else:
                        # mbc_fevervisit_labresult.csv
                        df_fv = pd.read_csv(item)
                        if os.path.exists(MBC_FVISIT_CSV_DIR) and os.path.getsize(MBC_TVISIT_CSV_DIR) > 0:
                            df_fv.to_csv(MBC_FVISIT_CSV_DIR, index=False, header=False, mode='a')
                        else:
                            df_fv.to_csv(MBC_FVISIT_CSV_DIR, index=False)
                else:
                    # print(item.name.split('_'))
                    # pedvac_labresult.csv
                    pedvac_df = pd.read_csv(item)
                    if os.path.exists(PEDVAC_CSV_DIR) and os.path.getsize(PEDVAC_CSV_DIR) > 0:
                        pedvac_df.to_csv(PEDVAC_CSV_DIR, index=False, header=False, mode='a')
                    else:
                        pedvac_df.to_csv(PEDVAC_CSV_DIR, index=False)


def import_records(record, project):
    m19_csv_file = '../data/import_m19_data.csv'
    p21_csv_file = '../data/import_p21_data.csv'

    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        # read the file import_json file
        # if os.path.getsize(record) != 0:
        #     with open(record) as jf:
        #         import_record = json.load(jf)
        #
        # data = json.dumps(import_record)

        if os.path.getsize(record) != 0:
            # convert json data to csv object
            # use the read the csv object or file to be imported into REDCap database
            df_obj = pd.read_json(record, orient='records', precise_float=True)
            if project == 'M19':
                df_obj.to_csv(f'../data/{m19_csv_file}', index=False)

                with open(f'../data/{m19_csv_file}') as csv_file:
                    data = csv_file.read()

            else:
                df_obj.to_csv(f'../data/{p21_csv_file}', index=False)

                with open(f'../data/{p21_csv_file}') as csv_file:
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
                    logging.info(f"{count.get('count', 0)} of {project} record(s) were imported successfully!!!")
                    print(count)
                else:
                    count = re.sub(r"[\\{}]", "", r.text)
                    logger.error(f'HTTP Status:{r.status_code} - {count}')

                # delete the import_data.csv file
                if project == 'M19':
                    if os.path.exists(f'../data/{m19_csv_file}'):  # check if the file exist before deleting it
                        os.remove(f'../data/{m19_csv_file}')
                else:
                    if os.path.exists(f'../data/{p21_csv_file}'):
                        os.remove(f'../data/{p21_csv_file}')

                # write the data to csv file(s)
                write_result_csv(record, project)

                # copy the transfer or imported data to a csv file in the cvs dir
                to_csv_file()
            else:
                # write the data to csv file(s) if there is no internet connection
                write_result_csv(record, project)
        else:
            logger.info(f'No {project} data to import.')

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
