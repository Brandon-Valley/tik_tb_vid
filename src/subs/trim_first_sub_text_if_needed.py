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

    # get fuzz str of transcript_str of spoken dialog in vid between start and end time of first sub
    first_sub_line_start_time_sec = subs[0].start / 1000
    first_sub_line_end_time_sec   = subs[0].end   / 1000
    # print(f"{aeu.get_transcript_from_vid(in_vid_path, first_sub_line_start_time_sec, first_sub_line_end_time_sec, with_confidence=True)=}")
    # transcript_str, transcript_str_confidence  = aeu.get_transcript_from_vid(in_vid_path, subs[0].start, subs[0].end, with_confidence=True)
    transcript_str, transcript_str_confidence  = aeu.get_transcript_from_vid(in_vid_path, 0, first_sub_line_end_time_sec, with_confidence=True)
    print(f"{transcript_str=}")
    print(f"{transcript_str_confidence=}")
    # LATER do something with transcript_str_confidence?

    cleaned_transcript_str = fc.get_cleaned_line_text_str__from__sub_line_text_str(transcript_str)
    transcript_fuzz_str = fc.get_subs_fuzz_str__from__all_sub_lines_cleaned_text_str(cleaned_transcript_str)


    # first_sub_line_text = subs[0].text

    new_sub_line_text_l = []

    fist_sub_line_text_str = subs[0].text
    for newline_char in ["\\n", "\\N", "\\r"]:
        fist_sub_line_text_str = fist_sub_line_text_str.replace(newline_char, " \\n")

    # s_space_first_sub_line_text_l = subs[0].text.split(" ")
    s_space_first_sub_line_text_l = fist_sub_line_text_str.split(" ")
    for i in range(len(s_space_first_sub_line_text_l)):
        new_line_text = " ".join(s_space_first_sub_line_text_l[i:])

        # remove leading newlines
        new_line_text = new_line_text.lstrip(" \\n")

        print(f"{new_line_text=}")
        new_sub_line_text_l.append(new_line_text)

    print(f"{new_sub_line_text_l=}")

    fuzz_ratio_new_sub_line_text_l_d = {}

    # fill line_text_l_fuzz_ratio_d
    new_sub_line_text_fuzz_str_l = []
    # for s_space_first_sub_line_text in s_space_first_sub_line_text_l:
    for new_sub_line_text in new_sub_line_text_l:
        cleaned_new_sub_line_text_str = fc.get_cleaned_line_text_str__from__sub_line_text_str(new_sub_line_text)
        new_sub_line_text_fuzz_str = fc.get_subs_fuzz_str__from__all_sub_lines_cleaned_text_str(cleaned_new_sub_line_text_str)

        # dont duplicate effort by checking if a prev. str gave the same fuzz_str
        if new_sub_line_text_fuzz_str in new_sub_line_text_fuzz_str_l:
            continue
        print(f"adding {new_sub_line_text_fuzz_str=}")
        new_sub_line_text_fuzz_str_l.append(new_sub_line_text_fuzz_str)

        # fill fuzz_ratio_new_sub_line_text_l_d
        fuzz_ratio = fuzz.ratio(new_sub_line_text_fuzz_str, transcript_fuzz_str)

        if fuzz_ratio in fuzz_ratio_new_sub_line_text_l_d.keys():
            fuzz_ratio_new_sub_line_text_l_d[fuzz_ratio].append(new_sub_line_text)
        else:
            fuzz_ratio_new_sub_line_text_l_d[fuzz_ratio] = [new_sub_line_text]

    print("fuzz_ratio_new_sub_line_text_l_d:")
    pprint(fuzz_ratio_new_sub_line_text_l_d)

    best_fuzz_ratio = max(fuzz_ratio_new_sub_line_text_l_d.keys())
    raw_best_new_sub_line_text_str = fuzz_ratio_new_sub_line_text_l_d[best_fuzz_ratio][0]

    capped_best_new_sub_line_text_str = raw_best_new_sub_line_text_str.capitalize()

    subs[0].text = capped_best_new_sub_line_text_str

    subs.save(out_sub_path)



if __name__ == '__main__':
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')
    new_sub_path = trim_first_sub_text_if_needed("C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__National_Dog_Day__Clip____TBS/f3_Family Guy.S08E07.Jerome Is the New Black.FQM.srt",
    "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy___TBS/Family_Guy__National_Dog_Day__Clip____TBS/Family_Guy__National_Dog_Day__Clip____TBS.mp4",
    "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__National_Dog_Day__Clip____TBS/first_sub_trimmed_test.srt")

    print(f"{new_sub_path=}")
    print("End of Main")







