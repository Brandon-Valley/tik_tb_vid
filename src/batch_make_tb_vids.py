from pprint import pprint
import random
import time
import vid_edit_utils as veu
from pathlib import Path
import os
from os.path import join
import random

from make_tb_vid import make_tb_vid
from vid_edit_utils import Impossible_Dims_Exception

import cfg

from Matched_Vid_Sub_Dir import Matched_Vid_Sub_Dir

from sms.file_system_utils import file_system_utils as fsu
from sms.thread_tools.Simple_Thread_Manager import Simple_Thread_Manager


# Misc.
THREADING_ENABLED = True
TIK_BEST_VID_DIM_TUP = (1080,1920) # W x H

# Big Data Paths
IGNORE_DIR_PATH           = os.path.join(cfg.BIG_DATA_DIR_PATH, "ignore")

# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "Family_Guy___TBS")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "man_edit_big_clips__init_to_amish__no_cuts")
PLAYLIST_OG_VIDS_DIR_PATH    = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/o_mp4_srt_dirs"
# PLAYLIST_OG_VIDS_DIR_PATH    = "C:/p/tik_tb_vid_big_data/ignore/test/w_subs_no_subs_tiny_test"
# PLAYLIST_OG_VIDS_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/playlist_og_clips/fg_ns_mp4/Family_Guy___TBS"
# PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "fg_pl_tbs__single_short_test")
# PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "test_2_short")
# PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "fg_pl_tbs__10_clips_full_len_test")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "test_easy_black_boarders")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "test_chicken")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "test_harvest")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "fg_pl_tbs__manual_edit_mkvs__test")
# cfg.BATCH_TB_VIDS_OUT_DIR_PATH       = os.path.join(IGNORE_DIR_PATH, "final_output")
# FINAL_OUT_NO_SUBS_DIR_PATH = os.path.join(cfg.BATCH_TB_VIDS_OUT_DIR_PATH, "no_subs")
# FINAL_OUT_W_SUBS_DIR_PATH  = os.path.join(cfg.BATCH_TB_VIDS_OUT_DIR_PATH, "w_subs")
OG_LONG_BOTTOM_VIDS_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "og_long_bottom_vids")


# For testing
OG_CLIPS_DIR_PATH = os.path.join(cfg.BIG_DATA_DIR_PATH, "og_clips")

ERROR_ON_IMPOSSIBLE_DIMS_EXP = False


def _get_rand_bottom_vid_to_time_trim(og_long_bottom_vids_dir_path, top_vid_path):
    top_vid_len = veu.get_vid_length(top_vid_path)

    # build possible_bottom_vid_path_len_d
    possible_bottom_vid_path_len_d = {}
    
    og_long_bottom_vid_path_l = fsu.get_dir_content_l(og_long_bottom_vids_dir_path, object_type = 'file', content_type = 'abs_path')
    for og_long_bottom_vid_path in og_long_bottom_vid_path_l:
        og_long_bottom_vid_len = veu.get_vid_length(og_long_bottom_vid_path)
        
        if top_vid_len <= og_long_bottom_vid_len:
            possible_bottom_vid_path_len_d[og_long_bottom_vid_path] = og_long_bottom_vid_len

    # Make choice of bottom vid by random weighted by vid len
    # Not perfectly random for showing every part of every clip but good enough for now
    # Could probably be more efficient
    weighted_rand_choice_l = []
    for bottom_vid_path, bottom_vid_len in possible_bottom_vid_path_len_d.items():
        weighted_rand_choice_l += [bottom_vid_path] * int(bottom_vid_len)
    rand_chosen_bottom_vid_path = random.choice(weighted_rand_choice_l)
    
    print("`Randomly` choose bottom vid: ", rand_chosen_bottom_vid_path)
    return rand_chosen_bottom_vid_path

def make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(crop_sides_by_percent, og_vid_path, out_dir_path):
    og_vid_file_name = fsu.get_basename_from_path(og_vid_path, include_ext = False)
    # out_vid_path = os.path.join(vid_edits_dir_path, og_vid_file_name + f"_tsbp_{crop_sides_by_percent}.mp4")
    # out_vid_path = os.path.join(vid_edits_dir_path, og_vid_file_name + f"_tsbfd_{crop_sides_by_percent}.mp4")

    rand_chosen_bottom_vid_path = _get_rand_bottom_vid_to_time_trim(OG_LONG_BOTTOM_VIDS_DIR_PATH, top_vid_path = og_vid_path)

    try:
        new_tb_vid_path = make_tb_vid(
                    final_vid_dim_tup = TIK_BEST_VID_DIM_TUP,
                    # out_vid_path = out_vid_path,
                    out_dir_path = out_dir_path,
                    top_vid_path = og_vid_path,
                    bottom_vid_path = rand_chosen_bottom_vid_path,
                    use_audio_from_str = "top",
                    time_trim_bottom_vid_method_str = "from_rand_start",
                    custom_edit_bottom_vid_method_str = "crop_sides",
                    # custom_edit_top_vid_method_str = "crop_sides_by_percent",
                    # custom_edit_top_vid_method_str = "crop_sides_of_vid_to_match_aspect_ratio_from_exact_percent_of_final_dims",
                    custom_edit_top_vid_method_str = "crop_sides_of_vid_to_match_aspect_ratio_from_pref_percent_of_final_dims",
                    top_vid_custom_edit_percent = crop_sides_by_percent)
        return new_tb_vid_path
    except Impossible_Dims_Exception as e:
        if ERROR_ON_IMPOSSIBLE_DIMS_EXP:
            raise(e)
        else:
            print(f"WARNING: Got Impossible_Dims_Exception from make_tb_vid().\n \
            This probably means got to crop_sides_of_vid_to_match_aspect_ratio() and turned out that given dims were impossible.\n \
            Probably caused by crop_top_vid_sides_percent ({crop_sides_by_percent}) being set too high.\n \
            This should be avoided since now all the time spent processing up to that point has been wasted.\n \
            Ending current run of make_tb_vid() and deleting {out_dir_path=} if needed...")
            fsu.delete_if_exists(out_dir_path)
    return False


def _get_vid_sub_paths_data_dl__from__no_subs_dir_path(no_subs_dir_path):
    vid_file_path_l = fsu.get_dir_content_l(no_subs_dir_path, "file")

    vid_sub_paths_data_dl = []
    for vid_file_path in vid_file_path_l:
        vid_sub_paths_data_dl.append({
            "vid_path": vid_file_path,
            "sub_path": None
        })
    return vid_sub_paths_data_dl

def _get_vid_sub_paths_data_dl__from__w_subs_dir_path(w_subs_dir_path):
    vid_sub_dir_path_l = fsu.get_dir_content_l(w_subs_dir_path, "dir")
    
    mvsd_l = []
    for vid_sub_dir_path in vid_sub_dir_path_l:
        mvsd_l.append(Matched_Vid_Sub_Dir(vid_sub_dir_path))

    vid_sub_paths_data_dl = []
    for mvsd in mvsd_l:
        vid_sub_paths_data_dl.append({
            "vid_path": mvsd.vid_path,
            "sub_path": mvsd.sub_path
        })
    return vid_sub_paths_data_dl




def _get_vid_sub_paths_data_dl__from__w_subs_no_subs_parent_dir_path(in_dir_path):
    no_subs_dir_path = join(Path(in_dir_path), "no_subs")
    w_subs_dir_path = join(Path(in_dir_path), "w_subs")

    if not Path(no_subs_dir_path).is_dir() or not Path(w_subs_dir_path).is_dir():
        raise NotADirectoryError(f"Both dirs must exist: {no_subs_dir_path=} - {Path(no_subs_dir_path).is_dir()=},  {w_subs_dir_path=} - {Path(w_subs_dir_path).is_dir()=}")
    
    no_subs_vid_sub_paths_data_dl = _get_vid_sub_paths_data_dl__from__no_subs_dir_path(no_subs_dir_path)
    w_subs_vid_sub_paths_data_dl  = _get_vid_sub_paths_data_dl__from__w_subs_dir_path(w_subs_dir_path)
    total_vid_sub_paths_data_dl = w_subs_vid_sub_paths_data_dl + no_subs_vid_sub_paths_data_dl
    return total_vid_sub_paths_data_dl



####################################################################################################
# Main
####################################################################################################
def batch_make_tb_vids(og_vids_dir_path, out_w_subs_no_subs_parent_dir_path):
    start_time = time.time()
    fsu.delete_if_exists(cfg.BIG_DATA_WORKING_DIR_PATH)
    Path(cfg.BIG_DATA_WORKING_DIR_PATH).mkdir(parents=True, exist_ok=True)

    failed_top_vid_path_l = []
    out_no_subs_dir_path = join(out_w_subs_no_subs_parent_dir_path, "no_subs")
    out_w_subs_dir_path = join(out_w_subs_no_subs_parent_dir_path, "w_subs")


    def _st__make_vid_edits_for_single_vid(og_vid_path, og_sub_path = None):
        print(f"{og_vid_path=}")
        print(f"{veu.get_vid_length(og_vid_path)=}")

        # Set out_dir_path
        out_dir_path = out_no_subs_dir_path
        if og_sub_path != None:
            og_vid_file_name = fsu.get_basename_from_path(og_vid_path, include_ext = False)
            out_dir_path = join(out_w_subs_dir_path, og_vid_file_name)

        # Make TB vid
        new_tb_vid_file_path = make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(40, og_vid_path, out_dir_path)

        # If TB vid failed to create, add to fail list and return
        if not new_tb_vid_file_path:
            failed_top_vid_path_l.append(og_vid_path)
            return
        
        # If has sub, copy the original sub file to the new TB vid's dir and re-name it to the same name so it will play automatically in VLC media player
        if og_sub_path != None:
            new_tb_vid_file_stem = Path(new_tb_vid_file_path).stem
            new_sub_path = join(out_dir_path, f"{new_tb_vid_file_stem}.srt")
            print(f"Copying {og_sub_path=} to {new_sub_path=}...")
            fsu.copy_object_to_path(og_sub_path, new_sub_path)


    # Setup
    fsu.delete_if_exists(out_w_subs_no_subs_parent_dir_path)
    Path(out_w_subs_no_subs_parent_dir_path).mkdir(parents=True,exist_ok=True)

    vid_sub_paths_data_dl = _get_vid_sub_paths_data_dl__from__w_subs_no_subs_parent_dir_path(og_vids_dir_path)
    # print("vid_sub_paths_data_dl:")
    # pprint(vid_sub_paths_data_dl)

    with Simple_Thread_Manager(THREADING_ENABLED, cfg.NUM_CORES) as stm:
        for vid_sub_paths_data_d in vid_sub_paths_data_dl:
            stm.thread_func_if_enabled(_st__make_vid_edits_for_single_vid, vid_sub_paths_data_d["vid_path"], vid_sub_paths_data_d["sub_path"])
    
    # og_vid_path_l = fsu.get_dir_content_l(og_vids_dir_path, object_type = 'file', content_type = 'abs_path')
    # print(og_vid_path_l)

    # # Make vids in their own threads
    # with ThreadPoolExecutor(cfg.NUM_CORES) as executor:
    #     futures = []
    #     for og_vid_path in og_vid_path_l:
    #         # submit tasks and collect futures
    #         futures = [executor.submit(_st__make_vid_edits_for_single_vid, og_vid_path)]
    #     # wait for all tasks to complete
    #     print('Waiting for tasks to complete...')
    #     wait(futures)
    #     print('All tasks are done!')

    # Print any fails
    print("failed_top_vid_path_l:")
    pprint(failed_top_vid_path_l)
    print("Final batch_make_tb_vids() run time: ", time.time() - start_time)




def main():
    batch_make_tb_vids(PLAYLIST_OG_VIDS_DIR_PATH, cfg.BATCH_TB_VIDS_OUT_DIR_PATH)

if __name__ == "__main__":
    main()