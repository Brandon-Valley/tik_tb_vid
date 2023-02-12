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
import real_sub_dialog_match_tools



MAX_SUB_DIFF_RATIO = 0.4
MIN_AVG_MOST_CONFIDENT_LINE_DIALOG_FUZZ_RATIO = 60
SERIES_NAME = "Family Guy"

FINAL_MKVS_DIR_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "mkvs")
FINAL_MP4_SRT_DIRS_DIR_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "o_mp4_srt_dirs")
SSM_LOG_JSON_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "SSM_log.json")
SSM_STATS_JSON_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "SSM_stats.json")
FINAL_STATS_JSON_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "final_stats.json")
PL_DATA_DIR_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "YT_PL_DATA")
# SERIES_SUB_EN_DIR_PATH = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s4_16_and_17"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_test_pilot"


def make_no_subs_mkv(clip_dir_data):
    no_subs_mkv_path = join(FINAL_MKVS_DIR_PATH, f"S00E00__UNKNOWN__{clip_dir_data.clip_name}.mkv")
    veu.convert_vid_to_diff_format__no_subs(clip_dir_data.mp4_path, no_subs_mkv_path)

def get_clip_process_time(clip_process_start_time):
    return time.time() - clip_process_start_time

def downloaded_yt_clip_has_no_subs__make_no_sub_mkv__and_get_log_d(clip_dir_data, clip_process_start_time):
    make_no_subs_mkv(clip_dir_data)
    return {
                "clip_name": clip_dir_data.clip_name,
                "clip_mp4_path": clip_dir_data.mp4_path,
                "main_sub_file_path": None,
                "fuzz_ratio": None,
                "fail_reason": "Downloaded youtube clip has no subs",
                "made_vid" : True,
                "ep_sub_data_find_time": None,
                "trim_and_re_time_real_sub_time": None,
                "process_time" : get_clip_process_time(clip_process_start_time)
            }

def no_episode_sub_fuzzy_match_found__make_no_sub_mkv__and_get_log_d(clip_dir_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_eval_key):
    make_no_subs_mkv(clip_dir_data)
    return {
                "clip_name": clip_dir_data.clip_name,
                "clip_mp4_path": clip_dir_data.mp4_path,
                "main_sub_file_path": None,
                "fuzz_ratio": fuzz_ratio,
                "fail_reason": "No ep_sub_data found, no sub match in any episode of series",
                "made_vid" : True,
                "ep_sub_data_find_time": None,
                "trim_and_re_time_real_sub_time": None,
                "ep_sub_data_find_eval_key": ep_sub_data_find_eval_key,
                "process_time" : get_clip_process_time(clip_process_start_time)
            }

def fuzz_ratio_0__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time, ep_sub_data_find_eval_key):
    return {
                "clip_name": clip_dir_data.clip_name,
                "clip_mp4_path": clip_dir_data.mp4_path,
                "main_sub_file_path": ep_sub_data.main_sub_file_path,
                "fuzz_ratio": fuzz_ratio,
                "fail_reason": "fuzz_ratio == 0",
                "made_vid" : False,
                "ep_sub_data_find_time": ep_sub_data_find_time,
                "trim_and_re_time_real_sub_time": None,
                "ep_sub_data_find_eval_key": ep_sub_data_find_eval_key,
                "process_time" : get_clip_process_time(clip_process_start_time)
            }

def normal_successful_clip_w_subs_created__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time, trim_and_re_time_real_sub_time, ep_sub_data_find_eval_key, sub_diff_ratio_sub_path_l_d, passing_sub_diff_ratio_sub_path_l, avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d, line_dialog_fuzz_time, chosen_sub_path):
    # get num_sub_evals_saved_by_sub_diff_ratio
    num_paths_in_sub_diff_ratio_sub_path_l_d = 0
    for sub_diff_ratio, sub_path_l in sub_diff_ratio_sub_path_l_d.items():
        num_paths_in_sub_diff_ratio_sub_path_l_d += len(sub_path_l)
    num_sub_evals_saved_by_sub_diff_ratio = num_paths_in_sub_diff_ratio_sub_path_l_d - len(passing_sub_diff_ratio_sub_path_l)

    return {
                "clip_name": clip_dir_data.clip_name,
                "chosen_sub_path": chosen_sub_path,
                "clip_mp4_path": clip_dir_data.mp4_path,
                "main_sub_file_path": ep_sub_data.main_sub_file_path,
                "fuzz_ratio": fuzz_ratio,
                "fail_reason": None,
                "made_vid" : True,
                "ep_sub_data_find_time": ep_sub_data_find_time,
                "trim_and_re_time_real_sub_time": trim_and_re_time_real_sub_time,
                "ep_sub_data_find_eval_key": ep_sub_data_find_eval_key,
                "process_time" : get_clip_process_time(clip_process_start_time),
                "sub_diff_ratio_sub_path_l_d" : sub_diff_ratio_sub_path_l_d,
                "passing_sub_diff_ratio_sub_path_l": passing_sub_diff_ratio_sub_path_l,
                "num_paths_in_sub_diff_ratio_sub_path_l_d": num_paths_in_sub_diff_ratio_sub_path_l_d,
                "num_sub_evals_saved_by_sub_diff_ratio": num_sub_evals_saved_by_sub_diff_ratio,
                "line_dialog_fuzz_time": line_dialog_fuzz_time,
                "avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d": avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d
            }

def write_final_stats(run_log_l, main_start_time):
    stats_d = {"Total Run Time": str(int(time.time() - main_start_time) / 60) + " minutes",
                "Total Clips Processed": 0,
                "Total Vids Made": 0,
                "Total fuzz_ratio == None": 0,
                }
    fuzz_ratio_d = {}
    fail_reason_d = {}
    process_time_l = []
    trim_and_re_time_real_sub_time_l = []
    ep_sub_data_find_time_l = []

    for run_log_d in run_log_l:
        fuzz_ratio = run_log_d["fuzz_ratio"]
        fail_reason = run_log_d["fail_reason"]
        trim_and_re_time_real_sub_time = run_log_d["trim_and_re_time_real_sub_time"]

        if process_time_l != None:
            process_time_l.append(run_log_d["process_time"])
        if trim_and_re_time_real_sub_time != None:
            trim_and_re_time_real_sub_time_l.append(trim_and_re_time_real_sub_time)
        if run_log_d["ep_sub_data_find_time"] != None:
            ep_sub_data_find_time_l.append(run_log_d["ep_sub_data_find_time"])

        stats_d["Total Clips Processed"] += 1

        if run_log_d["made_vid"]:
            stats_d["Total Vids Made"] += 1

        if fuzz_ratio == None:
            stats_d["Total fuzz_ratio == None"] += 1
        else:
            if fuzz_ratio in fuzz_ratio_d.keys():
                fuzz_ratio_d[fuzz_ratio] += 1
            else:
                fuzz_ratio_d[fuzz_ratio] = 1

        if fail_reason != None:
            if fail_reason in fail_reason_d.keys():
                fail_reason_d[fail_reason] += 1
            else:
                fail_reason_d[fail_reason] = 1
        
    stats_d["fuzz_ratio_d"] = fuzz_ratio_d
    stats_d["fail_reason_d"] = fail_reason_d
    stats_d["process_time_l__AVG"] = statistics.mean(process_time_l)
    stats_d["process_time_l__MAX"] = max(process_time_l)
    if ep_sub_data_find_time_l != None and len(ep_sub_data_find_time_l) > 1:
        stats_d["ep_sub_data_find_time_l__AVG"] = statistics.mean(ep_sub_data_find_time_l)
        stats_d["ep_sub_data_find_time_l__MAX"] = max(ep_sub_data_find_time_l)

    else:
        stats_d["ep_sub_data_find_time_l__AVG"] = None
        stats_d["ep_sub_data_find_time_l__MAX"] = None



    if trim_and_re_time_real_sub_time_l != None and len(trim_and_re_time_real_sub_time_l) > 1:
        stats_d["trim_and_re_time_real_sub_time_l__AVG"] = statistics.mean(trim_and_re_time_real_sub_time_l)
        stats_d["trim_and_re_time_real_sub_time_l__MAX"] = max(trim_and_re_time_real_sub_time_l)
    else:
        stats_d["trim_and_re_time_real_sub_time_l__AVG"] = None
        stats_d["trim_and_re_time_real_sub_time_l__MAX"] = None


    # if len(trim_and_re_time_real_sub_time_l) == 0:
    #     stats_d["trim_and_re_time_real_sub_time_l__AVG"] = None
    #     stats_d["trim_and_re_time_real_sub_time_l__MAX"] = None
    # else:
    #     stats_d["trim_and_re_time_real_sub_time_l__AVG"] = statistics.mean(trim_and_re_time_real_sub_time_l)
    #     stats_d["trim_and_re_time_real_sub_time_l__MAX"] = max(trim_and_re_time_real_sub_time_l)

    json_logger.write(stats_d, FINAL_STATS_JSON_PATH)
