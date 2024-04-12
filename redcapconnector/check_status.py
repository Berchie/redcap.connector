import os
import re
import datetime
import sys
import click
import notify2
from pathlib import Path
from loguru import logger
from redcapconnector.config.log_config import handlers

# setting up the logging
logger.configure(
    handlers=handlers,
)


def redcap_connector_notification(message) -> any:
    try:
        notify2.init('REDCap Connector')
        n = notify2.Notification('REDCap Connector Notification', message, os.path.join(os.path.dirname(__file__), 'asset', 'redcap_logo.png'))
        n.set_urgency(level=2)
        n.show()
    except Exception as e:
        # pass
        print(e)


@click.command(options_metavar='<options>')
@click.option(
    '--days',
    type=int,
    # required=True,
    default=1,
    show_default=True,
    help="number of day(s) back to check the status of the transfer of analysis results",
    metavar='<int>'
)
def status(days):
    # display info
    """
    \b
    check whether transfer of analysis results from SENAITE LIMS to REDCap was done or successful.
    \b
    syntax:
        redcon status <options> [--days|-h|--help] <int>
    \b
    Examples:
    \b
      example 1:
        finding the 10-day transfer status
        $ redcon status --days 10
    \b
      example 2:
        finding yesterday's transfer status
        $ redcon status --days 1
    \b
      example 3:
        finding today's transfer status
        $ redcon status --days 0
    """

    # m19_csv = 'import_m19_data.csv'
    # p21_csv = 'import_p21_data.csv'
    try:
        search_dir = os.path.join(os.path.dirname(__file__), 'data', 'daily_result')
        successful_count = 0
        no_import_count = 0
        error_count = 0
        successful_project = []
        no_import_project = []
        no_senaite_record = []

        with open(os.path.join(os.path.dirname(__file__), 'log', 'redcap_connector.log')) as log_file:
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
                                successful_count += 1
                                successful_project.append('M19')
                            elif line_split[6] == 'P21':
                                successful_count += 1
                                successful_project.append('P21')
                        elif line_split[4].isalpha() and len(re.findall('No|data|to|import', line, flags=re.IGNORECASE)) != 0:
                            no_import_count += 1
                            no_import_project.append(line_split[5])

                    elif line_split[0] == check_date and 'ERROR:' in line_split:
                        # print(line)
                        error_count += 1

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

        if 0 < no_import_count < 2:

            # print(f'No transfer of {no_import_project} lab results from SENAITE to REDCap was not done on {check_date}')

            message = f'\nNo transfer of {no_import_project} lab results from SENAITE\n to REDCap was not done on {check_date}.'
            redcap_connector_notification(message=message)

        elif no_import_count == 2:

            # print(f'No transfer of lab results from the SENAITE to REDCap was not done on the {check_date}')

            message = f'\nNo transfer of lab results from the SENAITE to\n REDCap was not done on the {check_date}.'

            redcap_connector_notification(message=message)

        else:
            if 0 < successful_count < 8:
                if 'M19' not in successful_project:
                    # print(f'No transfer of MBC lab results from the SENAITE to REDCap was not done on the {check_date}')

                    message = f'\nNo transfer of MBC lab results from the SENAITE\n to REDCap was not done on the {check_date}.'

                    redcap_connector_notification(message=message)

                elif 'P21' not in successful_project:
                    # print(f'No transfer of PEDVAC lab results from the SENAITE to REDCap was not done on the {check_date}')

                    message = f'\nNo transfer of PEDVAC lab results from the SENAITE\n to REDCap was not done on the {check_date}.'

                    redcap_connector_notification(message=message)

                else:
                    # print(f'Both MBC and PEDVAC lab results transferred from the SENAITE\n to REDCap was sucessful on the {check_date}')

                    message = f'\nBoth MBC and PEDVAC lab results transferred from\n the SENAITE to REDCap was sucessful on the {check_date}'
                    redcap_connector_notification(message=message)

            elif successful_count == 0:

                # print(f'No transfer of both MBC and PEDVAC lab results from the SENAITE to REDCap was not done on the {check_date}')

                message = f'\nNo transfer of lab results from the SENAITE\n to REDCap was not done on the {check_date}.'

                redcap_connector_notification(message=message)

            # elif successful_project == 0:
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
        logger.opt(exception=True).error(f'Exception occurred: {e}')


if __name__ == '__main__':
    status(1)
