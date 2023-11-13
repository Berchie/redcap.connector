#!/usr/bin/env python

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


# load the .env values
config = dotenv_values("../.env")

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open('../config_log.yaml', 'r') as f:
    yaml_config = yaml.safe_load(f.read())
    logging.config.dictConfig(yaml_config)

logger = logging.getLogger(__name__)


# create variables
clients = {}
data = []  # this variable is to hold the all the compile lab results from senaite to be import into REDCap
analyses_data = {}
sampleTypes = []

# read the json file
fbc_keys = read_json('../config/redcap_variables.json')

# clear the content in the import_data.json file
try:
    if os.path.exists("../data/import_data.json"):
        with open("../data/import_data.json", "r+") as importfile:
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
        logger.error("An error occurred while connecting to SENAITE LIMS server.", exc_info=True)
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
    except Exception as er:
        logger.exception(f"An exception occurred - {er}", er, exc_info=True)


# keys or items to extract from respond data from senaite analyses
# "getClientSampleID" or "ClientSampleID", "getClientID", "getDateSampled" (work on the date "2023-10-12T13:56:00+00:00" to get "2023-10-12 13:56" for mbc )
#  "getSampleTypeTitle" or "SampleTypeTitle" (for comparison), "DateSampled", "items" "children"
#  "count"(number of found items), "pages" (number of total pages), "next" (URL to the next batch), "pagesize" (items per page)
# parameters for get_analysis_result() => project_id, from_date to_date (date range to filter the json data),
def get_analyses_result(project_id):
    nb_redcap_variables = {}  # to hold the next batch redcap variables

    mbc_t6_t12 = ['T6', 'T7', 'T8', 'T9', 'T10', 'T11']
    mbc_fever_visits = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15']
    try:
        # get the project name and client or project id
        client_id = project_id
        client_title = getClients()
        client_title = client_title[project_id]

        # connect to senaite via the senaite api
        res_analyses = requests.get(config["BASE_URL"] + "/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": client_title,
                                                                            "sort_on": "getDateSampled", "sort_order": "asc", "review_state": "published",
                                                                            "recent_modified": "this-week", "children": "true"},
                                    cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})

        # returns respond data as a JSON object
        r_data = json.dumps(res_analyses.json())
        r_data_dict = json.loads(r_data)

        if res_analyses.status_code == 200 and r_data_dict['items']:
            # returns JSON object as a dictionary

            r_data_dict_items = r_data_dict['items']

            # print(f"Number of found items: {r_data_dict['count']}")
            # print(f"number of total pages: {r_data_dict['pages']}")

            # total pages generated by the api. use this value in the while loop to get the next batch of the result
            # total_pages = r_data_dict['pages']

            # loop through the r_data_dict
            # print(r_data_dict_items)
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

                    # redcap record id
                    client_sample_id = str(r_data_dict_items[i]["getClientSampleID"])
                    client_sample_id = re.sub(r'--?', '-', client_sample_id)
                    print(client_sample_id)
                    if client_sample_id:
                        analyses_data[redcap_variables["id"]] = client_sample_id.replace(client_sample_id[10:], 'T0--1')

                        # slice the study id to get event name to search for the redcap event name
                        analyses_data[redcap_variables["Event_Name"]] = redcap_event(str(r_data_dict_items[i]["getClientSampleID"])[10:])

                        # date and time of FBC performed
                        analyses_data[redcap_variables['DateSampled']] = str(r_data_dict_items[i]['getDateSampled'])[:16].replace("T", " ")

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
                    data.append(analyses_data.copy())

                    analyses_data.clear()  # clear the analysis_data dictionary

            # fetch the next page of the analysis data or result
            # next_page = 2
            next_batch = r_data_dict['next']  # url for the next batch of records

            while next_batch is not None:  # next_page <= total_pages
                # print(r_data_dict['next'])

                # clear the analysis_data for the next analysis results or data
                analyses_data.clear()

                res_next_batch = requests.get(next_batch, cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})

                # return the response data as JSON object
                nb_data = json.dumps(res_next_batch.json())

                # check if the response data items is not empty and response status is OK (code 200)
                if res_next_batch.status_code == 200 and res_next_batch.json()['items']:
                    # print(f"This is page: {res_next_batch.json()['page']}")

                    # returns JSON object as a dictionary and assign to variable
                    next_batch_data = json.loads(nb_data)["items"]

                    # total number of items on a page. use as limiter for looping through the "items"
                    # nb_pagesize = json.loads(nb_data)["pagesize"]

                    # loop through nb_data
                    for nb in range(len(next_batch_data)):  # next_batch_data['pagesize']
                        if next_batch_data[nb]['getSampleTypeTitle'] == 'EDTA Blood':

                            # assign the corresponding redcap variables of a project or client
                            if client_id == 'M19':
                                mbc_visit_type_nb = re.sub(r"--?", '-', next_batch_data[nb].get("getClientSampleID"))[10:]

                                if mbc_visit_type_nb in mbc_t6_t12:
                                    nb_redcap_variables = fbc_keys['M19_FBC_TV']
                                elif mbc_visit_type_nb in mbc_fever_visits:
                                    nb_redcap_variables = fbc_keys['M19_FBC_FV']

                            # redcap record id
                            client_sample_id = str(r_data_dict_items[nb].get("getClientSampleID"))
                            client_sample_id = re.sub(r'--?', '-', client_sample_id)

                            if client_sample_id:
                                analyses_data[nb_redcap_variables['id']] = client_sample_id.replace(client_sample_id[10:], 'T0--1')

                                # slice the study id to get event name to search for the redcap event name
                                analyses_data[nb_redcap_variables["Event_Name"]] = redcap_event(str(next_batch_data[nb].get("getClientSampleID"))[10:])

                                # date and time of FBC performed
                                analyses_data[nb_redcap_variables['DateSampled']] = str(next_batch_data[nb]['getDateSampled'])[:16].replace("T", " ")

                                # assign the key children value to nb_data_children
                                # this contains the analysis result of participant's visit
                                nb_data_children = next_batch_data[nb]['children']

                                # loop through nb_data_children to get results of the analysis
                                for ch in range(next_batch_data[nb]['children_count'] - 2):

                                    # check if the analysis title or name is found in the redcap_variables dictionary
                                    if nb_data_children[ch]['title'] in nb_redcap_variables:
                                        # if true, get the key value of the analysis title from the redcap_variables json file
                                        # and use it as the key for the Result value e.g {"lf_fbchgb_q":"9.5"}
                                        if nb_data_children[ch]['Result'] == '----':
                                            result_Value = 0.0
                                        else:
                                            result_Value = float(nb_data_children[ch]['Result'])
                                        analyses_data.update({nb_redcap_variables[nb_data_children[ch]['title']]: result_Value})

                            # append the analysis results to the data list
                            # using the dictionary copy() method (dict.copy())
                            data.append((analyses_data.copy()))

                            analyses_data.clear()  # clear the analysis_data dictionary

                next_batch = res_next_batch.json()['next']  # assign the next batch url

                # next_page += 1  # increment the page count by 1

                # print or return data or write to json file
            write_json(data)
            return data
        else:
            logger.info("SENAITE: No records was found!")

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
    time_start_ = time.time()
    fbc = get_analyses_result('M19')
    print(json.dumps(fbc, indent=4))
    time_end_ = time.time()
    print(f'process time: {(time_end_ - time_start_)} seconds')
