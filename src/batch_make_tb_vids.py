import vid_edit_utils as veu
from pathlib import Path
import os
import random

from make_tb_vid import make_tb_vid

import cfg

from sms.file_system_utils import file_system_utils as fsu

# Misc.
TIK_BEST_VID_DIM_TUP = (1080,1920) # W x H

# Big Data Paths
IGNORE_DIR_PATH = os.path.join(cfg.BIG_DATA_DIR_PATH, "ignore")
PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "playlist_og_clips", "fg_pl_tbs")
FINAL_OUT_VID_DIR_PATH = os.path.join(IGNORE_DIR_PATH, "final_output")
OG_LONG_BOTTOM_VIDS = os.path.join(IGNORE_DIR_PATH, "og_long_bottom_vids")
MC_PARK_VID_PATH = os.path.join(OG_LONG_BOTTOM_VIDS, "mc_parkour_1hr_20min_Trim.mp4")

# For testing
OG_CLIPS_DIR_PATH = os.path.join(cfg.BIG_DATA_DIR_PATH, "og_clips")

####################################################################################################
# Main
####################################################################################################
def make_fg_mcpark_crop_sides_by_percent_tb_vid(crop_sides_by_percent, og_vid_path, vid_edits_dir_path):

    og_vid_file_name = fsu.get_basename_from_path(og_vid_path, include_ext = False)

    make_tb_vid(vid_dim_tup = TIK_BEST_VID_DIM_TUP,
                out_vid_path = os.path.join(vid_edits_dir_path, og_vid_file_name + f"_tsbp_{crop_sides_by_percent}.mp4"),
                top_vid_path = og_vid_path,
                bottom_vid_path = MC_PARK_VID_PATH,
                use_audio_from_str = "top",
                time_trim_bottom_vid_method_str = "from_rand_start",
                custom_edit_bottom_vid_method_str = "crop_sides",
                custom_edit_top_vid_method_str = "crop_sides_by_percent",
                crop_top_vid_sides_percent = crop_sides_by_percent)

def batch_make_tb_vids(og_vids_dir_path, out_dir_path):

    og_vid_path_l = fsu.get_dir_content_l(og_vids_dir_path, object_type = 'file', content_type = 'abs_path')
    print(og_vid_path_l)

    for og_vid_path in og_vid_path_l:

        print(f"{og_vid_path=}")
        print(f"{veu.get_vid_length(og_vid_path)=}")
        og_vid_file_name = fsu.get_basename_from_path(og_vid_path, include_ext = False)
        vid_len = int(veu.get_vid_length(og_vid_path))
        vid_edits_dir_path = os.path.join(out_dir_path, f"vl_{vid_len}__" + og_vid_file_name)

        fsu.delete_if_exists(vid_edits_dir_path)
        fsu.make_dir_if_not_exist(vid_edits_dir_path)

        # make_fg_mcpark_crop_sides_by_percent_tb_vid(5, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_crop_sides_by_percent_tb_vid(10, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_crop_sides_by_percent_tb_vid(15, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_crop_sides_by_percent_tb_vid(20, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_crop_sides_by_percent_tb_vid(25, og_vid_path, vid_edits_dir_path)
        make_fg_mcpark_crop_sides_by_percent_tb_vid(30, og_vid_path, vid_edits_dir_path)

def main():
    batch_make_tb_vids(PLAYLIST_OG_VIDS_DIR_PATH, FINAL_OUT_VID_DIR_PATH)

if __name__ == "__main__":
    main()