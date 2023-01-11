from pprint import pprint
import fuzz_common
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


def _get_best_ep_sub_partial_fuzz_ratio(ep_sub_data, auto_sub_fuzz_str):
    print("in _get_best_ep_sub_partial_fuzz_ratio()")
    best_fuzz_ratio = 0
    best_real_sub_partial_fuzz_str = None

    print(f"{ep_sub_data=}")
    pprint(ep_sub_data.partial_fuzz_str_l) #TMP

    # exit()
    json_logger.write(ep_sub_data.partial_fuzz_str_l, "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/tmp_partial.json")#TMP

    for real_sub_partial_fuzz_str in ep_sub_data.partial_fuzz_str_l:
        
        fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_partial_fuzz_str)
        # print(f"{auto_sub_fuzz_str=}")
        # print(f"{real_sub_partial_fuzz_str=}")
        print(f"{fuzz_ratio=}")
        # exit()

        if fuzz_ratio > best_fuzz_ratio:
            best_fuzz_ratio = fuzz_ratio
            best_real_sub_partial_fuzz_str = real_sub_partial_fuzz_str

    return best_fuzz_ratio, best_real_sub_partial_fuzz_str

    




# def get_real_episode_sub_data_from_auto_sub(auto_sub_path, ssm, lang, min_real_sub_total_fuzz_str_len):
def get_real_episode_sub_data_from_auto_sub(auto_sub_path, ssm, lang):
    print(f"Searching for best real sub file from auto sub file:{auto_sub_path}...")
    start_time = time.time()
    print(f"in get_real_episode_sub_data_from_auto_sub() - {auto_sub_path=}")
    print(f"{ssm.get_num_episodes_in_lang(lang)=}")

    auto_sub_fuzz_str = fuzz_common.get_fuzz_str_from_sub_path(auto_sub_path)

    ep_sub_data_l = ssm.get_episode_sub_data_l_for_lang(lang)

    print(f"{len(ep_sub_data_l)=}")

    best_fuzz_ratio = 0
    best_ep_sub_data = None
    best_ep_sub_best_partial_fuzz_str = None

    fuzz_ratio_file_path = os.path.join(f"C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS", Path(auto_sub_path).stem + "__fuzz_r.txt" ) #TMP
    fsu.delete_if_exists(fuzz_ratio_file_path)#TMP


    for ep_sub_data in ep_sub_data_l:
        print(f"  Checking {ep_sub_data.get_season_episode_str()}...")

        ep_sub_fuzz_ratio, ep_sub_best_partial_fuzz_str = _get_best_ep_sub_partial_fuzz_ratio(ep_sub_data, auto_sub_fuzz_str)
        print(f"{ep_sub_fuzz_ratio=}")
        
        two_parent_display_path = f"{Path(Path(ep_sub_data.main_sub_file_path).parent.__str__()).parent.name}/{Path(ep_sub_data.main_sub_file_path).parent.name}/{Path(ep_sub_data.main_sub_file_path).name}" #TMP
        txt_logger.write(f"{str(ep_sub_fuzz_ratio)} :{two_parent_display_path}\r" , fuzz_ratio_file_path, "append") #TMP

        if ep_sub_fuzz_ratio > best_fuzz_ratio:
            best_fuzz_ratio = ep_sub_fuzz_ratio
            best_ep_sub_data = ep_sub_data
            best_ep_sub_best_partial_fuzz_str = ep_sub_best_partial_fuzz_str

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

