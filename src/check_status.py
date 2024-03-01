import os
import re
import datetime
import click
import logging.config
import yaml
# import notify2
from pathlib import Path

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open(f'{os.path.abspath(".")}/config_log.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


# def redcap_connector_notification(message) -> any:
#     try:
#         notify2.init('REDCap Connector')
#         n = notify2.Notification('REDCap Connector Notification', message, "./asset/redcap_logo")
#         n.set_urgency(level='URGENCY_CRITICAL')
#         n.show()
#     except Exception:
#         pass


@click.command()
@click.option(
    '--days',
    type=int,
    # required=True,
    default=1,
    show_default=True,
    help="number of day(s) back to check the status of the transfer of analysis results"
)
def status(days):
    # m19_csv = 'import_m19_data.csv'
    # p21_csv = 'import_p21_data.csv'
    try:
        search_dir = f'{os.path.abspath(os.curdir)}/data/daily_result'
        successfulCount = 0
        noImportCount = 0
        errorCount = 0
        sucessfulProject = []
        no_import_project = []
        no_senaite_record = []

        with open(f'{os.path.abspath(".")}/log/redcap_connector.log') as log_file:
            statement = log_file.readlines()
            #  print(statement)
            check_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime('%d-%m-%Y')
            # click.echo(f'check date: {check_date}', color=True)

            for line in statement:
                line_split = line.split()
                # print(line_split)
                if line_split:
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
        for file_csv in Path(search_dir).iterdir():
            file_csv_split = file_csv.name.split('_')
            if file_csv.is_file() and file_csv.lstat().st_atime == datetime.date.today() - datetime.timedelta(days=days):
                if file_csv_split[0] == (datetime.date.today() - datetime.timedelta(days=days)).strftime('%Y%m%d') and file_csv_split[1][:-4] == 'haematology':
                    found_file.append('haematology')
                elif file_csv_split[0] == (datetime.date.today() - datetime.timedelta(days=days)).strftime('%Y%m%d') and file_csv_split[1][:-4] == 'chemistry':
                    found_file.append('chemistry')
                else:
                    logger.info('No search files found.')

        if 0 < noImportCount < 2:

            print(f'No transfer of {no_import_project} lab results from SENAITE to REDCap was not done on {check_date}')

            message = f'''
            No transfer of {no_import_project} lab results from SENAITE to REDCap was not done on {check_date}.
            These errors may be caused by a power failure, lack of internet connection, unavailability of the
            REDCap server, or server shutdown. Please check the SENAITE LIMS to confirm if samples for the projects
            were published from {check_date}. If samples were published from the specified date, please run the
            "redcap connector" command on the terminal for the projects, and ensure that both
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
            "redcap connector" command on the terminal for the projects, and ensure that both
            the internet and the REDCap server are available.
            '''

            # redcap_connector_notification(message=message)

        else:
            if 0 < successfulCount < 8:
                if 'M19' not in sucessfulProject:
                    print(f'No transfer of MBC lab results from the SENAITE to REDCap was not done on the {check_date}')

                    message = f'''
                                No transfer of MBC lab results from the SENAITE to REDCap was not done on the {check_date}.
                                These errors may be caused by a power failure, lack of internet connection, unavailability of the
                                REDCap server, or server shutdown. Please check the SENAITE LIMS to confirm if samples for the project
                                were published from {check_date}. If samples were published from the specified date, please run the
                                "redcap connector" command on the terminal for the project, and ensure that both
                                the internet and the REDCap server are available.
                                '''

                    # redcap_connector_notification(message=message)

                elif 'P21' not in sucessfulProject:
                    print(f'No transfer of PEDVAC lab results from the SENAITE to REDCap was not done on the {check_date}')

                    message = f'''
                                No transfer of PEDVAC lab results from the SENAITE to REDCap was not done on the {check_date}.
                                These errors may be caused by a power failure, lack of internet connection, unavailability of the
                                REDCap server, or server shutdown. Please check the SENAITE LIMS to confirm if samples for the project
                                were published from {check_date}. If samples were published from the specified date, please run the
                                "redcap connector" command on the terminal for the project, and ensure that both
                                the internet and the REDCap server are available.
                                '''

                    # redcap_connector_notification(message=message)

                else:
                    print(f'Both MBC and PEDVAC lab results transferred from the SENAITE to REDCap was sucessful on the {check_date}')

                    message = f'Both MBC and PEDVAC lab results transferred from\n the SENAITE to REDCap was sucessful on the {check_date}'
                    # redcap_connector_notification(message=message)

            elif successfulCount == 0:

                print(f'No transfer of of both MBC and PEDVAC lab results from the SENAITE to REDCap was not done on the {check_date}')

                message = f'''
                No transfer of lab results from the SENAITE to REDCap was not done on the {check_date}.
                These errors may be caused by a power failure, lack of internet connection, unavailability of the
                REDCap server, or server shutdown. Please check the SENAITE LIMS to confirm if samples for the projects
                were published from {check_date}. If samples were published from the specified date, please run the
                "redcap connector" command on the terminal for the projects, and ensure that both
                the internet and the REDCap server are available.
                '''

                # redcap_connector_notification(message=message)

            # elif sucessfulProject == 0:
            #     pass
            # TODO: write code to check which lab test type was not transfer in the new phase
            # TODO: change the successfulProject to len(found_file)

            # check if project lab result csv was found or created
            # if 0 < len(found_file) < 4:
            #     search_csv_file(mode='d', check_days=days)
            # elif len(found_file) == 0:
            #     search_csv_file(mode='a', check_days=days)
            # else:
            #     pass

    except Exception as e:
        logger.info(f'Error occurred: {e}')


if __name__ == '__main__':
    status(1)
