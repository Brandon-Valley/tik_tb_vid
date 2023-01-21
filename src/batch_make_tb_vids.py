
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait


from pprint import pprint
import random
import vid_edit_utils as veu
from pathlib import Path
import os
import random

from make_tb_vid import make_tb_vid
from vid_edit_utils import Impossible_Dims_Exception

import cfg

from sms.file_system_utils import file_system_utils as fsu

# Misc.
TIK_BEST_VID_DIM_TUP = (1080,1920) # W x H

# Big Data Paths
IGNORE_DIR_PATH           = os.path.join(cfg.BIG_DATA_DIR_PATH, "ignore")

# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "Family_Guy___TBS")
PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "man_edit_big_clips__init_to_amish__no_cuts")
# PLAYLIST_OG_VIDS_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/playlist_og_clips/fg_ns_mp4/Family_Guy___TBS"
# PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "fg_pl_tbs__single_short_test")
# PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "test_2_short")
# PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "fg_pl_tbs__10_clips_full_len_test")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "test_easy_black_boarders")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "test_chicken")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "test_harvest")
# PLAYLIST_OG_VIDS_DIR_PATH    = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "fg_pl_tbs__manual_edit_mkvs__test")
FINAL_OUT_VID_DIR_PATH       = os.path.join(IGNORE_DIR_PATH, "final_output")
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
        make_tb_vid(final_vid_dim_tup = TIK_BEST_VID_DIM_TUP,
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
        return True
    except Impossible_Dims_Exception as e:
        if ERROR_ON_IMPOSSIBLE_DIMS_EXP:
            raise(e)
        else:
            print(f"WARNING: Got Impossible_Dims_Exception from make_tb_vid().\n \
            This probably means got to crop_sides_of_vid_to_match_aspect_ratio() and turned out that given dims were impossible.\n \
            Probably caused by crop_top_vid_sides_percent ({crop_sides_by_percent}) being set too high.\n \
            This should be avoided since now all the time spent processing up to that point has been wasted.\n \
            Ending current run of make_tb_vid() and deleting {vid_edits_dir_path=} if needed...")
            fsu.delete_if_exists(vid_edits_dir_path)
    return False


####################################################################################################
# Main
####################################################################################################
def batch_make_tb_vids(og_vids_dir_path, out_dir_path):
    failed_top_vid_path_l = []

    def _st__make_vid_edits_for_single_vid(og_vid_path):
        print(f"{og_vid_path=}")
        print(f"{veu.get_vid_length(og_vid_path)=}")
        og_vid_file_name = fsu.get_basename_from_path(og_vid_path, include_ext = False)
        vid_len = int(veu.get_vid_length(og_vid_path))
        vid_edits_dir_path = os.path.join(out_dir_path, f"vl_{vid_len}__" + og_vid_file_name)

        # fsu.delete_if_exists(vid_edits_dir_path)
        # fsu.make_dir_if_not_exist(vid_edits_dir_path)

        # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(0,  og_vid_path, vid_edits_dir_path)
        # # # # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(5,  og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(10, og_vid_path, vid_edits_dir_path)
        # # # # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(15, og_vid_path, vid_edits_dir_path)
        # made_tb_vid = make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(40, og_vid_path, vid_edits_dir_path)
        made_tb_vid = make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(40, og_vid_path, out_dir_path)
        # # # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(25, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(30, og_vid_path, vid_edits_dir_path)
        # # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(35, og_vid_path, vid_edits_dir_path)

        # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(40, og_vid_path, vid_edits_dir_path)
        # # make_fg_mcpark_crop_sides_by_pref_percent_tb_vid(45, og_vid_path, vid_edits_dir_path)

        if not made_tb_vid:
            failed_top_vid_path_l.append(og_vid_path)

    # Setup
    fsu.delete_if_exists(out_dir_path)
    Path(out_dir_path).mkdir(parents=True,exist_ok=True)

    og_vid_path_l = fsu.get_dir_content_l(og_vids_dir_path, object_type = 'file', content_type = 'abs_path')
    print(og_vid_path_l)

    # Make vids in their own threads
    with ThreadPoolExecutor(cfg.NUM_CORES) as executor:
        futures = []
        for og_vid_path in og_vid_path_l:
            # submit tasks and collect futures
            futures = [executor.submit(_st__make_vid_edits_for_single_vid, og_vid_path)]
        # wait for all tasks to complete
        print('Waiting for tasks to complete...')
        wait(futures)
        print('All tasks are done!')

    # Print any fails
    print(f"{failed_top_vid_path_l=}")
    print(f"---")
    pprint(failed_top_vid_path_l)



def main():
    batch_make_tb_vids(PLAYLIST_OG_VIDS_DIR_PATH, FINAL_OUT_VID_DIR_PATH)

if __name__ == "__main__":
    main()