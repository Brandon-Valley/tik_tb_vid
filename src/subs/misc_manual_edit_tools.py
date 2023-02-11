import collections
import statistics
import time
import os
from os.path import join
from pathlib import Path
from pprint import pprint


if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

from YT_PL_DL_Data import YT_PL_DL_Data
from get_real_episode_sub_data_from_auto_sub import get_real_episode_sub_data_from_auto_sub
from trim_and_re_time_real_sub_file_from_auto_subs import trim_and_re_time_real_sub_file_from_auto_subs
from Series_Sub_Map import Series_Sub_map

from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
import vid_edit_utils as veu
import subtitle_utils
import cfg
import sub_diff_ratio_tools

# # SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__))
# POST_RUN_REPORTS_DIR_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "post_run_reports")
# POST_RUN_REPORT_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "post_run_report.json")
# WRONG_ANSWERS_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "wrong_answers.json")
# CLIP_NAME_CHOSEN_SUB_PATH_OD__LAST_RUN__JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "clip_name_chosen_sub_path_od__last_run.json")
# CLIP_NAME_CHOSEN_SUB_PATH_OD__CORRECT_ANSWERS__JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "clip_name_chosen_sub_path_od__correct_answers.json")
# RUN_LOG_L__SORTED_BY__BEST_AVG_LINE_DIALOG_FUZZ_RATIO_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "run_log_l__sorted_by__best_avg_line_dialog_fuzz_ratio.json")
# RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "run_log_l__sorted_by__best_sub_diff_ratio.json")
# RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS__W_SORTED__SUB_DIFF_RATIO_SUB_PATH_L_D_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "run_log_l__sorted_by__best_sub_diff_ratio__w_sorted__sub_diff_ratio_sub_path_l_d.json")



def make_all_nested_mp4_files_match_name_of_parent_dir(in_dir_path):
    file_path_l = fsu.get_dir_content_l(in_dir_path, "file", recurs_dirs=True)

    mp4_path_l = []
    for file_path in file_path_l:
        if Path(file_path).suffix == ".mp4":
            mp4_path_l.append(file_path)

    # print(f"{mp4_path_l=}")

    for mp4_path in mp4_path_l:
        parent_dir_name = Path(mp4_path).parent.name
        new_mp4_path = join(str(Path(mp4_path).parent), f"{parent_dir_name}.mp4")

        if os.path.abspath(new_mp4_path) != os.path.abspath(mp4_path):
            print(f"Renaming {mp4_path=} to {new_mp4_path=}...")
            fsu.rename_file_overwrite(mp4_path, new_mp4_path)
        

if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    make_all_nested_mp4_files_match_name_of_parent_dir("C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy___TBS")
    print("End of Main") 
