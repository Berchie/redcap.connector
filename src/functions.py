import os
import csv
import json
import logging.config
import yaml
import socket
import sys
from urllib.error import *
from urllib.request import urlopen as url
from time import localtime, strftime

# from pull_data_senaite import get_analyses_result

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
if os.path.exists(f'{os.path.abspath(os.curdir)}/config_log.yaml'):
    with open(f'{os.path.abspath(os.curdir)}/config_log.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)


logger = logging.getLogger(__name__)


def is_not_empty_file(filepath):
    try:
        return os.path.isfile(filepath) and os.path.getsize(filepath) > 0
    except IOError as err:
        print(f"An error occurred while locating the file - {err}")
        logger.error("An error occurred while locating the file.", exc_info=True)
    except Exception as Argument:
        logger.exception(f"An error occurred while locating the file - {Argument}", exc_info=True)


def read_json(file_path):
    try:
        # Opening JSON file
        file_json = open(file_path, 'r')
        # returns JSON object as a dictionary
        file_data = json.loads(file_json.read())

        # closing file
        file_json.close()

        return file_data
    except IOError as ioer:
        logger.error(f"There's an error reading the file. {ioer}", exc_info=True)
    except Exception as error:
        logger.exception(f"There's an error reading the file. {error}", exc_info=True)


def write_json(dictionary):
    try:
        # serializing json
        # json_object = json.dumps(dictionary, indent=4)

        # writing to the import_data.json
        with open(f"{os.path.abspath(os.curdir)}/data/import_data.json", "a+") as importfile:
            # importfile.write(json_object)
            json.dump(dictionary, importfile, indent=4)

    except IOError:
        logger.error('An error occurred while writing to the file.', exc_info=True)
    except Exception as error:
        logger.exception(f'An error occurred while writing to the file. {error}', exc_info=True)


# write the results to csv file
def write_result_csv(results, project_id):
    mbc_t6_t12 = ['T6', 'T7', 'T8', 'T9', 'T10', 'T11']
    mbc_fever_visits = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15']
    csv_columns = read_json("./config/redcap_variables.json")

    # data from the json file
    # analysis_result = read_json(datafile)

    # with open(data_import, 'r') as df:
    # data = df.read()
    #    new_data_dict = json.load(df)

    # if os.path.isfile(results):
    #     new_data_dict = read_json(results)
    # else:
    #     new_data_dict = json.loads(results)

    # new_data_dict = json.loads(json.dumps(results))
    new_data_dict = read_json(results)

    # new_data_dict = {}

    # for index in new_data_dict:
    #    print(index.values())

    # mbc_t6_t12_columns = []
    # mbc_fever_visits_columns = []
    # csv_filename = ""
    try:

        os.chdir(".")
        # print(os.path.abspath(os.curdir))
        file_path = f'{os.path.abspath(os.curdir)}/data'

        # determine project analysis result
        # and it event or visit

        for data_result in new_data_dict:
            if data_result:
                if project_id == 'M19':
                    if str(data_result['m_subbarcode'])[:3] == 'M19':

                        # write the T6-T12 (API) visits lab result to csv file
                        if str(data_result['redcap_event_name'])[0:3].rstrip('_').upper() in mbc_t6_t12:

                            # mbc_t6_t12_columns = data_result.keys()
                            mbc_t6_t12_columns = csv_columns["M19_FBC_TV"].values()

                            csv_filename = f'{strftime("%Y%m%d", localtime())}_mbc_t612visit_labresult.csv'

                            if is_not_empty_file(f'{file_path}/{csv_filename}'):

                                with open(f"{file_path}/{csv_filename}", 'a', newline='') as open_csvfile:
                                    csv_writer = csv.writer(open_csvfile)
                                    # for row in analysis_result[r]:
                                    lt_data = data_result  # typecast the string to dict
                                    # csv_writer.writerow(lt_data.values())  # use values of the dict
                                    csv_writer.writerow([lt_data.get(col, 0) for col in mbc_t6_t12_columns])  # make a list value in the order of the dict columns and write them

                            else:

                                with open(f"{file_path}/{csv_filename}", 'w', newline='') as open_csvfile:
                                    cs_writer = csv.writer(open_csvfile)
                                    cs_writer.writerow(mbc_t6_t12_columns)
                                    new_lt_data = data_result  # typecast the string to dict
                                    # cs_writer.writerow(lt_data)  # use the dict
                                    cs_writer.writerow([new_lt_data.get(col, 0) for col in mbc_t6_t12_columns])  # make a list value in the order of the dict columns and write them

                        elif str(data_result['redcap_event_name'])[0:3].rstrip('_').upper() in mbc_fever_visits:

                            # write the fever visits lab result to csv file
                            mbc_fever_visits_columns = csv_columns["M19_FBC_FV"].values()

                            csv_filename = f'{strftime("%Y%m%d", localtime())}_mbc_fevervisit_labresult.csv'

                            if is_not_empty_file(f'{file_path}/{csv_filename}'):

                                with open(f'{file_path}/{csv_filename}', 'a', newline="") as csvfile:
                                    writer = csv.writer(csvfile)
                                    lf_data = dict(data_result)  # typecast the string to dict
                                    # writer.writerow(lf_data.values())  # use values of the dict
                                    writer.writerow([lf_data.get(col, 0) for col in mbc_fever_visits_columns])  # make a list value in the order of the dict columns and write them

                            else:

                                # print(data)
                                with open(f"{file_path}/{csv_filename}", 'w', newline='') as csvfile:
                                    cs_writer = csv.writer(csvfile)
                                    cs_writer.writerow(mbc_fever_visits_columns)
                                    new_data = data_result  # typecast the string to list
                                    # cs_writer.writerow(new_data)  # use the dict
                                    cs_writer.writerow([new_data.get(col, 0) for col in mbc_fever_visits_columns])  # make a list value in the order of the dict columns and write them
                else:
                    # pedvac columns
                    pedvac_columns = csv_columns["PEDVAC"].values()

                    csv_filename = f'{strftime("%Y%m%d", localtime())}_pedvac_labresult.csv'

                    if is_not_empty_file(f'{file_path}/{csv_filename}'):

                        with open(f"{file_path}/{csv_filename}", 'a', newline='') as open_csvfile:
                            pcsv_writer = csv.writer(open_csvfile)
                            # for row in analysis_result[r]:
                            lab_data = data_result  # typecast the string to dict
                            # csv_writer.writerow(lt_data.values())  # use values of the dict
                            pcsv_writer.writerow([lab_data.get(col, 0) for col in pedvac_columns])  # make a list value in the order of the dict columns and write them

                    else:

                        with open(f"{file_path}/{csv_filename}", 'w', newline='') as open_csvfile:
                            pcs_writer = csv.writer(open_csvfile)
                            pcs_writer.writerow(pedvac_columns)
                            lab_data = data_result  # typecast the string to dict
                            # cs_writer.writerow(lt_data)  # use the dict
                            pcs_writer.writerow([lab_data.get(col, 0) for col in pedvac_columns])  # make a list value in the order of the dict columns and write them

    except IOError as ioe:
        logger.debug(f"An error occurred while writing to the file. {ioe}", exc_info=True)
    except Exception as e:
        logger.exception(f'An error occurred while writing to the file. {e}', exc_info=True)
    else:
        logger.info("Data successfully written to CSV file!!!")


# this function is to sort the analysis by their SortKey
def sort_analysis(analysis):
    try:
        sort_key_values = []
        for sk in range(len(analysis) - 2):
            sort_key_values.append(analysis[sk]["SortKey"])

        new_analysis = analysis.copy()

        for i in range(len(analysis) - 2):
            index = 0
            if analysis[i]["SortKey"] in sort_key_values:
                # the wbc sort key in senaite is 0. Its output is null in the api call.
                # assign 0 to the variable index instead of null for sort the analysis
                if not analysis[i]["SortKey"]:
                    index = 0
                else:
                    index = int(analysis[i]["SortKey"])
                # print(n)

            # used the replacement method of the list to rearrange or sort the analysis from 0 - nth number
            # Change or Replacement: To change the value of a specific item, refer to the index number
            new_analysis[index] = analysis[i]

    except KeyError as kr:
        logger.error(f"A key error occurred - {kr}", exc_info=True)
    except Exception as error:
        logger.exception(f"Exception Occurred. {error}", exc_info=True)
    else:
        return new_analysis


def check_internet_connection(redcap_url):
    try:
        pass
        # connect to a URL
        url(redcap_url, timeout=30)
        logger.info('Internet or REDCap Server connection is available')
        return True

    except ConnectionError as cr:
        logger.error(f"Connection error - {cr}", exc_info=True)
    except URLError as urlerror:
        logger.error(f"Internet or REDCap Server connection is not available. {urlerror}", exc_info=True)
        return False


def check_senaite_connection():
    s = ""
    try:
        # global senaite_server = "http://172.102.10.1"  # get the senaite url from the user (use  cli argument)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        # print("Socket successfully created")
    except socket.error as error:
        logger.error("socket creation failed with error %s" % error, exc_info=True)

    port = 80

    try:
        host_ip = socket.gethostbyname("www.google.com")
    except socket.gaierror as sg:
        logger.error("there was an error resolving the host", exc_info=True)
        sys.exit()
    else:
        s.connect((host_ip, port))
        logger.info("the socket has successfully connected to SENAITE")

    # try:
    #    s.connect((senaite_server, port))
    #    return True
    # except socket.error:
    #    print(socket.error.strerror)
    #    return False
    # finally:
    #    s.close()


# stop logging
logging.shutdown()

if __name__ == '__main__':
    data = [
        {
            "m_subbarcode": "M19-20754-T0--1",
            "redcap_event_name": "f6_arm_2",
            "lf_datefbc_t": "2023-11-02 09:54",
            "lf_fbcpdw_q": 11.2,
            "lf_fbcrbc_q": 4.19,
            "lf_fbcmpv_q": 9.6,
            "lf_fbcwbc_q": 8.34,
            "lf_fbcneutpro_q": 39.6,
            "lf_fbcneut_q": 3.3,
            "lf_fbcmchc_q": 33.8,
            "lf_fbcplt_q": 311.0,
            "lf_fbcmcv_q": 68.5,
            "lf_fbcplcr_q": 23.4,
            "lf_fbclym_q": 4.16,
            "lf_fbcrdwsd_q": 43.5,
            "lf_fbclympro_q": 49.9,
            "lf_fbcpct_q": 0.3,
            "lf_fbchct_q": 28.7,
            "lf_fbcmch_q": 23.2,
            "lf_fbcrdwcv_q": 17.3,
            "lf_fbcmid_q": 0.71,
            "lf_fbcmidpro_q": 8.5
        },
        {
            "m_subbarcode": "M19-21217-T0--1",
            "redcap_event_name": "t7_arm_2",
            "lt6_datefbc_t": "2023-11-02 12:48",
            "lt6_fbcpdw_q": 9.0,
            "lt6_fbcrbc_q": 5.18,
            "lt6_fbcmpv_q": 8.6,
            "lt6_fbcwbc_q": 8.2,
            "lt6_fbcneutpro_q": 21.9,
            "lt6_fbcneut_q": 1.8,
            "lt6_fbcmchc_q": 31.4,
            "lt6_fbcplt_q": 306.0,
            "lt6_fbcmcv_q": 72.0,
            "lt6_fbcplcr_q": 14.8,
            "lt6_fbclym_q": 5.36,
            "lt6_fbcrdwsd_q": 45.7,
            "lt6_fbclympro_q": 65.4,
            "lt6_fbcpct_q": 0.26,
            "lt6_fbchct_q": 37.3,
            "lt6_fbcmch_q": 22.6,
            "lt6_fbcrdwcv_q": 18.9,
            "lt6_fbcmid_q": 0.48,
            "lt6_fbchgb_q": 11.7,
            "lt6_fbcmidpro_q": 5.9
        }
    ]
    # check_internet_connection("https://redcap.bibbox.bnitm.de/")
    # check_senaite_connection()
    write_result_csv("./data/import_data.json", 'P21')  # ./data/import_data.json   <class 'list'>
    # read_json("data/import_data.json")
    # write_json("data/import_data.json")
