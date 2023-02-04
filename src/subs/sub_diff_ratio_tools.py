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
    print(f"in _get_num_ms_sub_1_non_matched_dialog()")
    print(f"    {subs_1_path=}")
    print(f"    {subs_2_path=}")
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


def get_sub_diff_ratio(auto_sub_path, real_sub_path):
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
    return diff_ratio


def get_sub_diff_ratio_sub_path_l_d(filtered_auto_sub_path, unique_final_vid_sub_path_l, filtered_real_subs_dir_path):
    Path(filtered_real_subs_dir_path).mkdir(parents=True, exist_ok=True)

    sub_match_score_sub_path_l_d = {}
    
    for unique_final_vid_sub_path in unique_final_vid_sub_path_l:
        print(f"{unique_final_vid_sub_path=}")
        # filtered_unique_final_vid_sub_path = join(filtered_real_subs_dir_path, f"FILTERED__{Path(unique_final_vid_sub_path).name}")
        file_name = f"FILTERED__" + Path(unique_final_vid_sub_path).name.split("_")[0] + ".srt"
        filtered_unique_final_vid_sub_path = join(filtered_real_subs_dir_path, file_name)

        su.write_filtered_subs(unique_final_vid_sub_path, filtered_unique_final_vid_sub_path)

        diff_ratio = get_sub_diff_ratio(filtered_auto_sub_path, filtered_unique_final_vid_sub_path)

        if diff_ratio in sub_match_score_sub_path_l_d.keys():
            sub_match_score_sub_path_l_d[diff_ratio].append(unique_final_vid_sub_path)
        else:
            sub_match_score_sub_path_l_d[diff_ratio] = [unique_final_vid_sub_path]

    return sub_match_score_sub_path_l_d


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')

    import get_init_mkvs_for_manual_edits
    get_init_mkvs_for_manual_edits.main()
    # # sub_match_score = get_sub_match_score(auto_sub_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy___TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS.en-orig.srt",
    # sub_match_score = get_sub_match_score(auto_sub_path = "C:/tmp/Family_Guy__Back_To_The_Pilot__Clip____TBS.en-orig__MANUAL_EDIT.srt",
    #  real_sub_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__Back_To_The_Pilot__Clip____TBS/f0_family.guy.s10e05.back.to.the.pilot.dvdrip.x264-demand.srt")
    # #  real_sub_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__Back_To_The_Pilot__Clip____TBS/f1_Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt")
    # #  real_sub_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__Back_To_The_Pilot__Clip____TBS/f3_Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.HI.srt")

    # # print(f"{sub_match_score=}")


    print("End of Main") 
