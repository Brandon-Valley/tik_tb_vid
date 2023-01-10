
import time
import os
from pathlib import Path
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
from YT_PL_DL_Data import YT_PL_DL_Data
from get_real_episode_sub_data_from_auto_sub import get_real_episode_sub_data_from_auto_sub
from trim_and_re_time_real_sub_file_from_auto_subs import trim_and_re_time_real_sub_file_from_auto_subs
from Series_Sub_Map import Series_Sub_map
import subtitle_utils
from pprint import pprint
import vid_edit_utils as veu

WORKING_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS"
FINAL_MKVS_DIR_PATH = os.path.join(WORKING_DIR_PATH, "mkvs")
RUN_LOG_JSON_PATH = os.path.join(WORKING_DIR_PATH, "run_log_l.json")
# SERIES_SUB_EN_DIR_PATH = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
# SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s4_16_and_17"
SERIES_SUB_EN_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
LANG = "en"

def make_no_subs_mkv(clip_dir_data):
    no_subs_mkv_path = os.path.join(FINAL_MKVS_DIR_PATH, f"S00E00__UNKNOWN__{clip_dir_data.clip_name}.mkv")
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

def no_episode_sub_fuzzy_match_found__make_no_sub_mkv__and_get_log_d(clip_dir_data, fuzz_ratio, clip_process_start_time):
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
                "process_time" : get_clip_process_time(clip_process_start_time)
            }

def fuzz_ratio_0__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time):
    return {
                "clip_name": clip_dir_data.clip_name,
                "clip_mp4_path": clip_dir_data.mp4_path,
                "main_sub_file_path": ep_sub_data.main_sub_file_path,
                "fuzz_ratio": fuzz_ratio,
                "fail_reason": "fuzz_ratio == 0",
                "made_vid" : False,
                "ep_sub_data_find_time": ep_sub_data_find_time,
                "trim_and_re_time_real_sub_time": None,
                "process_time" : get_clip_process_time(clip_process_start_time)
            }

def normal_successful_clip_w_subs_created__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time, trim_and_re_time_real_sub_time):
    return {
                "clip_name": clip_dir_data.clip_name,
                "clip_mp4_path": clip_dir_data.mp4_path,
                "main_sub_file_path": ep_sub_data.main_sub_file_path,
                "fuzz_ratio": fuzz_ratio,
                "fail_reason": None,
                "made_vid" : True,
                "ep_sub_data_find_time": ep_sub_data_find_time,
                "trim_and_re_time_real_sub_time": trim_and_re_time_real_sub_time,
                "process_time" : get_clip_process_time(clip_process_start_time)
            }

def main():
    fsu.delete_if_exists(FINAL_MKVS_DIR_PATH)
    Path(FINAL_MKVS_DIR_PATH).mkdir(parents=True, exist_ok=True)

    # # Clean freshly downloaded subtitles
    # #   - Removes things like un-labeled spanish subs in english sub list (EX: Herbert Clip)
    # tmp_ssm_for_cleaning = Series_Sub_map()
    # tmp_ssm_for_cleaning.load_lang(SERIES_SUB_EN_DIR_PATH, LANG)
    # tmp_ssm_for_cleaning.clean_subs_after_fresh_download(LANG)

    # TODO download yt playlist with youtube_utils.dl_yt_playlist__fix_sub_times_convert_to__mp4_srt()
    # Init std subtitles for whole series data
    ssm = Series_Sub_map()
    ssm.load_lang(SERIES_SUB_EN_DIR_PATH, LANG)
    
    if ssm.get_num_episodes_in_lang == 0:
        raise Exception(f"ERROR: ssm.get_num_episodes_in_lang == 0, this means something is wrong with loading ssm from {SERIES_SUB_EN_DIR_PATH=} in {LANG=}")
    print(f"{ssm.get_num_episodes_in_lang=}") 

    # Init std youtube playlist download data
    yt_pl_dl_dir_path = os.path.join(WORKING_DIR_PATH, "Family_Guy___TBS")
    yt_pl_dl_dir_data = YT_PL_DL_Data(yt_pl_dl_dir_path)

    run_log_l = []
    fail_clip_dir_path_l = []

    for clip_dir_data in yt_pl_dl_dir_data.clip_dir_data_l:
        clip_process_start_time = time.time()

        print(f"{clip_dir_data.clip_name=}")

        if not clip_dir_data.has_subs():
            print(f"Downloaded youtube clip has no subs, creating .mkv without subtitles...")
            log_d = downloaded_yt_clip_has_no_subs__make_no_sub_mkv__and_get_log_d(clip_dir_data, clip_process_start_time)
            run_log_l.append(log_d)
            json_logger.write(run_log_l, RUN_LOG_JSON_PATH)
            continue

        # Get sub data of episode that clip comes from (found by fuzzy searching w/ auto-subs)
        ep_sub_data, fuzz_ratio, ep_sub_data_find_time = get_real_episode_sub_data_from_auto_sub(clip_dir_data.auto_sub_path, ssm, LANG)

        if ep_sub_data == None:
            print("init_mkvs - After fuzzy-searching every episode's subs, did not find single episode with fuzz_ratio > 0, creating .mkv without subtitles...")
            log_d = no_episode_sub_fuzzy_match_found__make_no_sub_mkv__and_get_log_d(clip_dir_data, fuzz_ratio, clip_process_start_time)
            run_log_l.append(log_d)
            json_logger.write(run_log_l, RUN_LOG_JSON_PATH)
            continue

        # if have non-series clips mixed in with playlist/just have very low fuzz_ratio for some reason, add to fail list and move on
        if fuzz_ratio == 0:
            log_d = fuzz_ratio_0__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time)
            run_log_l.append(log_d)
            json_logger.write(run_log_l, RUN_LOG_JSON_PATH)
            continue

        new_srt_mkv_file_path_no_ext = os.path.join(FINAL_MKVS_DIR_PATH, f"{ep_sub_data.get_season_episode_str()}__{clip_dir_data.clip_name}")
        tmp_srt_path = new_srt_mkv_file_path_no_ext + f"{LANG}.srt"
        new_mkv_path = new_srt_mkv_file_path_no_ext + f".mkv"

        trim_and_re_time_real_sub_time = trim_and_re_time_real_sub_file_from_auto_subs(vid_path = clip_dir_data.mp4_path,
                                                                                        real_sub_file_path = ep_sub_data.main_sub_file_path,
                                                                                        auto_sub_file_path = clip_dir_data.auto_sub_path,
                                                                                        out_sub_path = tmp_srt_path)
        
        subtitle_utils.combine_mp4_and_sub_into_mkv(in_mp4_path = clip_dir_data.mp4_path,
                                                    in_sub_path = tmp_srt_path,
                                                    out_mkv_path = new_mkv_path)
        fsu.delete_if_exists(tmp_srt_path)

        log_d = normal_successful_clip_w_subs_created__get_log_d(clip_dir_data, ep_sub_data, fuzz_ratio, clip_process_start_time, ep_sub_data_find_time, trim_and_re_time_real_sub_time)
        run_log_l.append(log_d)
        json_logger.write(run_log_l, RUN_LOG_JSON_PATH)


        print("run_log_l vv")
        pprint(run_log_l)


    print("final run_log_lvv")
    pprint(run_log_l)

    json_logger.write(run_log_l, RUN_LOG_JSON_PATH)
    print("Done")


if __name__ == "__main__":
    import os.path as path
    print(f"Running " , path.abspath(__file__) , '...')
    main()
    print("End of Main") 