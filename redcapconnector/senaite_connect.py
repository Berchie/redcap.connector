import os
from dotenv import dotenv_values, load_dotenv
import requests
import json
import logging.config
import yaml
import click

# import the customize logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open(f'{os.getcwd()}/redcapconnector/config/config_log.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

# load .env variables
dotenv_path = os.path.abspath(f"{os.environ['HOME']}/.env")
if os.path.abspath(f"{os.environ['HOME']}/.env"):
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise logging.exception('Could not found the application environment variables!')


@click.command
def senaite_connect():
    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        reqs = requests.post(os.environ["BASE_URL"] + "/login", params={"__ac_name": os.environ['SENAITE_USERNAME'],
                                                                        "__ac_password": os.environ['SEANITE_PASSWORD']})

        # check if the response status is OK(200) and return data is not empty
        # before proceeding with writing the cookies to a file
        if reqs.status_code == 200 and reqs.json()["items"]:
            # print(json.dumps(reqs.json(), indent=2))

            # assigning cookies from the response header
            cookie = reqs.headers['Set-Cookie']

            # search and replace the COOKIE_NAME & COOKIE_VALUE values
            # in the .env file
            search_cookie_name = os.environ['COOKIE_NAME']
            replace_cookie_name = cookie.replace(";", "=").split("=")[0]

            search_cookie_value = os.environ['COOKIE_VALUE']
            replace_cookie_value = cookie.replace(";", "=").split("=")[1]

            # os.environ['COOKIE_NAME'] = replace_cookie_name
            # os.environ['COOKIE_VALUE'] = replace_cookie_value

            # open the file in a read mode
            with open(dotenv_path, 'r') as env_file:
                # env_file = open(dotenv_path, "r")

                # Reading the content of the file using the read() function them in a new variable
                data = env_file.read()

                # Searching and replacing the text using the replace() function
                data = data.replace(search_cookie_name, replace_cookie_name)
                data = data.replace(search_cookie_value, replace_cookie_value)

                # env_file.close()

            # open file in the write mode
            with open(dotenv_path, 'w') as fw:
                # fw = open(f"{os.path.abspath('..')}/.env", "w")
                # Writing the replaced data in our text (.env) file
                fw.write(data)

                # fw.close()

    except ConnectionError as cr:
        logging.error("Connection error while connecting to SENAITE LIMS.", exc_info=True)
    except IOError as ioerror:
        logger.error("An error occurred while reading the .evn file or write to the .env file", exc_info=True)
    except Exception as err:
        logging.exception("Exception occurred", exc_info=True)


# stop logging
logging.shutdown()

if __name__ == '__main__':
    senaite_connect()
    # print(f"{os.path.dirname('..')}/.env")
    # print(f"{os.path.abspath('..')}/.env")
