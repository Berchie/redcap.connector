import os
from dotenv import dotenv_values, load_dotenv
import requests
import click
import configparser
from loguru import logger
from redcapconnector.config.log_config import handlers

# setting up the logging
log_file_path = os.path.join(os.path.dirname(__file__), "log", 'redcap_connector.log')
logger.configure(
    handlers=handlers,
)

# load .env variables
dotenv_path = os.path.abspath(f"{os.environ['HOME']}/.env")
if os.path.abspath(f"{os.environ['HOME']}/.env"):
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise logger.exception('Could not found the application environment variables!')

example_context = """
        \b
        example 1: 
        ------------
            login to SENAITE
            redcon senaite-connect
        
        \b
        example 2:
        ------------
            help option for senaite-connect command
            $ redcon senaite-connect -h
"""


@click.command(options_metavar='<options>')
def senaite_connect():
    # display info
    """
    \b
    login to SENAITE LIMS.

    \b
    syntax:
        redcon senaite-connect <options>[-h|--help]
    \b
    Examples:
        \b
        example 1:
            login to SENAITE
            $ redcon senaite-connect
        \b
        example 2:
            help option for senaite-connect command
            $ redcon senaite-connect -h
    """

    try:
        # load the .env values
        env_config = dotenv_values("../.env")

        reqs = requests.post(os.environ["BASE_URL"] + "/login", params={"__ac_name": os.environ['SENAITE_USERNAME'],
                                                                        "__ac_password": os.environ['SENAITE_PASSWORD']})

        # check if the response status is OK(200) and return data is not empty
        # before proceeding with writing the cookies to a file
        if reqs.status_code == 200 and reqs.json()["items"]:
            # print(json.dumps(reqs.json(), indent=2))

            # assigning cookies from the response header
            cookie = reqs.headers['Set-Cookie']

            # set a new the COOKIE NAME & COOKIE VALUE in ini file
            replace_cookie_name = cookie.replace(";", "=").split("=")[0]

            replace_cookie_value = cookie.replace(";", "=").split("=")[1]

            # create instance of the configparser
            config = configparser.ConfigParser()

            config_file_path = os.path.join(os.path.dirname(__file__), 'config', 'cookie.ini')

            # read the cookie.ini file
            config.read(config_file_path)

            # escape the '%'
            if '%' in replace_cookie_value:
                replace_cookie_value = replace_cookie_value.replace("%", "%%")

            # update the cookie.ini file
            config.set('Cookie', 'name', replace_cookie_name)
            config.set('Cookie', 'value', replace_cookie_value)

            # write or update the cookie.ini Cookie section
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)

            logger.success("Login into SENAITE successfully.")

    except ConnectionError as cr:
        logger.error(f"Connection error while connecting to SENAITE LIMS. {cr}")
    except IOError as ioerror:
        logger.error(f"An error occurred while reading the .evn file or write to the .env file. {ioerror}", )
    except Exception as err:
        logger.opt(exception=True).error(f"Exception occurred. {err}")


# stop logging
# logging.shutdown()

if __name__ == '__main__':
    senaite_connect()
