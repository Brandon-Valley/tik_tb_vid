import os
from pathlib import Path
from pprint import pprint
# import regex

import re
import time

from fuzzywuzzy import fuzz
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import txt_logger
import pysubs2

FUZZ_STR_DELIM = " "

def get_fuzz_str_from_sub_path(sub_path):
    subs = pysubs2.load(sub_path, encoding="latin1")

    subs_fuzz_str = ""
    for line in subs:
        # Get rid of everything from start of line until ":"
        #  - "COMMENTATOR 1: They're just" --> " They're just"
        #    - From S06E01 - Blue Harvest
        after_colon_line = line.text.split(":")[-1]
        
        subs_fuzz_str = subs_fuzz_str + after_colon_line + FUZZ_STR_DELIM

    # Remove anything between () or []
    subs_fuzz_str = re.sub("[\(\[].*?[\)\]]", "", subs_fuzz_str)

    # Remove anything between {}
    subs_fuzz_str = re.sub(r' {[^}]*}','',subs_fuzz_str)

    subs_fuzz_str = subs_fuzz_str.replace("\\n", " ")
    subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
    subs_fuzz_str = subs_fuzz_str.replace("\\r", " ")

    subs_fuzz_str = subs_fuzz_str.replace("{\\i0}", " ")
    subs_fuzz_str = subs_fuzz_str.replace("{\\i1}", " ")

    subs_fuzz_str = subs_fuzz_str.replace(".", " ")
    subs_fuzz_str = subs_fuzz_str.replace("?", " ")
    subs_fuzz_str = subs_fuzz_str.replace("!", " ")

    subs_fuzz_str = subs_fuzz_str.replace("-", "")
    subs_fuzz_str = subs_fuzz_str.replace("'", "")
    subs_fuzz_str = subs_fuzz_str.replace('"', "")
    subs_fuzz_str = subs_fuzz_str.replace(":", "")
    subs_fuzz_str = subs_fuzz_str.replace(",", "")

    # Remove all other special chars except spaces
    subs_fuzz_str = re.sub('[^a-zA-Z.\d\s]', ' ', subs_fuzz_str)

    # Substitute multiple whitespace with single 0 whitespace
    subs_fuzz_str = ''.join(subs_fuzz_str.split())

    return subs_fuzz_str.lower()






# # TODO make more efficient
# TODO pass offset to use in exact match?
def get_partial_fuzz_str_l_from_total_fuzz_str(total_fuzz_str, min_partial_fuzz_str_num_char, min_overlap_char = None):

    # TODO add extra % allowed?
    if len(total_fuzz_str) == min_partial_fuzz_str_num_char:
        print(f"Given total_fuzz_str is exact same len as {min_partial_fuzz_str_num_char=}, so just returning [total_fuzz_str]...")
        return [total_fuzz_str]
    elif len(total_fuzz_str) < min_partial_fuzz_str_num_char:
        raise Exception(f"ERROR: {len(total_fuzz_str)=} can never be less than {min_partial_fuzz_str_num_char=}")


    # print("----------------------------------------------------------")

    # print(f"{len(total_fuzz_str)=}")
    # print(f"{min_partial_fuzz_str_num_char=}")
    # print(f"{min_partial_fuzz_str_num_char / 2 =}")
    # print(f"{len(total_fuzz_str) - min_partial_fuzz_str_num_char=}")

    partial_fuzz_str_l = []
    offset = 0

    while(offset + min_partial_fuzz_str_num_char < len(total_fuzz_str)):
        # print(f"  Top of while - {offset=}")
        new_end_index = offset + min_partial_fuzz_str_num_char
        # print(f"   {new_end_index=}")
        # partial_fuzz_str = total_fuzz_str[offset:min_partial_fuzz_str_num_char]
        partial_fuzz_str = total_fuzz_str[offset:new_end_index]
        partial_fuzz_str_l.append(partial_fuzz_str)
        # TODO make this more efficient vv

        min_offset = offset + int(min_partial_fuzz_str_num_char / 2)

        if min_overlap_char == None:
            offset = min_offset
        else:
            # offset = min_offset # TODO
            overlap_char_offset = offset + (min_partial_fuzz_str_num_char - min_overlap_char)

            if overlap_char_offset >= min_offset:
                offset = overlap_char_offset
            else:
                print(f"WARNING - {min_offset=} > {overlap_char_offset=} - using min offset")
                offset = min_offset



        # print(f"    Bottom of while - {offset=}")
        # print(f"      {offset + min_partial_fuzz_str_num_char=}")
        # print(f"        {min_partial_fuzz_str_num_char - (offset + min_partial_fuzz_str_num_char)=}")
        # print(f"          {(offset + min_partial_fuzz_str_num_char < len(total_fuzz_str))=}")
        

    # if perfect match, no need for final partial_sub_str
    if offset + min_partial_fuzz_str_num_char == len(total_fuzz_str):
        return partial_fuzz_str_l
        
    final_partial_sub_str = total_fuzz_str[len(total_fuzz_str) - min_partial_fuzz_str_num_char:]
    partial_fuzz_str_l.append(final_partial_sub_str)
    # print("partial_fuzz_str_l VV")
    # pprint(partial_fuzz_str_l)
    # pprint(len(partial_fuzz_str_l))

    # exit()
    # _tmp_test_partial_fuzz_str_l(partial_fuzz_str_l, min_partial_fuzz_str_num_char)
    # exit()
    return partial_fuzz_str_l






















# # # TODO make more efficient
# # TODO pass offset to use in exact match?
# def get_default_partial_fuzz_str_l_from_total_fuzz_str(total_fuzz_str, min_partial_fuzz_str_num_char):

#     # TODO add extra % allowed?
#     if len(total_fuzz_str) == min_partial_fuzz_str_num_char:
#         print(f"Given total_fuzz_str is exact same len as {min_partial_fuzz_str_num_char=}, so just returning [total_fuzz_str]...")
#         return [total_fuzz_str]
#     elif len(total_fuzz_str) < min_partial_fuzz_str_num_char:
#         raise Exception(f"ERROR: {total_fuzz_str=} can never be less than {min_partial_fuzz_str_num_char=}")


#     # print("----------------------------------------------------------")

#     # print(f"{len(total_fuzz_str)=}")
#     # print(f"{min_partial_fuzz_str_num_char=}")
#     # print(f"{min_partial_fuzz_str_num_char / 2 =}")
#     # print(f"{len(total_fuzz_str) - min_partial_fuzz_str_num_char=}")

#     partial_fuzz_str_l = []
#     offset = 0

#     while(offset + min_partial_fuzz_str_num_char < len(total_fuzz_str)):
#         # print(f"  Top of while - {offset=}")
#         new_end_index = offset + min_partial_fuzz_str_num_char
#         # print(f"   {new_end_index=}")
#         # partial_fuzz_str = total_fuzz_str[offset:min_partial_fuzz_str_num_char]
#         partial_fuzz_str = total_fuzz_str[offset:new_end_index]
#         partial_fuzz_str_l.append(partial_fuzz_str)
#         # TODO make this more efficient vv
#         offset = offset + int(min_partial_fuzz_str_num_char / 2)
#         # print(f"    Bottom of while - {offset=}")
#         # print(f"      {offset + min_partial_fuzz_str_num_char=}")
#         # print(f"        {min_partial_fuzz_str_num_char - (offset + min_partial_fuzz_str_num_char)=}")
#         # print(f"          {(offset + min_partial_fuzz_str_num_char < len(total_fuzz_str))=}")
        

#     # if perfect match, no need for final partial_sub_str
#     if offset + min_partial_fuzz_str_num_char == len(total_fuzz_str):
#         return partial_fuzz_str_l
        
#     final_partial_sub_str = total_fuzz_str[len(total_fuzz_str) - min_partial_fuzz_str_num_char:]
#     partial_fuzz_str_l.append(final_partial_sub_str)
#     # print("partial_fuzz_str_l VV")
#     # pprint(partial_fuzz_str_l)
#     # pprint(len(partial_fuzz_str_l))

#     # exit()
#     # _tmp_test_partial_fuzz_str_l(partial_fuzz_str_l, min_partial_fuzz_str_num_char)
#     # exit()
#     return partial_fuzz_str_l
    

def _tmp_test_partial_fuzz_str_l(partial_fuzz_str_l, min_partial_fuzz_str_num_char):
    print(f"{len(partial_fuzz_str_l)=}")

    for partial_fuzz_str_num, partial_fuzz_str in enumerate(partial_fuzz_str_l):
        print(f"partial_fuzz_str # {partial_fuzz_str_num} len: {len(partial_fuzz_str)=}")
    print(f"None should be larger than {min_partial_fuzz_str_num_char=}")


def _sub_path_to_fuzz_str(sub_path):
    print(f"{sub_path=}")#TMP 
    # subs = pysubs2.load(sub_path, encoding="utf-8")

    subs = pysubs2.load(sub_path, encoding="latin1")

    subs_fuzz_str = ""
    for line in subs:
        subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM

    # subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
    # subs_fuzz_str = subs_fuzz_str.replace("\'", " ")

    # MAX_SUB_LINES = 700
    # num_lines_to_add = MAX_SUB_LINES - len(subs)
    # for x in range(num_lines_to_add):
    #     subs_fuzz_str += "hi there this is an extra string to make things the same length" + str(x) + "\r"


    # return subs_fuzz_str.lower()
    return subs_fuzz_str





if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    import get_init_mkvs_for_manual_edits
    get_init_mkvs_for_manual_edits.main()


    # x = 10000000
    # s = ""
    # for i in range(x):
    #     s += "abc"

    # print("start")
    # print(len(s))
    print("End of Main") 
