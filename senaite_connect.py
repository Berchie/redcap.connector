#!/usr/bin/ python

import requests
import json
from dotenv import dotenv_values

# load the .env values
config = dotenv_values(".env")

reqs = requests.post(config["BASEURL"] + "/login", params={"__ac_name": config['SENAITE_USERNAME'],
                                                           "__ac_password": config['SEANITE_PASSWORD']})

# r = requests.post(config["BASE_URL"] + "/login",
#                  params={"__ac_name": config['SENAITE_USERNAME'], "__ac_password": config['SEANITE_PASSWORD']})

print(json.dumps(reqs.json(), indent=2))
print(f"COOKIE: {reqs.headers['Set-Cookie']}")
cookie = reqs.headers['Set-Cookie']
print('cookies name: ' + cookie.replace(";", "=").split("=")[0])
print('cookies value: ' + cookie.replace(";", "=").split("=")[1])

# print(f"COOKIE: {r.headers['Set-Cookie']}")

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
