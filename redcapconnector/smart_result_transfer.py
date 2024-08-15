import os
import configparser
import re
from pprint import pprint

import requests
import json
import logging.config
from dotenv import dotenv_values, load_dotenv
from loguru import logger
from redcapconnector.config.log_config import handlers
from redcapconnector.functions import read_json, write_json_smart
from redcapconnector.importdata_smart import data_import

# setting up the logging
logger.configure(
    handlers=handlers
)

# load .env variables
dotenv_path = os.path.abspath(f"{os.environ['HOME']}/.env")
if os.path.abspath(f"{os.environ['HOME']}/.env"):
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise logging.error('Could not found the application environment variables!')

# load the cookie.ini file values
cookie_config = configparser.ConfigParser()
cookie_config.read(os.path.join(os.path.dirname(__file__), "config", "cookie.ini"))

# read (load) smart_variables.json file
smart_variables = read_json(os.path.join(os.path.dirname(__file__), "config", "smart_variables.json"))


# clear the content in the import_data.json file
@logger.catch
def clear_import_json_file(json_file):
    if os.path.exists(os.path.join(os.path.dirname(__file__), "data", json_file)):
        with open(os.path.join(os.path.dirname(__file__), "data", json_file), 'r+') as importfile:
            # check if the file is not empty
            if importfile.read() is not None:
                # clear the file content
                importfile.truncate(0)


clear_import_json_file("smart_um_import_data.json")
clear_import_json_file("smart_sm_import_data.json")
clear_import_json_file("smart_rm_import_data.json")


def get_event_name(pid):
    try:
        event_dic = []
        pid_code = pid[:5]
        smart_api_token = ''

        if pid_code == "S24-1":
            smart_api_token = os.environ["SMART_UM_API_TOKEN"]
        elif pid_code == "S24-2":
            smart_api_token = os.environ["SMART_SM_API_TOKEN"]
        else:
            # RM
            smart_api_token = os.environ["SMART_RM_API_TOKEN"]

        data = {
            'token': smart_api_token,
            'content': 'event',
            'format': 'json',
            'returnFormat': 'json'
        }
        # r = requests.post('https://redcap-testing.bibbox.bnitm.de/api/', data=data)
        r = requests.post('https://redcap-kccr.bibbox.bnitm.de/api/', data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(r.json())
        events = json.loads(json.dumps(r.json()))
        # print(json.dumps(events, indent=4))
        for event in events:
            event_dic.append(event["unique_event_name"])

        return event_dic

    except ConnectionError as cerror:
        logger.error(f"Connection Error to REDCap database. Check your internet connection: {cerror}")


def get_group_name():
    try:
        data = {
            'token': os.environ["SMART_UM_API_TOKEN"],
            'content': 'dag',
            'format': 'json',
            'returnFormat': 'json'
        }
        r = requests.post('https://redcap-testing.bibbox.bnitm.de/api/', data=data)
        # print('HTTP Status: ' + str(r.status_code))
        print(json.dumps(r.json(), indent=4))
    except ConnectionError as ce:
        logger.error(f"Connection Error to REDCap database. {ce.errno}:{ce.strerror}")


def get_record_id(pid):
    try:

        # extract the 5 character of the pid to use for which pid variable to use
        pid_code = pid[:5]
        pid_var = ''
        smart_api_token = ''

        if pid_code == 'S24-1':
            pid_var = 'h01_3um'
            smart_api_token = os.environ["SMART_UM_API_TOKEN"]
        elif pid_code == 'S24-2':
            pid_var = 'h01_3umsm'
            smart_api_token = os.environ["SMART_SM_API_TOKEN"]
        else:
            pid_var = 'pid_fup_rm'
            smart_api_token = os.environ["SMART_RM_API_TOKEN"]

        data = {
            'token': smart_api_token,
            'content': 'record',
            'action': 'export',
            'format': 'json',
            'type': 'flat',
            'csvDelimiter': '',
            'fields[0]': 'id_um',
            'forms': '',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json',
            'filterLogic': f'[{pid_var}] = \'{pid}\''
        }
        r = requests.post(os.environ['SMART_API_URL'], data=data)
        # print('HTTP Status: ' + str(r.status_code))
        # print(r.json())
        return json.loads(json.dumps(r.json()))

    except ConnectionError as cer:
        logger.error(cer.strerror)


@logger.catch
def extract_visit_day(sampleid):
    # print(sampleid)
    # visit_day = ''
    visit = sampleid[-3:]
    if visit[0:1] == ' ' or visit[0:1] == '-':
        if len(visit.strip('-')) == 2 or len(visit.strip(' ')) == 2:
            # visit = visit.strip('-') or visit.strip(' ')
            visit = visit[1:]
            visit_day = f"{visit.strip()[0:1]}0{visit[-1:]}"
            return smart_variables["VISIT_DAYS"][visit_day]
    else:
        visit_day = f"{visit.strip()[1:2]}0{visit[-1:]}"
        return smart_variables["VISIT_DAYS"][visit]

    # return smart_variables["VISIT_DAYS"][visit_day]


@logger.catch
def extract_event_name(sampleid, visitday, visithr=''):
    # sampleid -> fnc parameter
    # id_arm = get_record_id(sampleid[0:11])

    # if id_arm:
    # id_arm = id_arm[0]["redcap_event_name"][13:]

    id_arm = "arm_1"

    visit_hour = ''

    if visithr != '':
        if visithr[0:1] == "H":
            if len(visithr) == 2 and visithr[0:1] == "H":
                visit_hour = visithr[-1:]
            elif len(visithr) == 3 and visithr[0:2] == "H0":
                visit_hour = visithr[-1:]
            else:
                visit_hour = visithr[-2:]
        elif visithr[0:2] == "AL":
            # ALH00 ALH0
            if len(visithr[2:].strip()) == 2 and visithr[0:2] == "H":
                visit_hour = visithr[-1:]
            elif len(visithr[2:].strip()) == 3 and visithr[0:2] == "H0":
                visit_hour = visithr[-1:]
            else:
                visit_hour = visithr[-2:]
        else:
            visit_hour = ''

    visit_day = visitday

    events = get_event_name(sampleid[0:11])

    for event in events:
        evt_s = event.split('_')
        match evt_s[0]:
            case "hour":
                evt_s_day = '_'.join((evt_s[2], evt_s[3]))
                if len(evt_s[1]) == 1 and evt_s[1] == visit_hour and evt_s_day == visit_day and event[-5:] == id_arm:
                    return event
                elif len(evt_s[1]) == 2 and evt_s[1] == visit_hour and evt_s_day == visit_day and event[-5:] == id_arm:
                    return event
            case "al":
                # al_hour_8_day_0_arm_3 al_hour_24_day_arm_3
                evt_s_day = '_'.join((evt_s[3], evt_s[4]))
                if len(evt_s[2]) == 1 and evt_s[2] == visit_hour and evt_s_day == visit_day and event[-5:] == id_arm:
                    return event
                elif len(evt_s[2]) == 2 and evt_s[2] == visit_hour and evt_s_day == visit_day and event[-5:] == id_arm:
                    return event
            case "day":
                # print(id_arm)
                evt_s_day = '_'.join((evt_s[0], evt_s[1]))
                if evt_s_day == visit_day and event[-5:] == id_arm:
                    return event
                elif evt_s_day == visit_day and event[-5:] == id_arm:
                    return event
            case _:
                if evt_s[0] == visit_day and event[-5:] == id_arm:
                    return event


@logger.catch
def extract_edta_visit(sampleid, day, hour=''):
    id_arm = get_record_id(sampleid[0:11])

    if id_arm:  # if id_arm is not null then extract the redcap arm
        id_arm = id_arm[0]["redcap_event_name"][13:]

        visit_hour = ''

        if hour != '':
            if hour[0:1] == "H":
                if len(hour) == 2 and hour[0:1] == "H":
                    visit_hour = hour[-1:]
                elif len(hour) == 3 and hour[0:2] == "H0":
                    visit_hour = hour[-1:]
                else:
                    visit_hour = hour[-2:]
            elif hour[0:2] == "AL":
                # ALH00 ALH0
                if len(hour[2:].strip()) == 2 and hour[0:2] == "H":
                    visit_hour = hour[-1:]
                elif len(hour[2:].strip()) == 3 and hour[0:2] == "H0":
                    visit_hour = hour[-1:]
                else:
                    visit_hour = hour[-2:]
            else:
                visit_hour = ''

        visit_day = day

        events = get_event_name(sampleid[0:11])

        for event in events:
            event_s = event.split('_')
            # print(evt_s)
            match event_s[0]:
                case "hour":
                    event_s_hday = '_'.join((event_s[0], event_s[1], event_s[2], event_s[3]))
                    event_s_day = '_'.join((event_s[2], event_s[3]))
                    if event_s_hday in smart_variables["VISIT_NO_EDTA"]:
                        if len(event_s[1]) == 1 and event_s[1] == visit_hour and event_s_day == visit_day and event[-5:] == id_arm:
                            # print(evt[0:12])
                            return smart_variables["VISIT_NO_EDTA"][event_s_hday]
                        elif len(event_s[1]) == 2 and event_s[1] == visit_hour and event_s_day == visit_day and event[-5:] == id_arm:
                            # print(evt[0:12])  # hour_8_day_0_arm_4
                            return smart_variables["VISIT_NO_EDTA"][event_s_hday]
                case "day":
                    event_s_day = '_'.join((event_s[0], event_s[1]))
                    if event_s_day in smart_variables["VISIT_NO_EDTA"]:
                        if event_s_day == visit_day and event[-5:] == id_arm:
                            return smart_variables["VISIT_NO_EDTA"][event_s_day]
                        elif event_s_day == visit_day and event[-5:] == id_arm:
                            return smart_variables["VISIT_NO_EDTA"][event_s_day]
                case _:
                    if event_s[0] == visit_day and event[-5:] == id_arm:
                        return smart_variables["VISIT_NO_EDTA"]["U"]


@logger.catch
def extract_um_edta_visit(sampleid, day, hour=''):
    id_arm = get_record_id(sampleid[0:11])

    if id_arm:  # if id_arm is not null then extract the redcap arm
        id_arm = id_arm[0]["redcap_event_name"][13:]

        visit_hour = ''

        if hour != '':
            if hour[0:1] == "H":
                if len(hour) == 2 and hour[0:1] == "H":
                    visit_hour = hour[-1:]
                elif len(hour) == 3 and hour[0:2] == "H0":
                    visit_hour = hour[-1:]
                else:
                    visit_hour = hour[-2:]
            elif hour[0:2] == "AL":
                # ALH00 ALH0
                if len(hour[2:].strip()) == 2 and hour[0:2] == "H":
                    visit_hour = hour[-1:]
                elif len(hour[2:].strip()) == 3 and hour[0:2] == "H0":
                    visit_hour = hour[-1:]
                else:
                    visit_hour = hour[-2:]
            else:
                visit_hour = ''

        visit_day = day

        events = get_event_name(sampleid[0:11])

        for event in events:
            event_s = event.split('_')
            # print(evt_s)
            match event_s[0]:
                case "hour":
                    event_s_hday = '_'.join((event_s[0], event_s[1], event_s[2], event_s[3]))
                    event_s_day = '_'.join((event_s[2], event_s[3]))
                    if event_s_hday in smart_variables["UM_VISIT_NO_EDTA"]:
                        if len(event_s[1]) == 1 and event_s[1] == visit_hour and event_s_day == visit_day and event[-5:] == id_arm:
                            # print(evt[0:12])
                            return smart_variables["UM_VISIT_NO_EDTA"][event_s_hday]
                        elif len(event_s[1]) == 2 and event_s[1] == visit_hour and event_s_day == visit_day and event[-5:] == id_arm:
                            # print(evt[0:12])  # hour_8_day_0_arm_4
                            return smart_variables["UM_VISIT_NO_EDTA"][event_s_hday]
                case "day":
                    event_s_day = '_'.join((event_s[0], event_s[1]))
                    if event_s_day in smart_variables["UM_VISIT_NO_EDTA"]:
                        if event_s_day == visit_day and event[-5:] == id_arm:
                            return smart_variables["UM_VISIT_NO_EDTA"][event_s_day]
                        elif event_s_day == visit_day and event[-5:] == id_arm:
                            return smart_variables["UM_VISIT_NO_EDTA"][event_s_day]
                case _:
                    if event_s[0] == visit_day and event[-5:] == id_arm:
                        return smart_variables["UM_VISIT_NO_EDTA"]["U"]


@logger.catch
def extract_heparin_visit(sample_id):
    visit = ''

    if len(sample_id.strip()) == 11:
        visit = smart_variables["VISIT_NO_HEPARIN"]["D00"]
    elif 12 < len(sample_id) <= 15:
        visit_code = sample_id[-3:]
        print(visit_code)

        if visit_code[0:1] == '-' or visit_code[0:1] == ' ':
            visit_code = visit_code[1:].strip()
            print(visit_code)

        visit_keys = smart_variables["VISIT_NO_HEPARIN"].keys()

        if visit_code in visit_keys:
            visit = smart_variables["VISIT_NO_HEPARIN"][visit_code]

    return visit


@logger.catch
def extract_rm_edta_visit(sample_id):
    visit = ''

    if len(sample_id.strip()) == 11:
        visit = smart_variables["VISIT_NO_FBC_RM"]["D07"]
    elif 12 < len(sample_id) <= 15:
        visit_code = sample_id[-3:]
        print(visit_code)

        if visit_code[0:1] == '-' or visit_code[0:1] == ' ':
            visit_code = visit_code[1:].strip()
            print(visit_code)

        visit_keys = smart_variables["VISIT_NO_FBC_RM"].keys()

        if visit_code in visit_keys:
            visit = smart_variables["VISIT_NO_FBC_RM"][visit_code]

    return visit


def transfer_smart_result(period, sample_type):
    try:
        smart_analysis_data = {}
        um_data = []
        sm_data = []
        rm_data = []
        next_batch = ''
        case_type = ''
        data_entry = ''

        # items_resp = requests.get(os.environ["BASE_URL"] + "/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": "SMART",
        items_resp = requests.get(f"{os.environ["BASE_URL"]}/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": "SMART",
                                                                              "sort_on": "getDateSampled", "getSampleTypeTitle": sample_type,
                                                                              "sort_order": "asc", "review_state": "published",
                                                                              "recent_modified": period, "children": "true"},
                                  cookies={cookie_config["Cookie"]["name"]: cookie_config["Cookie"]["value"]})

        next_pages = int(items_resp.json()["pages"])
        http_status_code = items_resp.status_code

        # print(items_resp.json())

        for batch in range(next_pages):

            if batch > 0:

                next_batch_resp = requests.get(next_batch, cookies={cookie_config["Cookie"]["name"]: cookie_config["Cookie"]["value"]})

                # returns respond data as a JSON object
                res_data = json.dumps(next_batch_resp.json())

                http_status_code = next_batch_resp.status_code

            else:
                # returns respond data as a JSON object
                res_data = json.dumps(items_resp.json())

            # cast the response json data to python object dictionary
            res_data_dict = json.loads(res_data)

            if http_status_code == 200 and res_data_dict["items"]:
                # returns JSON object as a dictionary
                res_data_dict_items = res_data_dict["items"]

                for item in range(len(res_data_dict_items)):

                    # extrac the sample id
                    client_sample_id = res_data_dict_items[item]["getClientSampleID"]

                    # get the redcap record id for 1st data entry
                    record_ids = get_record_id(client_sample_id[0:11])
                    record_id = ''
                    if record_ids:
                        if len(record_ids) > 1:
                            record_id = record_ids[0]['id_um']

                            # data entry
                            data_entry = record_ids[0]["id_um"][-3:]
                        else:
                            record_id = record_ids[0]['id_um']

                            # data entry
                            data_entry = record_ids[0]["id_um"][-3:]

                    vhour = res_data_dict_items[item]["getClientReference"]
                    vday = ''

                    # case type [UM|SM|RM]
                    if client_sample_id[:5] == "S24-1":
                        case_type = "UM"
                    elif client_sample_id[:5] == "S24-2":
                        case_type = "SM"
                    elif client_sample_id[:5] == "R01-1":
                        case_type = "RM"

                    if client_sample_id:
                        # S24-2001-AG-D04 S24-2001-AG-D4 S24-2001-AG
                        # "unique_group_name": "assin_fosu"
                        if 11 <= len(client_sample_id) <= 15:

                            # record id
                            smart_analysis_data.update({"id_um": record_id})

                            # event name (redcap_event_name)
                            if vhour == '':
                                if len(client_sample_id.strip()) == 11:
                                    cid = "-".join([client_sample_id, 'D00'])
                                    vday = extract_visit_day(cid)
                                    vhour = "H00"
                                    smart_analysis_data.update({"redcap_event_name": extract_event_name(cid, vday, vhour)})
                                elif 11 < len(client_sample_id.strip()) <= 15:
                                    vday = extract_visit_day(client_sample_id)
                                    if vday == 'day_3':
                                        vhour = 'H72'
                                    elif vday == 'day_0':
                                        vhour = "H00"
                                    smart_analysis_data.update({"redcap_event_name": extract_event_name(client_sample_id, vday, vhour)})
                                    # else:
                                    #     vhr = 'H00'
                                    #     smart_analysis_data.update({"redcap_event_name": extract_event_name(client_sample_id, vday, vhr)})
                            else:
                                vday = extract_visit_day(client_sample_id)
                                event_name = extract_event_name(client_sample_id, vday, vhour)
                                smart_analysis_data.update({"redcap_event_name": event_name})

                            # data access ground name
                            pid = client_sample_id[0:11]
                            smart_analysis_data.update({"redcap_data_access_group": smart_variables["DATA_ACCESS_GROUP"][pid[9:11]]})

                            # edta/biochemistry visit
                            # print(vhour)
                            if case_type == "UM":
                                if sample_type == "EDTA Blood":
                                    smart_analysis_data.update({"visit_no_edta": extract_um_edta_visit(client_sample_id, vday, vhour)})
                                    #getClientOrderNumber

                                    smart_analysis_data.update({"fblood_edta": "1"})

                                    smart_analysis_data.update({"c01_date_and_time_of_fbc": res_data_dict_items[item]["getClientOrderNumber"]})
                                else:
                                    # heparin
                                    smart_analysis_data.update({"visit_no_sid": extract_heparin_visit(client_sample_id, vday, vhour)})

                                    smart_analysis_data.update({"fblood_edta": "1"})

                            elif case_type == "SM":
                                if sample_type == "EDTA Blood":
                                    smart_analysis_data.update({"visit_no_edta": extract_edta_visit(client_sample_id, vday, vhour)})

                                    smart_analysis_data.update({"fblood_edta": "1"})

                                    smart_analysis_data.update({"c01_date_and_time_of_fbc": res_data_dict_items[item]["getClientOrderNumber"]})
                                else:
                                    # heparin
                                    smart_analysis_data.update({"visit_no_sid": extract_heparin_visit(client_sample_id)})

                                    smart_analysis_data.update({"fblood_edta": "1"})

                            else:
                                # "RM"
                                smart_analysis_data.update({"visitno_rm1": extract_rm_edta_visit(client_sample_id)})
                                smart_analysis_data.update({"b03_rm": "1"})
                                smart_analysis_data.update({"c01_rm1": res_data_dict_items[item]["getClientOrderNumber"]})

                            # children data
                            analysis_counts = res_data_dict_items[item]["children"]

                            # loop through the children object to get values or results of the analysis
                            for analysis_count in range(len(analysis_counts) - 1):
                                # check if the analysis title or name is found in the redcap_variables dictionary
                                # if children_data[child]["title"] in redcap_variables:
                                # if true, get the key value of the analysis title from the redcap_variables json file
                                # and use it as the key for the Result value e.g {"lf_fbchgb_q":"9.5"}

                                if sample_type == "EDTA Blood":
                                    # print(analysis_counts[analysis_count]["Result"])
                                    if analysis_counts[analysis_count].get("Result", "----") == "----":
                                        result = 00.00
                                    else:
                                        result = float(analysis_counts[analysis_count]["Result"])

                                    # analysis results/count
                                    fbc_keys = smart_variables["FBC"].keys()
                                    rm_fbc_keys = smart_variables["FBC_RM"].keys()
                                    fbc_title = re.sub(r'[\[\]]', '', str([analysis_counts[analysis_count]["title"]])).strip("'")
                                    # print(fbc_keys)
                                    if case_type == "RM":
                                        if fbc_title in rm_fbc_keys:
                                            smart_analysis_data.update({smart_variables["FBC_RM"][analysis_counts[analysis_count]["title"]]: result})

                                    else:

                                        if fbc_title in fbc_keys:
                                            smart_analysis_data.update({smart_variables["FBC"][analysis_counts[analysis_count]["title"]]: result})

                                else:
                                    # sample type -> Heparin Blood

                                    if analysis_counts[analysis_count]["Result"] == "----":
                                        heparin_result = 00.00
                                    else:
                                        heparin_result = float(analysis_counts[analysis_count]["Result"])

                                    # analysis count/results
                                    chem_keys = smart_analysis_data["BIOCHEMISTRY"].keys()
                                    chem_count_keys = sample_type["BIOCHEMISTRY_VALUE"].keys()
                                    chem_title = re.sub(r'[\[\]]', '', str([analysis_counts[analysis_count]["title"]])).strip("'")

                                    if analysis_counts[analysis_count]["Result"]:
                                        if chem_title in chem_keys:
                                            smart_analysis_data.update({smart_analysis_data["BIOCHEMISTRY"][chem_title]: "1"})

                                        if chem_title in chem_count_keys:
                                            smart_analysis_data.update({smart_analysis_data["BIOCHEMISTRY_VALUE"][chem_title]: heparin_result})

                        # append analysis counts data list
                        if smart_analysis_data and record_ids:
                            if case_type == "UM":
                                um_data.append(smart_analysis_data.copy())

                                # update the record id for the 2nd data entry
                                # and update the list
                                # record_id_2de = record_ids[1]['id_um']

                                if len(record_ids) > 1:
                                    record_id_2de = record_ids[1]["id_um"][0:12]
                                else:
                                    record_id_2de = record_ids[0]["id_um"][0:12]

                                if data_entry == "--1":
                                    record_id_2de = f"{record_id_2de}--2"
                                else:
                                    record_id_2de = f"{record_id_2de}--1"

                                smart_analysis_data.update({"id_um": record_id_2de})
                                um_data.append(smart_analysis_data.copy())

                            elif case_type == "SM":
                                # SM
                                sm_data.append(smart_analysis_data.copy())

                                # update the record id for the 2nd data entry
                                # and update the list
                                # record_id_2de = record_ids[1]['id_um']

                                if len(record_ids) > 1:  # check the length to help to choose the right index
                                    record_id_2de = record_ids[1]["id_um"][0:12]
                                else:
                                    record_id_2de = record_ids[0]["id_um"][0:12]

                                if data_entry == "--1":
                                    record_id_2de = f"{record_id_2de}--2"
                                else:
                                    record_id_2de = f"{record_id_2de}--1"

                                smart_analysis_data.update({"id_um": record_id_2de})
                                sm_data.append(smart_analysis_data.copy())
                            else:
                                # RM
                                rm_data.append(smart_analysis_data.copy())

                                # update the record id for the 2nd data entry
                                # and update the list

                                if len(record_ids) > 1:
                                    record_id_2de = record_ids[1]["id_um"][0:11]
                                else:
                                    record_id_2de = record_ids[1]["id_um"][0:11]

                                if data_entry == "--1":
                                    record_id_2de = f"{record_id_2de}--2"
                                else:
                                    record_id_2de = f"{record_id_2de}--1"

                                smart_analysis_data.update({"id_um": record_id_2de})
                                rm_data.append(smart_analysis_data.copy())

                    # clear the smart_analysis_data dictionary
                    smart_analysis_data.clear()

            else:
                logger.info(f"SENAITE: No SMART {'lab count'} lab records was found!")

            next_batch = res_data_dict["next"]

        # write to json file
        sm_json_file = os.path.join(os.path.dirname(__file__), "data", "smart_sm_import_data.json")
        um_json_file = os.path.join(os.path.dirname(__file__), "data", "smart_um_import_data.json")
        rm_json_file = os.path.join(os.path.dirname(__file__), "data", "smart_rm_import_data.json")

        if um_data:
            write_json_smart(um_data, um_json_file)

        if sm_data:
            write_json_smart(sm_data, sm_json_file)

        if rm_data:
            write_json_smart(rm_data, rm_json_file)

        # importing the data or results into REDCap project database
        # data_import(sample_type)

        dum_data = json.dumps(um_data, indent=4)
        dsm_data = json.dumps(sm_data, indent=4)
        drm_data = json.dumps(rm_data, indent=4)
        print(dum_data)
        print(dsm_data)
        print(drm_data)

    except ConnectionError as cer:
        logger.error(f"Connection Error to SENAITE LIMS. {cer.errno}:{cer.strerror}")


if __name__ == '__main__':
    transfer_smart_result("this-month", "EDTA Blood")
