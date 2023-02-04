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

FUZZ_STR_DELIM = ' '
MKV_TOOL_NIX_FIRST_SUB_TRACK_ID = 2 


def _get_and_check_real_and_auto_subs(real_sub_file_path, auto_sub_file_path):
    real_subs = pysubs2.load(real_sub_file_path, encoding="latin1")
    auto_subs = pysubs2.load(auto_sub_file_path, encoding="latin1")

    if len(real_subs) == 0:
        raise Exception(f"ERROR: {len(real_subs)=} - I assume this is a problem?")
    if len(auto_subs) == 0:
        raise Exception(f"ERROR: {len(auto_subs)=} - I assume this is a problem?")
    if len(auto_subs) > len(real_subs):
        raise Exception(f"ERROR: {len(auto_subs)=} > {len(real_subs)=} - This should never be possible, maybe sub formats are weird? {real_sub_file_path=}, {auto_sub_file_path=}")

    return real_subs, auto_subs

def _compare_sub_slots_for_single_offset(real_subs, auto_subs, sub_slot_offset):
    print(f"..in _compare_sub_slots_for_single_offset() - {sub_slot_offset=}")
    sub_slot_score = 0
    # best_auto_sub_line_match_index = None
    best_auto_sub_line_match_index = 0
    best_auto_sub_line_match_score = 0

    # print(f"..{len(auto_sub_line)=}")
    for auto_sub_line_num, auto_sub_line in enumerate(auto_subs):
        real_sub_line = real_subs[auto_sub_line_num + sub_slot_offset]
        # print(f"....{real_sub_line.text=}")

        auto_sub_line_match_score = fuzz.ratio(auto_sub_line.text, real_sub_line.text)
        # print(f"......{auto_sub_line_match_score=}")
        sub_slot_score += auto_sub_line_match_score

        if auto_sub_line_match_score > best_auto_sub_line_match_score:
            best_auto_sub_line_match_score = auto_sub_line_match_score
            best_auto_sub_line_match_index = auto_sub_line_num

    return sub_slot_score, best_auto_sub_line_match_index

def _get_best_sub_slot_offset_and_best_line_match_index(real_subs, auto_subs):
    possible_sub_slots = len(real_subs) - len(auto_subs)
    print(f"{possible_sub_slots=}")

    best_sub_slot_offset = 0
    best_sub_slot_score = 0
    best_auto_sub_line_match_index_for_best_sub_slot_offset = 0 # is this correct thing to do if auto_subs == real_subs?
                                                                # any way len(auto_subs) == len(real_subs) but auto_subs != real_subs? # TODO test
    for sub_slot_offset in range(possible_sub_slots):
        print(f"{sub_slot_offset=}")
        sub_slot_score, best_auto_sub_line_match_index = _compare_sub_slots_for_single_offset(real_subs, auto_subs, sub_slot_offset)
        print(f"......{sub_slot_score=}")
        print(f"......{best_auto_sub_line_match_index=}")

        if best_auto_sub_line_match_index == None:
            raise Exception(f"ERROR: {best_auto_sub_line_match_index=}, this means maybe some subs are empty or something else happened? This can happen even if its a legit show clip (EX: Herbert), This error happens when fuzz ratio is 0 for every episode.  Can happen when there are very few subtitles to match, possibly with long pauses in-between, possibly with sound effects that become false subs (like glass breaking == Thank you), possibly with hard to understand characters (Herbert)")

        if sub_slot_score > best_sub_slot_score:
            print(f"....new lead sub_slot found:")
            best_sub_slot_offset = sub_slot_offset
            best_sub_slot_score = sub_slot_score
            best_auto_sub_line_match_index_for_best_sub_slot_offset = best_auto_sub_line_match_index
            print(f"      - {best_sub_slot_offset=}")
            print(f"      - {best_sub_slot_score=}")
            print(f"      - {best_auto_sub_line_match_index_for_best_sub_slot_offset=}")

    print("Final best sub_slot for file:")
    print(f"  - {best_sub_slot_offset=}")
    print(f"  - {best_sub_slot_score=}")
    print(f"  - {best_auto_sub_line_match_index_for_best_sub_slot_offset=}")
    print(f"  - {auto_subs[best_auto_sub_line_match_index_for_best_sub_slot_offset].text=}")
    print(f"  - {real_subs[best_sub_slot_offset + best_auto_sub_line_match_index_for_best_sub_slot_offset].text=}")

    return best_sub_slot_offset, best_auto_sub_line_match_index_for_best_sub_slot_offset


def _get_real_sub_shift_num_ms(best_match_real_sub_line, best_match_auto_sub_line):

    if best_match_auto_sub_line.start > best_match_real_sub_line.start:
        raise Exception(f"ERROR: {best_match_auto_sub_line.start=} > {best_match_real_sub_line.start=} - This should never be possible. Last time this happened it was caused by picking wrong real subs episode.")

    real_sub_shift_num_ms = best_match_real_sub_line.start - best_match_auto_sub_line.start

    return real_sub_shift_num_ms


def _clean_trimmed_subs(in_sub_path, out_sub_path, vid_num_ms):
    clean_sub_line_l = []
    subs = pysubs2.load(in_sub_path, encoding="latin1")

    # clean 0'ed start
    # will have subs like: 00:00:00,400 --> 00:00:00,400
    for line_num, line in enumerate(subs):
        if line.start == line.end:
            subs[line_num] == None
        else:
            print(f"Found first good subs text = {line.text=}")
            clean_sub_line_l = subs[line_num:]
            break

    # Remove end that lasts past length of vid
    for line_num, line in enumerate(clean_sub_line_l):
        # if line.start > vid_num_ms or line.end > vid_num_ms:
        # LATER if too many vids have one small half-second blip of subtitles appear at very end, should add MIN_LAST_SUB_LEN so long dialog at end is not lost
        if line.start > vid_num_ms:
            clean_sub_line_l = clean_sub_line_l[:line_num]
            print(f"found first line past end of vid: {line.text=}")
            break

    su.write_manual_sub_line_l(clean_sub_line_l, out_sub_path)


def _make_final_vid_trimmed_re_timed_sub_from_real_sub(out_sub_path, clip_dir_data, real_sub_path, real_subs, best_match_auto_sub_line, best_match_real_sub_line):
    real_sub_shift_num_ms = _get_real_sub_shift_num_ms(best_match_real_sub_line, best_match_auto_sub_line)
    print(f"{real_sub_shift_num_ms=}")
    neg_real_sub_shift_num_ms = real_sub_shift_num_ms * -1

    # init shift
    real_subs.shift(ms = neg_real_sub_shift_num_ms)

    ms_shifted_sub_path        = os.path.join(clip_dir_data.trim_re_time_working_dir_path, f"MS_SHIFTED__{Path(real_sub_path).name}")
    synced_ms_shifted_sub_path = os.path.join(clip_dir_data.trim_re_time_working_dir_path, f"MS_SHIFTED__SYNCED__{Path(real_sub_path).name}")

    print(f"{ms_shifted_sub_path=}")
    real_subs.save(ms_shifted_sub_path)

    # This will throw warning, this is normal:  WARNING: low quality of fit. Wrong subtitle file?
    # This happens b/c did not trim out the first part of re-timed srt which is all set to 0 (like the theme) and did not trim end
    su.sync_subs_with_vid(vid_path     = clip_dir_data.mp4_path,
                          in_sub_path  = ms_shifted_sub_path,
                          out_sub_path = synced_ms_shifted_sub_path)
    # rest of real subs still in final .srt, need to clean or it will mess with vid len once embedded to mkv
    vid_num_ms = veu.get_vid_length(clip_dir_data.mp4_path) * 1000
    print(f"{vid_num_ms=}")

    _clean_trimmed_subs(synced_ms_shifted_sub_path, out_sub_path, vid_num_ms)


def _get_best_match_non_main_subs_line(best_match_auto_sub_line, non_main_subs):
    best_fuzz_ratio = 0
    best_match_non_main_subs_line = None

    for non_main_sub_line in non_main_subs:
        fuzz_ratio = fuzz.ratio(best_match_auto_sub_line.text, non_main_sub_line.text)

        if fuzz_ratio > best_fuzz_ratio:
            best_fuzz_ratio = fuzz_ratio
            best_match_non_main_subs_line = non_main_sub_line

    return best_match_non_main_subs_line


def _make_non_main_final_vid_subs__and__get_final_vid_sub_path_l(main_final_vid_sub_path, clip_dir_data, ep_sub_data, best_match_auto_sub_line):
    def _single_thread_non_main_final_vid_subs(non_main_final_vid_sub_path, non_main_sub_path, best_match_auto_sub_line, clip_dir_data):
        print(f"in _single_thread_non_main_final_vid_subs() - {non_main_final_vid_sub_path=}")
        # get best_match_non_main_subs_line
        non_main_subs = pysubs2.load(non_main_sub_path, encoding="latin1")
        best_match_non_main_subs_line = _get_best_match_non_main_subs_line(best_match_auto_sub_line, non_main_subs)
        print(best_match_non_main_subs_line.text)

        print(f"{non_main_final_vid_sub_path=}")

        # LATER thread this? syncing tipples runtime
        _make_final_vid_trimmed_re_timed_sub_from_real_sub(out_sub_path             = non_main_final_vid_sub_path,
                                                           clip_dir_data            = clip_dir_data,
                                                           real_sub_path            = non_main_sub_path,
                                                           real_subs                = non_main_subs,
                                                           best_match_auto_sub_line = best_match_auto_sub_line,
                                                           best_match_real_sub_line = best_match_non_main_subs_line)

    final_vid_sub_path_l = [main_final_vid_sub_path]

    print(f"{len(ep_sub_data.non_main_sub_file_path_l)=}")
    
    # start the thread pool
    with ThreadPoolExecutor(cfg.NUM_CORES) as executor:
        futures = []
        for non_main_sub_num, non_main_sub_path in enumerate(ep_sub_data.non_main_sub_file_path_l):
            non_main_final_vid_sub_path = clip_dir_data.get_final_vid_sub_path(non_main_sub_path, non_main_sub_num + 1)
            final_vid_sub_path_l.append(non_main_final_vid_sub_path)
            # submit tasks and collect futures
            futures = [executor.submit(_single_thread_non_main_final_vid_subs, non_main_final_vid_sub_path, non_main_sub_path, best_match_auto_sub_line, clip_dir_data)]

        # wait for all tasks to complete
        print('Waiting for tasks to complete...')
        wait(futures)
        print('All tasks are done!')

    return final_vid_sub_path_l


def get_sub_path_lang_dl__from__final_vid_sub_path_l(final_vid_sub_path_l, lang):
    """
        sub_path_lang_dl = [
                            {
                                "path": "<ABS_PATH_TO_SUB_FILE_1>",
                                "lang": "en2"
                            },
                            {
                                "path": "<ABS_PATH_TO_SUB_FILE_2>",
                                "lang": "en3"
                            },
                        ]
    """
    sub_path_lang_dl = []
    for final_vid_sub_num, final_vid_sub_path in enumerate(final_vid_sub_path_l):
        sub_path_lang_dl.append({
            "path": final_vid_sub_path,
            "lang": f"{lang}{final_vid_sub_num + MKV_TOOL_NIX_FIRST_SUB_TRACK_ID}"
        })
    return sub_path_lang_dl


def _get_unique_final_vid_sub_path_l__and__rename_duplicates(final_vid_sub_path_l):
    unique_sub_path_l, dup_sub_path_l = fsu.get_file_path_l_w_duplicate_files_removed(final_vid_sub_path_l, return_removed_file_path_l = True, verbose = False)
    # Want to keep duplicate subs for record-keeping/testing purposes
    for dup_sub_path in dup_sub_path_l:
        new_file_name = f"DUPLICATE__{Path(dup_sub_path).name}"
        new_file_path = os.path.join(Path(dup_sub_path).parent.__str__(), new_file_name)
        fsu.rename_file_overwrite(dup_sub_path, new_file_path)

    # There is a very rare issue that can cause _clean_trimmed_subs() to write an empty file.
    # It is caused by ms shifting including a first subtitle that is not actually spoken in the video
    #   - Likely caused by the video being cut immediately after the dialog ends
    # Example: S04E01 - Family_Guy__Comic_Book__Clip____TBS - "Family Guy - 04x01 - North by North Quahog.HDTV.Addic7ed.com.srt"
    # Should probably dig deeper to find the root of this issue, but for now, just skip the sub if this happens
    #   - (Kinda like how duplicates are treated)
    unique_non_empty_sub_path_l = []
    for unique_sub_path in unique_sub_path_l:
        if os.path.getsize(unique_sub_path) == 0:
            new_file_name = f"EMPTY__{Path(unique_sub_path).name}"
            new_file_path = os.path.join(Path(unique_sub_path).parent.__str__(), new_file_name)
            fsu.rename_file_overwrite(unique_sub_path, new_file_path)
        else:
            unique_non_empty_sub_path_l.append(unique_sub_path)

    return unique_non_empty_sub_path_l

def trim_and_re_time_real_sub_file_from_auto_subs(clip_dir_data, ep_sub_data, lang):
    """
        - After finding correct real sub file with faster get_real_episode_sub_data_from_auto_sub(),
          go through real_sub_file and find exact amount to shift real_sub_file by to align to clip.
            - This is done by finding real_sub_shift_num_ms
        - Then use this real_sub_shift_num_ms to shift real sub path to align with clip
            - This will get things close but not perfect yet
        - Then sub sync to make sure everything aligns perfectly
        - Finally, trim out the unused sub lines from the new re-timed real_sub_file
            - This is needed b/c otherwise it messes with vid length of final vid once embedded as
              single mkv. # TODO for all
    """

    print(f"in trim_and_re_time_real_sub_file_from_auto_subs()")
    print(f"{clip_dir_data.mp4_path=}")
    print(f"{ep_sub_data.main_sub_file_path=}")
    print(f"{clip_dir_data.auto_sub_path=}")

    # init
    start_time = time.time()

    # Read subs and validate inputs
    real_subs, auto_subs = _get_and_check_real_and_auto_subs(ep_sub_data.main_sub_file_path, clip_dir_data.auto_sub_path)

    # Find best match data from main episode subs
    s_time = time.time()
    main_best_sub_slot_offset, best_auto_sub_line_match_index_for_best_sub_slot_offset = _get_best_sub_slot_offset_and_best_line_match_index(real_subs, auto_subs)
    exe_time = time.time() - s_time
    print(f"_get_best_sub_slot_offset_and_best_line_match_index() took {exe_time} seconds.")
    print("after _get_best_sub_slot_offset_and_best_line_match_index()")
    print(f"  {main_best_sub_slot_offset=}")
    print(f"  {best_auto_sub_line_match_index_for_best_sub_slot_offset=}")

    sub_path_lang_dl = []

    main_final_vid_sub_path = clip_dir_data.get_final_vid_sub_path(ep_sub_data.main_sub_file_path, 0)

    best_match_auto_sub_line = auto_subs[best_auto_sub_line_match_index_for_best_sub_slot_offset]
    best_match_real_sub_line = real_subs[main_best_sub_slot_offset + best_auto_sub_line_match_index_for_best_sub_slot_offset]

    _make_final_vid_trimmed_re_timed_sub_from_real_sub(main_final_vid_sub_path, clip_dir_data, ep_sub_data.main_sub_file_path, real_subs, best_match_auto_sub_line, best_match_real_sub_line)

    # Make final sub file for every non-main-sub as well
    # final_vid_sub_path_l[0] == main_final_vid_sub_path
    final_vid_sub_path_l = _make_non_main_final_vid_subs__and__get_final_vid_sub_path_l(main_final_vid_sub_path, clip_dir_data, ep_sub_data, best_match_auto_sub_line)
    unique_final_vid_sub_path_l = _get_unique_final_vid_sub_path_l__and__rename_duplicates(final_vid_sub_path_l)

    print(f"{final_vid_sub_path_l=}")

    # sub_path_lang_dl = get_sub_path_lang_dl__from__final_vid_sub_path_l(final_vid_sub_path_l, lang)
    sub_path_lang_dl = get_sub_path_lang_dl__from__final_vid_sub_path_l(unique_final_vid_sub_path_l, lang) # TODO remove?
    print(f"{sub_path_lang_dl=}")

    total_time = time.time() - start_time
    return sub_path_lang_dl, unique_final_vid_sub_path_l, total_time



if __name__ == "__main__":
    # # real_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/family.guy.s10.e05.back.to.the.pilot.(2011).eng.1cd.(4413506)/Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt"
    # real_sub_file_path = "C:/p/tik_tb_vid_big_data/ignore/test/sub_match/family.guy.s10.e05.back.to.the.pilot.(2011).eng.1cd.(4413506)/Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt"
    # # auto_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"
    # auto_sub_file_path = "C:/p/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"
    # # out_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"
    # out_sub_path = "C:/p/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"
    # # vid_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.mp4"
    # vid_path = "C:/p/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.mp4"
    # trim_and_re_time_real_sub_file_from_auto_subs(vid_path, real_sub_file_path, auto_sub_file_path, out_sub_path)
    import get_init_mkvs_for_manual_edits
    get_init_mkvs_for_manual_edits.main()
    print("Done")