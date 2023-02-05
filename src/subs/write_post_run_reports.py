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

# SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__))
POST_RUN_REPORT_JSON_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "post_run_report.json")
RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "run_log_l__sorted_by__best_sub_diff_ratio.json")
RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS__W_SORTED__SUB_DIFF_RATIO_SUB_PATH_L_D_JSON_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "run_log_l__sorted_by__best_sub_diff_ratio__w_sorted__sub_diff_ratio_sub_path_l_d.json")

def write_run_log_l__sorted_by__best_sub_diff_ratio():
    def _get_best_sub_dir_ratio(clip_data_d):
        # print(f"clip_data_d")
        # pprint(clip_data_d)
        # print(f"{len(clip_data_d)=}")

        best_sub_diff_ratio = 9999

        if "sub_diff_ratio_sub_path_l_d" in clip_data_d.keys():
            sub_diff_ratio_sub_path_l_d = clip_data_d["sub_diff_ratio_sub_path_l_d"]
            best_sub_diff_ratio = 999
            
            if len(sub_diff_ratio_sub_path_l_d) != 0:
                best_sub_diff_ratio_str = min(sub_diff_ratio_sub_path_l_d.keys())
                best_sub_path_l = sub_diff_ratio_sub_path_l_d[best_sub_diff_ratio_str]
                best_sub_diff_ratio = float(best_sub_diff_ratio_str)
        return best_sub_diff_ratio

    run_log_l = json_logger.read(cfg.RUN_LOG_JSON_PATH)

    sorted_run_log_l = sorted(run_log_l, key=lambda clip_data_d: _get_best_sub_dir_ratio(clip_data_d))
    print(f"Writing {RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH}...")
    json_logger.write(sorted_run_log_l, RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH)

def write_run_log_l__sorted_by__best_sub_diff_ratio__w_sorted__sub_diff_ratio_sub_path_l_d():
    # def _get_best_sub_dir_ratio(clip_data_d):
    #     # print(f"clip_data_d")
    #     # pprint(clip_data_d)
    #     # print(f"{len(clip_data_d)=}")

    #     best_sub_diff_ratio = 9999

    #     if "sub_diff_ratio_sub_path_l_d" in clip_data_d.keys():
    #         sub_diff_ratio_sub_path_l_d = clip_data_d["sub_diff_ratio_sub_path_l_d"]
    #         best_sub_diff_ratio = 999
            
    #         if len(sub_diff_ratio_sub_path_l_d) != 0:
    #             best_sub_diff_ratio_str = min(sub_diff_ratio_sub_path_l_d.keys())
    #             best_sub_path_l = sub_diff_ratio_sub_path_l_d[best_sub_diff_ratio_str]
    #             best_sub_diff_ratio = float(best_sub_diff_ratio_str)
    #     return best_sub_diff_ratio

    sorted_run_log_l = json_logger.read(RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH)
    new_log_l = []

    for clip_data_d in sorted_run_log_l:
        if "sub_diff_ratio_sub_path_l_d" in clip_data_d.keys():
            # clip_data_d["sub_diff_ratio_sub_path_l_d"] = sorted(clip_data_d["sub_diff_ratio_sub_path_l_d"])
            clip_data_d["sub_diff_ratio_sub_path_l_d"] = collections.OrderedDict(sorted(clip_data_d["sub_diff_ratio_sub_path_l_d"].items()))
        new_log_l.append(clip_data_d)

    # sorted_run_log_l = sorted(run_log_l, key=lambda clip_data_d: _get_best_sub_dir_ratio(clip_data_d))
    print(f"Writing {RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS__W_SORTED__SUB_DIFF_RATIO_SUB_PATH_L_D_JSON_PATH}...")
    json_logger.write(sorted_run_log_l, RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS__W_SORTED__SUB_DIFF_RATIO_SUB_PATH_L_D_JSON_PATH)


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    write_run_log_l__sorted_by__best_sub_diff_ratio()
    write_run_log_l__sorted_by__best_sub_diff_ratio__w_sorted__sub_diff_ratio_sub_path_l_d()
    print("End of Main") 
