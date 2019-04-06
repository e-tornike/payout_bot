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
    ".*(Hinfahrt)\s*:\s*(?P<startBahnhof>\w+) - (?P<zielBahnhof>\w+),\s* mit \s*(?P<train_type>\w+)",
    "(Herr|Frau) \w+ \w+",
    "(Uber).*(ICE)(?P<train_number>\d+)"
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
        
if __name__ == "__main__":
    AngabenZurReise().check()