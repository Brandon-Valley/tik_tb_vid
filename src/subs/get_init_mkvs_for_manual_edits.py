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
from main_run_logging import    get_clip_process_time, \
                                downloaded_yt_clip_has_no_subs__make_no_sub_mkv__and_get_log_d, \
                                no_episode_sub_fuzzy_match_found__make_no_sub_mkv__and_get_log_d, \
                                fuzz_ratio_0__get_log_d, \
                                normal_successful_clip_w_subs_created__get_log_d, \
                                write_final_stats
from Series_Sub_Map import Series_Sub_map

from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
import vid_edit_utils as veu
import subtitle_utils
import cfg
import sub_diff_ratio_tools
import real_sub_dialog_match_tools

MAX_SUB_DIFF_RATIO = 0.4
MIN_AVG_MOST_CONFIDENT_LINE_DIALOG_FUZZ_RATIO = 70
SERIES_NAME = "Family Guy"

FINAL_MKVS_DIR_PATH = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "mkvs")
FINAL_MP4_SRT_DIRS_DIR_PATH = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "o_mp4_srt_dirs")
SSM_LOG_JSON_PATH = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "SSM_log.json")
SSM_STATS_JSON_PATH = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "SSM_stats.json")
FINAL_STATS_JSON_PATH = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "final_stats.json")
PL_DATA_DIR_PATH = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "YT_PL_DATA")
# SERIES_SUB_EN_DIR_PATH = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s4_16_and_17"
SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_92"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_test_pilot"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_iPhone"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_steel_v_test"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_comic_book_test"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en__s1e5__how_joe_became"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s1_e1and2_1_and_none"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s1_e1and2"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s06E1_and_2_blue_harvest_test__and_pilot__and_max_min"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s06E1_and_2_blue_harvest_test__and_pilot"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_blue_harvest_test__s6e1_and_s1e1"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s06E1_and_2_blue_harvest_test"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_S10E20andS1E4__and__s15e14_and_s10_e5"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s5_e17"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_S10E20andS1E4"
LANG = "en"

# def make_no_subs_mkv(clip_dir_data):
#     no_subs_mkv_path = os.path.join(FINAL_MKVS_DIR_PATH, f"S00E00__UNKNOWN__{clip_dir_data.clip_name}.mkv")
#     veu.convert_vid_to_diff_format__no_subs(clip_dir_data.mp4_path, no_subs_mkv_path)

# def get_clip_process_time(clip_process_start_time):
#     return time.time() - clip_process_start_time

# def downloaded_yt_clip_has_no_subs__make_no_sub_mkv__and_get_log_d(clip_dir_data, clip_process_start_time):
#     make_no_subs_mkv(clip_dir_data)
#     return {
#                 "clip_name": clip_dir_data.clip_name,
#                 "clip_mp4_path": clip_dir_data.mp4_path,
#                 "main_sub_file_path": None,
#                 "fuzz_ratio": None,
#                 "fail_reason": "Downloaded youtube clip has no subs",
#                 "made_vid" : True,
#                 "ep_sub_data_find_time": None,
#                 "trim_and_re_time_real_sub_time": None,
#                 "process_time" : get_clip_process_time(clip_process_start_time)
#             }

# def no_episode_sub_fuzzy_match_found__make_no_sub_mkv__and_get_log_d(clip_dir_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_eval_key):
#     make_no_subs_mkv(clip_dir_data)
#     return {
#                 "clip_name": clip_dir_data.clip_name,
#                 "clip_mp4_path": clip_dir_data.mp4_path,
#                 "main_sub_file_path": None,
#                 "fuzz_ratio": fuzz_ratio,
#                 "fail_reason": "No ep_sub_data found, no sub match in any episode of series",
#                 "made_vid" : True,
#                 "ep_sub_data_find_time": None,
#                 "trim_and_re_time_real_sub_time": None,
#                 "ep_sub_data_find_eval_key": ep_sub_data_find_eval_key,
#                 "process_time" : get_clip_process_time(clip_process_start_time)
#             }

# def fuzz_ratio_0__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time, ep_sub_data_find_eval_key):
#     return {
#                 "clip_name": clip_dir_data.clip_name,
#                 "clip_mp4_path": clip_dir_data.mp4_path,
#                 "main_sub_file_path": ep_sub_data.main_sub_file_path,
#                 "fuzz_ratio": fuzz_ratio,
#                 "fail_reason": "fuzz_ratio == 0",
#                 "made_vid" : False,
#                 "ep_sub_data_find_time": ep_sub_data_find_time,
#                 "trim_and_re_time_real_sub_time": None,
#                 "ep_sub_data_find_eval_key": ep_sub_data_find_eval_key,
#                 "process_time" : get_clip_process_time(clip_process_start_time)
#             }

# def normal_successful_clip_w_subs_created__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time, trim_and_re_time_real_sub_time, ep_sub_data_find_eval_key, sub_diff_ratio_sub_path_l_d, passing_sub_diff_ratio_sub_path_l):
#     num_paths_in_sub_diff_ratio_sub_path_l_d = 0
#     for sub_diff_ratio, sub_path_l in sub_diff_ratio_sub_path_l_d.items():
#         num_paths_in_sub_diff_ratio_sub_path_l_d += len(sub_path_l)

#     num_sub_evals_saved_by_sub_diff_ratio = num_paths_in_sub_diff_ratio_sub_path_l_d - len(passing_sub_diff_ratio_sub_path_l)
#     return {
#                 "clip_name": clip_dir_data.clip_name,
#                 "clip_mp4_path": clip_dir_data.mp4_path,
#                 "main_sub_file_path": ep_sub_data.main_sub_file_path,
#                 "fuzz_ratio": fuzz_ratio,
#                 "fail_reason": None,
#                 "made_vid" : True,
#                 "ep_sub_data_find_time": ep_sub_data_find_time,
#                 "trim_and_re_time_real_sub_time": trim_and_re_time_real_sub_time,
#                 "ep_sub_data_find_eval_key": ep_sub_data_find_eval_key,
#                 "process_time" : get_clip_process_time(clip_process_start_time),
#                 "sub_diff_ratio_sub_path_l_d" : sub_diff_ratio_sub_path_l_d,
#                 "passing_sub_diff_ratio_sub_path_l": passing_sub_diff_ratio_sub_path_l,
#                 "num_paths_in_sub_diff_ratio_sub_path_l_d": num_paths_in_sub_diff_ratio_sub_path_l_d,
#                 "num_sub_evals_saved_by_sub_diff_ratio": num_sub_evals_saved_by_sub_diff_ratio
#             }

# def write_final_stats(run_log_l, main_start_time):
#     stats_d = {"Total Run Time": str(int(time.time() - main_start_time) / 60) + " minutes",
#                 "Total Clips Processed": 0,
#                 "Total Vids Made": 0,
#                 "Total fuzz_ratio == None": 0,
#                 }
#     fuzz_ratio_d = {}
#     fail_reason_d = {}
#     process_time_l = []
#     trim_and_re_time_real_sub_time_l = []
#     ep_sub_data_find_time_l = []

#     for run_log_d in run_log_l:
#         fuzz_ratio = run_log_d["fuzz_ratio"]
#         fail_reason = run_log_d["fail_reason"]
#         trim_and_re_time_real_sub_time = run_log_d["trim_and_re_time_real_sub_time"]

#         if process_time_l != None:
#             process_time_l.append(run_log_d["process_time"])
#         if trim_and_re_time_real_sub_time != None:
#             trim_and_re_time_real_sub_time_l.append(trim_and_re_time_real_sub_time)
#         if run_log_d["ep_sub_data_find_time"] != None:
#             ep_sub_data_find_time_l.append(run_log_d["ep_sub_data_find_time"])

#         stats_d["Total Clips Processed"] += 1

#         if run_log_d["made_vid"]:
#             stats_d["Total Vids Made"] += 1

#         if fuzz_ratio == None:
#             stats_d["Total fuzz_ratio == None"] += 1
#         else:
#             if fuzz_ratio in fuzz_ratio_d.keys():
#                 fuzz_ratio_d[fuzz_ratio] += 1
#             else:
#                 fuzz_ratio_d[fuzz_ratio] = 1

#         if fail_reason != None:
#             if fail_reason in fail_reason_d.keys():
#                 fail_reason_d[fail_reason] += 1
#             else:
#                 fail_reason_d[fail_reason] = 1
        
#     stats_d["fuzz_ratio_d"] = fuzz_ratio_d
#     stats_d["fail_reason_d"] = fail_reason_d
#     stats_d["process_time_l__AVG"] = statistics.mean(process_time_l)
#     stats_d["process_time_l__MAX"] = max(process_time_l)
#     if ep_sub_data_find_time_l != None and len(ep_sub_data_find_time_l) > 1:
#         stats_d["ep_sub_data_find_time_l__AVG"] = statistics.mean(ep_sub_data_find_time_l)
#         stats_d["ep_sub_data_find_time_l__MAX"] = max(ep_sub_data_find_time_l)

#     else:
#         stats_d["ep_sub_data_find_time_l__AVG"] = None
#         stats_d["ep_sub_data_find_time_l__MAX"] = None



#     if trim_and_re_time_real_sub_time_l != None and len(trim_and_re_time_real_sub_time_l) > 1:
#         stats_d["trim_and_re_time_real_sub_time_l__AVG"] = statistics.mean(trim_and_re_time_real_sub_time_l)
#         stats_d["trim_and_re_time_real_sub_time_l__MAX"] = max(trim_and_re_time_real_sub_time_l)
#     else:
#         stats_d["trim_and_re_time_real_sub_time_l__AVG"] = None
#         stats_d["trim_and_re_time_real_sub_time_l__MAX"] = None


#     # if len(trim_and_re_time_real_sub_time_l) == 0:
#     #     stats_d["trim_and_re_time_real_sub_time_l__AVG"] = None
#     #     stats_d["trim_and_re_time_real_sub_time_l__MAX"] = None
#     # else:
#     #     stats_d["trim_and_re_time_real_sub_time_l__AVG"] = statistics.mean(trim_and_re_time_real_sub_time_l)
#     #     stats_d["trim_and_re_time_real_sub_time_l__MAX"] = max(trim_and_re_time_real_sub_time_l)

#     json_logger.write(stats_d, FINAL_STATS_JSON_PATH)


# TODO remove?
def _copy_mp4_and_first_srt_to_dir(in_mp4_path, sub_path_lang_dl):
    dir_path = os.path.join(FINAL_MP4_SRT_DIRS_DIR_PATH, Path(in_mp4_path).stem)
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    if sub_path_lang_dl != None and len(sub_path_lang_dl) > 0:
        sub_path = sub_path_lang_dl[0]["path"]
        fsu.copy_objects_to_dest(sub_path, dir_path)

    fsu.copy_objects_to_dest(in_mp4_path, dir_path)


def _get_passing_sub_diff_ratio_sub_path_l(sub_diff_ratio_sub_path_l_d):
    passing_sub_diff_ratio_sub_path_l = []
    for sub_diff_ratio, sub_path_l in sub_diff_ratio_sub_path_l_d.items():
        if sub_diff_ratio <= MAX_SUB_DIFF_RATIO:
            passing_sub_diff_ratio_sub_path_l += sub_path_l
    return passing_sub_diff_ratio_sub_path_l

def _copy_mp4_and_best_sub_if_good_enough_to_dir__line_dialog_fuzz_ratio__method(in_mp4_path, avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d):
    dir_path = os.path.join(FINAL_MP4_SRT_DIRS_DIR_PATH, "no_subs")
    chosen_sub_path = None

    if len(avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d.keys()) != 0:
        best_fuzz_ratio = max(avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d.keys())
        print(f"{best_fuzz_ratio=}")

        sub_path_l = avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d[best_fuzz_ratio]
        sub_path = sub_path_l[0]

        if best_fuzz_ratio >= MIN_AVG_MOST_CONFIDENT_LINE_DIALOG_FUZZ_RATIO:
            dir_path = os.path.join(FINAL_MP4_SRT_DIRS_DIR_PATH, "w_subs", Path(in_mp4_path).stem)
            Path(dir_path).mkdir(parents=True, exist_ok=True)

            # Rename srt to be same name as mp4 so VLC Media Player will play subs automatically
            new_srt_file_name = f"{Path(in_mp4_path).stem}.srt"
            new_srt_path = join(dir_path, new_srt_file_name)
            fsu.copy_object_to_path(sub_path, new_srt_path)
            chosen_sub_path = sub_path
    
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    fsu.copy_objects_to_dest(in_mp4_path, dir_path)
    return chosen_sub_path


def _copy_mp4_and_best_sub_if_good_enough_to_dir__sub_diff_ratio_sub_path_l_d__method(in_mp4_path, sub_diff_ratio_sub_path_l_d):
    dir_path = os.path.join(FINAL_MP4_SRT_DIRS_DIR_PATH, "no_subs")

    if len(sub_diff_ratio_sub_path_l_d.keys()) != 0:

        best_sub_diff_ratio = min(sub_diff_ratio_sub_path_l_d.keys())
        print(f"{best_sub_diff_ratio=}")

        sub_path_l = sub_diff_ratio_sub_path_l_d[best_sub_diff_ratio]
        # print(f"{sub_path_l=}")
        # print(f"{len(sub_path_l)=}")
        sub_path = sub_path_l[0]

        if best_sub_diff_ratio <= MAX_SUB_DIFF_RATIO:
            dir_path = os.path.join(FINAL_MP4_SRT_DIRS_DIR_PATH, "w_subs", Path(in_mp4_path).stem)
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            # fsu.copy_objects_to_dest(sub_path, dir_path)

            # Rename srt to be same name as mp4 so VLC Media Player will play subs automatically
            new_srt_file_name = f"{Path(in_mp4_path).stem}.srt"
            new_srt_path = join(dir_path, new_srt_file_name)
            fsu.copy_object_to_path(sub_path, new_srt_path)
        # else:
        #     dir_path = os.path.join(FINAL_MP4_SRT_DIRS_DIR_PATH, "no_subs")
        #     Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    fsu.copy_objects_to_dest(in_mp4_path, dir_path)


def main():
    main_start_time = time.time()
    fsu.delete_if_exists(FINAL_MKVS_DIR_PATH)
    Path(FINAL_MKVS_DIR_PATH).mkdir(parents=True, exist_ok=True)
    fsu.delete_if_exists(FINAL_MP4_SRT_DIRS_DIR_PATH)
    Path(FINAL_MP4_SRT_DIRS_DIR_PATH).mkdir(parents=True,exist_ok=True)

    # # Clean freshly downloaded subtitles
    # #   - Removes things like un-labeled spanish subs in english sub list (EX: Herbert Clip)
    # tmp_ssm_for_cleaning = Series_Sub_map()
    # tmp_ssm_for_cleaning.load_lang(SERIES_SUB_EN_DIR_PATH, LANG)
    # tmp_ssm_for_cleaning.clean_subs_after_fresh_download(LANG)
    # exit()


    # TODO download yt playlist with youtube_utils.dl_yt_playlist__fix_sub_times_convert_to__mp4_srt()
    # Init std youtube playlist download data
    yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy___TBS")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__pilot")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__steel_v_test")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__iPhane_test")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy___TBS__comic_book_test")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__How_joe_became")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__star_trek")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__alcho_and_pilot")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__alcho")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__pilot_and_tea_party")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__blue_harvest_and_pilot_test")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__blue_harvest_and_pilot_and_herbert_test")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__pilot_and_herbert_test")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy__TBS__blue_harvest_test")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy___TBS__google_earth_test__and__pilot")
    # yt_pl_dl_dir_path = os.path.join(cfg.INIT_MKVS_WORKING_DIR_PATH, "Family_Guy___TBS__google_earth_test")
    yt_pl_dl_dir_data = YT_PL_DL_Data(yt_pl_dl_dir_path, PL_DATA_DIR_PATH)
    print(f"{yt_pl_dl_dir_data.max_fuzz_str_len=}")
 
    # Init std subtitles for whole series data
    ssm = Series_Sub_map()
    ssm.load_lang(SERIES_SUB_EN_DIR_PATH, LANG, SERIES_NAME, yt_pl_dl_dir_data.max_fuzz_str_len)
    ssm.write_log_json(SSM_LOG_JSON_PATH)
    ssm.write_stats_json(SSM_STATS_JSON_PATH)
    
    if ssm.get_num_episodes_in_lang == 0:
        raise Exception(f"ERROR: ssm.get_num_episodes_in_lang == 0, this means something is wrong with loading ssm from {SERIES_SUB_EN_DIR_PATH=} in {LANG=}")
    print(f"{ssm.get_num_episodes_in_lang=}") 


    run_log_l = []

    for clip_dir_data in yt_pl_dl_dir_data.clip_dir_data_l:
        clip_process_start_time = time.time()

        print(f"{clip_dir_data.clip_name=}")

        if not clip_dir_data.has_subs():
            print(f"Downloaded youtube clip has no subs, creating .mkv without subtitles...")
            log_d = downloaded_yt_clip_has_no_subs__make_no_sub_mkv__and_get_log_d(clip_dir_data, clip_process_start_time)
            run_log_l.append(log_d)
            json_logger.write(run_log_l, cfg.RUN_LOG_JSON_PATH)
            continue

        # Get sub data of episode that clip comes from (found by fuzzy searching w/ auto-subs)
        print("Fuzzy-Searching for real episode subs using auto-subs...")
        # min_real_sub_total_fuzz_str_len = ssm.get_min_fuzz_str_len_for_lang(LANG)
        # ep_sub_data, fuzz_ratio, ep_sub_data_find_time = get_real_episode_sub_data_from_auto_sub(clip_dir_data.auto_sub_path, ssm, LANG, min_real_sub_total_fuzz_str_len)
        # ep_sub_data, fuzz_ratio, ep_sub_data_find_time = get_real_episode_sub_data_from_auto_sub(clip_dir_data.auto_sub_path, ssm, LANG)
        # fuzz_ratio, ep_sub_data, ep_sub_partial_fuzz_str, ep_sub_data_find_time 
        # out_tup = get_real_episode_sub_data_from_auto_sub(clip_dir_data.auto_sub_path, ssm, LANG)
        fuzz_ratio, ep_sub_data, ep_sub_data_find_eval_key, ep_sub_data_find_time = get_real_episode_sub_data_from_auto_sub(clip_dir_data, ssm, LANG)
        print(f"{clip_dir_data.auto_sub_path=}")
        print(f"{fuzz_ratio             =}")
        print(f"{ep_sub_data            =}")
        print(f"{ep_sub_data_find_eval_key=}") # TODO log this
        print(f"{ep_sub_data_find_time  =}")
        # exit()

        if ep_sub_data == None:
            print("init_mkvs - After fuzzy-searching every episode's subs, did not find single episode with fuzz_ratio > 0, creating .mkv without subtitles...")
            log_d = no_episode_sub_fuzzy_match_found__make_no_sub_mkv__and_get_log_d(clip_dir_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_eval_key)
            run_log_l.append(log_d)
            json_logger.write(run_log_l, cfg.RUN_LOG_JSON_PATH)
            continue

        print(f"Found real sub match for auto_sub: {ep_sub_data.main_sub_file_path=} is the real sub match to {clip_dir_data.auto_sub_path} w/ {fuzz_ratio=}")
        # exit()

        # if have non-series clips mixed in with playlist/just have very low fuzz_ratio for some reason, add to fail list and move on
        if fuzz_ratio == 0:
            log_d = fuzz_ratio_0__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time, ep_sub_data_find_eval_key)
            run_log_l.append(log_d)
            json_logger.write(run_log_l, cfg.RUN_LOG_JSON_PATH)
            continue

        new_srt_mkv_file_path_no_ext = os.path.join(FINAL_MKVS_DIR_PATH, f"{ep_sub_data.get_season_episode_str()}__{clip_dir_data.clip_name}")
        tmp_srt_path = new_srt_mkv_file_path_no_ext + f"{LANG}.srt"
        new_mkv_path = new_srt_mkv_file_path_no_ext + f".mkv"

        sub_path_lang_dl, unique_final_vid_sub_path_l, trim_and_re_time_real_sub_time = trim_and_re_time_real_sub_file_from_auto_subs(clip_dir_data, ep_sub_data, LANG)

        print(f"{unique_final_vid_sub_path_l=}") # TMP
        print(f"{trim_and_re_time_real_sub_time=}")

        # TMP move
        filtered_auto_sub_path = join(clip_dir_data.data_dir_path, "filtered_auto_subs.srt")
        Path(filtered_auto_sub_path).parent.mkdir(parents=True, exist_ok=True)
        subtitle_utils.write_filtered_subs(clip_dir_data.auto_sub_path, filtered_auto_sub_path)
    
        sub_diff_ratio_sub_path_l_d = sub_diff_ratio_tools.get_sub_diff_ratio_sub_path_l_d(filtered_auto_sub_path,
                                                                                           unique_final_vid_sub_path_l,
                                                                                           ep_sub_data.filtered_real_subs_dir_path)
        print(f"{sub_diff_ratio_sub_path_l_d=}")

        passing_sub_diff_ratio_sub_path_l = _get_passing_sub_diff_ratio_sub_path_l(sub_diff_ratio_sub_path_l_d)

        avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d, line_dialog_fuzz_time = real_sub_dialog_match_tools.get_avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d(
                                                                                               clip_dir_data.mp4_path,
                                                                                               passing_sub_diff_ratio_sub_path_l,
                                                                                               ep_sub_data.filtered_real_subs_dir_path)

        # subtitle_utils.combine__mp4__and__sub_path_lang_dl__into_mkv(in_mp4_path           = clip_dir_data.mp4_path,
        #                                                              sub_path_lang_dl      = sub_path_lang_dl,
        #                                                              out_mkv_path          = new_mkv_path,
        #                                                              default_sub_track_num = 0)
        # # subtitle_utils.make_embedded_mkv_sub_track_show_by_default(new_mkv_path)
        # # fsu.delete_if_exists(tmp_srt_path)

        # _copy_mp4_and_first_srt_to_dir(clip_dir_data.mp4_path, sub_path_lang_dl)
        # _copy_mp4_and_best_sub_if_good_enough_to_dir__sub_diff_ratio_sub_path_l_d__method(clip_dir_data.mp4_path, sub_diff_ratio_sub_path_l_d)
        chosen_sub_path = _copy_mp4_and_best_sub_if_good_enough_to_dir__line_dialog_fuzz_ratio__method(clip_dir_data.mp4_path, avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d)



        # print("before normal_successful_clip_w_subs_created__get_log_d()")
        log_d = normal_successful_clip_w_subs_created__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time, trim_and_re_time_real_sub_time, ep_sub_data_find_eval_key, sub_diff_ratio_sub_path_l_d, passing_sub_diff_ratio_sub_path_l, avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d, line_dialog_fuzz_time, chosen_sub_path)
        run_log_l.append(log_d)
        json_logger.write(run_log_l, cfg.RUN_LOG_JSON_PATH)


        print("run_log_l vv")
        pprint(run_log_l)


    print("final run_log_lvv")
    pprint(run_log_l)

    json_logger.write(run_log_l, cfg.RUN_LOG_JSON_PATH)
    write_final_stats(run_log_l, main_start_time)
    print("Done")


if __name__ == "__main__":
    import os.path as path
    print(f"Running " , path.abspath(__file__) , '...')
    main()
    # fpl = fsu.get_dir_content_l("C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en/s09","file", recurs_dirs=True)
    # for file_path in fpl:
    #     if file_path.__contains__("S10"):
    #         print(file_path)
    #         fsu.delete_if_exists(file_path)
    print("End of Main") 