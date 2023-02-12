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
from sms.thread_tools import Simple_Thread_Manager
import vid_edit_utils as veu
import subtitle_utils as su
import fuzz_common as fc

THREADING_ENABLED = True
MAX_NUM_MS__FIRST_SUB_END__WORTH_CHECKING = 5000



def _get_worth_and_not_worth_checking__matched_vid_sub_dir_lists(matched_vid_sub_dir_l):
    def _worth_checking(in_sub_path):
        subs = pysubs2.load(in_sub_path, encoding="latin1")
        if subs[0].end <= MAX_NUM_MS__FIRST_SUB_END__WORTH_CHECKING:
            return True
        return False
    
    worth_checking_mvsd_l = []
    not_worth_checking_mvsd_l = []

    for mvsd in matched_vid_sub_dir_l:
        if _worth_checking(mvsd.sub_path):
            worth_checking_mvsd_l.append(mvsd)
        else:
            not_worth_checking_mvsd_l.append(worth_checking_mvsd_l)

    return worth_checking_mvsd_l, not_worth_checking_mvsd_l


def trim_first_sub_text_if_needed(in_sub_path, in_vid_path, out_sub_path):
    subs = pysubs2.load(in_sub_path, encoding="latin1")

    # TODO How to tell if this needs to be done?
    # TODO How long does this take? just do this to every clip?
    # if subs[0].start != 0:
    #     return in_sub_path

    # get fuzz str of transcript_str of spoken dialog in vid between start and end time of first sub
    first_sub_line_start_time_sec = subs[0].start / 1000
    first_sub_line_end_time_sec   = subs[0].end   / 1000

    transcript_str, transcript_str_confidence  = aeu.get_transcript_from_vid(in_vid_path, 0, first_sub_line_end_time_sec, with_confidence=True)
    print(f"{transcript_str=}")
    print(f"{transcript_str_confidence=}")
    # LATER do something with transcript_str_confidence?

    cleaned_transcript_str = fc.get_cleaned_line_text_str__from__sub_line_text_str(transcript_str)
    transcript_fuzz_str = fc.get_subs_fuzz_str__from__all_sub_lines_cleaned_text_str(cleaned_transcript_str)

    new_sub_line_text_l = []

    fist_sub_line_text_str = subs[0].text
    for newline_char in ["\\n", "\\N", "\\r"]:
        fist_sub_line_text_str = fist_sub_line_text_str.replace(newline_char, " \\n")

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
    for new_sub_line_text in new_sub_line_text_l:
        cleaned_new_sub_line_text_str = fc.get_cleaned_line_text_str__from__sub_line_text_str(new_sub_line_text)
        new_sub_line_text_fuzz_str = fc.get_subs_fuzz_str__from__all_sub_lines_cleaned_text_str(cleaned_new_sub_line_text_str)

        # dont duplicate effort by checking if a prev. str gave the same fuzz_str
        if new_sub_line_text_fuzz_str in new_sub_line_text_fuzz_str_l:
            continue
        print(f"adding {new_sub_line_text_fuzz_str=}")
        new_sub_line_text_fuzz_str_l.append(new_sub_line_text_fuzz_str)

        # fill fuzz_ratio_new_sub_line_text_l_d
        # LATER add early return if first check of full text is like 99% match?
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

    # If go through whole process and turns out best fuzz came from OG, say so and do nothing if in_sub_path == in_sub_path
    if subs[0].text == capped_best_new_sub_line_text_str:
        print(f"OG first sub text was already best match")
        if in_sub_path == in_sub_path:
            return

    subs[0].text = capped_best_new_sub_line_text_str
    subs.save(out_sub_path)



def trim_first_sub_text_if_needed__for_matched_vid_sub_dir_l(matched_vid_sub_dir_l):
    print("Trimming 1st sub text if needed for matched_vid_sub_dir_l...")
    worth_checking_mvsd_l, not_worth_checking_mvsd_l = _get_worth_and_not_worth_checking__matched_vid_sub_dir_lists(matched_vid_sub_dir_l)
    print(f"{len(worth_checking_mvsd_l)=}")
    print(f"{len(not_worth_checking_mvsd_l)=}")

    # with Simple_Thread_Manager(THREADING_ENABLED, cfg.NUM_CORES) as stm:
    #     for mvsd in matched_vid_sub_dir_l:
    #         stm.thread_func_if_enabled(trim_first_sub_text_if_needed, str1, str2)



if __name__ == '__main__':
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')
    from process_matched_vid_sub_dirs import process_matched_vid_sub_dirs
    process_matched_vid_sub_dirs()



    # new_sub_path = _trim_first_sub_text_if_needed("C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__National_Dog_Day__Clip____TBS/f3_Family Guy.S08E07.Jerome Is the New Black.FQM.srt",
    # "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy___TBS/Family_Guy__National_Dog_Day__Clip____TBS/Family_Guy__National_Dog_Day__Clip____TBS.mp4",
    # "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__National_Dog_Day__Clip____TBS/first_sub_trimmed_test.srt")

    # print(f"{new_sub_path=}")
    print("End of Main")







