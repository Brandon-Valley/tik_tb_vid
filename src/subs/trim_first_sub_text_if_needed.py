from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

from collections import namedtuple
from pprint import pprint
import re
from typing import Optional, List, Tuple, Sequence
from pysubs2.common import IntOrFloat

import time
import os
import pysubs2
from pathlib import Path
from fuzzywuzzy import fuzz
import time


if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

import cfg
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import txt_logger
import vid_edit_utils as veu
import subtitle_utils as su
import fuzz_common as fc



def trim_first_sub_text_if_needed(in_sub_path):
    subs = pysubs2.load(in_sub_path, encoding="latin1")

    if subs[0].start != 0:
        return in_sub_path

    line_text_l_fuzz_ratio_d = {}

    # first_sub_line_text = subs[0].text
    new_line_text_l = []

    # fill keys of new_line_text_l
    s_space_first_sub_line_text_l = subs[0].text.split(" ")
    for i in range(len(s_space_first_sub_line_text_l)):
        new_line_text = " ".join(s_space_first_sub_line_text_l[i:])[1:]
        print(f"{new_line_text=}")
        new_line_text_l.append(new_line_text_l)

    print(f"{new_line_text_l=}")

    fuzz_ratio_s_space_first_sub_line_text_l_d = {}

    # fill line_text_l_fuzz_ratio_d
    fuzz_str_set = set()
    for s_space_first_sub_line_text in s_space_first_sub_line_text_l:
        cleaned_line_text_str = fc.get_cleaned_line_text_str__from__sub_line_text_str(s_space_first_sub_line_text)
        fuzz_str = fc.get_subs_fuzz_str__from__all_sub_lines_cleaned_text_str(cleaned_line_text_str)

        # dont duplicate effort by checking if a prev. str gave the same fuzz_str
        if fuzz_str in fuzz_str_set:
            continue
        fuzz_str_set.add(fuzz_str)

        # fill fuzz_ratio_s_space_first_sub_line_text_l_d
        







