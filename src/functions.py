#!/usr/bin/env python

from urllib.request import urlopen as url
import logging
import json

# logging any error or any exception to a log file
logging.basicConfig(filename='../log/logfile.log', encoding='utf-8', format="%(asctime)s - %(message)s\n",
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


def read_json(file_path):
    try:
        # Opening JSON file
        f = open(file_path, 'r')
        # returns JSON object as a dictionary
        file_data = json.loads(f.read())
        # closing file
        f.close()

        return file_data
    except IOError:
        print("There's an error reading the file.", IOError.errno)
    except Exception as error:
        logging.exception(f"There's an error reading the file: {error: }")


def write_json(dictionary):
    try:
        # serializing json
        json_object = json.dumps(dictionary, indent=4)

        # writing to the import_data.json
        with open("../data/import_data.json", "a+") as importfile:
            importfile.write(json_object)

    except IOError:
        print('An error occurred while writing to the file.', IOError.errno)
    except Exception as error:
        logging.exception(f'An error occurred while writing to the file: {error: }')


def internet_available():
    try:
        pass
        # connect to a URL
        url("https://www.google.com/", timeout=5)
        print('SUCCESS: Internet connection is available')
    except ConnectionError as error:
        print("FAIL: Internet connection is not available")


# stop logging
logging.shutdown()
