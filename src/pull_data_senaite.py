#!/usr/bin/ python

# import modules
from dotenv import dotenv_values
import requests
import json
import logging

# load the .env values
config = dotenv_values("../.env")

# logging any error or any exception to a log file
logging.basicConfig(filename='../log/logfile.log', encoding='utf-8', format="%(asctime)s - %(message)s\n",
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

# create variables
clients = {}
data = []  # this variable is to hold the all the compile lab results from senaite to be import into REDCap
analyses_data = {}
sampleTypes = []

# Opening JSON file
f = open('../config/redcap_variables.json', 'r')
# returns JSON object as a dictionary
fbc_keys = json.loads(f.read())
# closing file
f.close()


# define function for each active connection to senaite
# getClients() is to get the clients in senaite lims
def getClients():
    # connection to the senaite via the senaite api "title"
    resq = requests.get(config["BASE_URL"] + "/client", cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})

    # print(json.dumps(resq.json(), indent=2))

    client_data = {}

    if resq.status_code == 200 and resq.json()["items"]:
        for item in resq.json()["items"]:
            client_data[item["getClientID"]] = item["title"]

    # print(client_data)
    return client_data


def getSampleType():
    # connection to the senaite via the senaite api
    res_sample = requests.get(config["BASE_URL"] + "/SampleType", cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})
    # print(json.dumps(resq.json(), indent=2))

    samples = []

    if res_sample.status_code == 200 and res_sample.json()["items"]:
        for item in res_sample.json()["items"]:
            samples.append(item["title"])

    # print(samples)
    return samples


# keys or items to extract from respond data from senaite analyses
# "getClientSampleID" or "ClientSampleID", "getClientID", "getDateSampled" (work on the date "2023-10-12T13:56:00+00:00" to get "2023-10-12 13:56" for mbc )
#  "getSampleTypeTitle" or "SampleTypeTitle" (for comparison), "DateSampled", "items" "children"
#  "count"(number of found items), "pages" (number of total pages), "next" (URL to the next batch), "pagesize" (items per page)
def getanalyses_result():
    # connect to senaite via the senaite api
    res_analyses = requests.get(config["BASE_URL"] + "/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": "Malaria Birth Cohort - MBC",
                                                                        "sort_on": "getDateSampled", "sort_order": "asc",
                                                                        "recent_created": "yesterday this-week", "children": "true"},
                                cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})

    # returns respond data as a JSON object
    r_data = json.dumps(res_analyses.json())

    # returns JSON object as a dictionary
    r_data_dict = json.loads(r_data)
    r_data_dict_items = r_data_dict['items']
    print(f"Number of found items: {r_data_dict['count']}")
    print(f"number of total pages: {r_data_dict['pages']}")

    # loop through the r_data_dict
    for i in range(r_data_dict['count']):
        # check if the sample type is EDTA blood
        if r_data_dict_items[i]["getSampleTypeTitle"] == 'EDTA Blood':
            analyses_data["ch_subbbarcode"] = r_data_dict_items[i]["getClientSampleID"]
            analyses_data[fbc_keys["M19_FBC_FV"]['DateSampled']] = str(r_data_dict_items[i]['getDateSampled'])[:16].replace("T"," ")

            # children_items = r_data_dict_items[i]['children']

            # loop through the children object to get values or results of the analysis
            for child in range(r_data_dict_items[i]["children_count"] - 2):
                # check if the analysis title or name is found in the redcap_variables json file
                if r_data_dict_items[i]["children"][child]["title"] in fbc_keys["M19_FBC_FV"]:
                    # if true, get the key value of the analysis title from the redcap_variables json file
                    # and use it as the key for the Result value e.g {"lf_fbchgb_q":"9.5"}
                    analyses_data.update({fbc_keys["M19_FBC_FV"][r_data_dict_items[i]["children"][child]["title"]]:
                                              r_data_dict_items[i]["children"][child]["Result"]})

                    # update the data list variable with the analyses_data
                    # will later update or write it to a json for import into REDCap
                    data.append(analyses_data)
        # analyses_data.clear()

    # print or return data
    return data


try:
    # call the getCleints() function
    clients = getClients()
    sampleTypes = getSampleType()
    fbc = getanalyses_result()

    print(clients)
    print(sampleTypes)
    print(json.dumps(fbc_keys, indent=2))
    print(fbc)


# resq_item = requests.get(config["BASE_URL"] + "/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": "Malaria Birth Cohort - MBC",
#                                                                  "children": "true"}, cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})
# print(json.dumps(resq_item.json()["items"][2]["children"], indent=2))
# print(f'Length of Analyses: {len(resq_item.json()["items"][0]["Analyses"])}')
except Exception as error:
    logging.exception(f"Unexpected {error: }")

# stop logging
logging.shutdown()
