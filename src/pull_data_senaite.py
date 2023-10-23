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
try:
    # connection to the senaite via the senaite api
    resq = requests.get(config["BASE_URL"] + "/client", cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})
    # print(json.dumps(resq.json(), indent=2))

    if resq.status_code == 200 and resq.json()["items"]:
        for item in resq.json()["items"]:
            print(item["title"])
            clients[item["getClientID"]] = item["title"]

    print(clients)

    resq_item = requests.get(config["BASE_URL"] + "/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": "Malaria Birth Cohort - MBC",
                                                                     "children": "true"}, cookies={config["COOKIE_NAME"]: config["COOKIE_VALUE"]})
    print(json.dumps(resq_item.json()["items"][2]["children"], indent=2))
    # print(f'Length of Analyses: {len(resq_item.json()["items"][0]["Analyses"])}')
except Exception as error:
    logging.exception(f"Unexpected {error: }")

# stop logging
logging.shutdown()
