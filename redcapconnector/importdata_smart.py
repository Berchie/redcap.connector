import os
import re
# import sys
# from pathlib import Path
from time import localtime, strftime
from redcapconnector.functions import read_json, check_internet_connection, write_result_csv
from dotenv import dotenv_values, load_dotenv
import requests
import json
import logging.config
# import yaml
import logging
import csv
# from redcapconnector.sendemail import email_notification
from loguru import logger
from redcapconnector.config.log_config import handlers


# setting up the logging
logger.configure(
    handlers=handlers,
)

# load .env variables
dotenv_path = os.path.abspath(f"{os.environ['HOME']}/.env")
if os.path.abspath(f"{os.environ['HOME']}/.env"):
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise logging.exception('Could not found the application environment variables!')

# bio-chemistry fieldnames
um_fieldnames = ["id_um","redcap_event_name","redcap_data_access_group","visit_no_sid","sptaken_heparin","pro_heparin","c10_2_if_done","c07_heparin", "c07_2_if_done","ggt_heparin","c09_2_if_done","alb_heparin","c05_2_if_done","alp_heparin","c08_2_if_done","c04_1_bild","c04_1", "alt_heparin","c05_2_if_done_2","c03_1_bilt","c03_2_if_done"]
sm_fieldnames = ["id_um","redcap_event_name","redcap_data_access_group","visit_no_sid","sptaken_heparin","urea_heparin","c11_2_if_done","gluc_heparin", "c13_2_if_done","crea_heparin","c12_2_if_done", "lact_heparin", "c14_2_if_done"]

# writing the imported results to CSV file (SMART project)
@logger.catch
def result_csv_smart(sample_type, jsonfile, case_type):
    if case_type == "UM":
        case = 'um'
    elif case_type == "SM":
        case = 'sm'
    else:
        case = 'rm'

    if sample_type == 'EDTA Blood':
        csv_file = os.path.join(os.path.dirname(__file__), "data", "csv", f"smart_{case}_haematology.csv")
    else:
        csv_file = os.path.join(os.path.dirname(__file__), "data", "csv", f"smart_{case}_biochemistry.csv")

    # open or read the json file
    with open(os.path.join(os.path.dirname(__file__), "data", jsonfile), 'r') as json_file:
        json_results = json.load(json_file)

        # open the csv file
        if sample_type == "EDTA Blood":
            if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
                with open(csv_file, 'a', newline='', encoding='utf-8-sig') as data_file:
                    csv_writer = csv.DictWriter(data_file, json_results[0].keys())
                    # csv_writer.writeheader()

                    for row in json_results:
                        new_row = {
                            "id_um": row["id_um"],
                            "redcap_event_name": row["redcap_event_name"],
                            "redcap_data_access_group": row["redcap_data_access_group"],
                            "visit_no_edta": row["visit_no_edta"],
                            "hgb_edta": row["hgb_edta"],
                            "mon_edta": row["mon_edta"],
                            "bas_edta": row["bas_edta"],
                            "rbc_edta": row["rbc_edta"],
                            "lym_edta": row["lym_edta"],
                            "hct_edta": row["hct_edta"],
                            "eosi_edta": row["eosi_edta"],
                            "wbc_edta": row["wbc_edta"],
                            "neu_edta": row["neu_edta"],
                            "plt_edta": row["plt_edta"]
                        }
                        csv_writer.writerow(new_row)
            else:
                with open(csv_file, 'a', newline='', encoding='utf-8-sig') as data_file:
                    csv_writer = csv.DictWriter(data_file, json_results[0].keys())
                    csv_writer.writeheader()

                    for row in json_results:
                        new_row = {
                            "id_um": row["id_um"],
                            "redcap_event_name": row["redcap_event_name"],
                            "redcap_data_access_group": row["redcap_data_access_group"],
                            "visit_no_edta": row["visit_no_edta"],
                            "hgb_edta": row["hgb_edta"],
                            "mon_edta": row["mon_edta"],
                            "bas_edta": row["bas_edta"],
                            "rbc_edta": row["rbc_edta"],
                            "lym_edta": row["lym_edta"],
                            "hct_edta": row["hct_edta"],
                            "eosi_edta": row["eosi_edta"],
                            "wbc_edta": row["wbc_edta"],
                            "neu_edta": row["neu_edta"],
                            "plt_edta": row["plt_edta"]
                        }
                        csv_writer.writerow(new_row)
        else:
            if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
                with open(csv_file, 'a', newline='', encoding='utf-8-sig') as data_file:
                    if case_type == "UM":
                        csv_writer = csv.DictWriter(data_file, fieldnames=um_fieldnames)
                    else:
                        csv_writer = csv.DictWriter(data_file, fieldnames=sm_fieldnames)
                    # csv_writer.writeheader()

                    for row in json_results:
                        if case_type == "UM":
                            new_row = {
                                "id_um": row["id_um"],
                                "redcap_event_name": row["redcap_event_name"],
                                "redcap_data_access_group": row["redcap_data_access_group"],
                                "visit_no_sid": row["visit_no_sid"],
                                "sptaken_heparin": row["sptaken_heparin"],
                                "pro_heparin": row.get("pro_heparin","2"),
                                "c10_2_if_done": row.get("c10_2_if_done",0),
                                "ggt_heparin": row.get("ggt_heparin","2"),
                                "c09_2_if_done": row.get("c09_2_if_done",0),
                                "c07_heparin": row.get("c07_heparin","2"),
                                "c07_2_if_done": row.get("c07_2_if_done", 0),
                                "alb_heparin": row.get("alb_heparin", "2"),
                                "c05_2_if_done": row.get("c05_2_if_done", 0),
                                "alp_heparin": row.get("alp_heparin", "2"),
                                "c08_2_if_done": row.get("c08_2_if_done", 0),
                                "c04_1_bild": row.get("c04_1_bild", "2"),
                                "c04_1": row.get("c04_1", 0),
                                "alt_heparin": row.get("alt_heparin", "2"),
                                "c05_2_if_done_2": row.get("c05_2_if_done_2", 0),
                                "c03_1_bilt": row.get("c03_1_bilt", "2"),
                                "c03_2_if_done": row.get("c03_2_if_done", 0),
                            }
                        elif case_type == "SM":
                            new_row = {
                                "id_um": row["id_um"],
                                "redcap_event_name": row["redcap_event_name"],
                                "redcap_data_access_group": row["redcap_data_access_group"],
                                "visit_no_sid": row["visit_no_sid"],
                                "sptaken_heparin": row["sptaken_heparin"],
                                "lact_heparin": row.get("lact_heparin", "2"),
                                "c14_2_if_done": row.get("c14_2_if_done", 0),
                                "gluc_heparin": row.get("gluc_heparin", "2"),
                                "c13_2_if_done": row.get("c13_2_if_done", 0),
                                "urea_heparin": row.get("urea_heparin", "2"),
                                "c11_2_if_done": row.get("c11_2_if_done", 0),
                                "crea_heparin": row.get("crea_heparin", "2"),
                                "c12_2_if_done": row.get("c12_2_if_done", 0)
                            }
                        csv_writer.writerow(new_row)
            else:
                with open(csv_file, 'a', newline='', encoding='utf-8-sig') as data_file:
                    if case_type == "UM":
                        csv_writer = csv.DictWriter(data_file, fieldnames=um_fieldnames)
                    else:
                        csv_writer = csv.DictWriter(data_file, fieldnames=sm_fieldnames)

                    csv_writer.writeheader()

                    for row in json_results:
                        if case_type == "UM":
                            new_row = {
                                "id_um": row["id_um"],
                                "redcap_event_name": row["redcap_event_name"],
                                "redcap_data_access_group": row["redcap_data_access_group"],
                                "visit_no_sid": row["visit_no_sid"],
                                "sptaken_heparin": row["sptaken_heparin"],
                                "pro_heparin": row.get("pro_heparin","2"),
                                "c10_2_if_done": row.get("c10_2_if_done",0),
                                "ggt_heparin": row.get("ggt_heparin","2"),
                                "c09_2_if_done": row.get("c09_2_if_done",0),
                                "c07_heparin": row.get("c07_heparin","2"),
                                "c07_2_if_done": row.get("c07_2_if_done", 0),
                                "alb_heparin": row.get("alb_heparin", "2"),
                                "c05_2_if_done": row.get("c05_2_if_done", 0),
                                "alp_heparin": row.get("alp_heparin", "2"),
                                "c08_2_if_done": row.get("c08_2_if_done", 0),
                                "c04_1_bild": row.get("c04_1_bild", "2"),
                                "c04_1": row.get("c04_1", 0),
                                "alt_heparin": row.get("alt_heparin", "2"),
                                "c05_2_if_done_2": row.get("c05_2_if_done_2", 0),
                                "c03_1_bilt": row.get("c03_1_bilt", "2"),
                                "c03_2_if_done": row.get("c03_2_if_done", 0),
                            }
                        elif case_type == "SM":
                            new_row = {
                                "id_um": row["id_um"],
                                "redcap_event_name": row["redcap_event_name"],
                                "redcap_data_access_group": row["redcap_data_access_group"],
                                "visit_no_sid": row["visit_no_sid"],
                                "sptaken_heparin": row["sptaken_heparin"],
                                "lact_heparin": row.get("lact_heparin", "2"),
                                "c14_2_if_done": row.get("c14_2_if_done", 0),
                                "gluc_heparin": row.get("gluc_heparin", "2"),
                                "c13_2_if_done": row.get("c13_2_if_done", 0),
                                "urea_heparin": row.get("urea_heparin", "2"),
                                "c11_2_if_done": row.get("c11_2_if_done", 0),
                                "crea_heparin": row.get("crea_heparin", "2"),
                                "c12_2_if_done": row.get("c12_2_if_done", 0)
                            }
                        csv_writer.writerow(new_row)


# convert json data to CSV file for the daily run (SMART Project)
@logger.catch
def json_csv_smart(smart_type, jsonfile, case_type):
    if case_type == "UM":
        case = 'um'
    elif case_type == "SM":
        case = 'sm'
    else:
        case = 'rm'

    if smart_type == 'EDTA Blood':
        csv_file = os.path.join(os.path.dirname(__file__), "data", "daily_result", f"{strftime("%Y%m%d", localtime())}_smart_{case}_haematology.csv")
    else:
        csv_file = os.path.join(os.path.dirname(__file__), "data", "daily_result", f"{strftime("%Y%m%d", localtime())}_smart_{case}_biochemistry.csv")

    # open or read the json file
    with open(os.path.join(os.path.dirname(__file__), "data", jsonfile), 'r') as json_file:
        json_results = json.load(json_file)

        # open the csv file
        if smart_type=="EDTA Blood":
            if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
                with open(csv_file, 'a', newline='', encoding='utf-8-sig') as data_file:
                    csv_writer = csv.DictWriter(data_file, json_results[0].keys())
                    # csv_writer.writeheader()

                    for row in json_results:
                        new_row = {
                            "id_um": row["id_um"],
                            "redcap_event_name": row["redcap_event_name"],
                            "redcap_data_access_group": row["redcap_data_access_group"],
                            "visit_no_edta": row["visit_no_edta"],
                            "hgb_edta": row["hgb_edta"],
                            "mon_edta": row["mon_edta"],
                            "bas_edta": row["bas_edta"],
                            "rbc_edta": row["rbc_edta"],
                            "lym_edta": row["lym_edta"],
                            "hct_edta": row["hct_edta"],
                            "eosi_edta": row["eosi_edta"],
                            "wbc_edta": row["wbc_edta"],
                            "neu_edta": row["neu_edta"],
                            "plt_edta": row["plt_edta"]
                        }
                        csv_writer.writerow(new_row)
            else:
                with open(csv_file, 'a', newline='', encoding='utf-8-sig') as data_file:
                    csv_writer = csv.DictWriter(data_file, json_results[0].keys())
                    csv_writer.writeheader()

                    for row in json_results:
                        new_row = {
                            "id_um": row["id_um"],
                            "redcap_event_name": row["redcap_event_name"],
                            "redcap_data_access_group": row["redcap_data_access_group"],
                            "visit_no_edta": row["visit_no_edta"],
                            "hgb_edta": row["hgb_edta"],
                            "mon_edta": row["mon_edta"],
                            "bas_edta": row["bas_edta"],
                            "rbc_edta": row["rbc_edta"],
                            "lym_edta": row["lym_edta"],
                            "hct_edta": row["hct_edta"],
                            "eosi_edta": row["eosi_edta"],
                            "wbc_edta": row["wbc_edta"],
                            "neu_edta": row["neu_edta"],
                            "plt_edta": row["plt_edta"]
                        }
                        csv_writer.writerow(new_row)
        else:
            if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
                with open(csv_file, 'a', newline='', encoding='utf-8-sig') as data_file:
                    if case_type == "UM":
                        csv_writer = csv.DictWriter(data_file, fieldnames=um_fieldnames)
                    else:
                        csv_writer = csv.DictWriter(data_file, fieldnames=sm_fieldnames)
                    # csv_writer.writeheader()

                    for row in json_results:
                        if case_type == "UM":
                            new_row = {
                                "id_um": row["id_um"],
                                "redcap_event_name": row["redcap_event_name"],
                                "redcap_data_access_group": row["redcap_data_access_group"],
                                "visit_no_sid": row["visit_no_sid"],
                                "sptaken_heparin": row["sptaken_heparin"],
                                "pro_heparin": row.get("pro_heparin","2"),
                                "c10_2_if_done": row.get("c10_2_if_done",0),
                                "ggt_heparin": row.get("ggt_heparin","2"),
                                "c09_2_if_done": row.get("c09_2_if_done",0),
                                "c07_heparin": row.get("c07_heparin","2"),
                                "c07_2_if_done": row.get("c07_2_if_done", 0),
                                "alb_heparin": row.get("alb_heparin", "2"),
                                "c05_2_if_done": row.get("c05_2_if_done", 0),
                                "alp_heparin": row.get("alp_heparin", "2"),
                                "c08_2_if_done": row.get("c08_2_if_done", 0),
                                "c04_1_bild": row.get("c04_1_bild", "2"),
                                "c04_1": row.get("c04_1", 0),
                                "alt_heparin": row.get("alt_heparin", "2"),
                                "c05_2_if_done_2": row.get("c05_2_if_done_2", 0),
                                "c03_1_bilt": row.get("c03_1_bilt", "2"),
                                "c03_2_if_done": row.get("c03_2_if_done", 0),
                            }
                        elif case_type == "SM":
                            new_row = {
                                "id_um": row["id_um"],
                                "redcap_event_name": row["redcap_event_name"],
                                "redcap_data_access_group": row["redcap_data_access_group"],
                                "visit_no_sid": row["visit_no_sid"],
                                "sptaken_heparin": row["sptaken_heparin"],
                                "lact_heparin": row.get("lact_heparin", "2"),
                                "c14_2_if_done": row.get("c14_2_if_done", 0),
                                "gluc_heparin": row.get("gluc_heparin", "2"),
                                "c13_2_if_done": row.get("c13_2_if_done", 0),
                                "urea_heparin": row.get("urea_heparin", "2"),
                                "c11_2_if_done": row.get("c11_2_if_done", 0),
                                "crea_heparin": row.get("crea_heparin", "2"),
                                "c12_2_if_done": row.get("c12_2_if_done", 0)
                            }
                        csv_writer.writerow(new_row)
            else:
                with open(csv_file, 'a', newline='', encoding='utf-8-sig') as data_file:
                    if case_type == "UM":
                        csv_writer = csv.DictWriter(data_file, fieldnames=um_fieldnames)
                    else:
                        csv_writer = csv.DictWriter(data_file, fieldnames=sm_fieldnames)

                    csv_writer.writeheader()

                    for row in json_results:
                        if case_type == "UM":
                            new_row = {
                                 "id_um": row["id_um"],
                                "redcap_event_name": row["redcap_event_name"],
                                "redcap_data_access_group": row["redcap_data_access_group"],
                                "visit_no_sid": row["visit_no_sid"],
                                "sptaken_heparin": row["sptaken_heparin"],
                                "pro_heparin": row.get("pro_heparin","2"),
                                "c10_2_if_done": row.get("c10_2_if_done",0),
                                "ggt_heparin": row.get("ggt_heparin","2"),
                                "c09_2_if_done": row.get("c09_2_if_done",0),
                                "c07_heparin": row.get("c07_heparin","2"),
                                "c07_2_if_done": row.get("c07_2_if_done", 0),
                                "alb_heparin": row.get("alb_heparin", "2"),
                                "c05_2_if_done": row.get("c05_2_if_done", 0),
                                "alp_heparin": row.get("alp_heparin", "2"),
                                "c08_2_if_done": row.get("c08_2_if_done", 0),
                                "c04_1_bild": row.get("c04_1_bild", "2"),
                                "c04_1": row.get("c04_1", 0),
                                "alt_heparin": row.get("alt_heparin", "2"),
                                "c05_2_if_done_2": row.get("c05_2_if_done_2", 0),
                                "c03_1_bilt": row.get("c03_1_bilt", "2"),
                                "c03_2_if_done": row.get("c03_2_if_done", 0),
                            }
                        elif case_type == "SM":
                            new_row = {
                                "id_um": row["id_um"],
                                "redcap_event_name": row["redcap_event_name"],
                                "redcap_data_access_group": row["redcap_data_access_group"],
                                "visit_no_sid": row["visit_no_sid"],
                                "sptaken_heparin": row["sptaken_heparin"],
                                "lact_heparin": row.get("lact_heparin", "2"),
                                "c14_2_if_done": row.get("c14_2_if_done", 0),
                                "gluc_heparin": row.get("gluc_heparin", "2"),
                                "c13_2_if_done": row.get("c13_2_if_done", 0),
                                "urea_heparin": row.get("urea_heparin", "2"),
                                "c11_2_if_done": row.get("c11_2_if_done", 0),
                                "crea_heparin": row.get("crea_heparin", "2"),
                                "c12_2_if_done": row.get("c12_2_if_done", 0)
                            }
                        csv_writer.writerow(new_row)


def data_import(sample):
    # m19_csv_file = 'import_m19_data.csv'
    # p21_csv_file = 'import_p21_data.csv'
    # record = f'{os.path.abspath("..")}/data/import_data.json'
    case_title = ""

    # create for loop import the two json files
    try:
        case_type = ("UM", "RM", "SM")

        for case in case_type:

            if case == "UM":
                record = os.path.join(os.path.dirname(__file__), "data", "smart_um_import_data.json")

                # API TOKEN for the REDCap database
                api_token = os.environ['SMART_UM_API_TOKEN']

                json_file = "smart_um_import_data.json"
            elif case == "RM":

                record = os.path.join(os.path.dirname(__file__), "data", "smart_rm_import_data.json")

                # API TOKEN for the REDCap database
                api_token = os.environ['SMART_SM_API_TOKEN']

                json_file = "smart_rm_import_data.json"

            else:
                # SM
                record = os.path.join(os.path.dirname(__file__), "data", "smart_sm_import_data.json")

                # API TOKEN for the REDCap database
                api_token = os.environ.get("SMART_SM_API_TOKEN")

                json_file = "smart_sm_import_data.json"

            # load the .env values
            env_config = dotenv_values("../.env")

            # read the file import_json file
            if os.path.getsize(record) != 0:
                with open(record) as jf:
                    import_record = json.load(jf)

                data = json.dumps(import_record)

                # API TOKEN for the REDCap database
                # api_token = os.environ['SMART_API_TOKEN']

                if case == "RM":
                    rm_data = {
                        'token': '935BB33DD80F87535B923024CA5E0782',
                        'content': 'record',
                        'action': 'import',
                        'format': 'json',
                        'type': 'flat',
                        'overwriteBehavior': 'overwrite',
                        'forceAutoNumber': 'false',
                        'data': data,
                        'returnContent': 'count',
                        'returnFormat': 'json'
                    }
                else:
                    fields = {
                        'token': api_token,
                        'content': 'record',
                        'action': 'import',
                        'format': 'json',  # json csv
                        'type': 'flat',
                        'overwriteBehavior': 'normal',  # overwrite normal
                        'data': data,
                        'returnContent': 'ids',  # count #ids
                        'returnFormat': 'json'
                    }

                # check for internet is available or REDCap server is online(available)
                if check_internet_connection("https://redcap-kccr.bibbox.bnitm.de/"):
                    # import records into the REDCap database
                    if case == "RM":
                        r = requests.post(os.environ['SMART_API_URL'], data=rm_data, timeout=15)
                    else:
                        r = requests.post(os.environ['SMART_API_URL'], data=fields, timeout=15)
                    # print(f'HTTP Status: {str(r.status_code)}')
                    res = r.json()

                    count = len(res)

                    if r.status_code == 200:
                        if sample == 'EDTA Blood':
                            logger.success(f"{count} of SMART {case}'s FBC record(s) were imported successfully!!!")
                        else:
                            logger.success(f"{count} of SMART {case}'s BioChemistry record(s) were imported successfully!")

                        # import_success_msg = f"{count} of SMART's BioChemistry record(s) were imported successfully!"
                        # sample_ids = res

                        # email notification
                        # email_notification(msg=import_success_msg, record_id=record_ids)

                        # convert json to CSV
                        json_csv_smart(sample, json_file, case)

                        # write the import data to CSV file
                        result_csv_smart(sample, json_file, case)

                    else:
                        error_msg = re.sub(r"[\\{}]", "", r.text)
                        logger.error(f'HTTP Status:{r.status_code} - {error_msg}')

            else:
                if sample == "EDTA Blood":
                    logger.info(f"No SMART {case}'s  FBC results to import.")
                else:
                    logger.info(f"No SMART {case}'s BioChemistry results to import.")

            # when record successful imported write it to csv(import_data_[date&time])
            # or json file(imported_fbc_data.json). use function for both.
            # write_result_csv(data)

    except IOError as ioerror:
        logger.error(f"There's an error importing data. {ioerror}", exc_info=True)
    except Exception as error:
        logging.exception(f"Exception Occurred. {error}", exc_info=True)


if __name__ == '__main__':
    data_import("Heparin")
    # logger.info('import log test')
    # record_data = os.path.join(os.path.dirname(__file__), "data", "smart_sm_import_data.json")
    # json_csv_smart(smart_type= "Heparin",jsonfile=record_data, case_type= "SM")