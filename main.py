import json

from dotenv import dotenv_values

conf = dotenv_values(".env")

# Opening JSON file
f = open("config/redcap_variables.json","r")
# returns JSON object as a dictionary
data_json = json.loads(f.read())
print(data_json["M19_FBC_FV"]['WBC'])
# closing file
f.close()

