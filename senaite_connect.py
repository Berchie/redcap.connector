#!/usr/bin/ python
from dotenv import dotenv_values
import datetime
import requests
import json
import logging

# load the .env values
config = dotenv_values(".env")

# logging any error or any exception to a log file
logging.basicConfig(filename='logfile.log', encoding='utf-8', format="%(asctime)s - %(message)s",
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

try:
    reqs = requests.post(config["BASE_URL"] + "/login", params={"__ac_name": config['SENAITE_USERNAME'],
                                                                "__ac_password": config['SEANITE_PASSWORD']})

    # check if the response status is OK(200) and return data is not empty
    # before proceeding with writing the cookies to a file
    if reqs.status_code == 200 and reqs.json()["items"]:
        print(json.dumps(reqs.json(), indent=2))

        # assigning cookies from the response header
        cookie = reqs.headers['Set-Cookie']

        # search and replace the COOKIE_NAME & COOKIE_VALUE values
        # in the .env file
        search_cookie_name = config['COOKIE_NAME']
        replace_cookie_name = cookie.replace(";", "=").split("=")[0]

        search_cookie_value = config['COOKIE_VALUE']
        replace_cookie_value = cookie.replace(";", "=").split("=")[1]

        # open the file in a read mode
        f = open(".env", "r")

        # Reading the content of the file using the read() function them in a new variable
        data = f.read()

        # Searching and replacing the text using the replace() function
        data = data.replace(search_cookie_name, replace_cookie_name)
        data = data.replace(search_cookie_value, replace_cookie_value)

        f.close()

        # open file in the write mode
        fw = open(".env", "w")
        # Writing the replaced data in our text (.env) file
        fw.write(data)

        fw.close()

except Exception as err:
    logging.exception(f"Unexpected {err=}, {type(err)=}")

# stop logging
logging.shutdown()
