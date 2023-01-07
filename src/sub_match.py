import os
import pysubs2
from sms.file_system_utils import file_system_utils as fsu
import subtitle_utils
from pathlib import Path
# from fuzzysearch import find_near_matches

from fuzzywuzzy import fuzz

import time


FUZZ_STR_DELIM = ' '

# def _subs_to_subs_fuzz_str(in_subs):
#     subs_fuzz_str = ""
#     for line in in_subs:
#         subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM
#     return subs_fuzz_str

# def _get_fuzzy_search_match_from_fuzz_strs(real_subs_fuzz_str, auto_subs_fuzz_str):
#     # search for 'PATTERN' with a maximum Levenshtein Distance of 1
#     # match = find_near_matches('PATTERN', '---PATERN---', max_l_dist=1)
#     match = find_near_matches(auto_subs_fuzz_str, real_subs_fuzz_str, max_l_dist=1)
#     print(f"{match=}")
#     # [Match(start=3, end=9, dist=1, matched="PATERN")]
#     return match

def _get_and_check_real_and_auto_subs(real_sub_file_path, auto_sub_file_path):
    real_subs = pysubs2.load(real_sub_file_path, encoding="utf-8")
    auto_subs = pysubs2.load(auto_sub_file_path, encoding="utf-8")

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
    best_auto_sub_line_match_index = False
    best_auto_sub_line_match_score = 0

    for auto_sub_line_num, auto_sub_line in enumerate(auto_subs):
        real_sub_line = real_subs[auto_sub_line_num + sub_slot_offset]

        auto_sub_line_match_score = fuzz.ratio(auto_sub_line.text, real_sub_line.text)
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
        # print(f"......{sub_slot_score=}")
        # print(f"......{best_auto_sub_line_match_index=}")

        if best_auto_sub_line_match_index == False:
            raise Exception(f"ERROR: {best_auto_sub_line_match_index=}, this means maybe some subs are empty or something else happened?")
        
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


def _get_real_sub_shift_num_ms(real_subs, auto_subs, best_sub_slot_offset, best_auto_sub_line_match_index_for_best_sub_slot_offset):
    print("in _get_real_sub_shift_num_ms()")
    best_match_auto_sub_line = auto_subs[best_auto_sub_line_match_index_for_best_sub_slot_offset]
    best_match_real_sub_line = real_subs[best_sub_slot_offset + best_auto_sub_line_match_index_for_best_sub_slot_offset]
    print(f"--{best_match_auto_sub_line.text=}")
    print(f"--{best_match_real_sub_line.text=}")
    print(f"--{best_match_auto_sub_line.start=}")
    print(f"--{best_match_real_sub_line.start=}")

    if best_match_auto_sub_line.start > best_match_real_sub_line.start:
        raise Exception(f"ERROR: {best_match_auto_sub_line.start=} > {best_match_real_sub_line.start=} - This should never be possible.")

    real_sub_shift_num_ms = best_match_real_sub_line.start - best_match_auto_sub_line.start

    return real_sub_shift_num_ms

def trim_and_re_time_real_sub_file_from_auto_subs(vid_path, real_sub_file_path, auto_sub_file_path, out_sub_path):

    fsu.delete_if_exists(out_sub_path)
    Path(out_sub_path).parent.mkdir(parents=True, exist_ok=True)

    real_subs, auto_subs = _get_and_check_real_and_auto_subs(real_sub_file_path, auto_sub_file_path)

    s_time = time.time()
    best_sub_slot_offset, best_auto_sub_line_match_index_for_best_sub_slot_offset = _get_best_sub_slot_offset_and_best_line_match_index(real_subs, auto_subs)
    exe_time = time.time() - s_time
    print(f"_get_best_sub_slot_offset_and_best_line_match_index() took {exe_time} seconds.")
    print("after _get_best_sub_slot_offset_and_best_line_match_index()")
    print(f"  {best_sub_slot_offset=}")
    print(f"  {best_auto_sub_line_match_index_for_best_sub_slot_offset=}")

    real_sub_shift_num_ms = _get_real_sub_shift_num_ms(real_subs, auto_subs, best_sub_slot_offset, best_auto_sub_line_match_index_for_best_sub_slot_offset)
    print(f"{real_sub_shift_num_ms=}")
    neg_real_sub_shift_num_ms = real_sub_shift_num_ms * -1

    # init shift
    real_subs.shift(ms = neg_real_sub_shift_num_ms)
    tmp_ms_shifted_sub_path = os.path.join(Path(out_sub_path).parent.__str__(), Path(out_sub_path).stem + "__TMP_MS_SHIFTED" + ''.join(Path(out_sub_path).suffixes))
    print(f"{tmp_ms_shifted_sub_path=}")
    real_subs.save(tmp_ms_shifted_sub_path)
    
    # This will throw warning, this is normal:  WARNING: low quality of fit. Wrong subtitle file?
    # This happens b/c did not trim out the first part of re-timed srt which is all set to 0 (like the theme) and did not trim end
    subtitle_utils.sync_subs_with_vid(vid_path = vid_path,
     in_sub_path = tmp_ms_shifted_sub_path,
      out_sub_path = out_sub_path)

    # rest of real subs still in final .srt but that seems not to matter
    # clean up
    fsu.delete_if_exists(tmp_ms_shifted_sub_path)

if __name__ == "__main__":
    real_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/family.guy.s10.e05.back.to.the.pilot.(2011).eng.1cd.(4413506)/Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt"
    auto_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"
    out_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"
    vid_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.mp4"
    trim_and_re_time_real_sub_file_from_auto_subs(vid_path, real_sub_file_path, auto_sub_file_path, out_sub_path)

    print("Done")