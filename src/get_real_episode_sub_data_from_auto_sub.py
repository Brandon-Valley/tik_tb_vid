from pprint import pprint
import fuzz_common as fc
import os
from pathlib import Path
import regex

import re
import time

from fuzzywuzzy import fuzz
from Series_Sub_Map import Series_Sub_map
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import txt_logger
from sms.logger import json_logger
import pysubs2

FUZZ_STR_DELIM = "\r"
# NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD = 11 # TODO play with this?  11.95 minutes
# NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD = 10 # TODO play with this?  11.95 minutes
NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD = 9 # TODO play with this?  11.95 minutes
MIN_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_UNTIL_GIVE_UP = 4 # TODO play with this?  11.95 minutes
# NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD = 5 # TODO play with this? "16.55 minutes - 14 unknown
# NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD = 2 # TODO play with this? ""20.95 minutes - 7 unknown
# NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD = 4 # TODO play with this? " "19.25 minutes"
SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ = "init_partial_fuzz_search_method"
SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED = "auto_sub_fuzz_len_based"

EVAL_KEY__SUCCESS = "EVAL_KEY__SUCCESS"
EVAL_KEY__NO_CLEAR_WINNER = "EVAL_KEY__NO_CLEAR_WINNER"
EVAL_KEY__ALL_FR_SAME = "EVAL_KEY__ALL_FR_SAME"


CLIPS_DATA_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/CLIPS_DATA/"

# def get_real_episode_sub_data_from_auto_sub__OLD_METHOD(auto_sub_path, ssm, lang):
#     start_time = time.time()
#     print(f"in get_real_episode_sub_data_from_auto_sub() - {auto_sub_path=}")
#     print(f"{ssm.get_num_episodes_in_lang(lang)=}")

#     auto_sub_fuzz_str = _sub_path_to_fuzz_str(auto_sub_path)

#     lang_ep_sub_data_l = ssm.get_episode_sub_data_l_for_lang(lang)

#     print(f"{len(lang_ep_sub_data_l)=}")

#     best_fuzz_ratio = 0
#     best_lang_ep_sub_data_obj = None

#     fuzz_ratio_file_path = os.path.join(f"C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS", Path(auto_sub_path).stem + "__fuzz_r.txt" ) #TMP
#     fsu.delete_if_exists(fuzz_ratio_file_path)#TMP


#     for lang_ep_sub_data in lang_ep_sub_data_l:
#         print(f"  Checking {lang_ep_sub_data.get_season_episode_str()}...")
#         real_sub_path = lang_ep_sub_data.main_sub_file_path
#         real_sub_fuzz_str = _sub_path_to_fuzz_str(real_sub_path)
#         # txt_logger.write([real_sub_fuzz_str], f"C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/{lang_ep_sub_data.get_season_episode_str()}.txt") #TMP

#         # TODO comment out
#         # print(f"{auto_sub_fuzz_str=}")
#         print(f">>{real_sub_fuzz_str=}<<")
#         # print(f"{real_sub_fuzz_str[-15:]=}")

#         # fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_fuzz_str)
#         fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_fuzz_str)

#         print(f"########{fuzz_ratio=}")         # TODO comment out
#         # print(f"########{regex.match('(' + auto_sub_fuzz_str + '){e<=1}', real_sub_fuzz_str)=}")         # TODO comment out
#         # txt_logger.write(fuzz, f"C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/{lang_ep_sub_data.get_season_episode_str()}_fuzz.txt", "append") #TMP
#         # txt_logger.write(f"{str(fuzz_ratio)} - {real_sub_path}\r" , fuzz_ratio_file_path, "append") #TMP
#         # txt_logger.write(f"{str(fuzz_ratio)} - {Path(real_sub_path).parents}\r" , fuzz_ratio_file_path, "append") #TMP
#         # two_parent_display_path = Path(real_sub_path).parent.__str__()
#         two_parent_display_path = f"{Path(Path(real_sub_path).parent.__str__()).parent.name}/{Path(real_sub_path).parent.name}/{Path(real_sub_path).name}"
#         # txt_logger.write(f"{str(fuzz_ratio)}:{os.path.parent(os.path.parent(real_sub_path))}\{os.path.parent(real_sub_path)}\{Path(real_sub_path).name}\r" , fuzz_ratio_file_path, "append") #TMP
#         txt_logger.write(f"{str(fuzz_ratio)} :{two_parent_display_path}\r" , fuzz_ratio_file_path, "append") #TMP


#         if fuzz_ratio > best_fuzz_ratio:
#             print(f"New best_lang_ep_sub_data_obj found: {lang_ep_sub_data}")
#             best_fuzz_ratio = fuzz_ratio
#             best_lang_ep_sub_data_obj = lang_ep_sub_data

#         print(f"just finished checking {real_sub_path=}, {fuzz_ratio=}")         # TODO comment out
    
#     print(f"{auto_sub_path=}") # TMP
#     print(f"Final {best_fuzz_ratio=}, {best_lang_ep_sub_data_obj}")
#     if best_lang_ep_sub_data_obj == None:
#         print("After fuzzy-searching every episode's subs, did not find single episode with fuzz_ratio > 0, returning None")

#     # exit()#TMP


#     total_time = time.time() - start_time
#     return best_lang_ep_sub_data_obj, best_fuzz_ratio, total_time








# def _sub_path_to_fuzz_str(sub_path):
#     # subs = pysubs2.load(sub_path, encoding="utf-8")
#     subs = pysubs2.load(sub_path, encoding="latin1")

#     subs_fuzz_str = ""
#     for line in subs:
#         subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM

#     line_l = []

#     subs_fuzz_str = subs_fuzz_str.replace("\\n", "\\N")
#     subs_fuzz_str = subs_fuzz_str.replace("\\r", "\\N")
#     subs_fuzz_str = subs_fuzz_str.replace("\\N", "$$$$$")
#     # for line in subs_fuzz_str.split("\\N"):
#     for line in subs_fuzz_str.split("$$$$$"):
#         line_l.append(re.sub(r"[^a-zA-Z0-9]+", ' ', line)) # For some reason having no spaces gave slightly better results

#     subs_fuzz_str = ""
#     for line in line_l:
#         subs_fuzz_str += line + "\r"
#     # # subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
#     # subs_fuzz_str = subs_fuzz_str.replace("\\N", "\r")
#     # subs_fuzz_str = subs_fuzz_str.replace("\\'", "'")

#     # # subs_fuzz_str = subs_fuzz_str.replace("♪", "")
#     # # subs_fuzz_str = subs_fuzz_str.replace(" It seems today", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace("that all you see ", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace(" Is violence in movies", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace("and sex on TV ", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace(" But where are those", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace("good old-fashioned values ", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace(" On which we used to rely? ", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace(" Lucky there's a family guy ", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace(" Lucky there's a man", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace("who positively can do ", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace(" All the things that make us ", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace(" Laugh and cry ", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace(" He's... a...", '')
#     # # subs_fuzz_str = subs_fuzz_str.replace("Fam... ily... Guy! ", '')

#     # subs_fuzz_str = subs_fuzz_str.replace("{\\i1}", "")
#     # subs_fuzz_str = subs_fuzz_str.replace("{\\i0}", "")

#     # # subs_fuzz_str = re.sub('[^A-Za-z0-9]+', '', subs_fuzz_str)
#     # subs_fuzz_str = re.sub(r"[^a-zA-Z0-9]+", '', subs_fuzz_str)
#     return subs_fuzz_str.lower()
#     # return subs_fuzz_str

# def _sub_path_to_fuzz_str(sub_path):
#     subs = pysubs2.load(sub_path, encoding="latin1")

#     subs_fuzz_str = ""
#     for line in subs:
#         subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM

#     MAX_SUB_LINES = 450
#     num_lines_to_add = MAX_SUB_LINES - len(subs)
#     for x in range(num_lines_to_add):
#         subs_fuzz_str += "hi there this is an extra string to make things the same length" + str(x)

#     line_l = []

#     # subs_fuzz_str = subs_fuzz_str.replace("\\n", "\\N")
#     # subs_fuzz_str = subs_fuzz_str.replace("\\r", "\\N")
#     # subs_fuzz_str = subs_fuzz_str.replace("\\N", "$$$$$")
#     # # for line in subs_fuzz_str.split("\\N"):
#     # for line in subs_fuzz_str.split("$$$$$"):
#     #     line_l.append(re.sub(r"[^a-zA-Z0-9]+", ' ', line)) # For some reason having no spaces gave slightly better results

#     # subs_fuzz_str = ""
#     # for line in line_l:
#     #     subs_fuzz_str += line + "\r"
#     # subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
#     # # subs_fuzz_str = subs_fuzz_str.replace("\\N", "\r")
#     # # subs_fuzz_str = subs_fuzz_str.replace("\\'", "'")
#     # subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
#     subs_fuzz_str = subs_fuzz_str.replace("\\'", "'")

#     # subs_fuzz_str = subs_fuzz_str.replace("♪", "")
#     # subs_fuzz_str = subs_fuzz_str.replace(" It seems today", '')
#     # subs_fuzz_str = subs_fuzz_str.replace("that all you see ", '')
#     # subs_fuzz_str = subs_fuzz_str.replace(" Is violence in movies", '')
#     # subs_fuzz_str = subs_fuzz_str.replace("and sex on TV ", '')
#     # subs_fuzz_str = subs_fuzz_str.replace(" But where are those", '')
#     # subs_fuzz_str = subs_fuzz_str.replace("good old-fashioned values ", '')
#     # subs_fuzz_str = subs_fuzz_str.replace(" On which we used to rely? ", '')
#     # subs_fuzz_str = subs_fuzz_str.replace(" Lucky there's a family guy ", '')
#     # subs_fuzz_str = subs_fuzz_str.replace(" Lucky there's a man", '')
#     # subs_fuzz_str = subs_fuzz_str.replace("who positively can do ", '')
#     # subs_fuzz_str = subs_fuzz_str.replace(" All the things that make us ", '')
#     # subs_fuzz_str = subs_fuzz_str.replace(" Laugh and cry ", '')
#     # subs_fuzz_str = subs_fuzz_str.replace(" He's... a...", '')
#     # subs_fuzz_str = subs_fuzz_str.replace("Fam... ily... Guy! ", '')

#     subs_fuzz_str = subs_fuzz_str.replace("{\\i1}", "")
#     subs_fuzz_str = subs_fuzz_str.replace("{\\i0}", "")

#     # subs_fuzz_str = re.sub('[^A-Za-z0-9]+', '', subs_fuzz_str)
#     # subs_fuzz_str = re.sub(r"[^a-zA-Z0-9]+", '', subs_fuzz_str)



#     return subs_fuzz_str.lower()
#     # return subs_fuzz_str


# def _sub_path_to_fuzz_str(sub_path):
#     # subs = pysubs2.load(sub_path, encoding="utf-8")
#     subs = pysubs2.load(sub_path, encoding="latin1")

#     subs_fuzz_str = ""
#     for line in subs:
#         subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM

#     # subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
#     subs_fuzz_str = subs_fuzz_str.replace("\\N", "\n")
#     subs_fuzz_str = subs_fuzz_str.replace("\\'", "'")
#     subs_fuzz_str = subs_fuzz_str.replace("{\\i1}", "")
#     subs_fuzz_str = subs_fuzz_str.replace("{\\i0}", "")
#     # return subs_fuzz_str.lower()
#     return subs_fuzz_str

# def _sub_path_to_fuzz_str(sub_path):
#     print(f"{sub_path=}")#TMP 
#     # subs = pysubs2.load(sub_path, encoding="utf-8")

#     subs = pysubs2.load(sub_path, encoding="latin1")

#     subs_fuzz_str = ""
#     for line in subs:
#         subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM

#     # subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
#     # subs_fuzz_str = subs_fuzz_str.replace("\'", " ")

#     # MAX_SUB_LINES = 700
#     # num_lines_to_add = MAX_SUB_LINES - len(subs)
#     # for x in range(num_lines_to_add):
#     #     subs_fuzz_str += "hi there this is an extra string to make things the same length" + str(x) + "\r"


#     # return subs_fuzz_str.lower()
#     return subs_fuzz_str

# # TODO make ep in SSM do this on init so it does not happen X100!!!!!!!!!!!!!!
# # TODO make more efficient
# def _sub_path_to_fuzz_str_l(sub_path):
#     print(f"{sub_path=}")#TMP 
#     # subs = pysubs2.load(sub_path, encoding="utf-8")

#     subs = pysubs2.load(sub_path, encoding="latin1")

#     subs_fuzz_str = ""
#     for line in subs:
#         subs_fuzz_str = subs_fuzz_str + line.text + " "

#     # subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
#     # subs_fuzz_str = subs_fuzz_str.replace("\'", " ")

#     # MAX_SUB_LINES = 700
#     # num_lines_to_add = MAX_SUB_LINES - len(subs)
#     # for x in range(num_lines_to_add):
#     #     subs_fuzz_str += "hi there this is an extra string to make things the same length" + str(x) + "\r"


#     # return subs_fuzz_str.lower()
#     return subs_fuzz_str


def _get_best_ep_sub_partial_fuzz_ratio(ep_sub_data, auto_sub_fuzz_str, method_key, partial_fuzz_str_len=None):
    print(f"in _get_best_ep_sub_partial_fuzz_ratio() - {method_key=}")
    best_fuzz_ratio = 0
    best_real_sub_partial_fuzz_str = None

    # print(f"{ep_sub_data=}")
    # pprint(ep_sub_data.partial_fuzz_str_l) #TMP

    # exit()
    # json_logger.write(ep_sub_data.partial_fuzz_str_l, "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/tmp_partial.json")#TMP

    # get partial_fuzz_str_l based on method_key
    if method_key == SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ:
        partial_fuzz_str_l = ep_sub_data.get_default_partial_fuzz_str_l()
    elif method_key == SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED:
        OLD_partial_fuzz_str_num_char = len(auto_sub_fuzz_str) * NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD # TMP THIS CAN CHANGE!
        print(f"{OLD_partial_fuzz_str_num_char=}")#TMP REMOVE
        # partial_fuzz_str_num_char = partial_fuzz_str_len # TMP THIS CAN CHANGE!
        ep_sub_total_fuzz_str = json_logger.read(ep_sub_data.total_fuzz_str_json_path)
        # partial_fuzz_str_l = ep_sub_data.get_custom_partial_fuzz_str_l(partial_fuzz_str_num_char, len(auto_sub_fuzz_str))
        print(f"{len(ep_sub_total_fuzz_str)=}")
        print(f"{partial_fuzz_str_len=}")
        print(f"{len(auto_sub_fuzz_str)=}")
        partial_fuzz_str_l = fc.get_partial_fuzz_str_l_from_total_fuzz_str(total_fuzz_str = ep_sub_total_fuzz_str,
                                                                                    # min_partial_fuzz_str_num_char = partial_fuzz_str_num_char,
                                                                                    min_partial_fuzz_str_num_char = partial_fuzz_str_len,
                                                                                    min_overlap_char = len(auto_sub_fuzz_str))
        # partial_fuzz_str_l = fc.get_partial_fuzz_str_l_from_total_fuzz_str(partial_fuzz_str_num_char, len(auto_sub_fuzz_str))
        # print(f"{partial_fuzz_str_l=}")
        print(f"{len(partial_fuzz_str_l)=}")
        # print("Hereeeeeeeeeeeeeeeee")
        # exit()
    
    print(f"{len(partial_fuzz_str_l)=}")

    for real_sub_partial_fuzz_str in partial_fuzz_str_l:
        
        fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_partial_fuzz_str)
        # print(f"{auto_sub_fuzz_str=}")
        # print(f"{real_sub_partial_fuzz_str=}")
        # print(f"{fuzz_ratio=}")
        # exit()

        if fuzz_ratio > best_fuzz_ratio:
            best_fuzz_ratio = fuzz_ratio
            best_real_sub_partial_fuzz_str = real_sub_partial_fuzz_str

    return best_fuzz_ratio, best_real_sub_partial_fuzz_str

    

def _predict_search_method(auto_sub_fuzz_str, ssm, lang):
    print("in _predict_search_method()")
    min_fuzz_str_len = ssm.get_min_fuzz_str_len_for_lang(lang)
    print(f"$$$ {len(auto_sub_fuzz_str)=}")
    print(f"$$$ {min_fuzz_str_len=}")
    print(f"$$$ {min_fuzz_str_len / len(auto_sub_fuzz_str)=}")
    print(f"$$$ {int(min_fuzz_str_len / len(auto_sub_fuzz_str))=}")
    print(f"$$$ {min_fuzz_str_len - len(auto_sub_fuzz_str)=}")

    min_fuzz_len_to_auto_sub_fuzz_len_ratio = min_fuzz_str_len / len(auto_sub_fuzz_str)

    if min_fuzz_len_to_auto_sub_fuzz_len_ratio < NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD:
        return SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ
    else:
        return SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED




def _write_fuzz_ratio_ep_sub_data_l_d_to_json(fuzz_ratio_ep_sub_data_l_d, json_path):
    fsu.delete_if_exists(json_path)#TMP
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)

    json_ser_d = {}
    for fuzz_ratio, ep_sub_data_l in fuzz_ratio_ep_sub_data_l_d.items():
        json_ser_d[fuzz_ratio] = []
        for ep_sub_data in ep_sub_data_l:
            json_ser_d[fuzz_ratio].append(str(ep_sub_data))
    print(f"Writing serializable fuzz_ratio_ep_sub_data_l_d to {json_path=}...")
    json_logger.write(json_ser_d, json_path)


def _get_fuzz_ratio_ep_sub_data_l_d(auto_sub_fuzz_str, ssm, lang, method_key, partial_fuzz_str_len = None):
    ep_sub_data_l = ssm.get_episode_sub_data_l_for_lang(lang)

    print(f"{len(ep_sub_data_l)=}")

    fuzz_ratio_ep_sub_data_l_d = {}

    for ep_sub_data in ep_sub_data_l:
        print(f"  Checking {ep_sub_data.get_season_episode_str()}...")

        ep_sub_fuzz_ratio, ep_sub_best_partial_fuzz_str = _get_best_ep_sub_partial_fuzz_ratio(ep_sub_data, auto_sub_fuzz_str, method_key, partial_fuzz_str_len)
        # print(f"{ep_sub_fuzz_ratio=}")

        if ep_sub_fuzz_ratio in fuzz_ratio_ep_sub_data_l_d.keys():
            fuzz_ratio_ep_sub_data_l_d[ep_sub_fuzz_ratio].append(ep_sub_data)
        else:
            fuzz_ratio_ep_sub_data_l_d[ep_sub_fuzz_ratio] = [ep_sub_data]
    return fuzz_ratio_ep_sub_data_l_d







def get_eval_of__fuzz_ratio_ep_sub_data_l_d(fuzz_ratio_ep_sub_data_l_d, ssm, lang, fuzz_ratio_ep_sub_data_l_d_json_path):

    # Evaluate fuzz_ratio_ep_sub_data_l_d

    if len(fuzz_ratio_ep_sub_data_l_d.keys()) == 0:
        raise Exception(f"ERROR, {fuzz_ratio_ep_sub_data_l_d=}, no clue how this happened")

    # If all episode's real sub's partial_fuzz_strs' gave same fuzz ratio
    #   - Try diff search method
    if len(fuzz_ratio_ep_sub_data_l_d.keys()) == 1 and ssm.get_num_episodes_in_lang(lang) != 1:
        # raise Exception("TMP NOT IMPLEMENTED - " + fuzz_ratio_ep_sub_data_l_d_json_path)
        return None, None, EVAL_KEY__ALL_FR_SAME

    # max_fuzz_ratio = max(fuzz_ratio_ep_sub_data_l_d, key=fuzz_ratio_ep_sub_data_l_d.get)
    max_fuzz_ratio = max(fuzz_ratio_ep_sub_data_l_d.keys())
    max_fuzz_ratio_ep_sub_data_l = fuzz_ratio_ep_sub_data_l_d[max_fuzz_ratio]

    # Success
    if len(max_fuzz_ratio_ep_sub_data_l) == 1:
        best_fuzz_ratio_ep_sub_data = max_fuzz_ratio_ep_sub_data_l[0]
        print(f"Success - Single ep_sub_data for highest {max_fuzz_ratio=} - {best_fuzz_ratio_ep_sub_data.get_season_episode_str()}, returning...")
        # fail_reason = None
        return max_fuzz_ratio, best_fuzz_ratio_ep_sub_data, EVAL_KEY__SUCCESS
    
    # If all episode's real sub's partial_fuzz_strs' DID NOT give same fuzz ratio, but also no clear winner
    else:
        return None, None, EVAL_KEY__NO_CLEAR_WINNER



def _search_method__auto_sub_fuzz_len_based(auto_sub_path, auto_sub_fuzz_str, ssm, lang, partial_fuzz_str_len = None):

    fuzz_ratio_ep_sub_data_l_d_json_path = os.path.join(CLIPS_DATA_DIR_PATH, Path(auto_sub_path).name.split(".")[0][:70], Path(auto_sub_path).name.split(".")[0][:70] + "_ip_fresdl_d.json" ) #TMP

    print(f"Getting fuzz_ratio_ep_sub_data_l_d for {auto_sub_path=}...")
    fuzz_ratio_ep_sub_data_l_d = _get_fuzz_ratio_ep_sub_data_l_d(auto_sub_fuzz_str, ssm, lang, method_key = SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED, partial_fuzz_str_len=partial_fuzz_str_len)
    _write_fuzz_ratio_ep_sub_data_l_d_to_json(fuzz_ratio_ep_sub_data_l_d, fuzz_ratio_ep_sub_data_l_d_json_path)


    fuzz_ratio, ep_sub_data, eval_str = get_eval_of__fuzz_ratio_ep_sub_data_l_d(fuzz_ratio_ep_sub_data_l_d, ssm, lang, fuzz_ratio_ep_sub_data_l_d_json_path)
    # print(f"{fuzz_ratio=}")
    # print(f"{ep_sub_data=}")
    # print(f"{eval_str=}")
    return fuzz_ratio, ep_sub_data, eval_str


def _search_method__init_partial_fuzz(auto_sub_path, auto_sub_fuzz_str, ssm, lang):
    fuzz_ratio_ep_sub_data_l_d_json_path = os.path.join(CLIPS_DATA_DIR_PATH, Path(auto_sub_path).name.split(".")[0][:70], Path(auto_sub_path).name.split(".")[0][:70] + "_lb_fresdl_d.json" ) #TMP

    print(f"Getting fuzz_ratio_ep_sub_data_l_d for {auto_sub_path=}...")
    fuzz_ratio_ep_sub_data_l_d = _get_fuzz_ratio_ep_sub_data_l_d(auto_sub_fuzz_str, ssm, lang, method_key=SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ)
    _write_fuzz_ratio_ep_sub_data_l_d_to_json(fuzz_ratio_ep_sub_data_l_d, fuzz_ratio_ep_sub_data_l_d_json_path)
    fuzz_ratio, ep_sub_data, eval_str = get_eval_of__fuzz_ratio_ep_sub_data_l_d(fuzz_ratio_ep_sub_data_l_d, ssm, lang, fuzz_ratio_ep_sub_data_l_d_json_path)

    # return fuzz_ratio, ep_sub_data, eval_str
    return fuzz_ratio, ep_sub_data, eval_str, fuzz_ratio_ep_sub_data_l_d
 


# def get_real_episode_sub_data_from_auto_sub(auto_sub_path, ssm, lang, min_real_sub_total_fuzz_str_len):
def get_real_episode_sub_data_from_auto_sub(auto_sub_path, ssm, lang):
    print(f"Searching for best real sub file from auto sub file:{auto_sub_path}...")
    start_time = time.time()
    print(f"in get_real_episode_sub_data_from_auto_sub() - {auto_sub_path=}")
    print(f"{ssm.get_num_episodes_in_lang(lang)=}")

    auto_sub_fuzz_str = fc.get_fuzz_str_from_sub_path(auto_sub_path)

    search_method_key = _predict_search_method(auto_sub_fuzz_str, ssm, lang)
    print(f"init predicted {search_method_key=}")

    if search_method_key == SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ:
        # fuzz_ratio, ep_sub_data, eval_key = _search_method__init_partial_fuzz(auto_sub_path, auto_sub_fuzz_str, ssm, lang)
        fuzz_ratio, ep_sub_data, eval_key, fuzz_ratio_ep_sub_data_l_d = _search_method__init_partial_fuzz(auto_sub_path, auto_sub_fuzz_str, ssm, lang)
        print(f"{fuzz_ratio=}")
        print(f"{ep_sub_data=}")
        print(f"{eval_key=}")

        if eval_key == EVAL_KEY__SUCCESS:
            total_time = time.time() - start_time
            return fuzz_ratio, ep_sub_data, eval_key, total_time
        # TODO SHOULD ADD SOMETHING HERE FOR EVAL_KEY__NO_CLEAR_WINNER - like if its just down to 2 subs
        elif eval_key == EVAL_KEY__NO_CLEAR_WINNER:
            print(f"{eval_key=}")
            pprint(fuzz_ratio_ep_sub_data_l_d)
            # raise Exception("TMP TODO")
            print(f"Init predicted {search_method_key=} was wrong, made it through every ep without finding clear winner, changing search_method_key to try len based...")
            search_method_key = SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED

        else:
            print(f"Init predicted {search_method_key=} was wrong, made it through every ep without success, changing search_method_key to try len based...")
            search_method_key = SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED


    print("hereeeeeee")


    if search_method_key == SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED:
        # print("print")
        # raise Exception("TMP EXEP - Not imlemented yet")
        # print( ("!!!!!!!!!!!! TODO !!!!!!!!!!TMP EXEP - Not imlemented yet")) # TODO
        # best_fuzz_ratio, best_ep_sub_data = None, None # TODO

        init_partial_fuzz_str_len = len(auto_sub_fuzz_str) * NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD
        print(f"{init_partial_fuzz_str_len=}")

        # for if got here from failed SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ and auto_sub_fuzz_str is very large
        if ssm.get_min_fuzz_str_len_for_lang(lang) < init_partial_fuzz_str_len:
            partial_fuzz_str_len = len(auto_sub_fuzz_str)
        else:
            partial_fuzz_str_len = init_partial_fuzz_str_len


        print(f"{partial_fuzz_str_len=}")

        while (partial_fuzz_str_len >= len(auto_sub_fuzz_str) * MIN_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_UNTIL_GIVE_UP):

            if ssm.get_min_fuzz_str_len_for_lang(lang) < partial_fuzz_str_len:
                raise Exception(f"ERROR: {ssm.get_min_fuzz_str_len_for_lang(lang)=} (from episode sub {ssm.get_min_fuzz_str_len_ep_sub_data_lang(lang)}) can never be less than {partial_fuzz_str_len=}")

            fuzz_ratio, ep_sub_data, eval_key = _search_method__auto_sub_fuzz_len_based(auto_sub_path, auto_sub_fuzz_str, ssm, lang, partial_fuzz_str_len)
            print(f"{fuzz_ratio=}")
            print(f"{ep_sub_data=}")
            print(f"{eval_key=}")
            if eval_key == EVAL_KEY__SUCCESS:
                break
            else:
                partial_fuzz_str_len = int(partial_fuzz_str_len / 2)


        if eval_key != EVAL_KEY__SUCCESS:
            print(f"After fuzzy-searching every episode's subs, did not find a match for auto-sub, returning None: {eval_key=}...")
        else:
            print(f"Found best real sub for auto-sub: {ep_sub_data}")

        total_time = time.time() - start_time
        return fuzz_ratio, ep_sub_data, eval_key, total_time

    print(f"{search_method_key=}")
    print(f"{partial_fuzz_str_len=}")
    raise Exception("SHOULD NEVER GET HERE")




    # ep_sub_data_l = ssm.get_episode_sub_data_l_for_lang(lang)

    # print(f"{len(ep_sub_data_l)=}")

    # best_fuzz_ratio = 0
    # best_ep_sub_data = None
    # best_ep_sub_best_partial_fuzz_str = None

    # fuzz_ratio_file_path = os.path.join(f"C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS", Path(auto_sub_path).stem + "__fuzz_r.txt" ) #TMP
    # fsu.delete_if_exists(fuzz_ratio_file_path)#TMP

    # fuzz_ratio_ep_sub_data_l_d_json_path = os.path.join(f"C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS", Path(auto_sub_path).stem + "__fuzz_ratio_ep_sub_data_l_d.json" ) #TMP
    # fsu.delete_if_exists(fuzz_ratio_ep_sub_data_l_d_json_path)#TMP



    # # LATER only store paths instead of ep_dir_data objects if low mem or too slow
    # fuzz_ratio_ep_sub_data_l_d = {}

    # for ep_sub_data in ep_sub_data_l:
    #     print(f"  Checking {ep_sub_data.get_season_episode_str()}...")

    #     ep_sub_fuzz_ratio, ep_sub_best_partial_fuzz_str = _get_best_ep_sub_partial_fuzz_raaaaaaaaaaaaatio(ep_sub_data, auto_sub_fuzz_str)
    #     print(f"{ep_sub_fuzz_ratio=}")

    #     se_str_real_sub_path_d = {"se_str": ep_sub_data.get_season_episode_str(),
    #                               "sub_path": ep_sub_data.main_sub_file_path}

    #     if ep_sub_fuzz_ratio in fuzz_ratio_ep_sub_data_l_d.keys():
    #         fuzz_ratio_ep_sub_data_l_d[ep_sub_fuzz_ratio].append(se_str_real_sub_path_d)
    #     else:
    #         fuzz_ratio_ep_sub_data_l_d[ep_sub_fuzz_ratio] = [se_str_real_sub_path_d]
        
    #     two_parent_display_path = f"{Path(Path(ep_sub_data.main_sub_file_path).parent.__str__()).parent.name}/{Path(ep_sub_data.main_sub_file_path).parent.name}/{Path(ep_sub_data.main_sub_file_path).name}" #TMP
    #     # txt_logger.write(f"{str(ep_sub_fuzz_ratio)} :{two_parent_display_path}\r" , fuzz_ratio_file_path, "append") #TMP
    #     json_logger.write(fuzz_ratio_ep_sub_data_l_d, fuzz_ratio_ep_sub_data_l_d_json_path)

        # if ep_sub_fuzz_ratio > best_fuzz_ratio:
        #     print(f"    {ep_sub_data.get_season_episode_str()} - Found new best fuzz ratio - {ep_sub_fuzz_ratio=}")
        #     best_fuzz_ratio = ep_sub_fuzz_ratio
        #     best_ep_sub_data = ep_sub_data
        #     best_ep_sub_best_partial_fuzz_str = ep_sub_best_partial_fuzz_str
    print(f"{len(auto_sub_fuzz_str)=}")
    print("HEEEEEEEEEERRRRRRRRRREEEEEEEEEEE")
    exit() # FIXME
    if best_ep_sub_data == None:
        print("After fuzzy-searching every episode's subs, did not find single episode with fuzz_ratio > 0, returning None")
    else:
        print(f"Found best real sub for auto-sub: {ep_sub_data}")

    total_time = time.time() - start_time
    return best_fuzz_ratio, best_ep_sub_data, best_ep_sub_best_partial_fuzz_str, total_time




    #     real_sub_path = ep_sub_data.main_sub_file_path
    #     real_sub_fuzz_str = _sub_path_to_fuzz_str(real_sub_path)
    #     # txt_logger.write([real_sub_fuzz_str], f"C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/{ep_sub_data.get_season_episode_str()}.txt") #TMP

    #     # TODO comment out
    #     # print(f"{auto_sub_fuzz_str=}")
    #     print(f">>{real_sub_fuzz_str=}<<")
    #     # print(f"{real_sub_fuzz_str[-15:]=}")

    #     # fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_fuzz_str)
    #     fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_fuzz_str)

    #     print(f"########{fuzz_ratio=}")         # TODO comment out
    #     two_parent_display_path = f"{Path(Path(real_sub_path).parent.__str__()).parent.name}/{Path(real_sub_path).parent.name}/{Path(real_sub_path).name}" #TMP
    #     txt_logger.write(f"{str(fuzz_ratio)} :{two_parent_display_path}\r" , fuzz_ratio_file_path, "append") #TMP


    #     if fuzz_ratio > best_fuzz_ratio:
    #         print(f"New best_ep_sub_data found: {ep_sub_data}")
    #         best_fuzz_ratio = fuzz_ratio
    #         best_ep_sub_data = ep_sub_data

    #     print(f"just finished checking {real_sub_path=}, {fuzz_ratio=}")         # TODO comment out
    
    # print(f"{auto_sub_path=}") # TMP
    # print(f"Final {best_fuzz_ratio=}, {best_ep_sub_data}")
    # if best_ep_sub_data == None:
    #     print("After fuzzy-searching every episode's subs, did not find single episode with fuzz_ratio > 0, returning None")

    # # exit()#TMP


    # total_time = time.time() - start_time
    # return best_ep_sub_data, best_fuzz_ratio, total_time


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')

    # test_srt_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"

    # lang = "en"
    # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
    # # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_test_pilot"
    # # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_test_s10_and_11"
    # ssm = Series_Sub_map()
    # ssm.load_lang(in_dir_path, lang)
    # print(f"{ssm.get_num_episodes_in_lang(lang)=}")

    # get_real_episode_sub_data_from_auto_sub(test_srt_path, ssm, lang)

    import get_init_mkvs_for_manual_edits
    get_init_mkvs_for_manual_edits.main()
    print("End of Main") 


