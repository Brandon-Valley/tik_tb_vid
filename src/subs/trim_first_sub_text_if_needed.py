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
from sms.audio_edit_utils import audio_edit_utils as aeu
from sms.logger import txt_logger
import vid_edit_utils as veu
import subtitle_utils as su
import fuzz_common as fc

def trim_first_sub_text_if_needed(in_sub_path, in_vid_path, out_sub_path):
    subs = pysubs2.load(in_sub_path, encoding="latin1")

    # TODO How to tell if this needs to be done?
    # TODO How long does this take? just do this to every clip?
    # if subs[0].start != 0:
    #     return in_sub_path

    # get transcript_str of spoken dialog in vid between start and end time of first sub
    first_sub_line_start_time_sec = subs[0].start / 1000
    first_sub_line_end_time_sec   = subs[0].end   / 1000
    # print(f"{aeu.get_transcript_from_vid(in_vid_path, first_sub_line_start_time_sec, first_sub_line_end_time_sec, with_confidence=True)=}")
    # transcript_str, transcript_str_confidence  = aeu.get_transcript_from_vid(in_vid_path, subs[0].start, subs[0].end, with_confidence=True)
    transcript_str, transcript_str_confidence  = aeu.get_transcript_from_vid(in_vid_path, 0, first_sub_line_end_time_sec, with_confidence=True)
    print(f"{transcript_str=}")
    print(f"{transcript_str_confidence=}")

    # LATER do something with transcript_str_confidence?

    # first_sub_line_text = subs[0].text
    new_line_text_l = []

    # fill keys of new_line_text_l
    s_space_first_sub_line_text_l = subs[0].text.split(" ")
    for i in range(len(s_space_first_sub_line_text_l)):
        new_line_text = " ".join(s_space_first_sub_line_text_l[i:])
        # TODO Remove leading newlines from new_line_text
        # new_line_text = 

        print(f"{new_line_text=}")
        new_line_text_l.append(new_line_text)

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

        print("fuzz_str_set:")
        pprint(fuzz_str_set)
        # fill fuzz_ratio_s_space_first_sub_line_text_l_d


if __name__ == '__main__':
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')
    new_sub_path = trim_first_sub_text_if_needed("C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__National_Dog_Day__Clip____TBS/f3_Family Guy.S08E07.Jerome Is the New Black.FQM.srt",
    "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy___TBS/Family_Guy__National_Dog_Day__Clip____TBS/Family_Guy__National_Dog_Day__Clip____TBS.mp4",
    "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__National_Dog_Day__Clip____TBS/first_sub_trimmed_test.srt")

    print(f"{new_sub_path=}")
    print("End of Main")







