#!/usr/bin/env python
import json
import logging
import socket
import sys
from urllib.error import *
from urllib.request import urlopen as url

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
        print("There's an error reading the file.", file_path)
    except Exception as error:
        logging.exception(f"There's an error reading the file: {error: }")


def write_json(dictionary):
    try:
        # serializing json
        # json_object = json.dumps(dictionary, indent=4)

        # writing to the import_data.json
        with open("../data/import_data.json", "a+") as importfile:
            # importfile.write(json_object)
            json.dump(dictionary, importfile, indent=4)

    except IOError:
        print('An error occurred while writing to the file.', IOError.errno)
    except Exception as error:
        logging.exception(f'An error occurred while writing to the file: {error: }')


def check_internet_connection():
    try:
        pass
        # connect to a URL
        url("https://www.google.com/", timeout=5)
        print('SUCCESS: Internet connection is available')
        return True
    except URLError:
        print("FAIL: Internet connection is not available")
        return False


def check_senaite_connection():
    s = ""
    try:
        # global senaite_server = "http://172.102.10.1"  # get the senaite url from the user (use  cli argument)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        print("Socket successfully created")
    except socket.error as error:
        print("socket creation failed with error %s" % error)

    port = 80

    try:
        host_ip = socket.gethostbyname("https://senaite.bnitm.de/senaite")
    except socket.gaierror:
        print("there was an error resolving the host")
        sys.exit()

    s.connect((host_ip, port))
    print("the socket has successfully connected to google")

    #try:
    #    s.connect((senaite_server, port))
    #    return True
    #except socket.error:
    #    print(socket.error.strerror)
    #    return False
    #finally:
    #    s.close()


# stop logging
logging.shutdown()
