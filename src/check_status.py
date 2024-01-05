import logging
import os
import re
import datetime
import pandas as pd
import requests
import logging.config
import yaml
# import notify2
from dotenv import dotenv_values
from functions import check_internet_connection
from pathlib import Path


# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open('../config_log.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


# def redcap_connector_notification(message) -> any:
#     try:
#         notify2.init('REDCap Connector')
#         n = notify2.Notification('REDCap Connector Notification', message)
#         n.set_urgency(level='URGENCY_CRITICAL')
#         n.show()
#     except Exception:
#         pass


def records_to_csv_file(csv_file):
    MBC_TVISIT_CSV_DIR = '../data/csv/mbc_tvisit_labresult.csv'
    MBC_FVISIT_CSV_DIR = '../data/csv/mbc_fevervisit_labresult.csv'
    PEDVAC_CSV_DIR = '../data/csv/pedvac_labresult.csv'

    try:
        records = csv_file.name.split('_')
        if records[1] == 'mbc':
            if 'mbc_t612visit_labresult.csv' in records:
                df_tv = pd.read_csv(csv_file)
                if os.path.exists(MBC_TVISIT_CSV_DIR) and os.path.getsize(MBC_TVISIT_CSV_DIR) > 0:
                    df_tv.to_csv(MBC_TVISIT_CSV_DIR, index=False, header=False, mode='a')
                else:
                    df_tv.to_csv(MBC_TVISIT_CSV_DIR, index=False)
            else:
                # mbc_fevervisit_labresult.csv
                df_fv = pd.read_csv(csv_file)
                if os.path.exists(MBC_FVISIT_CSV_DIR) and os.path.getsize(MBC_TVISIT_CSV_DIR) > 0:
                    df_fv.to_csv(MBC_FVISIT_CSV_DIR, index=False, header=False, mode='a')
                else:
                    df_fv.to_csv(MBC_FVISIT_CSV_DIR, index=False)
        else:
            # print(item.name.split('_'))
            # pedvac_labresult.csv
            pedvac_df = pd.read_csv(csv_file)
            if os.path.exists(PEDVAC_CSV_DIR) and os.path.getsize(PEDVAC_CSV_DIR) > 0:
                pedvac_df.to_csv(PEDVAC_CSV_DIR, index=False, header=False, mode='a')
            else:
                pedvac_df.to_csv(PEDVAC_CSV_DIR, index=False)
    except IOError as ioerror:
        logger.error(f"There's an error writing data to csv file. {ioerror}")


def import_csv_data(csv_file, project):
    try:

        # load the .env values
        env_config = dotenv_values("../.env")

        with open(csv_file, 'r') as csvfile:
            data = csvfile.read()

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

            # copy the transfer or imported data to a csv file in the cvs dir
            records_to_csv_file(csv_file)
        else:
            # send a system notification if there is no internet connection
            pass

    except IOError as ioerror:
        logger.error(f"There's an error importing data. {ioerror}", exc_info=True)
    except Exception as error:
        logging.exception(f"Exception Error Occurred. {error}", exc_info=True)


def search_csv_file(mode='a', project='', check_days=1):
    SEARCH_DIR = '../data'
    str_date = (datetime.date.today() - datetime.timedelta(days=check_days)).strftime('%Y%m%d')
    CHECK_DATE = (datetime.date.today() - datetime.timedelta(days=check_days))

    try:

        for item in Path(SEARCH_DIR).iterdir():
            # print(item)
            match mode:
                case 's':
                    if project:
                        if item.is_file() and item.name.split('_')[0] == str_date:
                            print(item.name.split('_'))
                            if project == 'M19':
                                if item.name.split('_')[1] == 'mbc' and 't612visit' == item.name.split('_')[2]:
                                    print(item)
                                    import_csv_data(item, project)
                                elif item.name.split('_')[1] == 'mbc' and 't612visit' == item.name.split('_')[2]:
                                    import_csv_data(item, project)
                                else:
                                    logging.info('CHECK_STATUS: No csv file for either MBC T6-T12 or Fever visit lab results was found')
                                    message = f'''
                                    No csv file for either MBC T6-T12 or Fever visit lab results was found.
                                    Check the SENAITE LIMS if sample for the project was published from {CHECK_DATE}.
                                    If sample was published from the said date above, run the REDCap command below at the terminal 
                                    for the {project} project and make sure both internet and the REDCap server is available.
                                    '''
                                    # redcap_connector_notification(message=message)
                            else:
                                if item.name.split('_')[1] == 'pedvac' and project == 'P21':
                                    print(item)
                                    import_csv_data(item, project)
                                else:
                                    logging.info('CHECK_STATUS: No csv file for PEDVAC lab results was found.')
                                    message = f'''
                                    No csv file for PEDVAC lab results was found.
                                    Check the SENAITE LIMS if sample for the project was published from {CHECK_DATE}.
                                    If sample was published from the said date above, run the REDCap command below at the terminal 
                                    for the {project} project and make sure both internet and the REDCap server is available.
                                    '''
                                    # redcap_connector_notification(message=message)
                    else:
                        logger.info('Project name was not provided.')
                case 'd':
                    if item.is_file() and item.name.split('_')[0] == str_date:
                        item_split = item.name.split('_')
                        if item_split[1] == 'mbc' and item_split[2] == 't612visit':
                            import_csv_data(item, 'M19')
                        elif item_split[1] == 'mbc' and item_split[2] == 'fevervisit':
                            import_csv_data(item, 'M19')
                        elif item_split[1] == 'pedvac':
                            import_csv_data(item, 'PEDVAC')
                        else:
                            logger.info('CHECK_STATUS: No csv file was found for either M19 and P21 lab results.')

                            message = f'''
                            No csv file was found for either M19 and P21 lab results.
                            Please check the SENAITE LIMS to confirm if the  sample has been published on {CHECK_DATE}. 
                            If the sample has been published, please run the REDCap command provided below for either 
                            project in the terminal. Please ensure that both the internet and REDCap server are available.
                            '''
                            # redcap_connector_notification(message=message)
                    # else:
                    #     logger.info('CHECK_STATUS: No csv file was found for both M19 and P21 lab results.')
                case 'a':
                    item_split = item.name.split('_')
                    if CHECK_DATE == item.lstat().st_atime and item.is_file():
                        if item_split[0] == 'import' and item_split[1] == 'm19':
                            import_csv_data(item, 'M19')
                        else:
                            logger.info('CHECK_STATUS: Import csv file was not found for M19 lab results..')

                            message = f'''
                            Import csv file was not found for MBC.The importing of records into the REDCap database 
                            has not been successful for the project. Please check the SENAITE LIMS to confirm if the 
                            sample has been published on {CHECK_DATE}. If the sample has been published, please run the 
                            REDCap command provided below for the project in the terminal. Please ensure that both the 
                            internet and REDCap server are available.
                            '''

                            # redcap_connector_notification(message=message)

                        if item_split[0] == 'import' and item_split[1] == 'p21':
                            import_csv_data(item, 'P21')
                        else:
                            logger.info('CHECK_STATUS: Import csv file was not found for M19 lab results.')

                            message = f'''
                            Import csv file was not found for PEDVAC.The importing of records into the REDCap database 
                            has not been successful for the project. Please check the SENAITE LIMS to confirm if the 
                            sample has been published on {CHECK_DATE}. If the sample has been published, please run the 
                            REDCap command provided below for the project in the terminal. Please ensure that both the 
                            internet and REDCap server are available.
                            '''

                            # redcap_connector_notification(message=message)

                    # else:
                    #     logger.info('CHECK_STATUS: No importation of records into REDCap database was done for either M19 or P21.')
                case _:
                    logger.info('Mode not found.')

    except IOError as error:
        logger.error(f"There's an error searching csv file and importing data. {error}")


def status(project='', period=1) -> any:
    search_dir = '../data'
    # m19_csv = 'import_m19_data.csv'
    # p21_csv = 'import_p21_data.csv'
    successfulCount = 0
    noImportCount = 0
    errorCount = 0
    sucessfulProject = []
    no_import_project = []
    no_senaite_record = []

    with open('../log/redcap_connector.log') as log_file:
        statement = log_file.readlines()
        #  print(statement)
        check_date = (datetime.date.today() - datetime.timedelta(days=period)).strftime('%d-%m-%Y')
        print(f'check date: {check_date}')

        for line in statement:
            line_split = line.split()
            # print(line_split)
            if line_split[0] == check_date and 'INFO:' in line_split and 'CHECK_STATUS:' not in line_split:

                if line_split[4].isnumeric() and int(line_split[4]) > 0 and 'record(s) were imported successfully!!!' in line:
                    if line_split[6] == 'M19':
                        successfulCount += 1
                        sucessfulProject.append('M19')
                    elif line_split[6] == 'P21':
                        successfulCount += 1
                        sucessfulProject.append('P21')
                elif line_split[4].isalpha() and len(re.findall('No|data|to|import', line, flags=re.IGNORECASE)) != 0:
                    noImportCount += 1
                    no_import_project.append(line_split[5])

            elif line_split[0] == check_date and 'ERROR:' in line_split:
                # print(line)
                errorCount += 1

            if line_split[0] == check_date and 'SENAITE:' in line_split:
                if line_split[6] == 'M19' or line_split[6] == 'P21':
                    no_senaite_record.append(line_split[6])

    # search for project csv file
    found_file = []
    for file in Path(search_dir).iterdir():
        file_split = file.name.split('_')
        if file.is_file() and file.lstat().st_atime == datetime.date.today() - datetime.timedelta(days=period):
            if file_split[0] == (datetime.date.today() - datetime.timedelta(days=period)).strftime('%Y%m%d') and file_split[2] == 't612visit':
                found_file.append('t612visit')
            elif file_split[0] == (datetime.date.today() - datetime.timedelta(days=period)).strftime('%Y%m%d') and file_split[2] == 'fevervisit':
                found_file.append('fevervisit')
            elif file_split[0] == (datetime.date.today() - datetime.timedelta(days=period)).strftime('%Y%m%d') and file_split[1] == 'pedvac':
                found_file.append('pedvac')
            else:
                logger.info('No search files found.')

    # print(f'Importation of records into REDCap database was successfully done {successfulCount} time(s)')
    # print(f'Projects : {sucessfulProject}')
    # print(f'No importation happened {noImportCount} time(s)')
    # pname1, pname2 = None, None
    # for p in no_senaite_record:
    #     if p:
    #         if p == 'M19':
    #             pname1 = 'MBC'
    #         else:
    #             pname2 = 'PEDVAC'
    # print(f 'SENAITE: No lab records was punished for {pname1}, {pname2} on {check_date}')

    if 0 < noImportCount < 2:

        print(f'No transfer of {no_import_project} lab results from SENAITE to REDCap was not done on {check_date}')

        message = f'''
        No transfer of {no_import_project} lab results from SENAITE to REDCap was not done on {check_date}.
        These errors may be caused by a power failure, lack of internet connection, unavailability of the
        REDCap server, or server shutdown. Please check the SENAITE LIMS to confirm if samples for the projects
        were published from {check_date}. If samples were published from the specified date, please run the
        "redcap connector" command below on the terminal for the projects, and ensure that both
        the internet and the REDCap server are available.
        '''
        # redcap_connector_notification(message=message)

    elif noImportCount == 2:

        print(f'No transfer of lab results from the SENAITE to REDCap was not done on the {check_date}')

        message = f'''
        No transfer of lab results from the SENAITE to REDCap was not done on the {check_date}.
        These errors may be caused by a power failure, lack of internet connection, unavailability of the
        REDCap server, or server shutdown. Please check the SENAITE LIMS to confirm if samples for the projects
        were published from {check_date}. If samples were published from the specified date, please run the
        "redcap connector" command below on the terminal for the projects, and ensure that both
        the internet and the REDCap server are available.
        '''

        # redcap_connector_notification(message=message)

    else:
        if successfulCount == 1:
            if 'M19' not in sucessfulProject:
                search_csv_file(mode='s', project='M19', check_days=period)
            elif 'P21' not in sucessfulProject:
                search_csv_file(mode='s', project='P21', check_days=period)
        elif sucessfulProject == 0:
            # check if project lab result csv was found or created
            if 0 < len(found_file) < 4:
                search_csv_file(mode='d', check_days=period)
            elif len(found_file) == 0:
                search_csv_file(mode='a', check_days=period)
        else:
            pass
        # else:
        #     pass


if __name__ == '__main__':
    status(period=0)
