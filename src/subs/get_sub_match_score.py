from os.path import join
from pathlib import Path
import pysubs2

if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

from sms.file_system_utils import file_system_utils as fsu
import vid_edit_utils as veu
import subtitle_utils as su


def _get_num_ms_sub_1_non_matched_dialog(subs_1_path, subs_2_path):
    subs_1 = pysubs2.load(subs_1_path, encoding="latin1")
    subs_2 = pysubs2.load(subs_2_path, encoding="latin1")
    s1_cur_i = 0
    s2_cur_i = 0
    num_ms = 0

    while (s1_cur_i < len(subs_1)):
        s1_line = subs_1[s1_cur_i]

        # if found end of subs_2 but there is still subs_1 left, add s1 duration and move to next until done
        # s1|                   [X] [X] [X] ...
        #   |-----------------------------------
        # s2|   [  ]  [ LAST ]
        if s2_cur_i == len(subs_2):
            num_ms += s1_line.end - s1_line.start
            s1_cur_i += 1
            continue

        s2_line = subs_2[s2_cur_i]

        # s1|               [    ]
        #   |-----------------------------------
        # s2|   [  ]  [  ]
        if s1_line.start >= s2_line.end:
            s2_cur_i += 1
            continue

        # s1|   [XX]  [XX]
        #   |-----------------------------------
        # s2|               [    ]
        if s1_line.end <= s2_line.start:
            num_ms += s1_line.end - s1_line.start
            s1_cur_i += 1
            continue

        # s1|  [X  ]    > |    [ ]
        #   |---------- > |------------------------
        # s2|    [   ]  > |    [   ]
        # if s1_line.start < s2_line.start and s1_line.end > s2_line.start:
        if s1_line.start < s2_line.start:
            if not (s1_line.end > s2_line.start):
                raise Exception("Should not be possible")
            num_ms += s2_line.start - s1_line.start
            subs_1[s1_cur_i].start = s2_line.start
            continue

        # s1|     [   ] > |      [   ]
        #   |---------- > |-----------
        # s2|   [   ]   > |      [ ]  
        # if s1_line.start > s2_line.start and s1_line.start < s2_line.end:
        if s1_line.start > s2_line.start:
            if not (s1_line.start < s2_line.end):
                raise Exception("Should not be possible")
            subs_2[s2_cur_i].start = s1_line.start
            continue

        # s1| [
        #   |--
        # s2| [
        if s1_line.start == s2_line.start:
        # s1| [ ] []      > |     []      
        #   |------------ > |------------ 
        # s2| [ ]    []   > |        []   
            if s1_line.end == s2_line.end:
                s1_cur_i += 1
                s2_cur_i += 1
            # s1| [   ]      > |   [ ]      
            #   |----------- > |----------- 
            # s2| [ ]   []   > |       []   
            elif s1_line.end > s2_line.end:
                subs_1[s1_cur_i].start = s2_line.end
                s2_cur_i += 1
            # s1| [ ]   []   > |       []   
            #   |----------- > |----------- 
            # s2| [   ]      > |   [ ]      
            elif s1_line.end < s2_line.end:
                subs_2[s2_cur_i].start = s1_line.end
                s1_cur_i += 1
            continue

    return num_ms


def _get_num_ms_dialog_of_sub(subs_path):
    subs = pysubs2.load(subs_path, encoding="latin1")
    num_ms = 0
    for line in subs:
        line_num_ms = line.end - line.start
        num_ms += line_num_ms
    return num_ms


def get_sub_match_score(auto_sub_path, real_sub_path):
    num_ms_1 = _get_num_ms_sub_1_non_matched_dialog(auto_sub_path, real_sub_path)
    print(f"{num_ms_1=}")
    num_ms_2 = _get_num_ms_sub_1_non_matched_dialog(real_sub_path, auto_sub_path)
    print(f"{num_ms_2=}")
    total_diff_num_ms = num_ms_1 + num_ms_2
    print(f"{total_diff_num_ms=}")

    total_auto_subs_num_ms = _get_num_ms_dialog_of_sub(auto_sub_path)
    total_real_subs_num_ms__JUST_FOR_TEST = _get_num_ms_dialog_of_sub(real_sub_path) 
    print(f"{total_real_subs_num_ms__JUST_FOR_TEST=}")
    print(f"{total_auto_subs_num_ms=}")

    diff_ratio = total_diff_num_ms / total_auto_subs_num_ms
    print(f"{diff_ratio=}")


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')

    # sub_match_score = get_sub_match_score(auto_sub_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy___TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS.en-orig.srt",
    sub_match_score = get_sub_match_score(auto_sub_path = "C:/tmp/Family_Guy__Back_To_The_Pilot__Clip____TBS.en-orig__MANUAL_EDIT.srt",
     real_sub_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__Back_To_The_Pilot__Clip____TBS/f0_family.guy.s10e05.back.to.the.pilot.dvdrip.x264-demand.srt")
    #  real_sub_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__Back_To_The_Pilot__Clip____TBS/f1_Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt")
    #  real_sub_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__Back_To_The_Pilot__Clip____TBS/f3_Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.HI.srt")

    # print(f"{sub_match_score=}")


    print("End of Main") 
