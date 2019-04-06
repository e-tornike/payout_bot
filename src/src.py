import re
# class Time():
#     hour = None
#     minute = None

       
#     def set_hour(self, hour_int):
#         assert type(hour_int) is int
#         assert hour_int < 24 and hour_int >= 0
#         self.hour = hour_int
        
#     def set_minute(self, minute_int):
#         assert type(minute_int) is int
#         assert minute_int >= 0 and minute_int < 60
#         self.minute = minute_int
    
# class Date():
#     day = None
#     month = None
#     year = None
    
#     def set_day(self, day_int):
#         assert type(day_int) is int
#         self.day = day_int
        
#     def set_month(self, month_int):
#         assert type(month_int) is int
#         self.month = int

#     def set_year(self, year_int):
#         assert type(year_int) is int
        
    
# from enum import Enum
# class TrainType(Enum):
#     ice = "ice"
#     ic = "ic"
#     re = "re"
#     rb = "rb"

# class TrainNumber():
#     pass


# class Train():
#     trainType = None
#     trainNo = None

# class AngabenZurReise():
#     startBanhof = None
#     zielBahnhof = None
#     arrivalDate = None
#     arrivalTime = None
#     arrivalTrain = None
    
#     def check(self):
#         has_non_fields = False
#         if None in [
#             self.startBanhof,
#             self.zielBahnhof,
#             self.arrivalDate,
#             self.arrivalTime,
#             self.arrivalTrain
#         ] : return False
#         return True

from collections import defaultdict
import requests
from PIL import Image


def empty_form():
    d = defaultdict(list)
    s = [
        ("date_tt", None),
        ("date_mm", None),
        ("date_yy", None),
        ("startBahnhof", None),
        ("zielBahnhof", None),
        ("abfahrt_startBahnhof_ltp", None),
        ("ankunft_zielBahnhof_ltp", None),
        ("ankunft_real_tt", None),
        ("ankunft_real_mm", None),
        ("ankunft_real_yy", None),
        ("ankunft_real_zugTyp", None),
        ("ankunft_real_zugNr", None),
        ("ankunft_real_hh", None),    
        ("ankunft_real_mm", None),    
        ("versp_zugType", None),
        ("versp_zugNr", None),
        ("versp_hh", None),    
        ("versp_mm", None),
        ("anschluss_verpasst", None),
        ("letzer_umstieg_im", None),
    ]
    for k, v in s:
        d[k].append(v)
    return d


re_list = [
    "(Hinfahrt)\s*:\s*(?P<startBahnhof>\w+) - (?P<zielBahnhof>\w+),\s* mit \s*(?P<train_type>\w+)",
    "(Herr|Frau) \w+ \w+",
    "(Über).*(ICE)(?P<train_number>\d+)",
    "(Gesamtpreis)\s*:\s*(?P<price>\d+,\d+)\s*(EUR)"
]        


def extract_data(list_of_texts, re_list):
    match_dict = {}
    
    p_list = list(map(re.compile, re_list))
    for txt_line in list_of_texts:
        for p in p_list:
            matches = p.match(txt_line)
            if matches:
                match_dict.update(matches.groupdict())
    return match_dict


def extract_data_from_image(image_path, re_list, subscription_key):
    ''' extracts form data from ticket screenshot'''
    try:
        analysis = request_ocr(image_path, subscription_key)
    except FileNotFoundError:
        raise FileNotFoundError
    except TimeoutError:
        raise TimeoutError
    text = get_text(analysis)
    form_data = extract_data(text, re_list)
    return form_data


def get_text(analysis):
    '''
    analysis = request_ocr("tickets.jpeg", s_key")
    :param analysis:
    :return:
    '''
    lines = analysis["regions"][1]["lines"]
    words = [line["words"] for line in lines]
    text = [' '.join(list(map(lambda x: x["text"], w))) for w in words]
    return text


def request_ocr(image_path, subscription_key):
    vision_base_url = "https://westeurope.api.cognitive.microsoft.com/vision/v2.0/"
    ocr_url = vision_base_url + "ocr"
    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/octet-stream'}
    params = {'language': 'unk', 'detectOrientation': 'true'}
    # data    = {'url': image_url}
    data = open(image_path, "rb").read()
    response = requests.post(ocr_url, headers=headers, params=params, data=data)
    response.raise_for_status()
    analysis = response.json()

    return analysis
