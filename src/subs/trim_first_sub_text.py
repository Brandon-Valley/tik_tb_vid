import collections
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

from collections import namedtuple
from pprint import pprint
import re
from typing import Optional, List, Tuple, Sequence
from pysubs2.common import IntOrFloat

import time
import os
from os.path import join
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
from sms.logger import json_logger
from sms.thread_tools.Simple_Thread_Manager import Simple_Thread_Manager
import vid_edit_utils as veu
import subtitle_utils as su
import fuzz_common as fc

THREADING_ENABLED = True

MAX_NUM_MS__FIRST_SUB_END__WORTH_CHECKING = 5000

# Most real matches are 100%
# Has to be high, otherwise will miss things like:
#   - "Carter, as your boss, I command you\nto have a viewing party"
#   - "Huh?\nDid I tell ya, Lois?"
MIN_FUZZ_RATION_TO_CHANGE_FIRST_SUB = 95

LOG_JSON_PATH = join(cfg.PROCESS_MATCHED_VID_SUB_DIRS_LOGS_DIR_PATH, "trim_first_sub_text_log.json")
INDIV_RUN_LOGS_DIR_PATH = join(cfg.PROCESS_MATCHED_VID_SUB_DIRS_LOGS_DIR_PATH, "trim_first_sub_text_indiv_runs")


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
            not_worth_checking_mvsd_l.append(mvsd)

    return worth_checking_mvsd_l, not_worth_checking_mvsd_l


def _trim_first_sub_text_if_needed(in_sub_path, in_vid_path, out_sub_path):
    def _cap_only_1st_letter_of_str(in_str):
        if len(in_str) == 0:
            raise ValueError(f"{len(in_str)=}, should not be possible")
        
        if not in_str[0].isalpha():
            return in_str
        
        if len(in_str) == 1:
            return in_str.capitalize()
        else:
            return in_str[0].capitalize() + in_str[1:]
        
    start_time = time.time()

    def _log_run(outcome_str, fuzz_ratio_new_sub_line_text_l_d = None):
        out_sub_path_log_str = out_sub_path # cant re-assign out_sub_path or else it becomes a local var and won't be able to access from higher scope
        if in_sub_path == out_sub_path:
            out_sub_path_log_str = "^^"

        run_od = collections.OrderedDict()
        run_od["outcome_str"]  = outcome_str
        run_od["in_sub_path"]  = in_sub_path
        run_od["out_sub_path"] = out_sub_path_log_str
        run_od["threaded_run_time"] = time.time() - start_time
        run_od["fuzz_ratio_new_sub_line_text_l_d"] = fuzz_ratio_new_sub_line_text_l_d

        out_json_path = join(INDIV_RUN_LOGS_DIR_PATH, f"run_od_{Path(in_sub_path).stem}.json")
        json_logger.write(run_od, out_json_path)

    def _get_normed_newlines_str(in_str):
        in_str = in_str.replace('\r\n', '\n').replace('\r', ' \n')
        in_str = in_str.replace('\\N', '\n')
        return in_str

    def _get_new_sub_line_text_l():

        # fist_sub_line_text_str = subs[0].text
        # fist_sub_line_text_str = fist_sub_line_text_str.replace('\r\n', '\n').replace('\r', ' \n')
        # fist_sub_line_text_str = fist_sub_line_text_str.replace('\\N', '\n')
        fist_sub_line_text_str = _get_normed_newlines_str(subs[0].text)

        # fist_sub_line_text_str = fist_sub_line_text_str.replace('\\\\N', '\n')
        print(f"{fist_sub_line_text_str=}")

        s_space_first_sub_line_text_l = fist_sub_line_text_str.split(" ")

        s_space_and_newline_first_sub_line_text_l = []
        for s_str in s_space_first_sub_line_text_l:
            s_space_and_newline_first_sub_line_text_l.append(s_str)

        init_new_sub_line_text_l = []

        # s_space_first_sub_line_text_l = re.split(' |.\n', fist_sub_line_text_str)
        for i in range(len(s_space_first_sub_line_text_l)):
            new_line_text = " ".join(s_space_first_sub_line_text_l[i:])

            # remove leading newlines
            new_line_text = new_line_text.lstrip(" \n")

            print(f"{new_line_text=}")
            init_new_sub_line_text_l.append(new_line_text)

            if "worried" in new_line_text:
                print("here")

        final_new_sub_line_text_l = []

        for init_str in init_new_sub_line_text_l:
            final_new_sub_line_text_l.append(init_str)

            newline_split_str_l = init_str.split(" ")
            if len(newline_split_str_l) > 1 and "\n" in newline_split_str_l[0]: # HACK assumes will never have multiple newlines between 2 spaces
                final_new_sub_line_text_l.append(init_str.split("\n")[1])

        print("final_new_sub_line_text_l:")
        pprint(final_new_sub_line_text_l)
        return final_new_sub_line_text_l

        

    subs = pysubs2.load(in_sub_path, encoding="latin1")

    # get fuzz str of transcript_str of spoken dialog in vid between start and end time of first sub
    first_sub_line_start_time_sec = subs[0].start / 1000
    first_sub_line_end_time_sec   = subs[0].end   / 1000

    transcript_str, transcript_str_confidence  = aeu.get_transcript_from_vid(in_vid_path, 0, first_sub_line_end_time_sec, with_confidence=True)
    print(f"{transcript_str=}")
    print(f"{transcript_str_confidence=}")
    # LATER do something with transcript_str_confidence?

    # if could not recognize any speech from 0 to first sub end, just return
    if transcript_str == False:
        print(f"    No speech recognized from start of vid to {first_sub_line_end_time_sec}, returning...")
        # LATER log?
        _log_run("NO_SPEECH_RECOGNIZED_FROM_START_OF_VID_TO_END_OF_FIRST_SUB")
        return

    final_new_sub_line_text_l = _get_new_sub_line_text_l()

    cleaned_transcript_str = fc.get_cleaned_line_text_str__from__sub_line_text_str(transcript_str)
    transcript_fuzz_str = fc.get_subs_fuzz_str__from__all_sub_lines_cleaned_text_str(cleaned_transcript_str)


    # print(f"{final_new_sub_line_text_l=}")

    fuzz_ratio_new_sub_line_text_l_d = {}

    # fill line_text_l_fuzz_ratio_d
    new_sub_line_text_fuzz_str_l = []
    for new_sub_line_text in final_new_sub_line_text_l:

        if "worried" in new_sub_line_text:
            print("here")


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

    capped_best_new_sub_line_text_str = _cap_only_1st_letter_of_str(raw_best_new_sub_line_text_str)
    # capped_best_new_sub_line_text_str = capped_best_new_sub_line_text_str.replace(" \\n", "\\n")
    capped_best_new_sub_line_text_str = capped_best_new_sub_line_text_str.replace(" \n", "\n")

    # If go through whole process and turns out best fuzz came from OG, say so and do nothing if in_sub_path == in_sub_path
    normed_newlines_og_first_sub_text_str = _get_normed_newlines_str(subs[0].text)
    if normed_newlines_og_first_sub_text_str == capped_best_new_sub_line_text_str:
        print(f"OG first sub text was already best match")
        if in_sub_path == in_sub_path:
            _log_run("OG_WAS_BEST_MATCH", fuzz_ratio_new_sub_line_text_l_d)
            return

    # - Throw exception if match is longest value in fuzz_ratio_new_sub_line_text_l_d, b/c that means it
    #   should have been caught above and something about your matching is wrong
    # Find longest_raw_new_sub_line_text_str
    longest_raw_new_sub_line_text_str = ""
    for _, new_sub_line_text_l in fuzz_ratio_new_sub_line_text_l_d.items():
        for new_sub_line_text in new_sub_line_text_l:
            if len(new_sub_line_text) > len(longest_raw_new_sub_line_text_str):
                longest_raw_new_sub_line_text_str = new_sub_line_text
    if longest_raw_new_sub_line_text_str == raw_best_new_sub_line_text_str:
        raise ValueError(f"{raw_best_new_sub_line_text_str=} is the longest value in fuzz_ratio_new_sub_line_text_l_d, but did not return above with 'OG_WAS_BEST_MATCH', that means something is wrong with your match, why does {subs[0].text=} != {capped_best_new_sub_line_text_str=}")

    # Need to meet or exceed MIN_FUZZ_RATION_TO_CHANGE_FIRST_SUB
    if best_fuzz_ratio < MIN_FUZZ_RATION_TO_CHANGE_FIRST_SUB:
        print(f"{best_fuzz_ratio=} < {MIN_FUZZ_RATION_TO_CHANGE_FIRST_SUB=}, so not changing first sub text to {capped_best_new_sub_line_text_str=}, returning...")
        _log_run("BEST_FUZZ_RATIO_TOO_LOW", fuzz_ratio_new_sub_line_text_l_d)
        return

    print(f"Trimming first sub line, \n    OG:  {subs[0].text}\n    New: {capped_best_new_sub_line_text_str}\n    Writing too: {out_sub_path}...")

    if "construct" in capped_best_new_sub_line_text_str: # TMP
        print("here")

    subs[0].text = capped_best_new_sub_line_text_str
    # subs.save(out_sub_path) # TODO PUT BACK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    _log_run("SUCCESS", fuzz_ratio_new_sub_line_text_l_d)


def _log_total(start_time, worth_checking_mvsd_l, not_worth_checking_mvsd_l):
    def _get_trim_first_sub_text_run_od_l__from__indiv_run_jsons():
        json_path_l = fsu.get_dir_content_l(INDIV_RUN_LOGS_DIR_PATH, "file")
        run_od_l = []
        for json_path in json_path_l:
            run_od = json_logger.read(json_path)
            run_od_l.append(run_od)
        return run_od_l
    
    def _get_run_outcome_str_occ_d(run_od_l):
        run_outcome_str_occ_d = {}

        for run_od in run_od_l:
            # print(f"{run_od=}")
            outcome_str = run_od["outcome_str"]
            if outcome_str in run_outcome_str_occ_d.keys():
                run_outcome_str_occ_d[outcome_str] += 1
            else:
                run_outcome_str_occ_d[outcome_str] = 1

        sorted_d = {k: v for k, v in sorted(run_outcome_str_occ_d.items(), key=lambda item: item[1])}
        return sorted_d


    run_od_l = _get_trim_first_sub_text_run_od_l__from__indiv_run_jsons()

    log_od = collections.OrderedDict()
    log_od["Total_Time"] = time.time() - start_time
    log_od["Total_matched_vid_sub_dirs"] = len(worth_checking_mvsd_l) + len(not_worth_checking_mvsd_l)
    log_od["len(worth_checking_mvsd_l)"] = len(worth_checking_mvsd_l)
    log_od["len(not_worth_checking_mvsd_l)"] = len(not_worth_checking_mvsd_l)
    log_od["run_outcome_str_occ_d"] = _get_run_outcome_str_occ_d(run_od_l)
    log_od["run_od_l"] = run_od_l
    log_od["not_worth_checking_mvsd__sub_path_l"] = [mvsd.sub_path for mvsd in not_worth_checking_mvsd_l]

    print(f"Writing total log of trim first sub text to {LOG_JSON_PATH}...")
    json_logger.write(log_od, LOG_JSON_PATH)


####################################################################################################
# MAIN
####################################################################################################
def trim_first_sub_text_if_needed__for_matched_vid_sub_dir_l(matched_vid_sub_dir_l):
    print("Trimming 1st sub text if needed for matched_vid_sub_dir_l...")
    start_time = time.time()
    worth_checking_mvsd_l, not_worth_checking_mvsd_l = _get_worth_and_not_worth_checking__matched_vid_sub_dir_lists(matched_vid_sub_dir_l)

    fsu.delete_if_exists(INDIV_RUN_LOGS_DIR_PATH)
    fsu.delete_if_exists(LOG_JSON_PATH)

    with Simple_Thread_Manager(THREADING_ENABLED, cfg.NUM_CORES) as stm:
        for mvsd in worth_checking_mvsd_l:
            # fix in-place
            stm.thread_func_if_enabled(_trim_first_sub_text_if_needed, mvsd.sub_path, mvsd.vid_path, mvsd.sub_path)

    _log_total(start_time, worth_checking_mvsd_l, not_worth_checking_mvsd_l)


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







