import os
import configparser
import requests
import json
import logging.config
from dotenv import dotenv_values, load_dotenv
from loguru import logger
from redcapconnector.config.log_config import handlers
from redcapconnector.functions import read_json

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


def get_event_name():
    try:
        event_dic = []

        data = {
            'token': 'A30D66109487A6CDA92545CF7D0EF191',
            'content': 'event',
            'format': 'json',
            'returnFormat': 'json'
        }
        r = requests.post('https://redcap-testing.bibbox.bnitm.de/api/', data=data)
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
            'token': 'A30D66109487A6CDA92545CF7D0EF191',
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

        if pid_code == 'S24-1':
            pid_var = 'h01_3um'
        elif pid_code == 'S24-2':
            pid_var = 'h01_3umsm'

        data = {
            'token': os.environ['SMART_API_TOKEN'],
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
        print(r.json())
        return json.loads(json.dumps(r.json()))

    except ConnectionError as cer:
        logger.error(cer.strerror)


def extract_visit_day(sampleid):
    visit = sampleid[-3:]
    if visit[0:1] == '' or visit[0:1] == '-':
        if len(visit.strip()) == 2:
            visit_day = f"{visit.strip()[0:1]}0{visit[-1:]}"
        else:
            visit_day = f"{visit.strip()[1:2]}0{visit[-1:]}"

    return smart_variables["VISIT_DAYS"][visit]


def extract_event_name(sampleid, visitday, visithr=''):
    id_arm = get_record_id(sampleid)
    id_arm = id_arm[0]["redcap_event_name"][13:]

    visit_hour = ''

    if visithr != '':
        if visithr[0:1] == "H":
            if (len(visithr) == 2 or len(visithr) == 3) and (visithr[0:1] == "H" or visithr[0:2] == "H0"):
                visit_hour = visithr[-1:]
            else:
                visit_hour = visithr[-2:]
        elif visithr[0:2] == "AL":
            #ALH00 ALH0
            if (len(visithr[2:].strip()) == 2 or len(visithr[2:].strip()) == 3) and (visithr[0:1] == "H" or visithr[0:2] == "H0"):
                visit_hour = visithr[-1:]
            else:
                visit_hour = visithr[-2:]
        else:
            visit_hour = ''

    visit_day = visitday

    events = get_event_name()

    for event in events:
        evt_s = event.split('_')
        match evt_s[0]:
            case "hour":
                evt_s_hr = '_'.join((evt_s[0], evt_s[1]))
                if len(evt_s[1]) == 1 and evt_s_hr == visit_hour and event[7:12] == visit_day and event[-5:] == id_arm:
                    return event
                elif len(evt_s[1]) == 2 and evt_s_hr == visit_hour and event[8:13] == visit_day and event[-5:] == id_arm:
                    return event
            case "al":
                evt_s_hr = '_'.join((evt_s[0], evt_s[1], evt_s[2]))
                if len(evt_s[2]) == 1 and evt_s_hr == visit_hour and event[7:12] == visit_day and event[-5:] == id_arm:
                    return event
                elif len(evt_s[2]) == 2 and evt_s_hr == visit_hour and event[8:13] == visit_day and event[-5:] == id_arm:
                    return event
            case "day":
                if event[7:12] == visit_day and event[-5:] == id_arm:
                    return event
                elif event[8:13] == visit_day and event[-5:] == id_arm:
                    return event
            case _:
                if evt_s[0] == visit_day and event[-5:] == id_arm:
                    return event


@logger.catch
def extract_edta_chem_visit(sampleid, day, hour=''):
    visit_hour = ''

    if hour != '':
        if hour[0:1] == "H":
            if (len(hour) == 2 or len(hour) == 3) and (hour[0:1] == "H" or hour[0:2] == "H0"):
                visit_hour = hour[-1:]
            else:
                visit_hour = hour[-2:]
        elif hour[0:2] == "AL":
            # ALH00 ALH0
            if (len(hour[2:].strip()) == 2 or len(hour[2:].strip()) == 3) and (hour[0:1] == "H" or hour[0:2] == "H0"):
                visit_hour = hour[-1:]
            else:
                visit_hour = hour[-2:]
        else:
            visit_hour = ''

    visit_day = day

    events = get_event_name()

    for evt in events:
        evt_s = evt.split('_')
        print(evt_s)
        match evt_s[0]:
            case "hour":
                if len(evt_s[1]) == 1 and evt_s[1] == visit_hour and evt[7:12] == visit_day:
                    print(evt[0:12])
                    print(smart_variables["VISIT_NO_EDTA"][evt[0:12]])
                elif len(evt_s[1]) == 2 and evt_s[1] == visit_hour and evt[8:13] == visit_day:
                    print(evt[0:12])  # hour_8_day_0_arm_4
                    print(smart_variables["VISIT_NO_EDTA"][evt[0:12]])
            case "day":
                if evt[0:6] == visit_day:
                    return smart_variables["VISIT_NO_EDTA"][evt[0:6]]
                elif evt[0:6] == visit_day:
                    return smart_variables["VISIT_NO_EDTA"][evt[0:6]]
            case _:
                if evt_s[0] == visit_day:
                    return smart_variables["VISIT_NO_EDTA"]["U"]


def transfer_smart_result(period, sample_type):
    try:
        smart_analysis_data = {}
        data = []
        next_batch = ''
        res_data = None
        batch = 0

        items_resp = requests.get(os.environ["BASE_URL"] + "/search", params={"catalog": "senaite_catalog_sample", "getClientTitle": "SMART",
                                                                              "sort_on": "getDateSampled", "getSampleTypeTitle": sample_type,
                                                                              "sort_order": "asc", "review_state": "published",
                                                                              "recent_modified": period, "children": "true"},
                                  cookies={cookie_config["Cookie"]["name"]: cookie_config["Cookie"]["value"]}, stream=True)

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

                    # children data
                    analysis_counts = res_data_dict_items[item]["children"]

                    # extrac the sample id
                    client_sample_id = res_data_dict_items[item]["getClientSampleID"]

                    # get the redcap record id
                    record_id = get_record_id(client_sample_id[0:11])
                    record_id = record_id[0]['id_um']
                    vhour = res_data_dict_items[item]["getClientReference"]

                    if client_sample_id:
                        # S24-2001-AG-D04 S24-2001-AG-D4 S24-2001-AG
                        # "unique_group_name": "assin_fosu"
                        if len(client_sample_id) > 11 and not len(client_sample_id) >= 15:

                            # record id
                            smart_analysis_data.update({"id_um": record_id})

                            # event name (redcap_event_name)
                            vday = extract_visit_day(client_sample_id)
                            if vhour == '' and len(client_sample_id.strip()) == 11:
                                cid = "-".join([client_sample_id, 'D00'])
                                day = extract_visit_day(cid)
                                smart_analysis_data.update({"redcap_event_name": extract_event_name(client_sample_id, day, "H00")})
                            else:
                                event_name = extract_event_name(client_sample_id[0:11], vday, vhour)
                                smart_analysis_data.update({"redcap_event_name": event_name})

                            # data access ground name
                            pid = client_sample_id[0:11]
                            smart_analysis_data.update({"redcap_data_access_group": smart_variables["DATA_ACCESS_GROUP"][pid[9:11]]})

                            # edta/biochemistry visit
                            smart_analysis_data.update({"visit_no_edta": extract_edta_chem_visit(client_sample_id[0:11], vday, vhour)})

                            # loop through the children object to get values or results of the analysis
                            for analysis_count in range(len(analysis_counts) - 2):
                                # check if the analysis title or name is found in the redcap_variables dictionary
                                # if children_data[child]["title"] in redcap_variables:
                                # if true, get the key value of the analysis title from the redcap_variables json file
                                # and use it as the key for the Result value e.g {"lf_fbchgb_q":"9.5"}
                                if analysis_counts[analysis_count]["Result"] == "----":
                                    result = 00.00
                                else:
                                    result = float(analysis_counts[analysis_count]["Result"])

                                # analysis results/count
                                smart_analysis_data.update({smart_variables["FBC"][analysis_counts[analysis_count]["title"]]: result})

                        # append analysis counts data list
                        if smart_analysis_data:
                            data.append(smart_analysis_data.copy())

                    # clear the smart_analysis_data dictionary
                    smart_analysis_data.clear()

            else:
                logger.info(f"SENAITE: No SMART {'lab count'} lab records was found!")

            next_batch = res_data_dict["next"]

        print(data)

    except ConnectionError as cer:
        logger.error(f"Connection Error to SENAITE LIMS. {cer.errno}:{cer.strerror}")


if __name__ == '__main__':
    transfer_smart_result("this-month", "EDTA Blood")

    # sample_label = 'S24-2001-AG-D04'
    # print(sample_label[0:11])  # get the pid
    # print(sample_label[0:5])  # extract dag (AG/AF)
    # print(smart_variables["DATA_ACCESS_GROUP"][sample_label[9:11]])  # get the full name of the dag
    #
    # print("-".join(["S24-1001-AG", 'D00']))
    #
    # get_group_name()
    # sid_arm = get_record_id('S24-2002-AG')
    # sid_arm = sid_arm[0]["redcap_event_name"][13:]
    # print(sid_arm)
    # xday = extract_visit_day("S24-2002-AG-D00")
    # print(xday)

    # visit_hour = '8'
    # visit_day = 'unscheduled'
    # events = get_event_name()
    # for evt in events:
    #     evt_s = evt.split('_')
    #     print(evt_s)
    #     match evt_s[0]:
    #         case "hour":
    #             if len(evt_s[1]) == 1 and evt_s[1] == visit_hour and evt[7:12] == visit_day:
    #                 print(evt[0:12])
    #                 print(smart_variables["VISIT_NO_EDTA"][evt[0:12]])
    #             elif len(evt_s[1]) == 2 and evt_s[1] == visit_hour and evt[8:13] == visit_day:
    #                 print(evt[0:12])  # hour_8_day_0_arm_4
    #                 print(smart_variables["VISIT_NO_EDTA"][evt[0:12]])
    #         case "day":
    #             if evt[0:6] == visit_day:
    #                 print(evt)
    #                 print(smart_variables["VISIT_NO_EDTA"][evt[0:6]])
    #             elif evt[0:6] == visit_day:
    #                 print(evt)
    #                 print(smart_variables["VISIT_NO_EDTA"][evt[0:6]])
    #         case _:
    #             if evt_s[0] == visit_day:
    #                 print(evt)
    #                 print(smart_variables["VISIT_NO_EDTA"]["U"])
