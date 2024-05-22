import configparser

from redcapconnector.functions import read_json, write_json
from redcapconnector.extract_redcap_data import *
import os
import re
import requests
import json
import logging.config
import time
import yaml
import sys
import click
from dotenv import dotenv_values
from redcapconnector.importdata import data_import
from tqdm import tqdm, trange
from loguru import logger
from redcapconnector.config.log_config import handlers

# setting up the logging
logger.configure(
    handlers=handlers,
)

# load .env variables
dotenv_path = os.path.abspath(f"{os.environ['HOME']}/.env")
if os.path.abspath(f"{os.environ['HOME']}/.env"):
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise logging.exception('Could not found the application environment variables!')

# load the cookie.ini file values
cookie_config = configparser.ConfigParser()
cookie_config.read(os.path.join(os.path.dirname(__file__), "config", "cookie.ini"))

# create variables
clients = {}
data = []  # this variable is to hold the all the compile lab results from senaite to be import into REDCap
analyses_data = {}
sampleTypes = []

# read the json file
fbc_keys = read_json(os.path.join(os.path.dirname(__file__), 'config', 'redcap_variables.json'))

# clear the content in the import_data.json file
try:
    if os.path.exists(os.path.join(os.path.dirname(__file__), "data", "import_data.json")):
        with open(os.path.join(os.path.dirname(__file__), "data", "import_data.json"), 'r+') as importfile:
            # check if the file is not empty
            if importfile.read() is not None:
                # clear the file content
                importfile.truncate(0)
except IOError as ioe:
    logger.error("An error occurred while reading the 'import_data.json' file")
except Exception as er:
    logger.exception(f"Exception occurred - {er}", exc_info=True)


# define function for each active connection to senaite
# getClients() is to get the clients in senaite lims
def get_clients():
    try:
        # connection to the senaite via the senaite api "title"
        resq = requests.get(os.environ["BASE_URL"] + "/client", cookies={cookie_config["Cookie"]["name"]: cookie_config["Cookie"]["value"]})

        # print(json.dumps(resq.json(), indent=2))

        client_data = {}

        if resq.status_code == 200 and resq.json()["items"]:
            for item in tqdm(resq.json()["items"], desc='Processing Clients from SENAITE'):
                time.sleep(0.1)
                client_data[item["getClientID"]] = item["title"]

        # print(client_data)
        return client_data
    except ConnectionError as cr:
        logger.error(f"An error occurred while connecting to SENAITE LIMS server. {cr}", exc_info=True)
    except Exception as err:
        logger.exception(f"Exception occurred - {err}", exc_info=True)


def get_sample_type():
    try:
        # connection to the senaite via the senaite api
        res_sample = requests.get(os.environ["BASE_URL"] + "/SampleType", cookies={cookie_config["Cookie"]["name"]: cookie_config["Cookie"]["value"]})
        # print(json.dumps(resq.json(), indent=2))

        samples = []

        if res_sample.status_code == 200 and res_sample.json()["items"]:
            for item in res_sample.json()["items"]:
                samples.append(item["title"])

        # print(samples)
        return samples
    except ConnectionError as cr:
        logger.error(f"A connection error occurred. {cr}", exc_info=True)
    except Exception as err:
        logger.exception(f"An exception occurred - {err}", er, exc_info=True)


# all event names in the Laboratory Result REDCap database
# we can use in the dropdown menu (GUI) or on the command line option
# for now I will use the sample id to identify the events***


# get the redcap events
@logger.catch
def project_events():
    events = get_events()

    project_event_names = []

    for event in events:
        project_event_names.append(event['event_name'])

    return project_event_names


# get the project redcap arm number
@logger.catch
def project_event_arm(project):
    arm_number = get_redcap_arms()

    for a in arm_number:
        if a['name'] == project:
            arm = a['arm_num']
            return arm


# get the project redcap event names
@logger.catch
def project_event_name(event, arm_number):
    events = get_events()

    for x in events:
        if x["event_name"] == event and x['arm_num'] == arm_number:
            event_name = x['unique_event_name']
            return event_name


# keys or items to extract from respond data from senaite analyses "getClientSampleID" or "ClientSampleID",
# "getClientID", "getDateSampled" (work on the date "2024-01-12T13:56:00+00:00" to get "2024-01-12 13:56" for mbc )
# "getSampleTypeTitle" or "SampleTypeTitle" (for comparison), "DateSampled", "items" "children" "count"(number of
# found items), "pages" (number of total pages), "next" (URL to the next batch), "pagesize" (items per page)
# parameters for get_analysis_result() => project_id, from_date to_date (date range to filter the json data),
# use keyword get the variable name of the analysis use unit to get the unit of the analysis

transfer_example_context = """
    \b
    example 1:
    -------------
        # transferring results without the period.[default period value: today]
        redcon transfer-result -p M19
    
    \b
    example 2:
    -------------
        # transferring result that was publish today
        redcon transfer-result -p M19 --period today
    
     \b
    example 3:
    -------------
        # transferring result that was publish three months ago or this month 
        redcon transfer-result -p M19 --period this-month
    
     \b
    example 4:
    -------------
        # help option for transfer-result command
        redcon transfer-result -h
"""


@click.command(options_metavar='<options>')
@click.option(
    '-p', '--project',
    type=click.Choice(['M19', 'P21']),
    required=True,
    help="name of the project. 'M19' => MBC, 'P21' => PEDVAC"
)
@click.option(
    '--period',
    type=click.Choice(['today', 'yesterday', 'this-week', 'this-month', 'this-year']),
    default='today',
    show_default=True,
    help='period or date the sample or analyses was published'
)
def transfer_result(project, period):

    # display info
    """
    \b
    transfer analysis results from SENAITE LIMS to REDCap

    \b
    syntax:
        redcon transfer-result <options1>[-p|--project|-h|--help] <options2>[--period]
    \b
    Examples:
        \b
        example 1:
            transferring results without the period.[default period value: today]
            $ redcon transfer-result -p M19
        \b
        example 2:
            transferring result that was published today
            $ redcon transfer-result -p M19 --period today
        \b
        example 3:
            transferring result that was published three months ago or this month
            $ redcon transfer-result -p M19 --period this-month
        \b
        example 4:
            help option for transfer-result command
            $ redcon transfer-result -h
    """

    mbc_t6_t12 = ['T6', 'T7', 'T8', 'T9', 'T10', 'T11']
    mbc_fever_visits = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15']

    # store the M19 or longitudinal project event record id. this id will be sent via email to DB manager
    record_ids = []

    try:
        # assign project name. This name will be used with
        if project == 'P21':
            project_name = 'PEDVAC'
        else:
            project_name = 'MBC'

        # get the project name and client or project id
        client_id = project
        client_title = get_clients()
        client_title = client_title[project]
        project_arm = project_event_arm(project_name)

        next_batch = None

        items_resp = requests.get(os.environ["BASE_URL"] + "/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": client_title,
                                                                              "sort_on": "getDateSampled", "sort_order": "asc", "review_state": "published",
                                                                              "recent_modified": period, "children": "true"},
                                  cookies={cookie_config["Cookie"]["name"]: cookie_config["Cookie"]["value"]}, stream=True)

        resp_pages = int(items_resp.json()["pages"])
        # next_batch = items_resp.json()['next']  # url for the next batch of records
        http_status_code = items_resp.status_code
        # print(resp_pages)

        # tqm progressbar
        for batch in trange(resp_pages, desc=f'Processing Analysis Results in {resp_pages} Batch(es)'):

            time.sleep(0.01)

            # click progressbar
            # with click.progressbar(range(resp_pages), label=f'Processing Analysis Results in {resp_pages} Batch(es)',fill_char=u'█', width=100) as bar:
            #     for batch in bar:
            if batch > 0:

                next_batch_resp = requests.get(next_batch, cookies={cookie_config["Cookie"]["name"]: cookie_config["Cookie"]["value"]})

                # returns respond data as a JSON object
                r_data = json.dumps(next_batch_resp.json())

                http_status_code = next_batch_resp.status_code

            else:
                # returns respond data as a JSON object
                r_data = json.dumps(items_resp.json())

            # cast the response json data to python object dictionary
            r_data_dict = json.loads(r_data)

            # next_batch = r_data_dict['next']  # url for the next batch of records

            # print(f"Batch: {batch}")

            if http_status_code == 200 and r_data_dict['items']:
                # returns JSON object as a dictionary

                r_data_dict_items = r_data_dict['items']

                for i in trange(len(r_data_dict_items), desc=f'Analysis Result Batch {batch + 1}', leave=False):

                    time.sleep(0.002)

                    # click progressbar 2 with click.progressbar(range(len(r_data_dict_items)),label=f'Analysis Result Batch {batch}', fill_char=u'⣿',
                    # width=100, empty_char="") as pbar: for i in pbar: check if the sample type is EDTA blood
                    if r_data_dict_items[i]["getSampleTypeTitle"] == 'EDTA Blood':

                        # print(r_data_dict_items[i]["getClientSampleID"])

                        if client_id == 'M19':
                            mbc_visit_type = re.sub(r'--?', '-', str(r_data_dict_items[i].get("getClientSampleID")))[10:]
                            # mbc_visit_type = str(r_data_dict_items[i]["getClientSampleID"])[10:]

                        # redcap record id
                        client_sample_id = str(r_data_dict_items[i]["getClientSampleID"])
                        client_sample_id = re.sub(r'--?', '-', client_sample_id)
                        # print(client_sample_id)

                        if client_sample_id:
                            if client_id == 'M19':
                                if len(client_sample_id) > 11 and not len(client_sample_id) >= 14:

                                    # add client_sample_id to the record_ids dictionary
                                    record_ids.append(client_sample_id)

                                    # replace the last characters of the client sample id (record id used by REDCap) with 'T0'
                                    record_id = client_sample_id.replace(client_sample_id[10:], "T0")
                                    analyses_data['l_barcode'] = record_id

                                    # slice the study id to get event name to search for the redcap event name
                                    analyses_data["redcap_event_name"] = project_event_name(str(r_data_dict_items[i]["getClientSampleID"])[10:], project_arm)

                                    # add the redcap complete form status for identification instruments
                                    # 0 --> Incomplete, 1 --> Unverified,  2 --> Complete
                                    analyses_data["identification_complete"] = str(2)

                                    # date and time of FBC performed or capture to the SENAITE
                                    result_capture_date = str(r_data_dict_items[i]['children'][0]['ResultCaptureDate'])[:16].replace("T", " ")
                                    analyses_data['h_datetime'] = result_capture_date
                                else:
                                    pass

                            elif client_id == 'P21':
                                if len(client_sample_id) > 11 and not len(client_sample_id) >= 14:
                                    analyses_data['l_barcode'] = client_sample_id
                                    # slice the study id to get event name to search for the redcap event name
                                    analyses_data["redcap_event_name"] = project_event_name('Laboratory', project_arm)

                                    # add the redcap complete form status for identification instruments
                                    # 0 --> Incomplete, 1 --> Unverified,  2 --> Complete
                                    analyses_data["identification_complete"] = str(2)

                                    # date and time of FBC performed 'ResultCaptureDate'
                                    result_capture_date = str(r_data_dict_items[i]['children'][0]['ResultCaptureDate'])[:16].replace("T", " ")
                                    analyses_data['h_datetime'] = result_capture_date

                        children_data = r_data_dict_items[i]['children']

                        # loop through the children object to get values or results of the analysis
                        if len(client_sample_id) > 11 and not len(client_sample_id) >= 14:
                            for child in range(r_data_dict_items[i]["children_count"] - 2):

                                # check if the analysis title or name is found in the redcap_variables dictionary
                                # if children_data[child]["title"] in redcap_variables:
                                # if true, get the key value of the analysis title from the redcap_variables json file
                                # and use it as the key for the Result value e.g {"lf_fbchgb_q":"9.5"}
                                if r_data_dict_items[i]["children"][child]["Result"] == '----':
                                    result = 0.0
                                else:
                                    result = r_data_dict_items[i]["children"][child]["Result"]
                                analyses_data.update({str(children_data[child]["Keyword"]).lower(): result})

                                # add the unit of the analysis
                                unit_variable_name = f'{str(children_data[child]["Keyword"]).lower()}_unit'
                                analyses_data.update({unit_variable_name: str(children_data[child]["Unit"])})

                            # add the redcap complete form status for haematology instrument
                            # 0 --> Incomplete, 1 --> Unverified,  2 --> Complete
                            analyses_data["haematology_complete"] = str(2)

                        # update the data list variable with the analyses_data
                        if analyses_data:
                            data.append(analyses_data.copy())

                    analyses_data.clear()  # clear the analysis_data dictionary
                # time.sleep(0.002)

            else:
                logger.info(f"SENAITE: No {project} lab records was found!")

            next_batch = r_data_dict['next']  # url for the next batch of records
            # print(f"Next Page: {next_batch}")

        # print or return data or write to json file
        if data:
            write_json(data)

        # importing the data or results into REDCap project database
        data_import(project,record_ids=record_ids)

        return data

    except ConnectionError as cr:
        logger.error(f"An error occurred while connecting to SENAITE LIMS server. {cr}", exc_info=True)
    except KeyError as kr:
        logger.error(f"Key Error Occurred. {kr}", exc_info=True)
    except ValueError as vr:
        logger.error(f"Value error occurred. {vr}", exc_info=True)
    except Exception as error:
        logger.exception(f"Exception occurred. {error}", exc_info=True)


if __name__ == '__main__':
    time_start_ = time.perf_counter()
    fbc = transfer_result('M19', 'this-week')
    print(json.dumps(fbc, indent=4))
    time_end_ = time.perf_counter()
    print(f'process time: {(time_end_ - time_start_)} seconds')
