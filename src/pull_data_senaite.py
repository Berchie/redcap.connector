# import modules
from dotenv import dotenv_values
from functions import read_json, write_json
from extract_redcap_data import *
import os
import re
import requests
import json
import logging.config
import time
import yaml
# import click
import sys

# add the path of the new different folder (the folder from where we want to import the modules)
sys.path.insert(0, './src')

# load the .env values
config = dotenv_values(f"{os.path.abspath(os.curdir)}/.env")

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open(f'{os.path.abspath(os.curdir)}/config_log.yaml', 'r') as f:
    yaml_config = yaml.safe_load(f.read())
    logging.config.dictConfig(yaml_config)

logger = logging.getLogger(__name__)

# create variables
clients = {}
data = []  # this variable is to hold the all the compile lab results from senaite to be import into REDCap
analyses_data = {}
sampleTypes = []

# read the json file
fbc_keys = read_json(f'{os.path.abspath(os.curdir)}/config/redcap_variables.json')

# clear the content in the import_data.json file
try:
    if os.path.exists(f"{os.path.abspath(os.curdir)}/data/import_data.json"):
        with open(f"{os.path.abspath(os.curdir)}/data/import_data.json", "r+") as importfile:
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
def getClients():
    try:
        # connection to the senaite via the senaite api "title"
        resq = requests.get(config["BASE_URL"] + "/client", cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})

        # print(json.dumps(resq.json(), indent=2))

        client_data = {}

        if resq.status_code == 200 and resq.json()["items"]:
            for item in resq.json()["items"]:
                client_data[item["getClientID"]] = item["title"]

        # print(client_data)
        return client_data
    except ConnectionError as cr:
        logger.error(f"An error occurred while connecting to SENAITE LIMS server. {cr}", exc_info=True)
    except Exception as err:
        logger.exception(f"Exception occurred - {err}", exc_info=True)


def getSampleType():
    try:
        # connection to the senaite via the senaite api
        res_sample = requests.get(config["BASE_URL"] + "/SampleType", cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})
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


# keys or items to extract from respond data from senaite analyses
# "getClientSampleID" or "ClientSampleID", "getClientID", "getDateSampled" (work on the date "2024-01-12T13:56:00+00:00" to get "2024-01-12 13:56" for mbc )
#  "getSampleTypeTitle" or "SampleTypeTitle" (for comparison), "DateSampled", "items" "children"
#  "count"(number of found items), "pages" (number of total pages), "next" (URL to the next batch), "pagesize" (items per page)
# parameters for get_analysis_result() => project_id, from_date to_date (date range to filter the json data),

# @click.command()
# @click.option(
#     '-p', '--project',
#     type=click.Choice(['M19', 'P21']),
#     required=True,
#     help="name of the project. 'M19' => MBC, 'P21' => PEDVAC"
# )
# @click.option(
#     '--period',
#     type=click.Choice(['today', 'yesterday', 'this-week', 'this-month', 'this-year']),
#     default='today',
#     show_default=True,
#     help='period or date the sample or analysis was published'
# )
def get_analyses_result(project, period):
    mbc_t6_t12 = ['T6', 'T7', 'T8', 'T9', 'T10', 'T11']
    mbc_fever_visits = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15']

    try:

        # get the project name and client or project id
        client_id = project
        client_title = getClients()
        client_title = client_title[project]

        next_batch = None

        items_resp = requests.get(config["BASE_URL"] + "/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": client_title,
                                                                          "sort_on": "getDateSampled", "sort_order": "asc", "review_state": "published",
                                                                          "recent_modified": period, "children": "true"}, cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})

        resp_pages = int(items_resp.json()["pages"])
        # next_batch = items_resp.json()['next']  # url for the next batch of records
        http_status_code = items_resp.status_code
        # print(resp_pages)

        for batch in range(resp_pages):

            if batch > 0:

                next_batch_resp = requests.get(next_batch, cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})

                # returns respond data as a JSON object
                r_data = json.dumps(next_batch_resp.json())

                http_status_code = next_batch_resp.status_code

            else:
                # returns respond data as a JSON object
                r_data = json.dumps(items_resp.json())

            # cast the response json data python object dictionary
            r_data_dict = json.loads(r_data)

            # next_batch = r_data_dict['next']  # url for the next batch of records

            # print(f"Batch: {batch}")

            if http_status_code == 200 and r_data_dict['items']:
                # returns JSON object as a dictionary

                r_data_dict_items = r_data_dict['items']

                for i in range(len(r_data_dict_items)):

                    # check if the sample type is EDTA blood
                    if r_data_dict_items[i]["getSampleTypeTitle"] == 'EDTA Blood':

                        # print(r_data_dict_items[i]["getClientSampleID"])

                        redcap_variables = {}

                        if client_id == 'M19':
                            mbc_visit_type = re.sub(r'--?', '-', str(r_data_dict_items[i].get("getClientSampleID")))[10:]
                            # mbc_visit_type = str(r_data_dict_items[i]["getClientSampleID"])[10:]
                            if mbc_visit_type in mbc_t6_t12:
                                redcap_variables = fbc_keys['M19_FBC_TV']
                            elif mbc_visit_type in mbc_fever_visits:
                                redcap_variables = fbc_keys['M19_FBC_FV']
                        elif client_id == 'P21':
                            redcap_variables = fbc_keys['PEDVAC']

                        # redcap record id
                        client_sample_id = str(r_data_dict_items[i]["getClientSampleID"])
                        client_sample_id = re.sub(r'--?', '-', client_sample_id)
                        # print(client_sample_id)

                        if client_sample_id:
                            if client_id == 'M19':
                                if len(client_sample_id) > 11 and not len(client_sample_id) >= 14:
                                    analyses_data[redcap_variables["id"]] = client_sample_id.replace(client_sample_id[10:], 'T0--1')

                                    # slice the study id to get event name to search for the redcap event name
                                    analyses_data[redcap_variables["Event_Name"]] = redcap_event(str(r_data_dict_items[i]["getClientSampleID"])[10:], project)

                                    # date and time of FBC performed
                                    analyses_data[redcap_variables['DateSampled']] = str(r_data_dict_items[i]['getDateSampled'])[:16].replace("T", " ")

                            # elif client_id == 'P21':
                            #     analyses_data[redcap_variables["id"]] = client_sample_id
                            #
                            #     # slice the study id to get event name to search for the redcap event name
                            #     analyses_data[redcap_variables["Event_Name"]] = 'laboratory_arm_1'
                            #
                            #     # date and time of FBC performed
                            #     analyses_data[redcap_variables['DateSampled']] = str(r_data_dict_items[i]['getDateSampled'])[:10]
                            #     analyses_data[redcap_variables['TimeSampled']] = str(r_data_dict_items[i]['getDateSampled'])[11:16]
                            elif client_id == 'P21':
                                analyses_data[redcap_variables["id"]] = client_sample_id

                                # slice the study id to get event name to search for the redcap event name
                                analyses_data[redcap_variables["Event_Name"]] = 'laboratory_arm_1'

                                # date and time of FBC performed
                                analyses_data[redcap_variables['DateSampled']] = str(r_data_dict_items[i]['getDateSampled'])[:10]
                                analyses_data[redcap_variables['TimeSampled']] = str(r_data_dict_items[i]['getDateSampled'])[11:16]

                            children_data = r_data_dict_items[i]['children']

                            # loop through the children object to get values or results of the analysis
                            for child in range(r_data_dict_items[i]["children_count"] - 2):

                                # check if the analysis title or name is found in the redcap_variables dictionary
                                if children_data[child]["title"] in redcap_variables:
                                    # if true, get the key value of the analysis title from the redcap_variables json file
                                    # and use it as the key for the Result value e.g {"lf_fbchgb_q":"9.5"}
                                    if r_data_dict_items[i]["children"][child]["Result"] == '----':
                                        result = 0.0
                                    else:
                                        result = float(r_data_dict_items[i]["children"][child]["Result"])
                                    analyses_data.update({redcap_variables[children_data[child]["title"]]: result})

                        # update the data list variable with the analyses_data
                        if analyses_data:
                            data.append(analyses_data.copy())

                        # change the id to 2nd entry id for only MBC(M19) Project or double entry project database
                        if client_id == 'M19':
                            if len(client_sample_id) > 11 and not len(client_sample_id) >= 14:
                                analyses_data[redcap_variables["id"]] = client_sample_id.replace(client_sample_id[10:], 'T0--2')
                                data.append(analyses_data.copy())

                        analyses_data.clear()  # clear the analysis_data dictionary

            else:
                logger.info(f"SENAITE: No {project} lab records was found!")

            next_batch = r_data_dict['next']  # url for the next batch of records
            # print(f"Next Page: {next_batch}")

        # print or return data or write to json file
        if data:
            write_json(data)
        return data

    except ConnectionError as cr:
        logger.error(f"An error occurred while connecting to SENAITE LIMS server. {cr}", exc_info=True)
    except KeyError as kr:
        logger.error(f"Key Error Occurred. {kr}", exc_info=True)
    except ValueError as vr:
        logger.error(f"Value error occurred. {vr}", exc_info=True)
    except Exception as error:
        logger.exception(f"Exception occurred. {error}", exc_info=True)


# stop logging
logging.shutdown()

if __name__ == '__main__':
    time_start_ = time.perf_counter()
    fbc = get_analyses_result('M19', 'this-week')
    print(json.dumps(fbc, indent=4))
    time_end_ = time.perf_counter()
    print(f'process time: {(time_end_ - time_start_)} seconds')
